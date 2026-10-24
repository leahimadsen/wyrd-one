"""A lantern for your path: The Völva one to one, and reaching her.

/letmelightyourpath   A lantern for your path: the first 1:1 consult ($100, through the consult Payment Link) and the Lightning Path,
                the monthly 1:1 ($250: three one-hour calls a month and messaging between them).
/path           A member's own page on the Lightning Path: book a call, write to her, past messages, the plan.
/contact        A public form, so people can reach her on the site rather than through Substack.

Messages are emailed to MESSAGES_TO with the sender as reply-to, so she answers from her own inbox,
and they are kept in the database too (when one is connected) and listed at /admin/messages.
Loaded at the end of app.py, so it can use the site's helpers."""
import sys, time
from datetime import datetime, timezone
from flask import request, redirect

A = sys.modules.get("app") or sys.modules["__main__"]
app, config, billing, mailer, esc, money = A.app, A.config, A.billing, A.mailer, A.esc, A.money
from wyrd import store, accounts, testimonials

MAX = 5000


def _paras(text):
    return "".join(f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in text.strip().split("\n\n") if p.strip())


def _deliver(sender, subject, text, kind):
    """Email it to The Völva, replying straight to the sender. True if it went."""
    body = _paras(text)
    html = (f"<p><b>{esc(kind)}</b> from {esc(sender)}</p>{body}"
            f"<p style='color:#777'>Reply to this email and your answer goes straight to {esc(sender)}.</p>")
    return mailer.send(config.MESSAGES_TO, subject, html, f"{kind} from {sender}\n\n{text}\n\nReply to answer them.", reply_to=sender)


def _keep(email, text):
    if not store.ready(): return False
    try:
        store.add_message(email, text); return True
    except Exception as e:
        app.logger.error("message not kept: %s", e); return False


# ---------------- the offer ----------------
LANTERN = "/letmelightyourpath"


@app.get("/work-with-me")
def work_with_me_old():
    """The page's first address: old links and shares still arrive."""
    return redirect(LANTERN, 301)


@app.get(LANTERN)
def work_with_me():
    on = A.selling()
    consult = config.CONSULTATION_PAYMENT_LINK_URL
    c, p, n = money(config.CONSULT_CENTS), money(config.PATH_MONTHLY_CENTS), config.PATH_CALLS
    words = ["", "one", "two", "three", "four", "five", "six"]
    calls = words[n] if n < len(words) else str(n)
    consult_btn = (f'<a class="btn-buy" href="{esc(consult)}">Book a first consult, {c}</a>' if consult
                   else '<p class="muted">Booking opens soon. <a href="/contact">Write to me</a> in the meantime.</p>')
    path_btn = (f'<form method="post" action="/api/subscribe"><input type="hidden" name="plan" value="path-month">'
                f'<button class="btn-cast" type="submit">Begin the Lightning Path, {p} a month</button></form>' if on
                else '<p class="muted">Opening soon.</p>')
    body = f"""<h1>A lantern for your path</h1>
<p class="lede">I am an emissary of Aja Ekapada, the unborn, one-footed lord of Purva Bhadrapada, and as his emissary I can illuminate his burning path of electricity. One to one, I hold the lantern while you walk your own chart.</p>
<div class="wwm">
  <section class="offer wwm-lead"><p class="hall-kicker">Start here</p><h2>A first consult</h2><div class="price">{c}<small> once</small></div>
    <p>An initial 1:1 consult is {c}. We'll plan for an hour, but if we run a little over, there's no extra charge. I want us to have enough time to connect and understand what you need.</p>
    <ul><li>About an hour together, with no clock-watching</li>
      <li>After payment, give your birth details to open your full written reading, so we read from it together</li>
      <li>After payment, choose your 60-minute appointment in Calendly</li></ul>
    {consult_btn}</section>
  <section class="offer"><p class="hall-kicker">Month by month</p><h2>{esc(config.PATH_NAME)}</h2><div class="price">{p}<small> a month</small></div>
    <p>If you'd like the lantern carried further, {esc(config.PATH_NAME[:1].lower() + config.PATH_NAME[1:] if config.PATH_NAME.startswith('The ') else config.PATH_NAME)} is {p} a month. That includes {calls} one-hour calls each month, where we follow the current beneath the surface of things, plus messages between calls about where you are on the path or what you'd like lit next.</p>
    <ul><li>{calls.capitalize()} one-hour calls a month, booked from your page on the site</li>
      <li>Messaging between calls, from the same page</li>
      <li>Cancel any time; your place runs to the end of the month you've paid for</li></ul>
    {path_btn}</section>
</div>
<p class="note-box">I recommend starting with a consult, so we can meet and see whether walking this path together feels right.</p>
{testimonials.render("work")}
<h2>Questions</h2>
<div class="order-faq">
  <details><summary>What do I need for the consult?</summary><p>Your date, time and place of birth, the time from your birth certificate if you can. You give them after payment on your consultation page, where you also choose your appointment time.</p></details>
  <details><summary>How do I book my calls on the Lightning Path?</summary><p>From your page on the site, which opens as soon as you join. It's also where you write to me between calls.</p></details>
  <details><summary>Can I cancel the Lightning Path?</summary><p>Any time, from your account. You keep your place until the end of the month you've paid for.</p></details>
  <details><summary>Something else?</summary><p><a href="/contact">Write to me</a>.</p></details>
</div>"""
    return A.page(f"A Lantern for Your Path: a 1:1 Consult and {config.PATH_NAME} with The Völva · The Wyrd Console",
                  f"One to one with The Völva, emissary of Aja Ekapada: a first consult for {c}, about an hour, and {config.PATH_NAME}, {p} a month for {calls} one-hour calls and messages between them.",
                  body)


# ---------------- a member's page ----------------
def _walker():
    """(email, status) for someone on the Lightning Path (or the admin); otherwise a redirect."""
    email = A.signed_in()
    if not email: return None, redirect("/signin?next=/path")
    st = A.account_status(email)
    if st is None:
        return None, A.private(config.PATH_NAME, f"<h1>{esc(config.PATH_NAME)}</h1><p>We couldn't reach the payment system just now. Refresh in a moment.</p>", status=503)
    if not (st.get("path") or A.is_admin()): return None, redirect(LANTERN)
    return (email, st), None


@app.get("/path")
def path_page():
    who, bounce = _walker()
    if bounce: return bounce
    email, st = who
    joined = f'<p class="note-box">Welcome to {esc(config.PATH_NAME)}. Your payment went through.</p>' if request.args.get("joined") else ""
    sent = request.args.get("sent")
    note = {"1": '<p class="note-box">Sent. The reply will come to your inbox.</p>',
            "0": f'<p class="err">That didn\'t send. Please try again in a moment, or email {esc(config.MESSAGES_TO)}.</p>'}.get(sent, "")
    book = (f'<p><a class="btn-cast" href="{esc(config.BOOKING_URL)}" target="_blank" rel="noopener">Book a call</a></p>'
            if config.BOOKING_URL else '<p>Write below with a few times that suit you, and I\'ll confirm one.</p>')
    past = ""
    if store.ready():
        try: rows = store.messages(email)
        except Exception as e:
            app.logger.error("messages: %s", e); rows = []
        items = "".join(f'<li><span class="muted">{datetime.fromtimestamp(r["created"], timezone.utc).strftime("%-d %B %Y")}</span>{_paras(r["body"])}</li>' for r in rows)
        past = f'<h2>What you\'ve written</h2><ul class="path-msgs">{items}</ul>' if items else ""
    plans = '<form method="post" action="/billing/portal"><button class="alt" type="submit">Manage or cancel, change card, see receipts</button></form>' if st["plans"] else ""
    body = f"""<h1>{esc(config.PATH_NAME)}</h1><p class="muted">Signed in as {esc(email)}</p>{joined}{note}
<h2>Your calls</h2>
<p>{config.PATH_CALLS} one-hour calls each month, where we follow the current beneath the surface of things.</p>
{book}
<h2>Write to me</h2>
<p>Between calls, about where you are on the path or what you'd like lit next. It comes to me by email, and my reply comes to {esc(email)}.</p>
<form class="pg-form" method="post" action="/path/message">
<label>Your message <textarea name="body" rows="8" maxlength="{MAX}" required></textarea></label>
<button class="btn-cast" type="submit">Send</button></form>
{past}
<h2>Your plan</h2>{plans}
<p><a href="/account">Your account</a> · <a href="/account/data">Your data</a></p>"""
    return A.private(config.PATH_NAME, body)


@app.post("/path/message")
def path_message():
    who, bounce = _walker()
    if bounce: return bounce
    if not A.same_origin(): return redirect("/path")
    email, _ = who
    if A.limited(12, 3600): return A.private("Wait a little", "<h1>Wait a little</h1><p>That's a lot of messages in an hour. Try again shortly.</p>", status=429)
    text = (request.form.get("body") or "").strip()[:MAX]
    if not text: return redirect("/path")
    kept = _keep(email, text)
    sent = _deliver(email, f"{config.PATH_NAME}: a message from {email}", text, f"A message on {config.PATH_NAME}")
    return redirect("/path?sent=" + ("1" if sent or kept else "0"))


# ---------------- reaching her ----------------
@app.get("/contact")
def contact_page():
    done = request.args.get("sent")
    email = A.signed_in() or ""
    note = {"1": '<p class="note-box">Thank you. Your message is on its way, and the reply will come to the email you gave.</p>',
            "0": '<p class="err">That didn\'t send. Please try again in a moment.</p>'}.get(done, "")
    body = f"""<h1>Write to me</h1>
<p class="lede">Questions about a reading, the Order, a consult or the Lightning Path, or anything else. I read everything myself.</p>{note}
<form class="pg-form" method="post" action="/contact">
<label>Your name <input name="name" maxlength="80" autocomplete="name"></label>
<label>Your email <input name="email" type="email" required maxlength="254" autocomplete="email" value="{esc(email)}"></label>
<label>Your message <textarea name="body" rows="8" maxlength="{MAX}" required></textarea></label>
<label class="hp" aria-hidden="true">Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label>
<button class="btn-cast" type="submit">Send</button></form>
<p class="muted">Your name, email and message come to me by email and a copy is kept on the site; see <a href="/privacy">Privacy</a>.</p>
<p class="muted">Looking for something one to one? See <a href="/letmelightyourpath">a lantern for your path</a>: a first consult and the Lightning Path.</p>"""
    return A.page("Contact The Völva · The Wyrd Console", "Write to The Völva about a reading, the Order, or a consult one to one.", body)


@app.post("/contact")
def contact_send():
    if not A.same_origin(): return redirect("/contact")
    if A.limited(5, 3600): return A.private("Wait a little", "<h1>Wait a little</h1><p>Too many messages from here in the last hour. Try again later.</p>", status=429)
    if request.form.get("website"): return redirect("/contact?sent=1")            # a bot filled the hidden field
    email = accounts.clean_email(request.form.get("email"))
    text = (request.form.get("body") or "").strip()[:MAX]
    name = (request.form.get("name") or "").strip()[:80]
    if not email or not text: return redirect("/contact?sent=0")
    who = f"{name} <{email}>" if name else email
    kept = _keep(email, (f"{name}: " if name else "") + text)
    sent = _deliver(email, f"A message from {name or email} · The Wyrd Console", text, f"A message from {who}")
    return redirect("/contact?sent=" + ("1" if sent or kept else "0"))


# ---------------- for The Völva ----------------
@app.get("/admin/messages")
def admin_messages():
    A.admin_only()
    if not store.ready():
        return A.private("Messages", '<p class="crumbs"><a href="/admin">Admin</a></p><h1>Messages</h1><p>Messages are kept once the database is connected. Until then they come only by email.</p>')
    try:
        rows = store._run("SELECT email, body, created FROM messages ORDER BY created DESC LIMIT 200", (), "all")
    except Exception as e:
        rows = []; app.logger.error("admin messages: %s", e)
    items = "".join(f'<li><b>{esc(r["email"])}</b> <span class="muted">· {datetime.fromtimestamp(r["created"], timezone.utc).strftime("%-d %B %Y, %H:%M UTC")}</span>{_paras(r["body"])}</li>' for r in rows)
    return A.private("Messages", f"""<p class="crumbs"><a href="/admin">Admin</a></p><h1>Messages</h1>
<p class="muted">From the contact form and from the Lightning Path. Each one also came to {esc(config.MESSAGES_TO)} by email; reply there.</p>
<ul class="path-msgs">{items or "<li class='muted'>None yet.</li>"}</ul>""")
