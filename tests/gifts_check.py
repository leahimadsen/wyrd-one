"""Complimentary access from the admin: grant, expiry and revoke, against a pretend Stripe.

    python tests/gifts_check.py

The pretend Stripe answers at the HTTP layer (stripe_api._call), so every request
the site would send is recorded and checked: a gift must never open a checkout,
make a subscription or take a payment. Nothing here talks to Stripe or sends
email, and the ephemeris isn't needed."""
import os, sys, time, types, urllib.parse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.update(STRIPE_SECRET_KEY="sk_test_fake", ADMIN_PASSWORD="pw-for-tests", SECRET_KEY="k" * 40,
                  BASE_URL="https://example")
sys.modules["wyrd.ephemeris"] = types.SimpleNamespace(Ephemeris=lambda *a: object())   # gift routes never cast a chart

from wyrd import billing, mailer, stripe_api
import app as site

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- a pretend Stripe ----
CUST, SUBS, CALLS = {}, [], []

def fake_call(secret, method, path, fields=None):
    CALLS.append((method, path.split("?")[0]))
    url = urllib.parse.urlparse(path); q = dict(urllib.parse.parse_qsl(url.query))
    if method == "GET" and url.path == "/customers":
        return {"data": [c for c in CUST.values() if c["email"] == q["email"]]}
    if method == "GET" and url.path == "/customers/search":
        return {"data": [c for c in CUST.values() if c["metadata"].get("wyrd_gift") == "1"], "has_more": False}
    if method == "POST" and url.path == "/customers":
        cid = f"cus_{len(CUST) + 1}"
        CUST[cid] = {"id": cid, "email": fields["email"], "metadata": {"wyrd": fields.get("metadata[wyrd]", "")}}
        return CUST[cid]
    if method == "POST" and url.path.startswith("/customers/"):
        c = CUST[urllib.parse.unquote(url.path.split("/")[2])]
        c["metadata"].update({k[9:-1]: v for k, v in fields.items() if k.startswith("metadata[")})
        return c
    if method == "GET" and url.path == "/subscriptions":
        return {"data": [s for s in SUBS if s["customer"] == q["customer"]]}
    raise AssertionError(f"a gift should never call {method} {url.path}")

stripe_api._call = fake_call
MAIL = []
mailer.send = lambda to, subj, html, text="": MAIL.append(to) or True

def paid(cid, tier, status="active"):
    SUBS.append({"id": f"sub_{len(SUBS) + 1}", "customer": cid, "status": status, "metadata": {"tier": tier},
                 "cancel_at_period_end": False,
                 "items": {"data": [{"price": {"recurring": {"interval": "month"}}, "current_period_end": time.time() + 86400 * 20}]}})

TODAY = ["2026-10-11"]
billing.today = lambda: TODAY[0]

def status(email):
    billing.forget(email)
    return billing.status("sk_test_fake", email, fresh=True)

# ---- the admin, through the real routes ----
admin = site.app.test_client()
with admin.session_transaction() as s:
    s["admin"] = True; s["admin_at"] = time.time()
SAME = {"Sec-Fetch-Site": "same-origin"}

def grant(email, tier="member", length=None):
    form = {"email": email, "tier": tier}
    if length: form["length"] = length
    r = admin.post("/admin/gift/membership", data=form, headers=SAME)
    return urllib.parse.unquote_plus(r.headers.get("Location", ""))

def revoke(email):
    return admin.post("/admin/gift/end", data={"email": email}, headers=SAME)

def as_user(email):
    c = site.app.test_client()
    with c.session_transaction() as s: s["email"] = email
    return c

# ---- the form ----
page = admin.get("/admin/gifts").get_data(as_text=True)
check("30 days is offered and chosen by default", '<option value="30d" selected>30 days</option>' in page)
check("strangers can't see the gift admin", site.app.test_client().get("/admin/gifts").status_code == 404)
check("strangers can't grant", site.app.test_client().post("/admin/gift/membership", data={"email": "x@y.co"}, headers=SAME).status_code == 404)
check("a grant from another site is refused", admin.post("/admin/gift/membership", data={"email": "x@y.co"},
                                                          headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403)
check("strangers can't revoke", site.app.test_client().post("/admin/gift/end", data={"email": "x@y.co"}, headers=SAME).status_code == 404)
check("30 days from 11 October runs to the end of 10 November", site.gift_until("30d", date(2026, 10, 11)) == "2026-11-10")

# ---- a brand-new creator: 30 days of Professional ----
CALLS.clear()
done = grant("creator@x.co", "pro")              # the default length
check("grant goes through", "Given to creator@x.co, until the end of 10 November 2026" in done)
check("only customer records were touched: no checkout, subscription or payment",
      {p for _, p in CALLS} <= {"/customers", "/customers/search", "/subscriptions"} | {f"/customers/{c}" for c in CUST})
check("nothing was asked of the creator's card", not any("payment" in p or "checkout" in p or "invoice" in p for _, p in CALLS))
check("they're emailed", MAIL[-1] == "creator@x.co")
st = status("creator@x.co")
check("access is on", st["pro"] and st["gift"]["until"] == "2026-11-10" and not st["plans"])
check("the practice desk opens", as_user("creator@x.co").get("/pro").status_code == 200)
listed = admin.get("/admin/gifts").get_data(as_text=True)
check("the admin sees the account and its expiry", "creator@x.co · The Inner Circle until the end of 10 November 2026" in listed
      and "active" in listed)
check("their account page says when it ends", "until the end of 10 November 2026" in as_user("creator@x.co").get("/account").get_data(as_text=True))

TODAY[0] = "2026-11-10"
check("still on through the last day", status("creator@x.co")["pro"])
TODAY[0] = "2026-11-11"
st = status("creator@x.co")
check("expired the day after: back to free", not st["pro"] and not st["member"] and not st["gift"]["live"])
check("the practice desk sends them to the plans", as_user("creator@x.co").get("/pro").headers["Location"].endswith("/membership#pro"))
check("the admin list shows it ended", "ended" in admin.get("/admin/gifts").get_data(as_text=True))
check("no subscription was ever made", not SUBS)

# ---- revoke before expiry ----
TODAY[0] = "2026-10-11"
grant("early@x.co", "member", "30d")
check("membership gift on", status("early@x.co")["member"] and as_user("early@x.co").get("/api/me").get_json()["member"])
revoke("early@x.co")
st = status("early@x.co")
check("revoked: back to free at once", not st["member"] and st["gift"] is None)
check("revoked: member price gone", not as_user("early@x.co").get("/api/me").get_json()["member"])
check("revoked gifts leave the admin list", "early@x.co" not in admin.get("/admin/gifts").get_data(as_text=True))

# ---- someone who already pays ----
CUST["cus_paid"] = {"id": "cus_paid", "email": "payer@x.co", "metadata": {"wyrd": "1"}}
paid("cus_paid", "member")
before = [dict(s) for s in SUBS]
done = grant("payer@x.co", "pro", "30d")
check("the admin is told their subscription is untouched", "already pay for The Order" in done and "untouched" in done)
st = status("payer@x.co")
check("gift adds Professional on top of the paid membership", st["pro"] and st["member"])
TODAY[0] = "2026-11-11"
st = status("payer@x.co")
check("after expiry the paid membership remains", st["member"] and not st["pro"])
revoke("payer@x.co")
check("revoking keeps the paid membership", status("payer@x.co")["member"])
check("subscriptions were never changed", SUBS == before)

# ---- one person, two Stripe customers (checkout can make a second) ----
# The gift sits on the site's own record; the membership is paid on the other.
TODAY[0] = "2026-10-11"
CUST["cus_a"] = {"id": "cus_a", "email": "two@x.co", "metadata": {"wyrd": "1", "wyrd_gift": "1", "wyrd_gift_tier": "pro", "wyrd_gift_until": "2026-12-01"}}
CUST["cus_b"] = {"id": "cus_b", "email": "two@x.co", "metadata": {}}
paid("cus_b", "member")
check("a gift on the other record counts", status("two@x.co")["pro"])
revoke("two@x.co")
st = status("two@x.co")
check("revoke ends it on the record that holds it", not st["pro"] and CUST["cus_a"]["metadata"]["wyrd_gift"] == "0")
check("and the paid membership on the other carries on", st["member"])
grant("two@x.co", "pro", "30d")
check("a new grant isn't hidden by the old ended one", status("two@x.co")["pro"])
CUST["cus_a"]["metadata"].update(wyrd_gift="1", wyrd_gift_tier="pro", wyrd_gift_until="forever")
grant("two@x.co", "pro", "30d")
st = status("two@x.co")
check("a new grant replaces the earlier gift", st["gift"]["until"] == "2026-11-10" and CUST["cus_a"]["metadata"]["wyrd_gift"] == "0")
TODAY[0] = "2026-11-11"
st = status("two@x.co")
check("and expires on its own date", not st["pro"] and st["member"])

print("GIFTS CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
