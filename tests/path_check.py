"""Working one to one: the offer page, the Lightning Path page, messages, and the contact form.

    WYRD_DEV_NODE_EPH=1 python tests/path_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email: the payment system is pretended and mail stays in the outbox."""
import os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import config
config.SECRET_KEY = "test-key"; config.STRIPE_SECRET = "sk_test_x"
config.CONSULTATION_PAYMENT_LINK_URL = "https://buy.stripe.com/test_consult"
config.MESSAGES_TO = "volva@example.com"
import app as A
from wyrd import mailer, store, billing

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

A.app.secret_key = "test-key"
A.selling = lambda: True
STATUS = {}
A.account_status = lambda email, fresh=False: STATUS.get(email, dict(billing._empty()))
c = A.app.test_client()
same = {"Sec-Fetch-Site": "same-origin"}

# ---- the offer, open to everyone ----
r = c.get("/work-with-me")
check("the old address sends people to the new one for good", r.status_code == 301 and r.headers["Location"].endswith("/letmelightyourpath"))
r = c.get("/letmelightyourpath"); t = r.get_data(as_text=True)
check("the offer page is public", r.status_code == 200)
check("it offers the $100 consult through the consult payment link", "$100" in t and "https://buy.stripe.com/test_consult" in t)
check("it offers the Lightning Path at $250 a month for three calls", "$250" in t and "three one-hour calls" in t and 'value="path-month"' in t)
check("it recommends starting with a consult", "I recommend starting with a consult" in t)
r = c.get("/reports"); t = r.get_data(as_text=True)
check("Readings gives the consult its own highlighted place", 'class="one-to-one"' in t and 'href="/letmelightyourpath"' in t and "$100" in t)
check("Readings no longer sends people to Substack to reach her", "ask through" not in t and 'href="/contact"' in t)
check("the plan is known to checkout", A.PLANS["path-month"][0] == "path" and A.PLANS["path-month"][2]() == 25000)

# ---- the member's page ----
r = c.get("/path")
check("the Lightning Path page asks you to sign in", r.status_code == 302 and "/signin" in r.headers["Location"])
with c.session_transaction() as s: s["email"] = "walker@x.co"
r = c.get("/path")
check("someone not on the path is shown the offer", r.status_code == 302 and r.headers["Location"].endswith("/letmelightyourpath"))
STATUS["walker@x.co"] = dict(billing._empty(), path=True, customer="cus_1",
                              plans=[{"id": "sub_1", "tier": "path", "status": "active", "customer": "cus_1", "interval": "month", "periodEnd": 2000000000, "cancelAtEnd": False}])
r = c.get("/path"); t = r.get_data(as_text=True)
check("a member sees their page", r.status_code == 200 and "Write to me" in t and "3 one-hour calls" in t)
check("with no booking link set, they're told to write with times", "times that suit you" in t)
config.BOOKING_URL = "https://cal.example/volva"
check("with a booking link, they get a button", "https://cal.example/volva" in c.get("/path").get_data(as_text=True))
mailer.OUTBOX.clear()
r = c.post("/path/message", data={"body": "Can we look at my Saturn return next call?\n\nThank you."}, headers=same)
check("a message is accepted", r.status_code == 302 and "sent=1" in r.headers["Location"])
m = mailer.OUTBOX[-1] if mailer.OUTBOX else {}
check("it goes to The Völva, with the member as reply-to", m.get("to") == "volva@example.com" and m.get("reply_to") == "walker@x.co" and "Saturn return" in m.get("html", ""))
check("it is kept, and shown on their page", any("Saturn return" in x["body"] for x in store.messages("walker@x.co"))
      and "Saturn return" in c.get("/path").get_data(as_text=True))
r = c.post("/path/message", data={"body": "from elsewhere"}, headers={"Sec-Fetch-Site": "cross-site"})
check("a message posted from another site is refused", not any("from elsewhere" in x["body"] for x in store.messages("walker@x.co")))
check("the account page links to the path", 'href="/path"' in c.get("/account").get_data(as_text=True))

# ---- the contact form ----
with c.session_transaction() as s: s.clear()
t = c.get("/contact").get_data(as_text=True)
check("the contact page is public and has a form", 'action="/contact"' in t and 'name="body"' in t)
mailer.OUTBOX.clear()
r = c.post("/contact", data={"name": "Ingrid", "email": "ingrid@x.co", "body": "Do you read for children?"}, headers=same)
m = mailer.OUTBOX[-1] if mailer.OUTBOX else {}
check("a contact message reaches her, reply-to the sender", "sent=1" in r.headers["Location"] and m.get("reply_to") == "ingrid@x.co" and "children" in m.get("html", ""))
n = len(mailer.OUTBOX)
c.post("/contact", data={"email": "bot@x.co", "body": "spam", "website": "http://spam"}, headers=same)
check("a bot that fills the hidden field is quietly dropped", len(mailer.OUTBOX) == n)
r = c.post("/contact", data={"email": "not-an-email", "body": "hi"}, headers=same)
check("a bad email is turned back", "sent=0" in r.headers["Location"])
check("the sitemap lists both new pages", "/letmelightyourpath<" in A.pages.sitemap("https://x") and "/contact<" in A.pages.sitemap("https://x"))

print("PATH CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
