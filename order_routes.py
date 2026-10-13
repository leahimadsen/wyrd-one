"""The Order's Hall and the Inner Circle's practice desk.

The Hall (/hall): a member's home. This week's Body Weather, their chart opened up, the letters
of past weeks, charts for loved ones, what their place in the Order gives them, and their plan.

The practice desk (/pro): a practitioner's clients, every reading they've generated (reopened
without using a credit), private links to send a reading to a client, and their practice name.

Records live in wyrd/store.py (Postgres in production); plans and payments stay in Stripe.
Loaded at the end of app.py, so it can use the site's helpers."""
import base64, json, sys
from datetime import datetime, timezone
from flask import request, redirect, jsonify, abort

A = sys.modules.get("app") or sys.modules["__main__"]
app, config, billing, mailer, weather, esc = A.app, A.config, A.billing, A.mailer, A.weather, A.esc
from wyrd import store, stripe_api

FIRST = lambda b, email: ((b or {}).get("name") or "").split(" ")[0] or email.split("@")[0]


def _chart_link(b):
    """The free chart for a set of birth details, opened straight from a link."""
    q = base64.urlsafe_b64encode(json.dumps({k: b[k] for k in A.BIRTH_KEYS if b.get(k)}).encode()).decode().rstrip("=")
    return f"/chart?b={q}"


def _member():
    """(email, status) for a signed-in member of the Order or the Inner Circle; otherwise a redirect."""
    email = A.signed_in()
    if not email: return None, redirect("/signin?next=" + request.path)
    st = A.account_status(email)
    if st is None:
        return None, A.private("The Hall", "<h1>The Hall</h1><p>We couldn't reach the payment system just now. Refresh in a moment.</p>", status=503)
    if not (st["member"] or st["pro"]): return None, redirect("/membership")
    return (email, st), None


def _safe(fn, *a, default=None):
    """A read from the database that never takes the page down: if the database can't be reached
    (a free database waking up, say), the page shows without that part."""
    try: return fn(*a)
    except Exception as e:
        app.logger.error("store: %s", e)
        return default


# the parts that keep records, switched off until there's a database to keep them in (store.ready)
NEEDS_STORE = ("/hall/letters", "/hall/kin", "/api/hall/kin", "/pro/practice", "/pro/clients", "/pro/r/", "/pro/history", "/r/")


@app.before_request
def _store_or_not():
    p = request.path
    if store.ready() or not p.startswith(NEEDS_STORE): return None
    if p.startswith("/r/"): abort(404)
    if p.startswith("/api/"): return jsonify(error="Coming soon."), 503
    return redirect("/pro" if p.startswith("/pro") else "/hall")


def _week_letter(email, b):
    """This week's Body Weather, kept in the archive the first time it's made."""
    week = weather.monday().isoformat()
    if not store.ready(): return week, A.weather_for(b)
    have = _safe(store.letter, email, week)
    if have: return week, have["html"]
    html = A.weather_for(b)
    try: store.save_letter(email, week, html)
    except Exception: pass                           # the archive is a nicety; the letter still shows
    return week, html


def _plans_html(st):
    rows = []
    for p in st["plans"]:
        live = p["status"] in billing.LIVE
        end = datetime.fromtimestamp(p["periodEnd"], timezone.utc).strftime("%-d %B %Y") if p.get("periodEnd") else ""
        when = (f" · ends {end}" if p["cancelAtEnd"] else f" · renews {end}") if live and end else ""
        rows.append(f'<li>{"The Inner Circle" if p["tier"] == "pro" else "The Order"} ({p.get("interval") or "month"}ly) '
                    f'<span class="status {"on" if live else "off"}">{esc(p["status"].replace("_", " "))}</span>{when}</li>')
    g = st.get("gift")
    if g and g["live"]:
        rows.insert(0, f'<li>{"The Inner Circle" if g["tier"] == "pro" else "The Order"}, a gift from {esc(config.AUTHOR)}, {A.nice_until(g["until"])} <span class="status on">active</span></li>')
    portal = '<form method="post" action="/billing/portal"><button class="alt" type="submit">Manage or cancel, change card, see receipts</button></form>' if st["plans"] else ""
    return f'<ul>{"".join(rows)}</ul>{portal}'


USE_CURRENT = """<script src="/static/common.js"></script><script>
(() => {
  const c = WyrdCommon.current();
  const box = document.getElementById("useCurrent");
  if (c && box){
    box.hidden = false; const n = document.getElementById("noCurrent"); if (n) n.hidden = true;
    const b = box.querySelector("button"); b.textContent = "Use " + (c.birth.name || "the chart") + " (" + c.birth.date + ") for your Body Weather";
    b.onclick = async () => { const r = await fetch("/api/account/chart", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(c.birth)});
      if (r.ok) location.reload(); else box.insertAdjacentHTML("beforeend", '<p class="err">That chart couldn\\'t be saved. Cast it again and retry.</p>'); };
  }
  const kin = document.getElementById("kinAdd");
  if (kin){
    if (!c){ kin.querySelector(".kin-none").hidden = false; kin.querySelector("form").hidden = true; return; }
    const f = kin.querySelector("form"); f.querySelector(".kin-who").textContent = (c.birth.name || "the chart") + " (" + c.birth.date + ")";
    f.onsubmit = async e => { e.preventDefault();
      const r = await fetch("/api/hall/kin", {method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({label: f.elements.label.value || c.birth.name || "", birth: c.birth})});
      const j = await r.json().catch(() => ({}));
      if (r.ok) location.reload(); else f.insertAdjacentHTML("beforeend", '<p class="err">' + (j.error || "That chart couldn't be saved.") + '</p>'); };
  }
})();</script>"""


SOON_HALL = """<section class="hall-sec"><h2>Coming soon</h2><p>Every past letter kept here to reread, and charts for the people you love with their own weekly Body Weather.</p></section>"""


# ---------------- the Hall ----------------
@app.get("/hall")
def hall():
    who, bounce = _member()
    if bounce: return bounce
    email, st = who
    b = st.get("birth")
    joined = '<p class="note-box">Welcome to the Order. Your payment went through.</p>' if request.args.get("joined") else ""

    if b:
        week, letter = _week_letter(email, b)
        this_week = f"""<section class="hall-sec"><h2>This week's Body Weather</h2>
<p class="muted">The week of {datetime.strptime(week, "%Y-%m-%d").strftime("%-d %B %Y")}, for {A.chart_line(b)}. It also comes to your inbox every Monday.</p>
<div class="weather hall-letter">{letter}</div></section>"""
        chart = f"""<section class="hall-sec"><h2>Your chart, opened up</h2>
<p>In the Order your chart shows every activated rune read in full through its mansion, and the planets on each station of your body map.</p>
<p><a class="btn-cast" href="{_chart_link(b)}">Open your chart</a></p>
<p id="useCurrent" hidden><button class="alt" type="button"></button></p>
<p class="muted" id="noCurrent">To change the chart your letter is written for, <a href="/">cast it</a>, then come back here.</p></section>"""
    else:
        this_week = """<section class="hall-sec"><h2>This week's Body Weather</h2>
<p>Your letter is written for one chart. Choose it and the week appears here, and in your inbox every Monday.</p>
<p id="useCurrent" hidden><button class="btn-cast" type="button"></button></p>
<p class="muted" id="noCurrent"><a href="/">Cast your chart</a>, then come back here to choose it.</p></section>"""
        chart = ""

    db = store.ready()
    past = [l for l in (_safe(store.letters, email, default=[]) or []) if not b or l["week"] != weather.monday().isoformat()] if db else []
    archive = "".join(f'<li><a href="/hall/letters/{l["week"]}">The week of {datetime.strptime(l["week"], "%Y-%m-%d").strftime("%-d %B %Y")}</a></li>' for l in past)
    letters = f"""<section class="hall-sec"><h2>Past letters</h2>{f'<ul class="hall-list">{archive}</ul>' if archive else '<p class="muted">Each week\'s letter is kept here once it\'s written, so you can go back to it.</p>'}</section>"""

    kin = (_safe(store.kin, email, default=[]) or []) if db else []
    kin_rows = "".join(f"""<li><b>{esc(k["label"])}</b> <span class="muted">· {esc(k["birth"].get("date", ""))}</span>
  <a href="/hall/kin/{k["id"]}">This week's Body Weather</a> · <a href="{_chart_link(k["birth"])}">Open chart</a>
  <form method="post" action="/hall/kin/{k["id"]}/remove" class="inline"><button class="linkish" type="submit">Remove</button></form></li>""" for k in kin)
    loved = f"""<section class="hall-sec"><h2>Charts for loved ones</h2>
<p>Keep up to {store.KIN_MAX} charts for the people close to you and read their Body Weather each week too.</p>
{f'<ul class="hall-list">{kin_rows}</ul>' if kin_rows else ''}
<div id="kinAdd">{'' if len(kin) >= store.KIN_MAX else '''<p class="muted kin-none" hidden><a href="/">Cast their chart</a> in this browser, then come back here to keep it.</p>
<form class="kin-form"><p>Keep <b class="kin-who"></b>, the chart open in this browser, as
<input name="label" maxlength="60" placeholder="a name, e.g. Mum"> <button class="btn-cast" type="submit">Keep this chart</button></p></form>'''}</div></section>"""

    perks = f"""<section class="hall-sec"><h2>What the Order gives you</h2><ul class="hall-list">
<li>The Wyrd Reading for <b>{A.money(config.MEMBER_READING_CENTS)}</b> instead of {A.money(config.PRICE_CENTS)}. <a href="/chart#reading">Get yours →</a></li>
<li><b>{config.TOGETHER_MEMBER_OFF}% off</b> the reading together. <a href="/chart#compare">Add people in Compare →</a></li>
<li><b>Learning the Mandala</b>, the course, included when it opens.</li></ul></section>"""
    circle = f"""<section class="hall-sec"><h2>The Inner Circle</h2><p><a class="btn-cast" href="/pro">Open your practice desk</a>
<span class="muted">{st["proUse"]} of {config.PRO_READINGS_A_MONTH} client readings used this month.</span></p></section>""" if st["pro"] else ""
    plan = f"""<section class="hall-sec"><h2>Your place in the Order</h2>{_plans_html(st)}
<form method="post" action="/signout" style="margin-top:24px"><button class="alt" type="submit">Sign out</button></form></section>"""
    return A.private("The Hall", f"""<p class="hall-kicker">The Order</p><h1>The Hall</h1>
<p class="lede">Welcome back, {esc(FIRST(b, email))}. This is your room in the Order: your weather, your letters, your people.</p>{joined}
{this_week}{chart}{letters + loved if db else SOON_HALL}{perks}{circle}{plan}""", script=USE_CURRENT)


@app.get("/hall/letters/<week>")
def hall_letter(week):
    who, bounce = _member()
    if bounce: return bounce
    l = store.letter(who[0], week)
    if not l: abort(404)
    when = datetime.strptime(week, "%Y-%m-%d").strftime("%-d %B %Y")
    return A.private("Body Weather", f'<p class="crumbs"><a href="/hall">The Hall</a> › Past letters</p><h1>The week of {when}</h1><div class="weather">{l["html"]}</div>')


@app.get("/hall/kin/<kid>")
def hall_kin(kid):
    who, bounce = _member()
    if bounce: return bounce
    k = store.kin_one(who[0], kid)
    if not k: abort(404)
    try: letter = A.weather_for(k["birth"])
    except (A.BadInput, ValueError): letter = "<p>That chart's details no longer work. Remove it and keep it again.</p>"
    return A.private("Body Weather", f'<p class="crumbs"><a href="/hall">The Hall</a> › {esc(k["label"])}</p><div class="weather">{letter}</div>')


@app.post("/api/hall/kin")
def hall_kin_add():
    email = A.signed_in()
    if not email or not A.same_origin(): return jsonify(error="Sign in first."), 401
    st = A.account_status(email)
    if not st or not (st["member"] or st["pro"]): return jsonify(error="For the Order."), 403
    d = request.get_json(force=True, silent=True) or {}
    b = {k: str((d.get("birth") or {}).get(k, ""))[:80] for k in A.BIRTH_KEYS if (d.get("birth") or {}).get(k) not in (None, "")}
    try: A.birth_from(b)
    except (A.BadInput, ValueError): return jsonify(error="Those birth details don't work."), 400
    try: store.add_kin(email, str(d.get("label") or b.get("name") or "A loved one").strip() or "A loved one", b)
    except ValueError as e: return jsonify(error=str(e)), 400
    return jsonify(ok=True)


@app.post("/hall/kin/<kid>/remove")
def hall_kin_remove(kid):
    email = A.signed_in()
    if not email or not A.same_origin(): abort(403)
    store.remove_kin(email, kid)
    return redirect("/hall")


# ---------------- the Inner Circle's practice desk ----------------
def _pro():
    return A.pro_or_redirect()


def _birth_from_form(f):
    meta = {k: f.get(k, "").strip() for k in A.BIRTH_KEYS}
    if not meta["lat"]: meta.pop("lat"); meta.pop("lon"); meta.pop("tz")
    meta = {k: v[:80] for k, v in meta.items() if v}
    A.birth_from(meta)                               # raises when the details don't work
    return meta


def _client_form(c=None, action="/pro/clients"):
    form = open(A.os.path.join(A.HERE, "static", "pro-form.html"), encoding="utf-8").read()
    b = (c or {}).get("birth") or {}
    vals = {"name": (c or {}).get("name") or b.get("name", ""), "full_name": b.get("full_name", ""), "date": b.get("date", ""), "time": b.get("time", ""),
            "place_id": b.get("place_id", ""), "lat": b.get("lat", ""), "lon": b.get("lon", ""), "tz": b.get("tz", ""), "place_label": b.get("place_label", "")}
    for k, v in vals.items():
        form = form.replace(f'name="{k}"', f'name="{k}" value="{esc(v)}"', 1)
    form = form.replace('id="proPlace"', f'id="proPlace" value="{esc(vals["place_label"])}"', 1)
    form = form.replace('action="/pro/reading" target="_blank"', f'action="{action}"', 1)
    extra = f"""<label>Client's email <span>optional, to send them their reading</span><input name="email" type="email" maxlength="120" value="{esc((c or {}).get("email") or "")}"></label>
  <label class="f-wide">Notes <span>private to you</span><textarea name="notes" rows="3" maxlength="4000">{esc((c or {}).get("notes") or "")}</textarea></label>
  <button type="submit" class="btn-cast" name="kind" value="save">{"Save changes" if c else "Save the client"}</button>"""
    a = form.index('<button type="submit" class="btn-cast" name="kind" value="reading">')
    b2 = form.index('<p class="err" id="proErr"')
    return form[:a] + extra + form[b2:]


@app.get("/pro")
def pro_desk_home():
    who, bounce = _pro()
    if bounce: return bounce
    email, st = who
    left = max(0, config.PRO_READINGS_A_MONTH - st["proUse"])
    if not store.ready():                            # no database yet: one-off readings, nothing kept
        form = open(A.os.path.join(A.HERE, "static", "pro-form.html"), encoding="utf-8").read()
        return A.private("Practice desk", f"""<p class="hall-kicker">The Inner Circle</p><h1>Your practice desk</h1>
<p class="lede">Generate The Wyrd Reading or a week's Body Weather for a client.</p>
<div class="desk-meter"><b>{left}</b> of {config.PRO_READINGS_A_MONTH} client readings left this month · Body Weather is unlimited</div>
<section class="hall-sec"><h2>A reading for a client</h2>{form}</section>
<section class="hall-sec"><h2>Coming soon</h2><p>Your client list with private notes, every reading kept to reopen free, readings sent to clients by a private link, and your practice's name on each one.</p></section>""",
                         script='<script src="/static/common.js"></script><script src="/static/pro.js"></script>')
    name = store.practice_name(email)
    cl = store.clients(email)
    rows = "".join(f"""<tr><td><a href="/pro/clients/{c["id"]}"><b>{esc(c["name"])}</b></a><br><small class="muted">{esc(c["birth"].get("date", ""))} · {esc((c["birth"].get("place_label") or "").split(",")[0])}</small></td>
<td><form method="post" action="/pro/clients/{c["id"]}/reading" target="_blank" class="inline"><button class="btn-cast" type="submit">Reading</button></form>
<form method="post" action="/pro/clients/{c["id"]}/weather" target="_blank" class="inline"><button class="alt" type="submit">Body Weather</button></form></td></tr>""" for c in cl)
    recent = store.readings(email)[:5]
    rec = "".join(f'<li><a href="/pro/r/{r["token"]}" target="_blank">{esc(r["name"])}</a> <span class="muted">· {datetime.fromtimestamp(r["created"], timezone.utc).strftime("%-d %b %Y")}</span></li>' for r in recent)
    return A.private("Practice desk", f"""<p class="hall-kicker">The Inner Circle</p><h1>Your practice desk</h1>
<p class="lede">Your clients, their readings and their weather, in one place.</p>
<div class="desk-meter"><b>{left}</b> of {config.PRO_READINGS_A_MONTH} client readings left this month · Body Weather is unlimited · reopening a reading is free</div>
<section class="hall-sec"><h2>Your practice</h2><form method="post" action="/pro/practice" class="kin-form">
<p>Readings say <i>Prepared by</i> <input name="name" maxlength="80" value="{esc(name)}" placeholder="your practice's name"> <button class="alt" type="submit">Save</button></p></form></section>
<section class="hall-sec"><h2>Clients</h2>{f'<div class="tw"><table class="desk-clients">{rows}</table></div>' if rows else '<p class="muted">No clients yet. Add your first below.</p>'}</section>
<section class="hall-sec"><h2>Recent readings</h2>{f'<ul class="hall-list">{rec}</ul><p><a href="/pro/history">Every reading →</a></p>' if rec else '<p class="muted">Readings you generate are kept here, to reopen or send without using another credit.</p>'}</section>
<section class="hall-sec"><h2>Add a client</h2>{_client_form()}</section>""",
                     script='<script src="/static/common.js"></script><script src="/static/pro.js"></script>')


@app.post("/pro/practice")
def pro_practice():
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    store.set_practice_name(who[0], request.form.get("name", ""))
    return redirect("/pro")


@app.post("/pro/clients")
def pro_client_add():
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    try:
        b = _birth_from_form(request.form)
        cid = store.save_client(who[0], request.form.get("name", "").strip() or b.get("name") or "Client", b,
                                request.form.get("email", ""), request.form.get("notes", ""))
    except (A.BadInput, ValueError) as e:
        return A.private("Practice desk", f'<h1>Check the details</h1><p>{esc(str(e) or A.BAD_BIRTH)} <a href="/pro">Back</a></p>', status=400)
    return redirect(f"/pro/clients/{cid}")


@app.get("/pro/clients/<cid>")
def pro_client(cid):
    who, bounce = _pro()
    if bounce: return bounce
    c = store.client(who[0], cid)
    if not c: abort(404)
    hist = "".join(f"""<li><a href="/pro/r/{r["token"]}" target="_blank">{datetime.fromtimestamp(r["created"], timezone.utc).strftime("%-d %B %Y")}</a>
{f'<span class="muted">· sent to {esc(r["sent_to"])}</span>' if r.get("sent_to") else ""}</li>""" for r in store.readings(who[0], cid))
    return A.private(c["name"], f"""<p class="crumbs"><a href="/pro">Practice desk</a> › {esc(c["name"])}</p><h1>{esc(c["name"])}</h1>
<p class="muted">{A.chart_line(c["birth"])}{f' · {esc(c["email"])}' if c.get("email") else ""}</p>
<div class="desk-actions"><form method="post" action="/pro/clients/{cid}/reading" target="_blank" class="inline"><button class="btn-cast" type="submit">Generate a reading</button></form>
<form method="post" action="/pro/clients/{cid}/weather" target="_blank" class="inline"><button class="alt desk-btn" type="submit">This week's Body Weather</button></form>
<a class="alt" href="{_chart_link(c["birth"])}" target="_blank">Open their chart</a></div>
{f'<section class="hall-sec"><h2>Notes</h2><p class="desk-notes">{esc(c["notes"])}</p></section>' if c.get("notes") else ""}
<section class="hall-sec"><h2>Readings</h2>{f'<ul class="hall-list">{hist}</ul>' if hist else '<p class="muted">None yet.</p>'}</section>
<section class="hall-sec"><h2>Edit</h2>{_client_form(c, f"/pro/clients/{cid}/edit")}
<form method="post" action="/pro/clients/{cid}/remove" onsubmit="return confirm('Remove {esc(c["name"])} from your clients? Their readings stay in your history.')"><button class="linkish" type="submit">Remove this client</button></form></section>""",
                     script='<script src="/static/common.js"></script><script src="/static/pro.js"></script>')


@app.post("/pro/clients/<cid>/edit")
def pro_client_edit(cid):
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    try:
        b = _birth_from_form(request.form)
        store.save_client(who[0], request.form.get("name", "").strip() or "Client", b, request.form.get("email", ""), request.form.get("notes", ""), cid=cid)
    except KeyError: abort(404)
    except (A.BadInput, ValueError) as e:
        return A.private("Practice desk", f'<h1>Check the details</h1><p>{esc(str(e) or A.BAD_BIRTH)} <a href="/pro/clients/{cid}">Back</a></p>', status=400)
    return redirect(f"/pro/clients/{cid}")


@app.post("/pro/clients/<cid>/remove")
def pro_client_remove(cid):
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    store.remove_client(who[0], cid)
    return redirect("/pro")


def _banner(pro):
    name = store.practice_name(pro)
    return (f"Prepared by {esc(name)}, in the Inner Circle of The Wyrd Console · written by The Völva." if name
            else "Prepared in the Inner Circle of The Wyrd Console · written by The Völva.")


@app.post("/pro/clients/<cid>/reading")
def pro_client_reading(cid):
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    email, st = who
    c = store.client(email, cid)
    if not c: abort(404)
    if st["proUse"] >= config.PRO_READINGS_A_MONTH:
        return A.private("Practice desk", f'<h1>This month\'s readings are used</h1><p>Your plan includes {config.PRO_READINGS_A_MONTH} client readings a month. They renew on the 1st. Readings already in <a href="/pro/history">your history</a> reopen free.</p>', status=402)
    try:
        billing.count_pro_reading(config.STRIPE_SECRET, email)
    except stripe_api.StripeError:
        return A.private("Practice desk", '<h1>Try again</h1><p>We couldn\'t reach the payment system. <a href="/pro">Back</a></p>', status=502)
    token = store.add_reading(email, c["name"], dict(c["birth"], name=c["name"]), cid)
    return redirect(f"/pro/r/{token}")


@app.post("/pro/clients/<cid>/weather")
def pro_client_weather(cid):
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    c = store.client(who[0], cid)
    if not c: abort(404)
    return A.private("Body Weather", f'<p class="crumbs"><a href="/pro/clients/{cid}">{esc(c["name"])}</a></p><div class="weather">{A.weather_for(c["birth"])}</div>')


@app.get("/pro/r/<token>")
def pro_reading_open(token):
    who, bounce = _pro()
    if bounce: return bounce
    r = store.reading_by_token(token)
    if not r or r["pro"] != who[0].strip().lower(): abort(404)
    resp = A.render_reading(r["birth"], _banner(r["pro"]) + f' <a href="/pro/r/{token}/share">Send or share this reading →</a>')
    return resp


@app.get("/pro/r/<token>/share")
def pro_reading_share(token):
    who, bounce = _pro()
    if bounce: return bounce
    r = store.reading_by_token(token)
    if not r or r["pro"] != who[0].strip().lower(): abort(404)
    c = store.client(who[0], r["client"]) if r.get("client") else None
    link = f"{config.BASE_URL}/r/{token}"
    sent = f'<p class="note-box">Sent to {esc(r["sent_to"])}.</p>' if r.get("sent_to") else ""
    return A.private("Share a reading", f"""<p class="crumbs"><a href="/pro">Practice desk</a> › {esc(r["name"])}</p><h1>Share {esc(r["name"])}'s reading</h1>{sent}
<section class="hall-sec"><h2>The private link</h2><p>Anyone with this link can read it, so send it only to your client.</p>
<p><input class="share-link" readonly value="{esc(link)}" onclick="this.select()"> <button class="alt" type="button" onclick="navigator.clipboard.writeText('{esc(link)}');this.textContent='Copied'">Copy</button></p></section>
<section class="hall-sec"><h2>Email it to them</h2><form method="post" action="/pro/r/{token}/send" class="kin-form">
<p><input name="to" type="email" required maxlength="120" value="{esc((c or {}).get("email") or "")}" placeholder="client@example.com">
<button class="btn-cast" type="submit">Send the reading</button></p>
<label class="f-wide">A note from you <span>optional</span><textarea name="note" rows="3" maxlength="1500"></textarea></label></form></section>""")


@app.post("/pro/r/<token>/send")
def pro_reading_send(token):
    who, bounce = _pro()
    if bounce or not A.same_origin(): return bounce or abort(403)
    r = store.reading_by_token(token)
    if not r or r["pro"] != who[0].strip().lower(): abort(404)
    to = A.accounts.clean_email(request.form.get("to"))
    if not to: return A.private("Share a reading", f'<h1>Check the email address</h1><p><a href="/pro/r/{token}/share">Back</a></p>', status=400)
    name = store.practice_name(r["pro"]) or "Your astrologer"
    note = request.form.get("note", "").strip()[:1500]
    link = f"{config.BASE_URL}/r/{token}"
    ok = mailer.send(to, f"Your Wyrd Reading, from {name}",
        f"<p>{esc(name)} has prepared your Wyrd Reading.</p>" + (f"<p><i>{esc(note)}</i></p>" if note else "") +
        f'<p><a href="{esc(link)}">Open your reading</a>. Save it as a PDF from your browser\'s print menu to keep a copy.</p>',
        f"{name} has prepared your Wyrd Reading.\n\n{note}\n\nOpen it: {link}")
    if ok: store.mark_sent(r["pro"], token, to)
    msg = f"Sent to {esc(to)}." if ok else "Email isn't set up on the site yet, so copy the private link and send it yourself."
    return A.private("Share a reading", f'<h1>{"Sent" if ok else "Not sent"}</h1><p>{msg}</p><p><a href="/pro/r/{token}/share">Back</a> · <a href="/pro">Practice desk</a></p>')


@app.get("/pro/history")
def pro_history():
    who, bounce = _pro()
    if bounce: return bounce
    rows = "".join(f"""<tr><td><a href="/pro/r/{r["token"]}" target="_blank">{esc(r["name"])}</a></td>
<td>{datetime.fromtimestamp(r["created"], timezone.utc).strftime("%-d %b %Y")}</td><td>{esc(r.get("sent_to") or "")}</td>
<td><a href="/pro/r/{r["token"]}/share">Share</a></td></tr>""" for r in store.readings(who[0]))
    return A.private("Reading history", f"""<p class="crumbs"><a href="/pro">Practice desk</a></p><h1>Every reading</h1>
<p class="lede">Reopening a reading is free. It's rebuilt fresh each time, so the timing sections are always current.</p>
{f'<div class="tw"><table><tr><th>Client</th><th>Made</th><th>Sent to</th><th></th></tr>{rows}</table></div>' if rows else '<p class="muted">None yet.</p>'}""")


@app.get("/r/<token>")
def shared_reading(token):
    """A reading a practitioner shared: open to whoever holds the private link."""
    r = store.reading_by_token(token)
    if not r: abort(404)
    return A.render_reading(r["birth"], _banner(r["pro"]))


@app.get("/account")
def account_or_hall():
    """Members go to the Hall; everyone else sees the plain account page."""
    email = A.signed_in()
    if email:
        st = A.account_status(email, fresh=bool(request.args.get("joined")))
        if st and (st["member"] or st["pro"]):
            return redirect("/hall" + ("?joined=1" if request.args.get("joined") else ""))
    return A.account_page()
