"""Signing in is for those who pay: a sign-in link goes only to the Order, the Inner Circle, the
Lightning Path, a gift, someone whose plan has ended, or the owner. The page reads the same
whoever asks, so it never tells a stranger who is a member.

    WYRD_DEV_NODE_EPH=1 python tests/signin_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None); os.environ.pop("WYRD_DEV_SHOW_LINKS", None)
import config
config.SECRET_KEY = "test-key"; config.STRIPE_SECRET = "sk_test_x"; config.OWNER_EMAIL = "Owner@Example.com"
import app as A
from wyrd import billing, mailer, stripe_api

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

def plan(tier, status): return {"id": "sub_1", "tier": tier, "status": status}
PEOPLE = {
    "order@example.com":   {"member": True, "plans": [plan("member", "active")]},
    "circle@example.com":  {"pro": True, "plans": [plan("pro", "active")]},
    "path@example.com":    {"path": True, "plans": [plan("path", "active")]},
    "gifted@example.com":  {"member": True, "gift": {"tier": "member", "live": True, "until": None}},
    "lapsed@example.com":  {"plans": [plan("member", "canceled")]},
    "reader@example.com":  {"customer": "cus_reader"},          # bought a reading once: a customer, no plan
}
DOWN = {"down@example.com"}
ASKED = []
def fake_status(secret, email, fresh=False):
    ASKED.append((email, fresh))
    if email in DOWN: raise stripe_api.StripeError("unreachable")
    return {**billing._empty(), **PEOPLE.get(email, {})}
billing.status = fake_status
MAIL = []
mailer.send = lambda to, subject, html, text="", reply_to=None: MAIL.append(to) or True

web = A.app.test_client()
SAME = {"Sec-Fetch-Site": "same-origin"}
def ask(email):
    A._hits.clear()                            # the per-visitor limit isn't what's being tested here
    n = len(MAIL)
    r = web.post("/signin", data={"email": email, "next": "/account"}, headers=SAME)
    return r, len(MAIL) > n

page = web.get("/signin").get_data(as_text=True)
check("the sign-in page says it is for members", "Signing in is for members of the Order, the Inner Circle and the Lightning Path" in page)
check("and shows a non-member the way in", 'href="/membership"' in page and "needs no sign-in" in page)

for email in ("order@example.com", "circle@example.com", "path@example.com", "gifted@example.com", "lapsed@example.com"):
    r, sent = ask(email)
    check(f"{email.split('@')[0]}: a sign-in link is sent", r.status_code == 200 and sent)
check("membership is looked up fresh, so someone who has just joined is found", ASKED[-1] == ("lapsed@example.com", True))

r, sent = ask("owner@example.com")
check("the owner always gets a link", sent)

stranger, sent = ask("stranger@example.com")
check("someone who has never paid gets no link", stranger.status_code == 200 and not sent)
r, sent = ask("reader@example.com")
check("nor does someone who only bought a reading (it lives at its own link)", not sent)

member, _ = ask("order@example.com")
strip = lambda r, e: r.get_data(as_text=True).replace(e, "EMAIL")
check("the page reads the same for a member and a stranger", strip(member, "order@example.com") == strip(stranger, "stranger@example.com"))
check("and says a link comes only if the address belongs to a member", "If stranger@example.com belongs to a member" in stranger.get_data(as_text=True))

r, sent = ask("down@example.com")
check("when Stripe can't be reached, nothing is sent and the page says to try again", r.status_code == 503 and not sent)

r = web.post("/signin", data={"email": "order@example.com"}, headers={"Sec-Fetch-Site": "cross-site"})
check("a form posted from another site sends nothing", r.status_code == 429)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
