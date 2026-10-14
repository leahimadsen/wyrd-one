"""A paid reading reaches its buyer: the page, the PDF, the birth it was cast for, and for a
1:1 consultation the reading first and the call after it.

    WYRD_DEV_NODE_EPH=1 python tests/delivery_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email: Stripe is pretended at the HTTP layer and the
mail is caught."""
import json, os, re, sys, tempfile, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import config
config.SECRET_KEY = "test-key"; config.STRIPE_SECRET = "sk_test_x"; config.BASE_URL = "https://example"
config.CONSULTATION_PAYMENT_LINK_IDS = frozenset({"plink_consult"}); config.CONSULTATION_PAYMENT_LINK_URL = ""
config.BOOKING_URL = "https://calendly.example/volva"
import app as A
from wyrd import mailer, stripe_api

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- a pretend Stripe and a caught outbox ----
SESS, MARKS = {}, []
def fake_call(secret, method, path, fields=None):
    sid = urllib.parse.unquote(path.split("/checkout/sessions/")[1]) if "/checkout/sessions/" in path else None
    if method == "GET" and sid: return json.loads(json.dumps(SESS[sid]))
    if method == "POST" and sid:
        new = {k[9:-1]: v for k, v in (fields or {}).items() if k.startswith("metadata[")}
        SESS[sid]["metadata"].update(new); MARKS.append((sid, new))
        return SESS[sid]
    raise AssertionError(f"unexpected Stripe call {method} {path}")
stripe_api._call = fake_call

MAIL, MAIL_WORKS = [], [True]
def fake_send(to, subject, html, text="", reply_to=None):
    MAIL.append({"to": to, "subject": subject, "html": html, "text": text})
    return MAIL_WORKS[0]
mailer.send = fake_send
mailer.ready = lambda: True
A.run_later = lambda fn: fn()                 # the send runs at once here, not in a thread

BIRTH = {"name": "Freya", "date": "1990-05-17", "time": "14:30", "place_id": "", "lat": "51.5", "lon": "-0.13",
         "tz": "Europe/London", "place_label": "London, England"}
def paid(sid, meta, link=None, email="buyer@example.com"):
    SESS[sid] = {"id": sid, "status": "complete", "mode": "payment", "payment_status": "paid",
                 "customer_details": {"email": email}, "metadata": dict(meta), **({"payment_link": link} if link else {})}

web = A.app.test_client()

# ---- a reading bought on the site ----
paid("cs_reading1", BIRTH)
r = web.get("/reading?session_id=cs_reading1"); page = r.get_data(as_text=True)
check("the paid reading opens straight after payment", r.status_code == 200 and "Freya" in page)
check("it carries the birth it was cast for", "1990-05-17" in page and "London, England" in page)
check("and its Save as PDF button", "window.print()" in page)
check("an ordinary reading has no booking box", 'class="next"' not in page and "{{NEXT}}" not in page)
check("one email goes to the address paid with", len(MAIL) == 1 and MAIL[0]["to"] == "buyer@example.com")
m = MAIL[0]
check("it links the reading page", "https://example/reading?session_id=cs_reading1" in m["html"] and "https://example/reading?session_id=cs_reading1" in m["text"])
check("and the PDF of it", "session_id=cs_reading1&amp;pdf=1" in m["html"] and "session_id=cs_reading1&pdf=1" in m["text"])
check("and the birth details", all(x in m["html"] and x in m["text"] for x in ("Freya", "1990-05-17", "14:30", "London, England")))
check("no booking link for a reading on its own", "calendly" not in m["html"] and "consultation" not in m["subject"].lower())
check("Stripe remembers that it went", MARKS[-1] == ("cs_reading1", {"wyrd_mailed": "1"}))
A._mail_tried.clear()
web.get("/reading?session_id=cs_reading1")
check("a reload never sends it twice", len(MAIL) == 1)

# ---- when the mail doesn't go, nothing is marked and it is tried again later ----
MAIL_WORKS[0] = False; paid("cs_reading2", BIRTH)
web.get("/reading?session_id=cs_reading2")
check("a failed send is not marked as sent", SESS["cs_reading2"]["metadata"].get("wyrd_mailed") is None)
web.get("/reading?session_id=cs_reading2")
check("a reload straight after doesn't hammer the mail", len(MAIL) == 2)
A._mail_tried.clear(); MAIL_WORKS[0] = True
web.get("/reading?session_id=cs_reading2")
check("a later visit sends it once mail works", len(MAIL) == 3 and SESS["cs_reading2"]["metadata"].get("wyrd_mailed") == "1")

# ---- a 1:1 consultation: the reading first, the call after it ----
paid("cs_consult", {}, link="plink_consult", email="client@example.com")
r = web.get("/consultation?session_id=cs_consult"); land = r.get_data(as_text=True)
check("the consultation page puts the reading first", r.status_code == 200
      and land.index("Your written reading comes first") < land.index("Then choose the time for your call"))
check("and offers no booking before the reading is made", "calendly" not in land)
check("the details link opens the birth form", "details=1" in land and web.get("/consultation?session_id=cs_consult&details=1").status_code == 200)
check("nothing is mailed before the birth details are given", not any(x["to"] == "client@example.com" for x in MAIL))

n = len(MAIL)
r = web.post("/api/consultation-reading", json={"session_id": "cs_consult", "name": "Odin", "date": "1985-02-03", "time": "06:10", "place_id": 1})
if r.status_code != 200:                     # the sample places index may not hold id 1: take any place it has
    p = A.PLACES.search("London", 1) or A.PLACES.search("a", 1)
    r = web.post("/api/consultation-reading", json={"session_id": "cs_consult", "name": "Odin", "date": "1985-02-03", "time": "06:10", "place_id": p[0]["id"]})
check("giving the birth details opens the reading", r.status_code == 200 and r.get_json()["url"] == "/reading?session_id=cs_consult")
check("and the reading goes to the client's inbox at once", len(MAIL) == n + 1 and MAIL[-1]["to"] == "client@example.com")
m = MAIL[-1]
check("the email gives the reading and its PDF first", m["html"].index("Open your reading") < m["html"].index("Download it as a PDF") < m["html"].index("calendly"))
check("then the booking link for the call", "https://calendly.example/volva" in m["html"] and "https://calendly.example/volva" in m["text"])
check("with the birth it was cast for", "Odin" in m["text"] and "1985-02-03" in m["text"] and "06:10" in m["text"])
check("its subject names the consultation", "consultation" in m["subject"].lower())

r = web.get("/consultation?session_id=cs_consult")
check("coming back to the consultation page opens the reading", r.status_code == 302 and r.headers["Location"].endswith("/reading?session_id=cs_consult"))
page = web.get("/reading?session_id=cs_consult").get_data(as_text=True)
check("the consultation's reading has the booking at its top", 'class="next"' in page and "https://calendly.example/volva" in page
      and page.index('class="next"') < page.index('class="rd-'))
check("after the reading's own tools", page.index("window.print()") < page.index('class="next"'))
check("and the reading isn't mailed a second time", len(MAIL) == n + 1)

# ---- a reading together goes out the same way, naming everyone in it ----
pack = lambda n, d: json.dumps({"n": n, "d": d, "t": "09:00", "la": 51.5, "lo": -0.13, "tz": "Europe/London", "pl": "London, England"})
paid("cs_together", {"kind": "together", "people": "2", "p1": pack("Freya", "1990-05-17"), "p2": pack("Odin", "1988-11-02")}, email="pair@example.com")
n = len(MAIL)
r = web.get("/reading?session_id=cs_together")
check("a reading together opens and is mailed", r.status_code == 200 and len(MAIL) == n + 1 and MAIL[-1]["to"] == "pair@example.com")
check("its email names both births", all(x in MAIL[-1]["text"] for x in ("Freya", "1990-05-17", "Odin", "1988-11-02")) and "together" in MAIL[-1]["subject"])

# ---- the page itself ----
html = open(os.path.join(A.HERE, "static", "reading.html"), encoding="utf-8").read()
check("the PDF link opens the save-as-PDF window", 'get("pdf") === "1"' in html and "window.print()" in html)
check("the booking box stays out of the PDF", ".tools,.preview,.next{display:none}" in html)
consult = open(os.path.join(A.HERE, "static", "consult.html"), encoding="utf-8").read()
check("the offer page says the reading comes first, then the call",
      "Your full written reading first" in consult and consult.index("comes to your inbox") < consult.index("choose the time for our call"))

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
