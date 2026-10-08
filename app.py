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
from wyrd import accounts, billing, mailer, pages, weather
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

PRIVATE_PATHS = ("/c/", "/admin", "/gift/", "/account", "/signin", "/auth/", "/signout", "/pro", "/billing", "/api/subscribe", "/api/account", "/jobs/")

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
    email, member, customer = signed_in(), False, None
    try:
        if email:
            st = billing.status(config.STRIPE_SECRET, email)
            member, customer = st["member"] or st["pro"], st["customer"]
        s = stripe_api.create_checkout(config.STRIPE_SECRET, base_url=config.BASE_URL,
                                       price_id=None if member else config.STRIPE_PRICE_ID,
                                       price_cents=config.MEMBER_READING_CENTS if member else config.PRICE_CENTS,
                                       product_name=config.PRODUCT_NAME + (" (member price)" if member else ""), metadata=meta,
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

# ---------------- public pages search engines read ----------------
def page(title, desc, body, ld="", robots="index, follow", script="", status=200):
    """A server-made page in the console's look, with its own title, description and share preview."""
    t = open(os.path.join(HERE, "static", "page.html"), encoding="utf-8").read()
    who = (f'<a href="/account">Your account</a>' if signed_in() else '<a href="/signin">Sign in</a>')
    fill = {"TITLE": html.escape(title), "DESC": html.escape(desc), "ROBOTS": robots, "LD": ld, "BODY": body,
            "CANON": html.escape(config.BASE_URL + request.path), "BASE": html.escape(config.BASE_URL), "WHO": who, "SCRIPT": script}
    for k, v in fill.items(): t = t.replace("{{" + k + "}}", v)
    return Response(t, status=status, mimetype="text/html")

def private(title, body, script="", status=200):
    return page(title + " · The Wyrd Console", title, body, robots="noindex, nofollow", script=script, status=status)

@app.get("/googled81e0f187c4a1868.html")
def google_site_verification():
    """Google Search Console checks this file to confirm the site is Saga Devi's."""
    return send_from_directory(app.static_folder, "googled81e0f187c4a1868.html", mimetype="text/html")

@app.get("/robots.txt")
def robots():
    lines = ["User-agent: *", "Disallow: /admin", "Disallow: /account", "Disallow: /reading", "Disallow: /consultation",
             "Disallow: /c/", "Disallow: /pro", "Disallow: /auth/", "Disallow: /api/", f"Sitemap: {config.BASE_URL}/sitemap.xml"]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")

@app.get("/sitemap.xml")
def sitemap():
    return Response(pages.sitemap(config.BASE_URL), mimetype="application/xml")

@app.get("/reports")
def reports_page():
    return page(*pages.reports(config.BASE_URL, config.PRICE_CENTS, config.MEMBER_READING_CENTS))

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

@app.get("/learn/dharma")
def learn_dharma():
    return page(*pages.dharma_index(config.BASE_URL))

@app.get("/learn/dharma/gates/<int:g>")
def learn_dharma_gate(g):
    p = pages.dharma_gate(config.BASE_URL, g)
    if not p: abort(404)
    return page(*p)

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
        return billing.status(config.STRIPE_SECRET, email, fresh=fresh) if config.STRIPE_SECRET else billing._empty()
    except stripe_api.StripeError:
        return None

def esc(v): return html.escape(str(v))

@app.get("/signin")
def signin_page():
    nxt = accounts.safe_next(request.args.get("next", "/account"))
    if signed_in(): return redirect(nxt)
    return private("Sign in", f"""<h1>Sign in</h1>
<p class="lede">No password. Type your email and we'll send you a link that signs you in.</p>
<form class="pg-form" method="post" action="/signin"><input type="hidden" name="next" value="{esc(nxt)}">
<label>Email <input name="email" type="email" required autocomplete="email" maxlength="254"></label>
<button class="btn-cast" type="submit">Email me a sign-in link</button></form>
<p class="muted">Use the same email you paid with, and your membership is found automatically.</p>""")

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

@app.get("/membership")
def membership_page():
    on = selling()
    def buy(plan, label, lead=False):
        if not on: return '<p class="muted">Opening soon.</p>'
        return (f'<form method="post" action="/api/subscribe"><input type="hidden" name="plan" value="{plan}">'
                f'<button class="{"btn-buy" if lead else "btn-cast"}" type="submit">{label}</button></form>')
    m, y, pr = config.MEMBER_MONTHLY_CENTS, config.MEMBER_YEARLY_CENTS, config.PRO_MONTHLY_CENTS
    body = f"""<h1>Wyrd Membership</h1>
<p class="lede">Your body's weather, every week. How the planets land in the body you were born with and in your Dharma body, written in Saga Devi's words.</p>
<div class="plans">
  <section class="plan lead"><h2>Membership</h2><div class="price">{money(m)}<small> a month</small></div>
    <ul><li><b>Body Weather every Monday:</b> which centres the week's sky switches on in your birth body and your Dharma body, which stay open, and which of your gates it lights</li>
      <li>The Moon's mansion day by day, the week's stations and sign changes, and your Vimshottari period</li>
      <li>Your chart kept on your account, on any device</li>
      <li>The natal astrology reading for {money(config.MEMBER_READING_CENTS)} instead of {money(config.PRICE_CENTS)}</li></ul>
    {buy("member-month", f"Join for {money(m)} a month", True)}
    {buy("member-year", f"Or {money(y)} a year") if on else ""}</section>
  <section class="plan" id="pro"><h2>Professional</h2><div class="price">{money(pr)}<small> a month</small></div>
    <ul><li>For astrologers, coaches and practitioners working with clients</li>
      <li>Generate the full Wyrd reading for your clients: {config.PRO_READINGS_A_MONTH} a month included</li>
      <li>Body Weather for any client, any week</li>
      <li>Everything in the membership</li></ul>
    {buy("pro-month", f"Subscribe for {money(pr)} a month")}</section>
</div>
<p class="muted">Cancel any time from your account. Payments are handled by Stripe. Prefer one reading? <a href="/reports">The natal reading is {money(config.PRICE_CENTS)}, once.</a></p>"""
    ld = pages._ld({"@context": "https://schema.org", "@type": "Product", "name": config.MEMBER_NAME,
                    "description": "Weekly Body Weather astrology report for your birth body and Dharma body.",
                    "brand": {"@type": "Brand", "name": "The Wyrd Console"},
                    "offers": {"@type": "Offer", "price": f"{m / 100:.2f}", "priceCurrency": "USD", "url": config.BASE_URL + "/membership"}})
    return page("Weekly Astrology Membership: Body Weather · The Wyrd Console",
                f"A weekly astrology report for your own chart: how the week's planets land in your birth body and Dharma body. {money(m)} a month from Saga Devi.",
                body, ld)

@app.post("/api/subscribe")
def subscribe():
    plan = PLANS.get(request.form.get("plan", ""))
    if not plan or not same_origin(): abort(400)
    if not selling(): return redirect("/membership")
    email = signed_in()
    if not email: return redirect("/signin?" + urlencode({"next": "/membership"}))
    if limited(10): return private("Wait a minute", "<h1>Wait a minute</h1><p>Too many tries. Try again shortly.</p>", status=429)
    tier, name, cents, interval, price_id = plan
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

@app.get("/account")
def account_page():
    email = signed_in()
    if not email: return redirect("/signin?next=/account")
    st = account_status(email, fresh=bool(request.args.get("joined")))
    if st is None: return private("Your account", "<h1>Your account</h1><p>We couldn't reach the payment system just now. Refresh in a moment.</p>", status=503)
    rows = []
    for p in st["plans"]:
        live = p["status"] in billing.LIVE
        end = datetime.fromtimestamp(p["periodEnd"], timezone.utc).strftime("%-d %B %Y") if p.get("periodEnd") else ""
        when = (f" · ends {end}" if p["cancelAtEnd"] else f" · renews {end}") if live and end else ""
        rows.append(f'<li>{"Professional" if p["tier"] == "pro" else "Membership"} ({p.get("interval") or "month"}ly) '
                    f'<span class="status {"on" if live else "off"}">{esc(p["status"].replace("_", " "))}</span>{when}</li>')
    joined = '<p class="note-box">Welcome. Your payment went through.</p>' if request.args.get("joined") else ""
    g = st.get("gift")
    if g and g["live"]:
        rows.insert(0, f'<li>{"Professional" if g["tier"] == "pro" else "Membership"}, a gift from {esc(config.AUTHOR)}, {nice_until(g["until"])} <span class="status on">active</span></li>')
    portal_btn = '<form method="post" action="/billing/portal"><button class="alt" type="submit">Manage or cancel, change card, see receipts</button></form>' if st["plans"] else ""
    plans = f'<ul>{"".join(rows)}</ul>{portal_btn}' if rows else \
            '<p>You have no membership yet. <a href="/membership">See the membership</a>.</p>'
    member = st["member"] or st["pro"]
    chart = ""
    if member:
        b = st.get("birth")
        chart = f"""<h2>Your chart for Body Weather</h2>
<p>{chart_line(b) if b else "No chart saved yet."}</p>
<p id="useCurrent" hidden><button class="btn-cast" type="button">Use the chart open in this browser</button></p>
<p class="muted" id="noCurrent">To change it, <a href="/">cast the chart</a>, then come back here.</p>
{WEEK_LINK if b else ""}"""
    pro = f'<h2>Professional</h2><p><a href="/pro">Open your practice desk →</a> {st["proUse"]} of {config.PRO_READINGS_A_MONTH} client readings used this month.</p>' if st["pro"] else ""
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

WEEK_LINK = '<h2>This week</h2><p><a href="/account/weather">Read this week&#39;s Body Weather →</a></p>'
BIRTH_KEYS = ("name", "date", "time", "place_id", "lat", "lon", "tz", "place_label")

@app.post("/api/account/chart")
def account_chart():
    email = signed_in()
    if not email or not same_origin(): return jsonify(error="Sign in first."), 401
    st = account_status(email)
    if not st or not (st["member"] or st["pro"]): return jsonify(error="For members."), 403
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
    email = signed_in()
    if not email: return redirect("/signin?next=/account/weather")
    st = account_status(email)
    if not st or not (st["member"] or st["pro"]): return redirect("/membership")
    if not st.get("birth"): return redirect("/account")
    return private("Body Weather", f'<p class="crumbs"><a href="/account">Your account</a></p><div class="weather">{weather_for(st["birth"])}</div>')

# ---------------- the professional desk ----------------
BAD_BIRTH = "Those birth details don't work."

def pro_or_redirect():
    email = signed_in()
    if not email: return None, redirect("/signin?next=/pro")
    st = account_status(email)
    if not st or not st["pro"]: return None, redirect("/membership#pro")
    return (email, st), None

@app.get("/pro")
def pro_desk():
    who, bounce = pro_or_redirect()
    if bounce: return bounce
    left = max(0, config.PRO_READINGS_A_MONTH - who[1]["proUse"])
    form = open(os.path.join(HERE, "static", "pro-form.html"), encoding="utf-8").read()
    return private("Practice desk", f"""<h1>Your practice desk</h1>
<p class="lede">Generate the full Wyrd reading or a week's Body Weather for a client.</p>
<p class="muted">{left} of {config.PRO_READINGS_A_MONTH} client readings left this month. Body Weather is unlimited.</p>{form}""",
                   script='<script src="/static/common.js"></script><script src="/static/pro.js"></script>')

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
        return render_reading(meta, "Prepared with The Wyrd Console Professional · written by Saga Devi. Save it as a PDF from your browser's print menu.")
    except (BadInput, ValueError) as e:
        return private("Practice desk", f'<h1>Check the details</h1><p>{esc(str(e) or BAD_BIRTH)} <a href="/pro">Back</a></p>', status=400)
    except stripe_api.StripeError:
        return private("Practice desk", '<h1>Try again</h1><p>We couldn\'t reach the payment system. <a href="/pro">Back</a></p>', status=502)

# ---------------- gifts, from the admin only ----------------
from itsdangerous import URLSafeTimedSerializer, BadSignature as _BadSig
GIFT_READING_DAYS = 730
GIFT_LENGTHS = {"1": 1, "3": 3, "6": 6, "12": 12, "forever": None}

def gift_signer():
    return URLSafeTimedSerializer(config.SECRET_KEY, salt="wyrd-gift-reading")

def admin_only():
    if not is_admin(): abort(404)
    if request.method == "POST" and not same_origin(): abort(403)

def gift_until(choice):
    months = GIFT_LENGTHS.get(choice, 12)
    if months is None: return "forever"
    d = datetime.now(timezone.utc).date()
    y, m = divmod(d.month - 1 + months, 12)
    import calendar as _cal
    return f"{d.year + y:04d}-{m + 1:02d}-{min(d.day, _cal.monthrange(d.year + y, m + 1)[1]):02d}"

def nice_until(u):
    return "for good" if u == "forever" else "until " + datetime.strptime(u, "%Y-%m-%d").strftime("%-d %B %Y")

@app.get("/admin/gifts")
def admin_gifts():
    admin_only()
    msg = esc(request.args.get("done", ""))
    rows, problem = [], ""
    if config.STRIPE_SECRET:
        try:
            for c in billing.gifted(config.STRIPE_SECRET):
                g = billing.gift_of(c.get("metadata") or {})
                rows.append(f'<li>{esc(c.get("email"))} · {"Professional" if g["tier"] == "pro" else "Membership"} {nice_until(g["until"])} '
                            f'<span class="status {"on" if g["live"] else "off"}">{"active" if g["live"] else "ended"}</span> '
                            f'<form method="post" action="/admin/gift/end" style="display:inline"><input type="hidden" name="email" value="{esc(c.get("email"))}">'
                            f'<button class="alt" type="submit">End</button></form></li>')
        except stripe_api.StripeError as e:
            problem = f'<p class="err">Couldn\'t load the list from Stripe: {esc(e)}</p>'
    else:
        problem = '<p class="muted">Gifted memberships work once your Stripe key is set.</p>'
    lengths = "".join(f'<option value="{k}"{" selected" if k == "12" else ""}>{"For good" if v is None else f"{v} month" + ("s" if v > 1 else "")}</option>' for k, v in GIFT_LENGTHS.items())
    return private("Gifts", f"""<p class="crumbs"><a href="/admin">Admin</a></p><h1>Gifts</h1>
{f'<p class="note-box">{msg}</p>' if msg else ""}
<h2>Give a membership</h2>
<p class="muted">Nothing is charged. They get an email inviting them to sign in, and everything the plan includes works straight away.</p>
<form class="pg-form" method="post" action="/admin/gift/membership">
<label>Their email <input name="email" type="email" required maxlength="254"></label>
<label>Plan <select name="tier"><option value="member">Membership</option><option value="pro">Professional</option></select></label>
<label>For <select name="length">{lengths}</select></label>
<label>A note from you (optional) <input name="note" maxlength="300"></label>
<button class="btn-cast" type="submit">Give it</button></form>
<h2>Given so far</h2>{problem}<ul>{"".join(rows) or ("<li class='muted'>None yet.</li>" if not problem else "")}</ul>
<h2>Give a reading</h2><p>Use <a href="/admin">Generate a reading</a> and press <b>Make a gift link</b>. You get a private link to their full reading to send however you like.</p>""")

@app.post("/admin/gift/membership")
def admin_gift_membership():
    admin_only()
    email = accounts.clean_email(request.form.get("email"))
    tier = request.form.get("tier") if request.form.get("tier") in ("member", "pro") else "member"
    if not email: return redirect("/admin/gifts?" + urlencode({"done": "That email address doesn't look right."}))
    until = gift_until(request.form.get("length", "12"))
    try:
        billing.give(config.STRIPE_SECRET, email, tier, until)
    except stripe_api.StripeError as e:
        return redirect("/admin/gifts?" + urlencode({"done": f"Stripe said: {e}"}))
    plan = "Wyrd Console Professional" if tier == "pro" else "a Wyrd Membership"
    note = request.form.get("note", "").strip()[:300]
    link = f"{config.BASE_URL}/auth/{accounts.make_token(config.SECRET_KEY, email, '/account')}"
    sent = mailer.send(email, f"A gift from {config.AUTHOR}: {plan}",
        f"<p>{esc(config.AUTHOR)} has given you {plan}, {nice_until(until)}.</p>" + (f"<p><i>{esc(note)}</i></p>" if note else "") +
        f'<p><a href="{esc(link)}">Sign in to start</a> (this link works for {accounts.LINK_MINUTES} minutes; after that, sign in at {esc(config.BASE_URL)}/signin with this email).</p>',
        f"{config.AUTHOR} has given you {plan}, {nice_until(until)}.\n\n{note}\n\nSign in: {config.BASE_URL}/signin with this email address.")
    return redirect("/admin/gifts?" + urlencode({"done": f"Given to {email}, {nice_until(until)}." + ("" if sent else " Email isn't set up, so tell them to sign in with this address.")}))

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

@app.get("/healthz")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
