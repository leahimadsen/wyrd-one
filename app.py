"""The Wyrd Console — web server.

    pip install -r requirements.txt
    python scripts/build_places.py        # once: world places index
    python app.py                          # http://localhost:8000
"""
import html, hmac, json, math, os, re, time
from collections import defaultdict, deque
from datetime import date, datetime, timedelta, timezone

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
from wyrd import accounts, billing, mailer, pages, weather, store
from wyrd import together, together_more, sukuyo
import atexit

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(HERE, "static"), static_url_path="/static")
app.secret_key = config.SECRET_KEY or None
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
                  SESSION_COOKIE_SECURE=config.BASE_URL.startswith("https://"),
                  PERMANENT_SESSION_LIFETIME=30 * 86400)     # members stay signed in a month; the admin, 12 hours (is_admin)
ADMIN_HOURS = 12

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
    from wyrd import testimonials
    t = open(os.path.join(app.static_folder, "index.html"), encoding="utf-8").read()
    return Response(t.replace("<!--TESTIMONIALS-->", testimonials.render("home")), mimetype="text/html")

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

PRIVATE_PATHS = ("/c/", "/admin", "/gift/", "/welcome", "/account", "/signin", "/auth/", "/signout", "/pro", "/billing", "/api/subscribe", "/api/account", "/jobs/", "/hall", "/api/hall", "/r/")

@app.after_request
def private_reading_headers(response):
    if request.path in ("/reading", "/consultation", "/api/consultation-reading") or request.path.startswith(PRIVATE_PATHS):
        response.headers["Cache-Control"] = "no-store"
        # the admin's own forms need the browser to say they came from this site
        response.headers["Referrer-Policy"] = "same-origin" if request.path.startswith("/admin") else "no-referrer"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response

def consultation_session(sid):
    """Authorize against Stripe, never against a browser's paid flag."""
    if not config.STRIPE_SECRET or not (config.CONSULTATION_PAYMENT_LINK_IDS or config.CONSULTATION_PAYMENT_LINK_URL):
        return None, ("Consultation reports are not configured yet. Please write to support@wyrdconsole.com.", 503)
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
    if isinstance(data.get("full_name"), str) and data["full_name"].strip(): meta["full_name"] = data["full_name"].strip()[:80]
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
    c["navAsc"] = None                                    # the noon angles mean nothing: leave them out
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
    c["lex"] = lexicon(c)
    from wyrd import story, reading
    c["teaser"] = story.opening(c, c["dashaTree"], d.get("name", ""), reading.ENG)     # the reading's opening, as a taste
    from wyrd import medical
    c["bodyMap"] = medical.free(c)                                                     # the stations on the body, without the detail
    c["v"] = CHART_V
    return jsonify(chart=plain(c), place=b["place"], utc=b["ut"]["label"], ephemeris=EPH_NAME)

CHART_V = 6      # bump when a cast changes meaning (2: sidereal Dharma Design, 3: the vargas words, 4: the story's opening, 5: the body figure, 6: the pale engraving); common.js CHART_V must match

def lexicon(c):
    """The words the free pages need for this chart: each of its gates (name, title, a first line from the
    register, as on the public learning pages), the quality of each mansion, and the rune meanings."""
    from wyrd import pages as P
    gates = set()
    for rave in (c["natal"], c.get("dharma") or {}):
        for side in ("personality", "design"):
            for v in (rave.get(side) or {}).values():
                if isinstance(v, dict) and "gate" in v: gates.add(v["gate"])
    reg = P.C["REGISTER"]
    return {"gate": {str(g): {"name": P.C["GATE_NAME"].get(str(g), ""), "title": reg.get(str(g), {}).get("t", ""),
                              "gist": P.first(reg.get(str(g), {}).get("l"))} for g in sorted(gates)},
            "nak": [n[6] for n in P.C["NAKSHATRA"]],
            "rune": P.X["RUNES"],
            "vargas": VARGA_WORDS, "houseLife": P.X["HOUSE_LIFE"],
            "karakamsa": karakamsa_wish(c)}

VARGA_WORDS = json.load(open(os.path.join(HERE, "lib", "vargas.json"), encoding="utf-8"))

def karakamsa_wish(c):
    """The soul's wish for this chart's karakamsa (the Atmakaraka's navamsa sign), from lib/karakas.json."""
    from wyrd import reading_more as M
    ak = c["karaka"]["Atmakaraka"]; s = int(engine.norm(9 * c["sid"][ak]) // 30)
    w = M.KA["KARAKAMSA"][s].split(": ", 1)[-1]
    return w[:1].upper() + w[1:]

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


@app.get("/mandala")
def mandala_page():
    return send_from_directory(app.static_folder, "mandala.html")

# A public sample reading, so people can see what they would be buying.
# A made-up birth, not a real person: edit freely.
SAMPLE = {"name": "A sample chart", "date": "1988-09-23", "time": "06:40",
          "lat": 64.1466, "lon": -21.9426, "tz": "Atlantic/Reykjavik", "place_label": "Reykjavík, Iceland", "place_id": None}
_sample_page = {}

@app.get("/sample")
def sample_reading():
    if "page" not in _sample_page:
        _sample_page["page"] = render_reading(SAMPLE, "SAMPLE READING — this is a made-up chart, so you can see what a reading looks like. "
                                                      "<a href=\"/\" style=\"color:#fff\">Cast yours →</a>", sample=True).get_data(as_text=True)
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
    if d.get("unknown_time"): meta["unknown_time"] = "1"
    if isinstance(d.get("full_name"), str) and d["full_name"].strip(): meta["full_name"] = d["full_name"].strip()[:80]   # for the name's numbers
    if config.DEV_PREVIEW:
        from urllib.parse import urlencode
        return jsonify(url="/reading?" + urlencode({"preview": 1, **meta}))
    email, member, customer = signed_in(), False, None
    try:
        if email:
            st = billing.status(config.STRIPE_SECRET, email)
            member, customer = st["member"] or st["pro"], st["customer"]
        s = stripe_api.create_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL,
                                       price_id=None if member else config.STRIPE_PRICE_ID,
                                       price_cents=config.MEMBER_READING_CENTS if member else config.PRICE_CENTS,
                                       product_name=config.PRODUCT_NAME + (" (Order price)" if member else ""), metadata=meta,
                                       email=email or (d.get("email") or None), customer=customer)
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
        banner = "PREVIEW — no payment taken" if request.args.get("preview") else ""
        if meta.get("kind") == "together": return render_together(meta, banner)
        return render_reading(meta, banner)
    except BadInput:
        abort(400)

def render_reading(meta, banner="", sample=False):
    """The full reading page for a set of birth details. Used by the paid flow,
    the sample and the private admin, so all three are always the same reading."""
    b = birth_from(meta)
    c = cast_for(b)
    if str(meta.get("unknown_time", "")) in ("1", "true", "True", "on"):
        c = dict(c); c["sid"], c["trop"] = dict(c["sid"]), dict(c["trop"]); unknown_time(c)
    body = reading.build(c, engine.dasha_tree(c, jd_now()), meta)
    body = reading.contents(body) + body
    who = html.escape(meta.get("name") or "")
    born = f"{b['y']:04d}-{b['mo']:02d}-{b['d']:02d} · {b['hh']:02d}:{b['mi']:02d} ({b['ut']['label']}) · {html.escape(b['place']['label'])}"
    page = open(os.path.join(HERE, "static", "reading.html"), encoding="utf-8").read()
    return Response(page.replace("{{TITLE}}", config.SITE_TITLE).replace("{{WHO}}", who or "Your reading")
                        .replace("{{BORN}}", born).replace("{{OPENING}}", config.READING_OPENING)
                        .replace("{{CLOSING}}", config.READING_CLOSING).replace("{{AUTHOR}}", config.AUTHOR)
                        .replace("{{PREVIEW}}", banner).replace("{{BODY}}", body)
                        .replace("{{FOOTER}}", SAMPLE_FOOT if sample else f"<footer>Written by {config.AUTHOR} · The Web of Wyrd. This page is your reading; it stays at this address.</footer>"),
                    mimetype="text/html")

# ---------------- the reading together: two to nine people ----------------
def together_cents(n, member=False):
    """$22 for two, $11 for each person after that; members take TOGETHER_MEMBER_OFF percent off."""
    cents = config.TOGETHER_CENTS + config.TOGETHER_EXTRA_CENTS * max(0, n - 2)
    return cents * (100 - config.TOGETHER_MEMBER_OFF) // 100 if member else cents

def pack_person(d, b):
    """One person's birth, small enough for one Stripe metadata value (500 characters)."""
    p = {"n": (d.get("name") or "").strip()[:40], "d": d["date"], "t": d["time"], "la": round(b["place"]["lat"], 4),
         "lo": round(b["place"]["lon"], 4), "tz": b["place"]["tz"], "pl": (b["place"]["label"] or "")[:80]}
    if d.get("unknown_time"): p["u"] = 1
    if isinstance(d.get("full_name"), str) and d["full_name"].strip(): p["fn"] = d["full_name"].strip()[:80]   # for the numbers
    return json.dumps(p, ensure_ascii=False, separators=(",", ":"))

def unpack_person(v):
    p = json.loads(v)
    meta = {"name": p.get("n", ""), "date": p["d"], "time": p["t"], "lat": p["la"], "lon": p["lo"], "tz": p["tz"], "place_label": p.get("pl", "")}
    if p.get("u"): meta["unknown_time"] = "1"
    if p.get("fn"): meta["full_name"] = p["fn"]
    return meta

def together_people(meta):
    try:
        n = int(meta.get("people", 0))
        if not 2 <= n <= together.MAX_PEOPLE: raise ValueError
        return [unpack_person(meta[f"p{i}"]) for i in range(1, n + 1)]
    except (KeyError, ValueError, TypeError):
        raise BadInput("This reading's details are missing.")

@app.post("/api/checkout-together")
def checkout_together():
    if limited(10): return jsonify(error="Too many requests — wait a minute."), 429
    d = request.get_json(force=True, silent=True) or {}
    people = d.get("people") if isinstance(d.get("people"), list) else []
    if not 2 <= len(people) <= together.MAX_PEOPLE:
        return jsonify(error=f"A reading together is for two to {together.MAX_PEOPLE} people."), 400
    meta = {"kind": "together", "people": str(len(people))}
    for i, x in enumerate(people, 1):
        if not isinstance(x, dict): return jsonify(error="Check everyone's birth details."), 400
        try: meta[f"p{i}"] = pack_person(x, birth_from(x))
        except (BadInput, ValueError) as e:
            return jsonify(error=f"{(x.get('name') or f'Person {i}')[:40]}: {e or 'check the birth details.'}"), 400
    if config.DEV_PREVIEW:
        return jsonify(url="/reading?" + urlencode({"preview": 1, **meta}))
    email, member, customer = signed_in(), False, None
    try:
        if email:
            st = billing.status(config.STRIPE_SECRET, email)
            member, customer = st["member"] or st["pro"], st["customer"]
        s = stripe_api.create_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL, price_id=None,
                                       price_cents=together_cents(len(people), member),
                                       product_name=f"{config.TOGETHER_NAME}, for {len(people)}" + (" (Order price)" if member else ""),
                                       metadata=meta, email=email, customer=customer, cancel="/chart?cancelled=1#compare")
    except stripe_api.StripeError as e:
        app.logger.error("stripe: %s", e)
        return jsonify(error="Payment couldn't start. Please try again."), 502
    return jsonify(url=s["url"])

def render_together(meta, banner=""):
    people = []
    for m in together_people(meta):
        b = birth_from(m); c = cast_for(b)
        if m.get("unknown_time"): c = dict(c); c["sid"], c["trop"] = dict(c["sid"]), dict(c["trop"]); unknown_time(c)
        try: shuku = sukuyo.birth_shuku(EPH, b["y"], b["mo"], b["d"])       # for the bond by the lunar mansions
        except Exception: shuku = None
        people.append({"name": m["name"] or f"Person {len(people) + 1}", "C": c, "dasha": engine.dasha_tree(c, jd_now()), "b": b, "shuku": shuku,
                       "date": m["date"], "full_name": m.get("full_name", ""), "marks": together_more.sky_marks(EPH, c, jd_now())})
    body = together.build(people)
    body = reading.contents(body) + body
    who = html.escape(together.names_line([p["name"] for p in people]))
    born = " · ".join(f"{html.escape(p['name'])}, {p['b']['y']:04d}-{p['b']['mo']:02d}-{p['b']['d']:02d}" for p in people)
    page = open(os.path.join(HERE, "static", "reading.html"), encoding="utf-8").read()
    return Response(page.replace("{{TITLE}}", config.SITE_TITLE).replace("{{WHO}}", who)
                        .replace("{{BORN}}", born).replace("{{OPENING}}", together.T["OPENING"])
                        .replace("{{CLOSING}}", together.T["CLOSING"]).replace("{{AUTHOR}}", config.AUTHOR)
                        .replace("{{PREVIEW}}", banner).replace("{{BODY}}", body)
                        .replace("{{FOOTER}}", f"<footer>Written by {config.AUTHOR} · The Web of Wyrd. This page is your reading together; it stays at this address.</footer>"),
                    mimetype="text/html")

SAMPLE_FOOT = f"""<footer class="sample-cta"><p><b>That was a sample, cast for a made-up birth.</b> Yours is written for your own placements, every section of it.</p>
  <p><a href="/">Cast your free chart →</a> · <a href="/reports">Get your reading, {"$" + str(config.PRICE_CENTS // 100)} →</a> · <a href="/membership">The Order →</a></p>
  <p>Written by {config.AUTHOR} · The Web of Wyrd</p></footer>"""

# ---------------- the private admin ----------------
_login_tries = defaultdict(deque)

def admin_on():
    return bool(config.ADMIN_PASSWORD and config.SECRET_KEY)

def is_admin():
    return admin_on() and session.get("admin") is True and time.time() - session.get("admin_at", 0) < ADMIN_HOURS * 3600

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
    session.clear(); session["admin"] = True; session["admin_at"] = time.time(); session.permanent = True
    return redirect("/admin")

@app.post("/admin/logout")
def admin_logout():
    if same_origin(): session.clear()
    return redirect("/admin")

@app.post("/admin/reading")
def admin_reading():
    if not is_admin() or not same_origin(): abort(404)
    meta = {k: request.form.get(k, "") for k in BIRTH_KEYS}
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

# ---------------- public pages search engines read ----------------
# the members' rooms have their own look: the Order in magenta, the Inner Circle in turquoise
ROOM_COLOR = {"order": "#2a0624", "circle": "#03262b"}

def room_of(path):
    if path == "/hall" or path.startswith("/hall/"): return "order"
    if path == "/pro" or path.startswith("/pro/"): return "circle"
    return None

def page(title, desc, body, ld="", robots="index, follow", script="", status=200):
    """A server-made page in the console's look, with its own title, description and share preview."""
    t = open(os.path.join(HERE, "static", "page.html"), encoding="utf-8").read()
    who = (f'<a href="/account">Your account</a>' if signed_in() else '<a href="/signin">Sign in</a>')
    room = room_of(request.path)
    fill = {"BODYCLASS": f"pg room room-{room}" if room else "pg paper", "THEMECOLOR": ROOM_COLOR.get(room, "#e9e1d2"),
            "TITLE": html.escape(title), "DESC": html.escape(desc), "ROBOTS": robots, "LD": ld, "BODY": body,
            "CANON": html.escape(config.BASE_URL + request.path), "BASE": html.escape(config.BASE_URL), "WHO": who, "SCRIPT": script}
    for k, v in fill.items(): t = t.replace("{{" + k + "}}", v)
    return Response(t, status=status, mimetype="text/html")

@app.errorhandler(404)
def not_found(_e):
    return private("Not found", """<h1>This page isn't here</h1>
<p class="lede">The address may have changed, or the link was cut short.</p>
<p><a class="btn-cast" href="/">Cast your free chart</a></p>
<p><a href="/reports">Readings</a> · <a href="/learn">Learn</a> · <a href="/today">Today's sky</a></p>""", status=404)

def private(title, body, script="", status=200):
    return page(title + " · The Wyrd Console", title, body, robots="noindex, nofollow", script=script, status=status)

@app.get("/googled81e0f187c4a1868.html")
def google_site_verification():
    """Google Search Console checks this file to confirm the site is The Völva's."""
    return send_from_directory(app.static_folder, "googled81e0f187c4a1868.html", mimetype="text/html")

@app.get("/robots.txt")
def robots():
    lines = ["User-agent: *", "Disallow: /admin", "Disallow: /account", "Disallow: /reading", "Disallow: /consultation",
             "Disallow: /c/", "Disallow: /pro", "Disallow: /hall", "Disallow: /r/", "Disallow: /auth/", "Disallow: /api/", f"Sitemap: {config.BASE_URL}/sitemap.xml"]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")

@app.get("/sitemap.xml")
def sitemap():
    return Response(pages.sitemap(config.BASE_URL), mimetype="application/xml")

@app.get("/reports")
def reports_page():
    return page(*pages.reports(config.BASE_URL, config.PRICE_CENTS, config.MEMBER_READING_CENTS,
                               config.MEMBER_MONTHLY_CENTS, config.MEMBER_YEARLY_CENTS, config.PRO_MONTHLY_CENTS, config.PRO_READINGS_A_MONTH,
                               config.TOGETHER_CENTS, config.TOGETHER_EXTRA_CENTS, config.TOGETHER_MEMBER_OFF))

@app.get("/learn")
def learn_page():
    return page(*pages.learn_index(config.BASE_URL))

@app.get("/learn/gates/<int:g>")
def learn_gate(g):
    p = pages.gate(config.BASE_URL, g)
    if not p: abort(404)
    return page(*p)

@app.get("/learn/nakshatras/<s>")
def learn_nakshatra(s):
    p = pages.nakshatra(config.BASE_URL, s)
    if not p: abort(404)
    return page(*p)

@app.get("/learn/runes")
def learn_runes():
    return page(*pages.runes_index(config.BASE_URL))

@app.get("/learn/runes/<s>")
def learn_rune(s):
    p = pages.rune(config.BASE_URL, s)
    if not p: abort(404)
    return page(*p)

@app.get("/learn/numbers")
def learn_numbers():
    return page(*pages.numbers_learn(config.BASE_URL))

@app.get("/learn/dharma")
def learn_dharma():
    return page(*pages.dharma_index(config.BASE_URL))

@app.get("/learn/dharma/gates/<int:g>")
def learn_dharma_gate(g):
    p = pages.dharma_gate(config.BASE_URL, g)
    if not p: abort(404)
    return page(*p)

@app.get("/learn/signs")
def learn_signs():
    return page(*pages.signs_index(config.BASE_URL))

@app.get("/learn/signs/<s>")
def learn_sign(s):
    p = pages.sign(config.BASE_URL, s)
    if not p: abort(404)
    return page(*p)

# ---------------- accounts: sign in by email link ----------------
def signed_in():
    e = session.get("email")
    return e if isinstance(e, str) and accounts.clean_email(e) else None

def selling():
    """Subscriptions are on sale once Stripe, the signing key and email are all set."""
    return bool(config.STRIPE_SECRET and config.SECRET_KEY and mailer.ready())

def account_status(email, fresh=False):
    try:
        st = billing.status(config.STRIPE_SECRET, email, fresh=fresh) if config.STRIPE_SECRET else billing._empty()
    except stripe_api.StripeError:
        return None
    if is_admin() and email == accounts.clean_email(config.OWNER_EMAIL):    # the owner, in by admin password: everything open
        st = dict(st, member=True, pro=True)
    return st

def esc(v): return html.escape(str(v))

@app.get("/api/me")
def api_me():
    email, member = signed_in(), False
    if email and config.STRIPE_SECRET:
        try:
            st = billing.status(config.STRIPE_SECRET, email); member = bool(st["member"] or st["pro"])
        except stripe_api.StripeError:
            pass
    cents = config.MEMBER_READING_CENTS if member else config.PRICE_CENTS
    r = jsonify(signedIn=bool(email), member=member, readingPrice=money(cents),
                together={"two": together_cents(2, member), "extra": together_cents(3, member) - together_cents(2, member), "max": together.MAX_PEOPLE},
                prices={"reading": money(config.PRICE_CENTS), "member": money(config.MEMBER_READING_CENTS), "together": money(together_cents(2, member)),
                        "month": money(config.MEMBER_MONTHLY_CENTS), "year": money(config.MEMBER_YEARLY_CENTS)})
    r.headers["Cache-Control"] = "no-store"
    return r

@app.get("/signin")
def signin_page():
    nxt = accounts.safe_next(request.args.get("next", "/account"))
    if signed_in(): return redirect(nxt)
    return private("Sign in", f"""<h1>Sign in</h1>
<p class="lede">No password. Type your email and we'll send you a link that signs you in.</p>
<form class="pg-form" method="post" action="/signin"><input type="hidden" name="next" value="{esc(nxt)}">
<label>Email <input name="email" type="email" required autocomplete="email" maxlength="254"></label>
<button class="btn-cast" type="submit">Email me a sign-in link</button></form>
<p class="muted">Use the same email you paid with, and your place in the Order is found automatically.</p>""")

@app.post("/signin")
def signin_send():
    if limited(6, 600) or not same_origin(): return private("Sign in", "<h1>Wait a few minutes</h1><p>Too many sign-in links were asked for. Try again shortly.</p>", status=429)
    email = accounts.clean_email(request.form.get("email"))
    if not email or not config.SECRET_KEY:
        return private("Sign in", '<h1>Check the address</h1><p>That email address doesn\'t look right. <a href="/signin">Try again</a>.</p>', status=400)
    token = accounts.make_token(config.SECRET_KEY, email, request.form.get("next", "/account"))
    link = f"{config.BASE_URL}/auth/{token}"
    sent = mailer.send(email, "Your sign-in link for the Wyrd Console",
        f'<p>Here is your link to sign in to the Wyrd Console. It works for {accounts.LINK_MINUTES} minutes.</p><p><a href="{esc(link)}">Sign in</a></p><p>If you didn\'t ask for this, ignore it.</p>',
        f"Sign in to the Wyrd Console (works for {accounts.LINK_MINUTES} minutes): {link}\n\nIf you didn't ask for this, ignore it.")
    dev = f'<p class="note-box">Email isn\'t set up on this server, so here is the link: <a href="{esc(link)}">sign in</a></p>' if (not sent and os.environ.get("WYRD_DEV_SHOW_LINKS")) else ""
    return private("Check your email", f"""<h1>Check your email</h1>
<p class="lede">We sent a sign-in link to {esc(email)}. It works for {accounts.LINK_MINUTES} minutes.</p>
<p class="muted">Nothing there? Look in spam, or <a href="/signin">send another</a>.</p>{dev}""")

@app.get("/auth/<token>")
def auth_page(token):
    email, nxt = accounts.read_token(config.SECRET_KEY, token) if config.SECRET_KEY else (None, None)
    if not email:
        return private("Sign in", '<h1>That link has expired</h1><p>Sign-in links work for twenty minutes. <a href="/signin">Get a new one</a>.</p>', status=410)
    return private("Sign in", f"""<h1>Sign in as {esc(email)}</h1>
<form class="pg-form" method="post"><button class="btn-cast" type="submit">Sign in</button></form>""")

@app.post("/auth/<token>")
def auth_go(token):
    email, nxt = accounts.read_token(config.SECRET_KEY, token) if config.SECRET_KEY else (None, None)
    if not email or not same_origin(): return redirect("/signin")
    admin = {k: session[k] for k in ("admin", "admin_at") if k in session}
    session.clear(); session.update(admin); session["email"] = email; session.permanent = True
    return redirect(nxt)

@app.post("/signout")
def signout():
    if same_origin(): session.pop("email", None)
    return redirect("/")

# ---------------- membership and professional plans ----------------
PLANS = {
    "member-month": ("member", config.MEMBER_NAME, lambda: config.MEMBER_MONTHLY_CENTS, "month", config.MEMBER_MONTHLY_PRICE),
    "member-year":  ("member", config.MEMBER_NAME + " (yearly)", lambda: config.MEMBER_YEARLY_CENTS, "year", config.MEMBER_YEARLY_PRICE),
    "pro-month":    ("pro", config.PRO_NAME, lambda: config.PRO_MONTHLY_CENTS, "month", config.PRO_MONTHLY_PRICE),
}

def money(c): return f"${c / 100:.0f}" if c % 100 == 0 else f"${c / 100:.2f}"
pages.PRICE = money(config.PRICE_CENTS)

def months_free(m, y):
    """', three months free' when the yearly price is worth saying so."""
    n = round((12 * m - y) / m) if m else 0
    return f", {['', 'one', 'two', 'three', 'four', 'five', 'six'][n]} month{'s' if n > 1 else ''} free" if 0 < n <= 6 else ""

@app.get("/order")
def order_page(): return membership_page()          # the Order's own address; /membership still works

@app.get("/inner-circle")
def inner_circle(): return redirect("/order#pro")

_SAMPLE_WEATHER = {}

def sample_weather():
    """This week's Body Weather for the sample chart, made once a week, for the Order's page."""
    week = weather.monday().isoformat()
    if week not in _SAMPLE_WEATHER:
        try: _SAMPLE_WEATHER.clear(); _SAMPLE_WEATHER[week] = weather_for(dict(SAMPLE, name=""))
        except Exception as e:
            app.logger.error("sample weather: %s", e); return ""
    return _SAMPLE_WEATHER[week]

@app.get("/membership")
def membership_page():
    on = selling()
    def buy(plan, label, lead=False):
        if not on: return '<p class="muted">Opening soon.</p>'
        return (f'<form method="post" action="/api/subscribe"><input type="hidden" name="plan" value="{plan}">'
                f'<button class="{"btn-buy" if lead else "btn-cast"}" type="submit">{label}</button></form>')
    m, y, pr = config.MEMBER_MONTHLY_CENTS, config.MEMBER_YEARLY_CENTS, config.PRO_MONTHLY_CENTS
    from wyrd import testimonials
    sample = sample_weather()
    db = store.ready()                               # promise only what can be kept
    body = f"""<div class="order-hero"><p class="hall-kicker">Join</p><h1>The Order</h1>
<p class="lede">Your design's weather, every week. A letter each Monday on how the planets move through your Birth Design and your Dharma Design,
written in The Völva's words, and a Hall of your own on the site to keep it all in.</p>
{buy("member-month", f"Join the Order for {money(m)} a month", True)}</div>

<h2>What you receive</h2>
<ul class="order-gifts">
  <li><b>Body Weather, every Monday</b>Which centres the week's sky switches on in your Birth Design and your Dharma Design, which stay open, and which of your gates it lights. The Moon's mansion day by day, the week's stations and sign changes, and the Vimshottari era and chapter you're in.</li>
  <li><b>Your chart, opened up</b>Every activated rune read in full through its mansion, and the planets set on each station of your body map.</li>
  <li><b>The Hall</b>Your room on the site: this week's letter{", every past letter kept to reread," if db else ""} and your chart one click away.</li>
  {f"<li><b>Charts for loved ones</b>Keep up to {store.KIN_MAX} charts for the people close to you and read their Body Weather each week too.</li>" if db else ""}
  <li><b>Readings for less</b>The Wyrd Reading for {money(config.MEMBER_READING_CENTS)} instead of {money(config.PRICE_CENTS)}, and {config.TOGETHER_MEMBER_OFF}% off the reading together.</li>
  <li><b>Learning the Mandala</b>The course on working with the Wyrd Mandala, included when it opens.</li>
</ul>

{f'''<h2>A taste of a letter</h2>
<p class="muted">This week's Body Weather, written for a sample chart. Yours is written for your own.</p>
<div class="order-sample"><span class="ttl">Body Weather · this week · a sample chart</span><div class="weather">{sample}</div></div>''' if sample else ""}

<h2>How it works</h2>
<ol class="order-steps">
  <li>Join below. Payment is by Stripe; you're signed in straight away.</li>
  <li>In the Hall, choose the chart your letter is written for: cast it on the front page, then come back and keep it with one press.</li>
  <li>Your first letter is waiting in the Hall at once, and a new one comes to your inbox every Monday.</li>
  {"<li>Add the people you love, and read their weather beside yours.</li>" if db else ""}
</ol>

{testimonials.render("order")}

<h2>Choose your place</h2>
<div class="plans">
  <section class="plan lead" data-line="Your weather, every week."><h2>The Order</h2><div class="price">{money(m)}<small> a month</small></div>
    <p class="muted">or {money(y)} a year{months_free(m, y)}</p>
    <ul><li>Body Weather by email every Monday, for your Birth Design and your Dharma Design</li>
      <li>Your chart opened up: every rune in full, and the planets on your body map</li>
      <li>{f"The Hall: this week's letter, every past letter, and charts for up to {store.KIN_MAX} loved ones" if db else "The Hall: this week's letter and your chart, in one place"}</li>
      <li>The Wyrd Reading for {money(config.MEMBER_READING_CENTS)}, and {config.TOGETHER_MEMBER_OFF}% off the reading together</li>
      <li>Learning the Mandala, included when it opens</li></ul>
    {buy("member-month", f"Join the Order for {money(m)} a month", True)}
    {buy("member-year", f"Or {money(y)} a year") if on else ""}</section>
  <section class="plan" id="pro" data-line="For those who read for others."><h2>The Inner Circle</h2><div class="price">{money(pr)}<small> a month</small></div>
    <ul><li>For astrologers, coaches and practitioners working with clients</li>
      {"<li>A practice desk: keep your clients, their birth details and your private notes in one place</li>" if db else ""}
      <li>The Wyrd Reading for your clients, {config.PRO_READINGS_A_MONTH} a month{", each kept in your history to reopen free" if db else ""}</li>
      {"<li>Send a reading to your client by email or a private link, prepared under your practice's name</li>" if db else ""}
      <li>This week's Body Weather for any client, as often as you like</li>
      <li>Everything in the Order</li></ul>
    {buy("pro-month", f"Join the Inner Circle for {money(pr)} a month")}
    <p class="muted">Already in the Inner Circle? <a href="/signin?next=/pro">Sign in to your practice desk</a>.</p></section>
</div>

<h2>Questions</h2>
<div class="order-faq">
  <details><summary>Do I need to know my birth time?</summary><p>Yes, for Body Weather: the centres and gates it reads depend on the time. If you only know it roughly, cast your best guess; you can change the chart your letter is written for at any time in the Hall.</p></details>
  <details><summary>What are the Birth Design and the Dharma Design?</summary><p>Your Birth Design is your bodygraph as you were issued it: the planets at your birth and about eighty-eight days before. Your Dharma Design is those same moments in the sidereal zodiac, passed through the navamsa, the ninth harmonic of dharma: the shape your life matures toward. The Order's letter reads the week through both.</p></details>
  <details><summary>Can I cancel?</summary><p>Any time, from the Hall. You keep your place until the end of the month or year you've paid for, and the free chart stays yours either way.</p></details>
  <details><summary>Can I change from the Order to the Inner Circle?</summary><p>Yes. Press the Inner Circle's button while signed in and Stripe moves your plan across, charging only the difference.</p></details>
  <details><summary>Who writes the letters?</summary><p>The Völva. Every line of interpretation in the Wyrd Console is hers; the console sets it to your chart and the week's sky.</p></details>
</div>

<p class="muted">The free chart stays free, whether or not you join the Order: the whole path, the Wyrd Mandala, Compare for up to nine people, today's sky and the year ahead.
Payments are handled by Stripe. Prefer one reading? <a href="/reports">The Wyrd Reading is {money(config.PRICE_CENTS)}, once</a>,
and <a href="/reports">the reading together</a> is {money(config.TOGETHER_CENTS)} for two ({config.TOGETHER_MEMBER_OFF}% off for the Order).</p>"""
    ld = pages._ld({"@context": "https://schema.org", "@type": "Product", "name": config.MEMBER_NAME,
                    "description": "Weekly Body Weather astrology letter for your Birth Design and Dharma Design.",
                    "brand": {"@type": "Brand", "name": "The Wyrd Console"},
                    "offers": {"@type": "Offer", "price": f"{m / 100:.2f}", "priceCurrency": "USD", "url": config.BASE_URL + "/membership"}})
    return page("Join the Order: a Weekly Astrology Letter, and the Inner Circle for Practitioners · The Wyrd Console",
                f"A weekly astrology letter for your own chart: how the week's planets move through your Birth Design and Dharma Design. {money(m)} a month or {money(y)} a year from The Völva; the Inner Circle for practitioners.",
                body, ld)

@app.post("/api/subscribe")
def subscribe():
    plan = PLANS.get(request.form.get("plan", ""))
    if not plan or not same_origin(): abort(400)
    if not selling(): return redirect("/membership")
    email = signed_in()
    if limited(10): return private("Wait a minute", "<h1>Wait a minute</h1><p>Too many tries. Try again shortly.</p>", status=429)
    tier, name, cents, interval, price_id = plan
    if not email:                                   # not signed in: straight to Stripe, which asks for the email
        try:
            s = stripe_api.subscription_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL, customer=None, tier=tier, name=name,
                                                 cents=cents(), interval=interval, success="/welcome?session_id={CHECKOUT_SESSION_ID}",
                                                 cancel="/membership", price_id=price_id or None)
        except stripe_api.StripeError as e:
            app.logger.error("stripe: %s", e)
            return private("Try again", '<h1>Payment couldn\'t start</h1><p>Please <a href="/membership">try again</a>.</p>', status=502)
        return redirect(s["url"], code=303)
    try:
        st = billing.status(config.STRIPE_SECRET, email, fresh=True)
        if st[tier]: return redirect("/account")                       # already has it
        current = next((p for p in st["plans"] if p["status"] in billing.LIVE and p["tier"] == "member"), None)
        if tier == "pro" and current and price_id:                     # a member moves up in the portal, keeping one plan
            p = stripe_api.portal(config.STRIPE_SECRET, st["customer"], config.BASE_URL + "/account?joined=1", upgrade=current["id"])
            billing.forget(email)
            return redirect(p["url"], code=303)
        cid = billing.customer_for(config.STRIPE_SECRET, email)
        s = stripe_api.subscription_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL, customer=cid, tier=tier, name=name,
                                             cents=cents(), interval=interval, success="/account?joined=1", cancel="/membership",
                                             price_id=price_id or None)
    except stripe_api.StripeError as e:
        app.logger.error("stripe: %s", e)
        return private("Try again", '<h1>Payment couldn\'t start</h1><p>Please <a href="/membership">try again</a>.</p>', status=502)
    billing.forget(email)
    return redirect(s["url"], code=303)

@app.get("/welcome")
def welcome():
    """Back from Stripe after joining. Stripe has checked the email by taking the payment; if this checkout
    made a brand-new customer, sign them straight in. If the email already belonged to someone, send a
    sign-in link instead, so typing another person's email at checkout opens nothing of theirs."""
    try:
        cs = stripe_api.checkout_session(config.STRIPE_SECRET, request.args.get("session_id", "")) if config.STRIPE_SECRET else None
    except stripe_api.StripeError:
        cs = None
    if not cs or cs.get("mode") != "subscription" or cs.get("status") != "complete": return redirect("/membership")
    cust = cs.get("customer") if isinstance(cs.get("customer"), dict) else {}
    email = accounts.clean_email((cs.get("customer_details") or {}).get("email") or cust.get("email"))
    if not email: return redirect("/signin")
    billing.forget(email)
    fresh = time.time() - (cs.get("created") or 0) < 3600
    others = [c for c in stripe_api.find_customers(config.STRIPE_SECRET, email) if c.get("id") != cust.get("id")]
    if fresh and (not others or signed_in() == email):
        admin = {k: session[k] for k in ("admin", "admin_at") if k in session}
        session.clear(); session.update(admin); session["email"] = email; session.permanent = True
        try: stripe_api.update_customer_metadata(config.STRIPE_SECRET, cust["id"], {"wyrd": "1"})
        except (stripe_api.StripeError, KeyError): pass
        # a page, not a redirect: the sign-in cookie is only sent on a navigation that starts on this site
        return private("Welcome", f"""<meta http-equiv="refresh" content="1;url=/account?joined=1">
<h1>Welcome</h1><p class="lede">Your payment went through and you're signed in as {esc(email)}.</p>
<p><a class="btn-cast" href="/account?joined=1">Go to your account</a></p>""")
    token = accounts.make_token(config.SECRET_KEY, email, "/account?joined=1")
    link = f"{config.BASE_URL}/auth/{token}"
    mailer.send(email, "The Order: sign in",
        f'<p>You\'re in the Order. <a href="{esc(link)}">Sign in to your account</a> (this link works for {accounts.LINK_MINUTES} minutes).</p>',
        f"You're in the Order. Sign in: {link}")
    return private("Welcome", f"""<h1>Welcome</h1><p class="lede">Your payment went through.</p>
<p>We've sent a sign-in link to {esc(email)}. Open it to reach your account.</p>""")

@app.post("/billing/portal")
def billing_portal():
    email = signed_in()
    if not email or not same_origin(): return redirect("/signin")
    st = account_status(email)
    if not st or not st["customer"]: return redirect("/account")
    try:
        p = stripe_api.portal(config.STRIPE_SECRET, st["customer"], config.BASE_URL + "/account")
    except stripe_api.StripeError as e:
        app.logger.error("stripe portal: %s", e)
        return private("Manage plan", '<h1>Couldn\'t open billing</h1><p>Reply to any email from us and we\'ll change it for you.</p>', status=502)
    billing.forget(email)
    return redirect(p["url"], code=303)

def chart_line(b):
    return f'{esc(b.get("name") or "Your chart")} · {esc(b.get("date"))} {esc(b.get("time"))} · {esc((b.get("place_label") or "").split(",")[0])}'

def account_page():
    """The account page for those not in the Order; members are sent to the Hall (order_routes.py)."""
    email = signed_in()
    if not email: return redirect("/signin?next=/account")
    st = account_status(email, fresh=bool(request.args.get("joined")))
    if st is None: return private("Your account", "<h1>Your account</h1><p>We couldn't reach the payment system just now. Refresh in a moment.</p>", status=503)
    rows = []
    for p in st["plans"]:
        live = p["status"] in billing.LIVE
        end = datetime.fromtimestamp(p["periodEnd"], timezone.utc).strftime("%-d %B %Y") if p.get("periodEnd") else ""
        when = (f" · ends {end}" if p["cancelAtEnd"] else f" · renews {end}") if live and end else ""
        rows.append(f'<li>{"The Inner Circle" if p["tier"] == "pro" else "The Order"} ({p.get("interval") or "month"}ly) '
                    f'<span class="status {"on" if live else "off"}">{esc(p["status"].replace("_", " "))}</span>{when}</li>')
    joined = '<p class="note-box">Welcome. Your payment went through.</p>' if request.args.get("joined") else ""
    g = st.get("gift")
    if g and g["live"]:
        rows.insert(0, f'<li>{"The Inner Circle" if g["tier"] == "pro" else "The Order"}, a gift from {esc(config.AUTHOR)}, {nice_until(g["until"])} <span class="status on">active</span></li>')
    portal_btn = '<form method="post" action="/billing/portal"><button class="alt" type="submit">Manage or cancel, change card, see receipts</button></form>' if st["plans"] else ""
    plans = f'<ul>{"".join(rows)}</ul>{portal_btn}' if rows else \
            '<p>You\'re not in the Order yet. <a href="/membership">See the Order</a>.</p>'
    member = st["member"] or st["pro"]
    chart = ""
    if member:
        b = st.get("birth")
        chart = f"""<h2>Your chart for Body Weather</h2>
<p>{chart_line(b) if b else "No chart saved yet."}</p>
<p id="useCurrent" hidden><button class="btn-cast" type="button">Use the chart open in this browser</button></p>
<p class="muted" id="noCurrent">To change it, <a href="/">cast the chart</a>, then come back here.</p>
{WEEK_LINK if b else ""}"""
    pro = f'<h2>The Inner Circle</h2><p><a href="/pro">Open your practice desk →</a> {st["proUse"]} of {config.PRO_READINGS_A_MONTH} client readings used this month.</p>' if st["pro"] else ""
    script = """<script src="/static/common.js"></script><script>
(() => { const c = WyrdCommon.current(), box = document.getElementById("useCurrent"); if (!c || !box) return;
  box.hidden = false; document.getElementById("noCurrent").hidden = true;
  box.querySelector("button").textContent = "Use " + (c.birth.name || "the chart") + " (" + c.birth.date + ") for Body Weather";
  box.querySelector("button").onclick = async () => {
    const r = await fetch("/api/account/chart", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(c.birth)});
    if (r.ok) location.reload(); else box.insertAdjacentHTML("beforeend", '<p class="err">That chart couldn\\'t be saved. Cast it again and retry.</p>');
  };
})();</script>"""
    return private("Your account", f"""<h1>Your account</h1><p class="muted">Signed in as {esc(email)}</p>{joined}
<h2>Your plan</h2>{plans}{chart}{pro}
<form method="post" action="/signout" style="margin-top:40px"><button class="alt" type="submit">Sign out</button></form>""", script=script)

WEEK_LINK = '<h2>This week</h2><p><a href="/hall">Read this week&#39;s Body Weather →</a></p>'
BIRTH_KEYS = ("name", "date", "time", "place_id", "lat", "lon", "tz", "place_label", "full_name")

@app.post("/api/account/chart")
def account_chart():
    email = signed_in()
    if not email or not same_origin(): return jsonify(error="Sign in first."), 401
    st = account_status(email)
    if not st or not (st["member"] or st["pro"]): return jsonify(error="For the Order."), 403
    d = request.get_json(force=True, silent=True) or {}
    b = {k: str(d.get(k, ""))[:80] for k in BIRTH_KEYS if d.get(k) not in (None, "")}
    try: birth_from(b)
    except (BadInput, ValueError): return jsonify(error="Those birth details don't work."), 400
    try: billing.save_birth(config.STRIPE_SECRET, email, b)
    except stripe_api.StripeError: return jsonify(error="Couldn't save just now."), 502
    return jsonify(ok=True)

def weather_for(b, start=None):
    c = cast_for(birth_from(b))
    return weather.render(weather.week(EPH, c, start), (b.get("name") or "").split(" ")[0])

@app.get("/account/weather")
def account_weather():
    return redirect("/hall")                          # old letters link here; this week now lives in the Hall

# ---------------- the professional desk ----------------
BAD_BIRTH = "Those birth details don't work."

def pro_or_redirect():
    email = signed_in()
    if not email: return None, redirect("/membership#pro")       # what Professional is, with a sign-in link for those who have it
    st = account_status(email)
    if not st or not st["pro"]: return None, redirect("/membership#pro")
    return (email, st), None

@app.post("/pro/reading")
def pro_reading():
    who, bounce = pro_or_redirect()
    if bounce or not same_origin(): return bounce or abort(403)
    email, st = who
    meta = {k: request.form.get(k, "") for k in BIRTH_KEYS}
    if not meta["lat"]: meta.pop("lat"); meta.pop("lon"); meta.pop("tz")
    kind = request.form.get("kind", "reading")
    try:
        birth_from(meta)
        if kind == "weather":
            return private("Body Weather", f'<div class="weather">{weather_for(meta)}</div>')
        if st["proUse"] >= config.PRO_READINGS_A_MONTH:
            return private("Practice desk", f'<h1>This month\'s readings are used</h1><p>Your plan includes {config.PRO_READINGS_A_MONTH} client readings a month. They renew on the 1st.</p>', status=402)
        billing.count_pro_reading(config.STRIPE_SECRET, email)
        return render_reading(meta, "Prepared in the Inner Circle of The Wyrd Console · written by The Völva. Save it as a PDF from your browser's print menu.")
    except (BadInput, ValueError) as e:
        return private("Practice desk", f'<h1>Check the details</h1><p>{esc(str(e) or BAD_BIRTH)} <a href="/pro">Back</a></p>', status=400)
    except stripe_api.StripeError:
        return private("Practice desk", '<h1>Try again</h1><p>We couldn\'t reach the payment system. <a href="/pro">Back</a></p>', status=502)

# ---------------- gifts, from the admin only ----------------
from itsdangerous import URLSafeTimedSerializer, BadSignature as _BadSig
GIFT_READING_DAYS = 730
GIFT_LENGTHS = {"30d": "30 days", "1": 1, "3": 3, "6": 6, "12": 12, "forever": None}
GIFT_DEFAULT = "30d"            # complimentary access for creators: no card, nothing charged

def gift_signer():
    return URLSafeTimedSerializer(config.SECRET_KEY, salt="wyrd-gift-reading")

def admin_only():
    if not is_admin(): abort(404)
    if request.method == "POST" and not same_origin(): abort(403)

def gift_until(choice, today=None):
    """The gift's last day (YYYY-MM-DD, UTC) or "forever". It works through that whole day
    and has ended the day after."""
    d = today or date.fromisoformat(billing.today())      # the same clock the gift is checked against
    if choice == "30d": return (d + timedelta(days=30)).isoformat()
    months = GIFT_LENGTHS.get(choice, 12)
    if months is None: return "forever"
    y, m = divmod(d.month - 1 + months, 12)
    import calendar as _cal
    return f"{d.year + y:04d}-{m + 1:02d}-{min(d.day, _cal.monthrange(d.year + y, m + 1)[1]):02d}"

def nice_until(u):
    return "for good" if u == "forever" else "until the end of " + datetime.strptime(u, "%Y-%m-%d").strftime("%-d %B %Y")

@app.get("/admin/gifts")
def admin_gifts():
    admin_only()
    msg = esc(request.args.get("done", ""))
    rows, problem = [], ""
    if config.STRIPE_SECRET:
        try:
            for c in billing.gifted(config.STRIPE_SECRET):
                g = billing.gift_of(c.get("metadata") or {})
                rows.append(f'<li>{esc(c.get("email"))} · {"The Inner Circle" if g["tier"] == "pro" else "The Order"} {nice_until(g["until"])} '
                            f'<span class="status {"on" if g["live"] else "off"}">{"active" if g["live"] else "ended"}</span> '
                            f'<form method="post" action="/admin/gift/end" style="display:inline"><input type="hidden" name="email" value="{esc(c.get("email"))}">'
                            f'<button class="alt" type="submit">End</button></form></li>')
        except stripe_api.StripeError as e:
            problem = f'<p class="err">Couldn\'t load the list from Stripe: {esc(e)}</p>'
    else:
        problem = '<p class="muted">Gifts of the Order work once your Stripe key is set.</p>'
    lengths = "".join(f'<option value="{k}"{" selected" if k == GIFT_DEFAULT else ""}>{"For good" if v is None else v if isinstance(v, str) else f"{v} month" + ("s" if v > 1 else "")}</option>' for k, v in GIFT_LENGTHS.items())
    return private("Gifts", f"""<p class="crumbs"><a href="/admin">Admin</a></p><h1>Gifts</h1>
{f'<p class="note-box">{msg}</p>' if msg else ""}
<h2>Give a place in the Order</h2>
<p class="note-box" id="enter">To use the Order and the Inner Circle yourself: give <b>The Inner Circle</b>, <b>For good</b>, to your own email{f" ({esc(config.OWNER_EMAIL)})" if config.OWNER_EMAIL else ""}, then open the Hall from here. No email needed.</p>
{f'''<form method="post" action="/admin/enter"><button class="btn-cast" type="submit">Open the Hall as {esc(config.OWNER_EMAIL)}</button></form>''' if config.OWNER_EMAIL else
 '<p class="muted">To open the Hall from here, add <b>OWNER_EMAIL</b> (your own email) to the site\'s environment in Render.</p>'}
<p class="muted">Nothing is charged and no card is asked for. They get an email inviting them to sign in, and everything the plan includes works straight away. When it ends they are back on the free site, unless they pay for a plan of their own, which a gift never changes.</p>
<form class="pg-form" method="post" action="/admin/gift/membership">
<label>Their email <input name="email" type="email" required maxlength="254"></label>
<label>Plan <select name="tier"><option value="member">The Order</option><option value="pro">The Inner Circle</option></select></label>
<label>For <select name="length">{lengths}</select></label>
<label>A note from you (optional) <input name="note" maxlength="300"></label>
<button class="btn-cast" type="submit">Give it</button></form>
<h2>Given so far</h2>{problem}<ul>{"".join(rows) or ("<li class='muted'>None yet.</li>" if not problem else "")}</ul>
<h2>Give a reading</h2><p>Use <a href="/admin">Generate a reading</a> and press <b>Make a gift link</b>. You get a private link to their full reading to send however you like.</p>""")

@app.post("/admin/enter")
def admin_enter():
    """The admin, already in by password, signs in as the site's owner (OWNER_EMAIL) to use the Order and the
    Inner Circle like any member, without waiting for a sign-in email. Only ever the owner's own address."""
    admin_only()
    email = accounts.clean_email(config.OWNER_EMAIL)
    if not email: return redirect("/admin/gifts")
    session["email"] = email
    return redirect("/hall")

@app.post("/admin/gift/membership")
def admin_gift_membership():
    admin_only()
    email = accounts.clean_email(request.form.get("email"))
    tier = request.form.get("tier") if request.form.get("tier") in ("member", "pro") else "member"
    if not email: return redirect("/admin/gifts?" + urlencode({"done": "That email address doesn't look right."}))
    until = gift_until(request.form.get("length", GIFT_DEFAULT))
    try:
        paying = [p for p in billing.status(config.STRIPE_SECRET, email, fresh=True)["plans"] if p["status"] in billing.LIVE]
        billing.give(config.STRIPE_SECRET, email, tier, until)
    except stripe_api.StripeError as e:
        return redirect("/admin/gifts?" + urlencode({"done": f"Stripe said: {e}"}))
    plan = "a place in the Inner Circle" if tier == "pro" else "a place in the Order"
    note = request.form.get("note", "").strip()[:300]
    link = f"{config.BASE_URL}/auth/{accounts.make_token(config.SECRET_KEY, email, '/account')}"
    sent = mailer.send(email, f"A gift from {config.AUTHOR}: {plan}",
        f"<p>{esc(config.AUTHOR)} has given you {plan}, {nice_until(until)}.</p>" + (f"<p><i>{esc(note)}</i></p>" if note else "") +
        f'<p><a href="{esc(link)}">Sign in to start</a> (this link works for {accounts.LINK_MINUTES} minutes; after that, sign in at {esc(config.BASE_URL)}/signin with this email).</p>',
        f"{config.AUTHOR} has given you {plan}, {nice_until(until)}.\n\n{note}\n\nSign in: {config.BASE_URL}/signin with this email address.")
    also = (" They already pay for " + " and ".join("The Inner Circle" if p["tier"] == "pro" else "The Order" for p in paying) +
            "; that subscription is untouched and keeps billing as before.") if paying else ""
    return redirect("/admin/gifts?" + urlencode({"done": f"Given to {email}, {nice_until(until)}." + also + ("" if sent else " The email couldn't be sent" + (" (see the mail settings)" if mailer.ready() else ", as email isn't set up") + ", so tell them to sign in with this address.")}))

@app.post("/admin/gift/end")
def admin_gift_end():
    admin_only()
    email = accounts.clean_email(request.form.get("email"))
    if email:
        try: billing.end_gift(config.STRIPE_SECRET, email)
        except stripe_api.StripeError as e: return redirect("/admin/gifts?" + urlencode({"done": f"Stripe said: {e}"}))
    return redirect("/admin/gifts?" + urlencode({"done": f"Ended the gift for {email}."}))

@app.post("/admin/gift/reading")
def admin_gift_reading():
    admin_only()
    meta = {k: request.form.get(k, "") for k in BIRTH_KEYS}
    if not meta["lat"]: meta.pop("lat"); meta.pop("lon"); meta.pop("tz")
    try: birth_from(meta)
    except (BadInput, ValueError) as e:
        return private("Gift link", f'<h1>Check the details</h1><p>{esc(str(e) or BAD_BIRTH)} <a href="/admin">Back</a></p>', status=400)
    link = f"{config.BASE_URL}/gift/{gift_signer().dumps(meta)}"
    who = esc(meta.get("name") or "them")
    return private("Gift link", f"""<p class="crumbs"><a href="/admin">Admin</a></p><h1>A reading for {who}</h1>
<p>Send them this link. It opens their full reading, free, for the next two years.</p>
<p class="note-box" style="word-break:break-all"><a href="{esc(link)}">{esc(link)}</a></p>
<p><button class="btn-cast" type="button" id="copy">Copy the link</button></p>""",
        script=f"""<script>document.getElementById("copy").onclick = e => navigator.clipboard.writeText({json.dumps(link)}).then(() => e.target.textContent = "Copied", () => {{}});</script>""")

@app.get("/gift/<token>")
def gift_reading(token):
    if not config.SECRET_KEY or len(token) > 1500: abort(404)
    try: meta = gift_signer().loads(token, max_age=GIFT_READING_DAYS * 86400)
    except _BadSig: abort(404)
    if not isinstance(meta, dict): abort(404)
    try:
        return render_reading({k: str(v) for k, v in meta.items() if k in BIRTH_KEYS}, f"A gift from {config.AUTHOR}.")
    except (BadInput, ValueError):
        abort(404)

# ---------------- the weekly job: Body Weather to every member ----------------
@app.post("/jobs/weekly")
def jobs_weekly():
    tok = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not config.JOBS_TOKEN or not hmac.compare_digest(tok.encode(), config.JOBS_TOKEN.encode()): abort(404)
    from wyrd import jobs
    return jsonify(jobs.weekly(EPH, cast_for, birth_from, config))

import order_routes  # noqa: E402,F401  (the Hall and the practice desk; uses the helpers above)

@app.get("/healthz")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
