"""Accounts, plans, Body Weather and the weekly job, against a pretend Stripe.

    DATA_DIR=... python tests/members_check.py

Nothing here talks to Stripe or sends email."""
import json, os, sys, time, types
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from wyrd import accounts, billing, jobs, mailer, pages, weather, engine, stripe_api
from wyrd.ephemeris import Ephemeris

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- sign-in links ----
tok = accounts.make_token("k", "a@b.co", "/membership")
check("link reads back", accounts.read_token("k", tok) == ("a@b.co", "/membership"))
check("link signed with another key fails", accounts.read_token("other", tok) == (None, None))
check("tampered link fails", accounts.read_token("k", tok[:-2] + "xx") == (None, None))
check("next can't leave the site", accounts.safe_next("//evil.com") == "/account" and accounts.safe_next("https://x") == "/account")
check("emails cleaned", accounts.clean_email(" A@B.Co ") == "a@b.co" and accounts.clean_email("nope") is None)

# ---- a pretend Stripe ----
CUST = {"cus_1": {"id": "cus_1", "email": "m@x.co", "metadata": {"wyrd": "1", "wyrd_birth": json.dumps(
    {"name": "Freya Test", "date": "1990-05-17", "time": "14:30", "lat": "51.5", "lon": "-0.13", "tz": "Europe/London", "place_label": "London"})}}}
def sub(i, tier, status, cust="cus_1"):
    return {"id": f"sub_{i}", "customer": cust, "status": status, "metadata": {"tier": tier}, "cancel_at_period_end": False,
            "items": {"data": [{"price": {"recurring": {"interval": "month"}}, "current_period_end": time.time() + 86400}]}}
SUBS = [sub(1, "member", "active"), sub(2, "pro", "canceled")]
stripe_api.find_customer = lambda s, e: next((c for c in CUST.values() if c["email"] == e), None)
stripe_api.subscriptions = lambda s, c: [x for x in SUBS if x["customer"] == c]
stripe_api.update_customer_metadata = lambda s, c, f: CUST[c]["metadata"].update({k: str(v) for k, v in f.items()})

st = billing.status("sk", "m@x.co")
check("active membership found", st["member"] and not st["pro"])
check("cancelled professional plan doesn't count", any(p["tier"] == "pro" and p["status"] == "canceled" for p in st["plans"]))
check("saved chart read back", st["birth"]["name"] == "Freya Test")
check("stranger has nothing", not billing.status("sk", "who@x.co")["member"])
billing.count_pro_reading("sk", "m@x.co"); billing.count_pro_reading("sk", "m@x.co")
check("pro readings counted this month", billing.status("sk", "m@x.co", fresh=True)["proUse"] == 2)

# ---- gifts ----
CUST["cus_2"] = {"id": "cus_2", "email": "g@x.co", "metadata": {"wyrd_gift": "1", "wyrd_gift_tier": "pro", "wyrd_gift_until": "forever"}}
CUST["cus_3"] = {"id": "cus_3", "email": "old@x.co", "metadata": {"wyrd_gift": "1", "wyrd_gift_tier": "member", "wyrd_gift_until": "2020-01-01"}}
check("gift for good gives Professional", billing.status("sk", "g@x.co")["pro"])
check("ended gift gives nothing", not billing.status("sk", "old@x.co")["member"])
stripe_api.search_customers = lambda s, q: [c for c in CUST.values() if c["metadata"].get("wyrd_gift") == "1"]

# ---- Body Weather and the weekly job ----
eph = Ephemeris(config.DATA_DIR, config.EPHEMERIS_FILE)
from datetime import date
c = engine.cast(eph, 1990, 5, 17, 13.5, 51.5, -0.13)
w = weather.week(eph, c, date(2026, 10, 5))
check("week has seven moons", len(w["moon"]) == 7)
html = weather.render(w, "Freya")
check("report names both bodies", "Your birth body" in html and "Your Dharma body" in html)
check("no slow planet listed as this week's", all(set(ch["by"]) & weather.FAST for body in ("natal", "dharma") for ch in w[body]["channels"]))

jobs._live_subscriptions = lambda s: [dict(x, customer=CUST[x["customer"]]) for x in SUBS if x["status"] in jobs.LIVE]
jobs._sales = lambda s: {"readings": 3, "revenue": 13200}
mailer.OUTBOX.clear()
mailer.send = lambda to, subj, html, text="": mailer.OUTBOX.append({"to": to, "subject": subj}) or True
cfg = types.SimpleNamespace(STRIPE_SECRET="sk", BASE_URL="https://example", OWNER_EMAIL="owner@x.co")
from wyrd import timefix
def birth_from(b):
    y, mo, d = map(int, b["date"].split("-")); hh, mi = map(int, b["time"].split(":"))
    return {"ut": timefix.to_ut(y, mo, d, hh, mi, b["tz"]), "place": {"lat": float(b["lat"]), "lon": float(b["lon"])}}
cast_for = lambda b: engine.cast(eph, b["ut"]["y"], b["ut"]["mo"], b["ut"]["d"], b["ut"]["h"], b["place"]["lat"], b["place"]["lon"])
r1 = jobs.weekly(eph, cast_for, birth_from, cfg)
r2 = jobs.weekly(eph, cast_for, birth_from, cfg)
check("weekly job sends once, gifts included", r1["sent"] == 1 and r1["members"] == 2 and r2["sent"] == 0 and r2["skipped"] == 2)
check("owner summary sent", any(m["to"] == "owner@x.co" for m in mailer.OUTBOX))

# ---- pages for search ----
sm = pages.sitemap("https://example")
check("sitemap lists every learning page", sm.count("<url>") == 6 + 64 + 27 + 12)
t, d, body, ld = pages.reports("https://example", 4400, 3520)
check("readings page says astrology and the price", "Astrology" in t and '"price": "44.00"' in ld)

print("MEMBERS CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
