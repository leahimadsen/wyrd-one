"""The Order's Hall and the Inner Circle's practice desk, against a pretend Stripe and a throwaway database.

    python tests/hall_check.py
    WYRD_TEST_DATABASE_URL=postgres://...  python tests/hall_check.py     (the same against Postgres)

Nothing here talks to Stripe or sends email, and the ephemeris isn't needed: the weekly letter
and the reading itself are stood in for, so this checks the records and who may see them."""
import os, sys, tempfile, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.update(SECRET_KEY="k" * 40, BASE_URL="https://example", STRIPE_SECRET_KEY="sk_test_fake",
                  WYRD_DB_PATH=os.path.join(tempfile.mkdtemp(), "wyrd.db"))
os.environ.pop("DATABASE_URL", None)                 # never the live database
if os.environ.get("WYRD_TEST_DATABASE_URL"):         # a throwaway Postgres, to check the SQL there too
    os.environ["DATABASE_URL"] = os.environ["WYRD_TEST_DATABASE_URL"]
sys.modules["wyrd.ephemeris"] = types.SimpleNamespace(Ephemeris=lambda *a: object())

import app as site
import order_routes
from wyrd import store, billing, mailer
from flask import Response
if os.environ.get("WYRD_TEST_DATABASE_URL"):           # a throwaway Postgres starts empty, every run
    for t in ("letters", "kin", "practice", "clients", "readings"): store._run(f"DROP TABLE IF EXISTS {t}")
    store.reset_for_tests()

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

FREYA = {"name": "Freya Test", "date": "1990-05-17", "time": "14:30", "lat": "51.5", "lon": "-0.13", "tz": "Europe/London", "place_label": "London, UK"}
KIN = dict(FREYA, name="Mum", date="1960-02-01")
def status(member=False, pro=False, birth=None, use=0):
    return {"member": member, "pro": pro, "plans": [], "gift": None, "birth": birth, "customer": None, "proUse": use}

WHO = {"cur": None}
STATUS = {"m@x.co": status(member=True, birth=FREYA), "p@x.co": status(pro=True, use=0),
          "p2@x.co": status(pro=True), "free@x.co": status()}
site.signed_in = lambda: WHO["cur"]
site.account_status = lambda email, fresh=False: STATUS.get(email)
site.weather_for = lambda b, start=None: f"<p>WEATHER for {b.get('name', '')}</p>"
site.render_reading = lambda meta, banner="", sample=False: Response(f"READING {meta.get('name')} | {banner}", mimetype="text/html")
COUNTED, SENT = [], []
billing.count_pro_reading = lambda secret, email: COUNTED.append(email)
mailer.send = lambda to, subject, html_body, text=None: SENT.append((to, subject, html_body)) or True

c = site.app.test_client()
H = {"Sec-Fetch-Site": "same-origin"}
def as_(email): WHO["cur"] = email

# ---- the Hall ----
as_(None)
check("signed out: the Hall asks you to sign in", c.get("/hall").headers["Location"].startswith("/signin"))
as_("free@x.co")
check("not in the Order: the Hall shows the Order", c.get("/hall").headers["Location"] == "/membership")
check("not in the Order: /account is the plain account page", c.get("/account").status_code == 200)
as_("m@x.co")
check("member: /account goes to the Hall", c.get("/account").headers["Location"] == "/hall")
check("member: joined flag carried to the Hall", c.get("/account?joined=1").headers["Location"] == "/hall?joined=1")
r = c.get("/hall"); t = r.get_data(as_text=True)
check("the Hall opens", r.status_code == 200 and "The Hall" in t)
check("this week's letter is in it", "WEATHER for Freya Test" in t)
check("the Hall says no-store and noindex", r.headers.get("Cache-Control") == "no-store" and "noindex" in r.headers.get("X-Robots-Tag", ""))
week = site.weather.monday().isoformat()
check("this week's letter kept in the archive", store.letter("m@x.co", week) is not None)
store.save_letter("m@x.co", "2020-01-06", "<p>an old week</p>")
t = c.get("/hall").get_data(as_text=True)
check("past letters listed, this week not repeated", "/hall/letters/2020-01-06" in t and f"/hall/letters/{week}" not in t)
check("a past letter reopens", "an old week" in c.get("/hall/letters/2020-01-06").get_data(as_text=True))
check("an unknown week is not found", c.get("/hall/letters/1999-01-04").status_code == 404)
old = c.get("/account/weather")
check("old weather links land in the Hall", old.headers["Location"] == "/hall")

# ---- charts for loved ones ----
r = c.post("/api/hall/kin", json={"label": "Mum", "birth": KIN}, headers=H)
check("a loved one's chart kept", r.status_code == 200 and len(store.kin("m@x.co")) == 1)
kid = store.kin("m@x.co")[0]["id"]
check("their weather opens", "WEATHER for Mum" in c.get(f"/hall/kin/{kid}").get_data(as_text=True))
check("they're listed in the Hall", "Mum" in c.get("/hall").get_data(as_text=True))
check("bad birth details refused", c.post("/api/hall/kin", json={"label": "x", "birth": {"date": "nope"}}, headers=H).status_code == 400)
check("from another site refused", c.post("/api/hall/kin", json={"label": "x", "birth": KIN}, headers={"Sec-Fetch-Site": "cross-site"}).status_code == 401)
for i in range(store.KIN_MAX - 1): store.add_kin("m@x.co", f"k{i}", KIN)
check(f"no more than {store.KIN_MAX}", c.post("/api/hall/kin", json={"label": "one more", "birth": KIN}, headers=H).status_code == 400)
as_("p2@x.co")
check("someone else's loved one is not found", c.get(f"/hall/kin/{kid}").status_code == 404)
c.post(f"/hall/kin/{kid}/remove", headers=H)
check("someone else can't remove them", store.kin_one("m@x.co", kid) is not None)
as_("free@x.co")
check("not in the Order: can't keep charts", c.post("/api/hall/kin", json={"label": "x", "birth": KIN}, headers=H).status_code == 403)
as_("m@x.co")
c.post(f"/hall/kin/{kid}/remove", headers=H)
check("removed by its keeper", store.kin_one("m@x.co", kid) is None)
check("a member without the Inner Circle can't open the desk", c.get("/pro").headers["Location"] == "/membership#pro")

# ---- the practice desk ----
as_("p@x.co")
r = c.get("/pro"); t = r.get_data(as_text=True)
check("the desk opens", r.status_code == 200 and "Your practice desk" in t and "Add a client" in t)
check("the client form posts to the desk, not a new tab", 'action="/pro/clients"' in t and 'target="_blank"' not in t.split("Add a client")[1])
c.post("/pro/practice", data={"name": "Moonwise Astrology"}, headers=H)
check("practice name kept", store.practice_name("p@x.co") == "Moonwise Astrology")
form = dict(FREYA, name="Ada Client", email="Ada@Client.co", notes="Saturn return in March")
r = c.post("/pro/clients", data=form, headers=H)
cid = r.headers["Location"].rsplit("/", 1)[1]
cl = store.client("p@x.co", cid)
check("client saved", cl and cl["name"] == "Ada Client" and cl["email"] == "ada@client.co" and cl["birth"]["date"] == "1990-05-17")
t = c.get(f"/pro/clients/{cid}").get_data(as_text=True)
check("client page shows notes and a prefilled edit form", "Saturn return in March" in t and 'value="1990-05-17"' in t and 'value="London, UK"' in t)
check("bad details refused", c.post("/pro/clients", data=dict(form, date="1990-13-45"), headers=H).status_code == 400)
c.post(f"/pro/clients/{cid}/edit", data=dict(form, time="15:00", notes="moved"), headers=H)
cl = store.client("p@x.co", cid)
check("client edited", cl["birth"]["time"] == "15:00" and cl["notes"] == "moved")
check("their Body Weather", "WEATHER for" in c.post(f"/pro/clients/{cid}/weather", headers=H).get_data(as_text=True))

r = c.post(f"/pro/clients/{cid}/reading", headers=H)
token = r.headers["Location"].rsplit("/", 1)[1]
check("a reading uses one credit", COUNTED == ["p@x.co"])
t = c.get(f"/pro/r/{token}").get_data(as_text=True)
check("the reading opens with the practice's name", "READING Ada Client" in t and "Prepared by Moonwise Astrology" in t)
c.get(f"/pro/r/{token}")
check("reopening it uses no credit", COUNTED == ["p@x.co"])
check("it's in the history", "Ada Client" in c.get("/pro/history").get_data(as_text=True))
check("the share page offers the private link", f"https://example/r/{token}" in c.get(f"/pro/r/{token}/share").get_data(as_text=True))
c.post(f"/pro/r/{token}/send", data={"to": "ada@client.co", "note": "Enjoy"}, headers=H)
check("sent by email, with the link and note", SENT and SENT[-1][0] == "ada@client.co" and f"/r/{token}" in SENT[-1][2] and "Enjoy" in SENT[-1][2])
check("marked as sent", store.reading_by_token(token)["sent_to"] == "ada@client.co")

STATUS["p@x.co"]["proUse"] = site.config.PRO_READINGS_A_MONTH
check("no credits left: refused", c.post(f"/pro/clients/{cid}/reading", headers=H).status_code == 402 and len(COUNTED) == 1)
check("from another site refused", c.post(f"/pro/clients/{cid}/reading", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403)

as_(None)
t = c.get(f"/r/{token}").get_data(as_text=True)
check("the client opens their shared reading without signing in", "READING Ada Client" in t and "Moonwise" in t and "share" not in t.lower())
check("an unknown share link is not found", c.get("/r/not-a-token").status_code == 404)
check("robots keep out of the Hall and shared readings", "Disallow: /hall" in c.get("/robots.txt").get_data(as_text=True))

as_("p2@x.co")
check("another practitioner can't see the client", c.get(f"/pro/clients/{cid}").status_code == 404)
check("nor reopen the reading", c.get(f"/pro/r/{token}").status_code == 404)
check("nor its share page", c.get(f"/pro/r/{token}/share").status_code == 404)
check("nor send it", c.post(f"/pro/r/{token}/send", data={"to": "x@y.co"}, headers=H).status_code == 404)
c.post(f"/pro/clients/{cid}/remove", headers=H)
check("nor remove the client", store.client("p@x.co", cid) is not None)
check("nor edit them", c.post(f"/pro/clients/{cid}/edit", data=form, headers=H).status_code == 404)
check("their desk is empty", "No clients yet" in c.get("/pro").get_data(as_text=True))

as_("p@x.co")
c.post(f"/pro/clients/{cid}/remove", headers=H)
check("client removed, the reading kept", store.client("p@x.co", cid) is None and store.reading_by_token(token) is not None)

print("all good" if not bad else f"{bad} failed")
sys.exit(1 if bad else 0)
