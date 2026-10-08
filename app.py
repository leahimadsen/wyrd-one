"""The Wyrd Console — web server.

    pip install -r requirements.txt
    python scripts/build_places.py        # once: world places index
    python app.py                          # http://localhost:8000
"""
import html, hmac, json, math, os, re, time
from collections import defaultdict, deque
from datetime import datetime, timezone

from flask import Flask, abort, jsonify, request, send_from_directory, Response, redirect, session
from urllib.parse import urlencode

import config
from wyrd import engine, reading
from wyrd.places import Places
from wyrd.timefix import to_ut
from wyrd import stripe_api
from wyrd.transits import transits
from wyrd.extras import extras
from wyrd import calendar as wcal
from wyrd import pulse
import atexit

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(HERE, "static"), static_url_path="/static")
app.secret_key = config.SECRET_KEY or None
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
                  SESSION_COOKIE_SECURE=config.BASE_URL.startswith("https://"),
                  PERMANENT_SESSION_LIFETIME=12 * 3600)

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
    """Too many requests from one visitor to THIS endpoint in the last `per` seconds?
    Each endpoint keeps its own count, so browsing (place search, pulse) can never
    use up the allowance for casting a chart or opening checkout."""
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    q, now = _hits[(ip, request.endpoint)], time.time()
    while q and now - q[0] > per: q.popleft()
    q.append(now)
    return len(q) > n

def jd_now():
    return time.time() / 86400 + 2440587.5

def plain(o):
    """Skyfield hands back numpy numbers and booleans; JSON wants plain ones."""
    return json.loads(json.dumps(o, default=lambda value: value.item()))

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

# ---------------- the installable app ----------------
@app.get("/sw.js")
def service_worker():
    r = send_from_directory(app.static_folder, "sw.js", mimetype="text/javascript")
    r.headers["Cache-Control"] = "no-cache"             # browsers must always see the newest worker
    r.headers["Service-Worker-Allowed"] = "/"
    return r

@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(app.static_folder, "manifest.webmanifest", mimetype="application/manifest+json")

@app.get("/offline")
def offline():
    return send_from_directory(app.static_folder, "offline.html")

@app.get("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.static_folder, "icons"), "favicon-32.png", mimetype="image/png")

@app.get("/chart")
def chart_page():
    return send_from_directory(app.static_folder, "chart.html")

@app.get("/c/<slug>")
def consult_offer(slug):
    """The 1:1 consultation offer. Unlisted: only someone given the link finds it."""
    if not config.CONSULT_PATH or not hmac.compare_digest(slug.encode(), config.CONSULT_PATH.encode()): abort(404)
    page = open(os.path.join(HERE, "static", "consult.html"), encoding="utf-8").read()
    link = html.escape(config.CONSULTATION_PAYMENT_LINK_URL or "")
    return Response(page.replace("{{PAY_LINK}}", link).replace("{{AUTHOR}}", config.AUTHOR), mimetype="text/html")

@app.after_request
def private_reading_headers(response):
    if request.path in ("/reading", "/consultation", "/api/consultation-reading") or request.path.startswith(("/c/", "/admin")):
        response.headers["Cache-Control"] = "no-store"
        # the admin's own forms need the browser to say they came from this site
        response.headers["Referrer-Policy"] = "same-origin" if request.path.startswith("/admin") else "no-referrer"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response

def consultation_session(sid):
    """Authorize against Stripe, never against a browser's paid flag."""
    if not config.STRIPE_SECRET or not (config.CONSULTATION_PAYMENT_LINK_IDS or config.CONSULTATION_PAYMENT_LINK_URL):
        return None, ("Consultation reports are not configured yet. Please contact Leah.", 503)
    try:
        session = stripe_api.paid_session(config.STRIPE_SECRET, sid)
    except stripe_api.StripeError:
        return None, ("We couldn't verify your payment. Please try again shortly.", 502)
    if not session:
        return None, ("Payment has not been confirmed. If you just paid, keep this page and try again shortly.", 403)
    link = session.get("payment_link")
    if isinstance(link, dict): link = link.get("id")
    if session.get("status") != "complete" or session.get("mode") != "payment":
        return None, ("This checkout does not include a consultation report.", 403)
    allowed = link in config.CONSULTATION_PAYMENT_LINK_IDS
    if not allowed and config.CONSULTATION_PAYMENT_LINK_URL:
        try:
            details = stripe_api.payment_link(config.STRIPE_SECRET, link)
        except stripe_api.StripeError:
            return None, ("We couldn't verify your payment link. Please try again shortly.", 502)
        allowed = bool(details and details.get("url") == config.CONSULTATION_PAYMENT_LINK_URL)
    if not allowed:
        return None, ("This checkout does not include a consultation report.", 403)
    return session, None

def reading_url(sid):
    return "/reading?" + urlencode({"session_id": sid})

@app.get("/consultation")
def consultation():
    if limited(60): return "Too many requests — wait a minute.", 429
    sid = request.args.get("session_id", "")
    session, error = consultation_session(sid)
    if error: return error
    if session.get("metadata", {}).get("wyrd_report_ready") == "1":
        return redirect(reading_url(sid))
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/consultation-reading")
def consultation_reading():
    if limited(10): return jsonify(error="Too many requests — wait a minute."), 429
    data = request.get_json(silent=True)
    if not isinstance(data, dict): return jsonify(error="Please submit your birth details."), 400
    sid = data.get("session_id", "")
    session, error = consultation_session(sid)
    if error: return jsonify(error=error[0]), error[1]
    # A retry or return visit opens the saved report instead of replacing its birth data.
    if session.get("metadata", {}).get("wyrd_report_ready") == "1":
        return jsonify(url=reading_url(sid))
    try:
        # Resolve location on the server rather than trusting coordinates from the browser.
        clean = {k: data.get(k) for k in ("date", "time", "place_id")}
        birth = birth_from(clean)
        name = data.get("name") or ""
        if not isinstance(name, str): raise BadInput("Please enter a name as text.")
    except (BadInput, ValueError, TypeError, OverflowError) as e:
        message = str(e) if isinstance(e, BadInput) else "Choose a valid birthplace from the list."
        return jsonify(error=message), 400
    place = birth["place"]
    meta = {"name": name.strip()[:80], "date": clean["date"], "time": clean["time"],
            "place_id": place["id"], "place_label": place["label"],
            "lat": place["lat"], "lon": place["lon"], "tz": place["tz"],
            "wyrd_report_ready": "1"}
    try:
        stripe_api.save_birth_metadata(config.STRIPE_SECRET, sid, meta)
    except stripe_api.StripeError:
        return jsonify(error="Your payment is confirmed, but your details couldn't be saved. Please try again."), 502
    return jsonify(url=reading_url(sid))

@app.get("/api/places")
def places():
    if limited(120): return jsonify([]), 429
    return jsonify(PLACES.search(request.args.get("q", ""), 10))

def unknown_time(c):
    """No birth time: the chart is cast for noon and read with solar houses
    (the Sun's sign as the 1st house). The Moon can be anywhere in a day's
    travel, so report the mansions it may have stood in."""
    c["unknownTime"] = True
    c["ascS"], c["ascT"] = c["sid"]["Sun"], c["trop"]["Sun"]
    span = []
    for dt in (-0.5, 0, 0.5):
        jd = c["jd"] + dt
        name = engine.nak_of(engine.norm(EPH.positions(jd)["Moon"] - EPH.ayanamsa(jd)))
        if name not in span: span.append(name)
    c["moonSpan"] = span

@app.post("/api/chart")
def chart():
    if limited(): return jsonify(error="Too many requests — wait a minute."), 429
    d = request.get_json(force=True) or {}
    try:
        b = birth_from(d)
    except BadInput as e:
        return jsonify(error=str(e)), 400
    c = cast_for(b)
    if d.get("unknown_time"): unknown_time(c)
    now = jd_now()
    c["dashaTree"] = engine.dasha_tree(c, now)
    c["transits"] = transits(EPH, c, now)
    c["extras"] = extras(EPH, c, b)
    if c.get("unknownTime"): c["extras"]["placidus"] = None     # house cusps need a birth time
    return jsonify(chart=plain(c), place=b["place"], utc=b["ut"]["label"], ephemeris=EPH_NAME)

# ---------------- what's coming, today, and the sample reading ----------------
_cal_cache, _today_cache = {}, {}

@app.post("/api/calendar")
def calendar_api():
    if limited(10): return jsonify(error="Too many requests — wait a minute."), 429
    d = request.get_json(force=True) or {}
    try:
        b = birth_from(d)
    except BadInput as e:
        return jsonify(error=str(e)), 400
    start = math.floor(jd_now() - 0.5) + 0.5             # today, 0h UT
    key = (b["y"], b["mo"], b["d"], b["hh"], b["mi"], b["place"]["lat"], b["place"]["lon"], bool(d.get("unknown_time")), start)
    if key not in _cal_cache:
        c = cast_for(b)
        if d.get("unknown_time"): unknown_time(c)
        if len(_cal_cache) > 500: _cal_cache.clear()
        _cal_cache[key] = plain(wcal.year_for(EPH, c, start))
    return jsonify(start=start, events=_cal_cache[key])

@app.get("/api/today")
def today_api():
    if limited(120): return jsonify(error="Too many requests — wait a minute."), 429
    slot = int(time.time() // 900)                       # recomputed every 15 minutes
    if _today_cache.get("slot") != slot:
        _today_cache.update(slot=slot, data=plain(wcal.today(EPH, jd_now())))
    return jsonify(_today_cache["data"])

@app.get("/today")
def today_page():
    return send_from_directory(app.static_folder, "today.html")

# A public sample reading, so people can see what they would be buying.
# A made-up birth, not a real person: edit freely.
SAMPLE = {"name": "A sample chart", "date": "1988-09-23", "time": "06:40",
          "lat": 64.1466, "lon": -21.9426, "tz": "Atlantic/Reykjavik", "place_label": "Reykjavík, Iceland", "place_id": None}
_sample_page = {}

@app.get("/sample")
def sample_reading():
    if "page" not in _sample_page:
        _sample_page["page"] = render_reading(SAMPLE, "SAMPLE READING — this is a made-up chart, so you can see what a reading looks like. "
                                                      "<a href=\"/\" style=\"color:#fff\">Cast yours →</a>").get_data(as_text=True)
    return Response(_sample_page["page"], mimetype="text/html")

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
        if s.get("payment_link"):
            s, error = consultation_session(sid)
            if error: return error
            if s.get("metadata", {}).get("wyrd_report_ready") != "1":
                return redirect("/consultation?" + urlencode({"session_id": sid}))
        meta = s.get("metadata", {})
    try:
        return render_reading(meta, "PREVIEW — no payment taken" if request.args.get("preview") else "")
    except BadInput:
        abort(400)

def render_reading(meta, banner=""):
    """The full reading page for a set of birth details. Used by the paid flow,
    the sample and the private admin, so all three are always the same reading."""
    b = birth_from(meta)
    c = cast_for(b)
    body = reading.build(c, engine.dasha_tree(c, jd_now()), meta)
    who = html.escape(meta.get("name") or "")
    born = f"{b['y']:04d}-{b['mo']:02d}-{b['d']:02d} · {b['hh']:02d}:{b['mi']:02d} ({b['ut']['label']}) · {html.escape(b['place']['label'])}"
    page = open(os.path.join(HERE, "static", "reading.html"), encoding="utf-8").read()
    return Response(page.replace("{{TITLE}}", config.SITE_TITLE).replace("{{WHO}}", who or "Your reading")
                        .replace("{{BORN}}", born).replace("{{OPENING}}", config.READING_OPENING)
                        .replace("{{CLOSING}}", config.READING_CLOSING).replace("{{AUTHOR}}", config.AUTHOR)
                        .replace("{{PREVIEW}}", banner).replace("{{BODY}}", body), mimetype="text/html")

# ---------------- the private admin ----------------
_login_tries = defaultdict(deque)

def admin_on():
    return bool(config.ADMIN_PASSWORD and config.SECRET_KEY)

def is_admin():
    return admin_on() and session.get("admin") is True

def same_origin():
    """A form posted from this site, not another one."""
    site = request.headers.get("Sec-Fetch-Site")          # modern browsers say so directly
    if site: return site == "same-origin"
    src = request.headers.get("Origin") or request.headers.get("Referer") or ""
    return src.startswith(request.host_url.rstrip("/"))

def admin_page(name, **fill):
    page = open(os.path.join(HERE, "static", name), encoding="utf-8").read()
    for k, v in fill.items(): page = page.replace("{{" + k + "}}", v)
    return Response(page, mimetype="text/html")

@app.get("/admin")
def admin():
    if not admin_on(): abort(404)
    if not is_admin(): return admin_page("admin-login.html", ERROR="")
    return admin_page("admin.html")

@app.post("/admin/login")
def admin_login():
    if not admin_on(): abort(404)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    q, now = _login_tries[ip], time.time()
    while q and now - q[0] > 900: q.popleft()
    if len(q) >= 8:
        return admin_page("admin-login.html", ERROR="Too many tries. Wait fifteen minutes."), 429
    pw = request.form.get("password", "")
    if not same_origin() or not hmac.compare_digest(pw.encode(), config.ADMIN_PASSWORD.encode()):
        q.append(now)
        return admin_page("admin-login.html", ERROR="That password isn't right."), 401
    session.clear(); session["admin"] = True; session.permanent = True
    return redirect("/admin")

@app.post("/admin/logout")
def admin_logout():
    if same_origin(): session.clear()
    return redirect("/admin")

@app.post("/admin/reading")
def admin_reading():
    if not is_admin() or not same_origin(): abort(404)
    meta = {k: request.form.get(k, "") for k in ("name", "date", "time", "place_id", "lat", "lon", "tz", "place_label")}
    if not meta["lat"]: meta.pop("lat"); meta.pop("lon"); meta.pop("tz")
    try:
        return render_reading(meta, "Generated in your admin — no payment taken. Save it as a PDF from your browser's print menu.")
    except (BadInput, ValueError) as e:
        return admin_page("admin.html").get_data(as_text=True).replace(
            '<p class="err" id="admErr" role="alert"></p>', f'<p class="err" id="admErr" role="alert">{html.escape(str(e) or "Check the details.")}</p>'), 400

# ---------------- pulse: anonymous counts, so the console notices what people use ----------------
atexit.register(pulse.flush)
_next_cache = {"at": 0, "data": {}}

@app.post("/api/pulse")
def pulse_in():
    if limited(120) or (request.content_length or 0) > 8000: return "", 204
    try:
        d = json.loads(request.get_data(as_text=True) or "{}")
        pulse.record(d.get("e") or [], str(d.get("v") or ""))
    except (ValueError, AttributeError, TypeError):
        pass
    return "", 204

@app.get("/api/pulse/next")
def pulse_next():
    if time.time() - _next_cache["at"] > 600:
        try: _next_cache.update(at=time.time(), data=pulse.next_lands())
        except Exception: _next_cache["at"] = time.time()
    r = jsonify(_next_cache["data"]); r.headers["Cache-Control"] = "public, max-age=600"
    return r

@app.get("/admin/insights")
def admin_insights():
    if not is_admin(): return redirect("/admin")
    return admin_page("admin-insights.html", DATA=json.dumps(pulse.data()).replace("<", "\\u003c"),
                      SAVING="saved to GitHub every ten minutes" if pulse.TOKEN else "kept in memory only: set GITHUB_TOKEN in Render to keep them")

@app.post("/admin/insights/save")
def admin_insights_save():
    if not is_admin() or not same_origin(): abort(404)
    pulse.flush()
    return redirect("/admin/insights")

@app.get("/healthz")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
