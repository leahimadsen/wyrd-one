"""The Wyrd Console — web server.

    pip install -r requirements.txt
    python scripts/build_places.py        # once: world places index
    python app.py                          # http://localhost:8000
"""
import html, json, os, re, time
from collections import defaultdict, deque
from datetime import datetime, timezone

from flask import Flask, abort, jsonify, request, send_from_directory, Response

import config
from wyrd import engine, reading
from wyrd.places import Places
from wyrd.timefix import to_ut
from wyrd import stripe_api
from wyrd.transits import transits

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(HERE, "static"), static_url_path="/static")

# ---------------- ephemeris ----------------
def _load_ephemeris():
    try:
        from wyrd.ephemeris import Ephemeris
        return Ephemeris(config.DATA_DIR, config.EPHEMERIS_FILE), "NASA JPL DE440"
    except ImportError:
        if os.environ.get("WYRD_DEV_NODE_EPH"):        # local testing without Skyfield only
            from tests.verify_engine import NodeEph
            return NodeEph(), "console built-in (DEV ONLY)"
        raise
EPH, EPH_NAME = _load_ephemeris()

_db = os.path.join(config.DATA_DIR, "places.db")
PLACES = Places(_db if os.path.exists(_db) else os.path.join(config.DATA_DIR, "places-sample.db"))

# ---------------- small helpers ----------------
_hits = defaultdict(deque)
def limited(n=40, per=60):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    q, now = _hits[ip], time.time()
    while q and now - q[0] > per: q.popleft()
    q.append(now)
    return len(q) > n

def jd_now():
    return time.time() / 86400 + 2440587.5

class BadInput(Exception):
    pass

def birth_from(d):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(d.get("date", "")))
    t = re.fullmatch(r"(\d{1,2}):(\d{2})", str(d.get("time", "")))
    if not m or not t: raise BadInput("Please give a date and a time.")
    y, mo, dd = map(int, m.groups()); hh, mi = map(int, t.groups())
    if not (config.YEAR_MIN <= y <= config.YEAR_MAX): raise BadInput(f"Years {config.YEAR_MIN}–{config.YEAR_MAX} only.")
    try: datetime(y, mo, dd, hh, mi)
    except ValueError: raise BadInput("That date or time doesn't exist.")
    if d.get("lat") is not None and d.get("tz"):
        place = {"id": d.get("place_id"), "lat": float(d["lat"]), "lon": float(d["lon"]),
                 "tz": d["tz"], "label": d.get("place_label", "")}
    else:
        place = PLACES.get(d.get("place_id") or 0)
        if not place: raise BadInput("Choose your birthplace from the list.")
    ut = to_ut(y, mo, dd, hh, mi, place["tz"])
    return {"y": y, "mo": mo, "d": dd, "hh": hh, "mi": mi, "place": place, "ut": ut}

def cast_for(b):
    u = b["ut"]
    chart = engine.cast(EPH, u["y"], u["mo"], u["d"], u["h"], b["place"]["lat"], b["place"]["lon"], jd_now())
    return chart

# ---------------- pages ----------------
@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/places")
def places():
    if limited(120): return jsonify([]), 429
    return jsonify(PLACES.search(request.args.get("q", ""), 10))

@app.post("/api/chart")
def chart():
    if limited(): return jsonify(error="Too many requests — wait a minute."), 429
    try:
        b = birth_from(request.get_json(force=True) or {})
    except BadInput as e:
        return jsonify(error=str(e)), 400
    c = cast_for(b)
    now = jd_now()
    c["dashaTree"] = engine.dasha_tree(c, now)
    c["transits"] = transits(EPH, c, now)
    return jsonify(chart=c, place=b["place"], utc=b["ut"]["label"], ephemeris=EPH_NAME)

@app.post("/api/checkout")
def checkout():
    if limited(10): return jsonify(error="Too many requests — wait a minute."), 429
    d = request.get_json(force=True) or {}
    try:
        b = birth_from(d)
    except BadInput as e:
        return jsonify(error=str(e)), 400
    meta = {"name": (d.get("name") or "").strip()[:80], "date": d["date"], "time": d["time"],
            "place_id": b["place"]["id"], "place_label": b["place"]["label"],
            "lat": b["place"]["lat"], "lon": b["place"]["lon"], "tz": b["place"]["tz"]}
    if config.DEV_PREVIEW:
        from urllib.parse import urlencode
        return jsonify(url="/reading?" + urlencode({"preview": 1, **meta}))
    try:
        s = stripe_api.create_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL,
                                       price_id=config.STRIPE_PRICE_ID, price_cents=config.PRICE_CENTS,
                                       product_name=config.PRODUCT_NAME, metadata=meta,
                                       email=(d.get("email") or None))
    except stripe_api.StripeError as e:
        app.logger.error("stripe: %s", e)
        return jsonify(error="Payment couldn't start. Please try again."), 502
    return jsonify(url=s["url"])

@app.get("/reading")
def paid_reading():
    if request.args.get("preview") and config.DEV_PREVIEW:
        meta = request.args.to_dict()
    else:
        sid = request.args.get("session_id", "")
        try:
            s = stripe_api.paid_session(config.STRIPE_SECRET, sid) if config.STRIPE_SECRET else None
        except stripe_api.StripeError:
            s = None
        if not s: abort(404)
        meta = s.get("metadata", {})
    try:
        b = birth_from(meta)
    except BadInput:
        abort(400)
    c = cast_for(b)
    body = reading.build(c, engine.dasha_tree(c, jd_now()), meta)
    who = html.escape(meta.get("name") or "")
    born = f"{b['y']:04d}-{b['mo']:02d}-{b['d']:02d} · {b['hh']:02d}:{b['mi']:02d} ({b['ut']['label']}) · {html.escape(b['place']['label'])}"
    page = open(os.path.join(HERE, "static", "reading.html"), encoding="utf-8").read()
    return Response(page.replace("{{TITLE}}", config.SITE_TITLE).replace("{{WHO}}", who or "Your reading")
                        .replace("{{BORN}}", born).replace("{{OPENING}}", config.READING_OPENING)
                        .replace("{{CLOSING}}", config.READING_CLOSING).replace("{{AUTHOR}}", config.AUTHOR)
                        .replace("{{PREVIEW}}", "PREVIEW — no payment taken" if request.args.get("preview") else "")
                        .replace("{{BODY}}", body), mimetype="text/html")

@app.get("/healthz")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
