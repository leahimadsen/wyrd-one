"""Privacy: the policy page is public and linked everywhere, every response carries the security
headers, and a signed-in person can download and delete what the site keeps under their email
(and only theirs), with the saved chart cleared from Stripe too.

    WYRD_DEV_NODE_EPH=1 python tests/privacy_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import config
config.SECRET_KEY = "test-key"; config.STRIPE_SECRET = "sk_test_x"
import app as A
from wyrd import billing, store, stripe_api

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

BIRTH = {"name": "Ada", "date": "1990-05-01", "time": "12:00", "lat": "51.5", "lon": "-0.1", "tz": "Europe/London", "place_label": "London"}
ME, OTHER = "me@example.com", "other@example.com"
CUSTOMERS = {ME: [{"id": "cus_me", "metadata": {"wyrd_birth": json.dumps(BIRTH)}}, {"id": "cus_me2", "metadata": {}}]}
CLEARED, DOWN = [], set()
def fake_find(secret, email):
    if email in DOWN: raise stripe_api.StripeError("unreachable")
    return CUSTOMERS.get(email, [])
def fake_update(secret, cid, fields):
    CLEARED.append((cid, fields))
    for c in sum(CUSTOMERS.values(), []):
        if c["id"] == cid: c["metadata"].update(fields)
stripe_api.find_customers = fake_find
stripe_api.update_customer_metadata = fake_update
billing.status = lambda secret, email, fresh=False: {**billing._empty(), "customer": "cus_me", "member": True,
                                                    "birth": BIRTH if CUSTOMERS.get(email, [{}])[0].get("metadata", {}).get("wyrd_birth") else None}

web = A.app.test_client()
SAME = {"Sec-Fetch-Site": "same-origin"}

# ---- the policy ----
r = web.get("/privacy"); t = r.get_data(as_text=True)
check("the policy is public", r.status_code == 200 and "<h1>Privacy</h1>" in t)
check("search engines may read it", "noindex" not in t)
check("it names the contact address and its date", config.PRIVACY_EMAIL in t and config.PRIVACY_UPDATED in t)
check("it says free charts aren't stored and cards are never seen", "isn't stored on our server" in t and "We never see your card" in t)
check("it names every service that handles data", all(s in t for s in ("Stripe", "Render", "Neon", "Google Fonts", "GitHub", "Substack")))
check("it lists every key the browser keeps", all(k in t for k in ("wyrdChart", "wyrdSaved", "wyrdLearn", "wyrdVid", "wyrdMusic")))
check("it offers to clear this browser", 'id="clearBrowser"' in t and "caches.delete" in t)
check("it points members to their data", 'href="/account/data"' in t)
check("it's in the sitemap", "/privacy</loc>" in web.get("/sitemap.xml").get_data(as_text=True))
for path in ("/", "/chart", "/today", "/mandala", "/contact", "/reports"):
    check(f"{path} links to it", 'href="/privacy"' in web.get(path).get_data(as_text=True))
check("the contact form says where messages go", "a copy is kept on the site" in web.get("/contact").get_data(as_text=True))

# ---- headers ----
h = web.get("/").headers
check("no sniffing, no framing by other sites", h.get("X-Content-Type-Options") == "nosniff" and h.get("X-Frame-Options") == "SAMEORIGIN")
check("other sites are told only the origin", h.get("Referrer-Policy") == "strict-origin-when-cross-origin")
check("no camera, microphone or location", "geolocation=()" in h.get("Permissions-Policy", ""))
h = web.get("/signin").headers
check("private pages still send no referrer at all", h.get("Referrer-Policy") == "no-referrer" and h.get("Cache-Control") == "no-store")

# ---- the service worker keeps private pages off the device ----
sw = open(os.path.join(A.HERE, "static", "sw.js"), encoding="utf-8").read()
check("the service worker never caches a no-store response", "no-store" in sw)
check("nor the members' rooms or shared readings", all(p in sw for p in ("hall", "path", "together", "gift", "r\\/")))

# ---- your data ----
r = web.get("/account/data")
check("signed out, your data asks you to sign in", r.status_code == 302 and "/signin" in r.headers["Location"])
check("and the copy too", web.get("/account/data.json").status_code == 302)

for who in (ME, OTHER):
    store.save_letter(who, "2026-10-19", "<p>letter</p>")
    store.add_kin(who, "Mum", BIRTH)
    store.add_message(who, "hello")
    cid = store.save_client(who, "Client", BIRTH, "c@example.com", "notes")
    store.add_reading(who, "Client", BIRTH, cid)
store.set_practice_name(ME, "My practice")

with web.session_transaction() as s: s["email"] = ME
t = web.get("/account/data").get_data(as_text=True)
check("the page lists what's kept", all(x in t for x in ("1 Body Weather letter", "1 chart for a loved one", "1 client", "1 message", "your practice name", "kept at Stripe")))
check("and warns that client links stop working", "stop working" in t)
check("the account page (for members, the Hall) links to it", 'href="/account/data"' in web.get("/account", follow_redirects=True).get_data(as_text=True))
r = web.get("/account/data.json"); d = json.loads(r.get_data(as_text=True))
check("the copy downloads as a file", "attachment" in r.headers.get("Content-Disposition", ""))
check("the copy holds everything kept", d["email"] == ME and len(d["letters"]) == 1 and d["kin"][0]["label"] == "Mum"
      and d["clients"][0]["notes"] == "notes" and d["messages"][0]["body"] == "hello" and d["practice"] == "My practice"
      and d["body_weather_chart"]["name"] == "Ada")

web.post("/account/forget", data={}, headers=SAME)
check("without ticking the box nothing is deleted", store.kin(ME) and not CLEARED)
web.post("/account/forget", data={"sure": "1"}, headers={"Sec-Fetch-Site": "cross-site"})
check("a form from another site deletes nothing", store.kin(ME) and not CLEARED)

DOWN.add(ME)
r = web.post("/account/forget", data={"sure": "1"}, headers=SAME)
check("when Stripe can't be reached, nothing is deleted and it says so", r.status_code == 502 and store.kin(ME))
DOWN.clear()

r = web.post("/account/forget", data={"sure": "1"}, headers=SAME); t = r.get_data(as_text=True)
check("deleting says so and offers to clear the browser", r.status_code == 200 and "Your data is deleted" in t and 'id="clearBrowser"' in t)
left = store.everything(ME)
check("every record under the email is gone", not any(left[k] for k in ("letters", "kin", "clients", "readings", "messages", "practice")))
check("the saved chart is cleared at Stripe, only where there was one", CLEARED == [("cus_me", {"wyrd_birth": ""})])
o = store.everything(OTHER)
check("someone else's records are untouched", all(len(o[k]) == 1 for k in ("letters", "kin", "clients", "readings", "messages")))
check("and you're signed out", web.get("/account/data").status_code == 302)

print("\nPRIVACY CHECK " + ("PASSED" if not bad else f"FAILED ({bad})"))
sys.exit(1 if bad else 0)
