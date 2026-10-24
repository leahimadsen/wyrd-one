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
check("it names every service that handles data", all(s in t for s in ("Stripe", "Render", "Neon", "GitHub", "Substack")))
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

# ---- links that carry private details are sealed, not just signed ----
import base64, glob, logging, io, zlib
from itsdangerous import URLSafeTimedSerializer
from wyrd import accounts, sukuyo_learn
from wyrd.privacy import NoEmails
def readable(token, *needles):
    """Whether any needle can be read back out of a token the way anyone could try: base64, then zlib."""
    for part in token.lstrip(".").split("."):
        try: raw = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
        except Exception: continue
        for blob in (raw, zlib.decompress(raw) if raw[:1] == b"x" else b""):
            if any(n.encode() in blob for n in needles): return True
    return False
old_gift = URLSafeTimedSerializer(config.SECRET_KEY, salt="wyrd-gift-reading").dumps(BIRTH)
check("an old signed gift link really could be read (what sealing fixes)", readable(old_gift, "Ada", "1990-05-01"))
gift = A.gift_signer().dumps(BIRTH)
check("a gift link's name and birth can't be read from it", gift.startswith("gAAAAA") and not readable(gift, "Ada", "1990-05-01", "London"))
check("a sealed gift link opens the reading", web.get("/gift/" + gift).status_code == 200)
check("a gift link already sent still opens", web.get("/gift/" + old_gift).status_code == 200)
check("a tampered gift link doesn't", web.get("/gift/" + gift[:-6] + ("AAAAAA" if not gift.endswith("AAAAAA") else "BBBBBB")).status_code == 404)
tog = A.together_signer().dumps({"kind": "together", "people": "2", "p1": "x", "p2": "y"})
check("a reading-together link is sealed too", tog.startswith("gAAAAA") and not readable(tog, "together"))
tok = accounts.make_token(config.SECRET_KEY, "ada@example.com", "/account")
check("a sign-in link doesn't show the email address", not readable(tok, "ada@example.com") and "ada" not in tok)
check("and still signs that person in", accounts.read_token(config.SECRET_KEY, tok) == ("ada@example.com", "/account"))
check("a sealed link of one kind can't be used as another", accounts.read_token(config.SECRET_KEY, gift) == (None, None))

# ---- no third parties see visitors ----
own = [p for p in glob.glob(os.path.join(A.HERE, "static", "**", "*"), recursive=True) if p.endswith((".css", ".html", ".js"))] \
      + glob.glob(os.path.join(A.HERE, "wyrd", "*.py")) + [os.path.join(A.HERE, "app.py")]
check("no page loads fonts from Google", not [p for p in own if "fonts.googleapis.com" in open(p, encoding="utf-8").read()])
chars = set(json.load(open(os.path.join(A.HERE, "static", "fonts", "jp-chars.json"), encoding="utf-8")))
used = set()
for p in glob.glob(os.path.join(A.HERE, "lib", "*.json")) + glob.glob(os.path.join(A.HERE, "wyrd", "*.py")):
    used |= {c for c in open(p, encoding="utf-8").read() if "\u3000" <= c <= "\u9fff"}
check("the site's own Japanese font has every kanji and kana it shows (else run tools/fonts.py)", used <= chars)
check("the font files are all there", all(os.path.exists(os.path.join(A.HERE, u.lstrip("/"))) for f in glob.glob(os.path.join(A.HERE, "static", "fonts", "*.css"))
      for u in __import__("re").findall(r"url\((/static/fonts/[^)]+)\)", open(f, encoding="utf-8").read())))

# ---- birth details stay out of addresses and logs ----
common = open(os.path.join(A.HERE, "static", "common.js"), encoding="utf-8").read()
check("share links carry the birth after the #, never sent to the server", "/chart#b=" in common and "/chart?b=" not in common)
import order_routes
check("so do the Hall's chart links", order_routes._chart_link(BIRTH).startswith("/chart#b="))
check("the Sukuyō form posts its dates", 'method="post" action="/learn/sukuyo/find"' in sukuyo_learn.find_form())
r = web.post("/learn/sukuyo/find", data={"a": "1985-03-14"})
check("and the answer comes back, kept out of caches and search", r.status_code == 200 and r.headers.get("Cache-Control") == "no-store")
buf = io.StringIO(); h = logging.StreamHandler(buf); h.addFilter(NoEmails()); lg = logging.getLogger("privacy-test"); lg.addHandler(h); lg.propagate = False
lg.error("stripe: no customer %s", "Some.One+tag@Example.co.uk")
check("email addresses are taken out of log lines", "Example" not in buf.getvalue() and "[email]" in buf.getvalue())
check("the app's own logger is filtered", any(isinstance(f, NoEmails) for hd in A.app.logger.handlers for f in hd.filters))

print("\nPRIVACY CHECK " + ("PASSED" if not bad else f"FAILED ({bad})"))
sys.exit(1 if bad else 0)
