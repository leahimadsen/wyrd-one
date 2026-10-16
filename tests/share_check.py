"""A reading made in the admin opens at a link anyone can use: the one "Copy link to this reading"
copies, the one you send, and its PDF.

    WYRD_DEV_NODE_EPH=1 python tests/share_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email."""
import os, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ.update(ADMIN_PASSWORD="pw-for-tests", SECRET_KEY="k" * 40, BASE_URL="https://example",
                  WYRD_DB_PATH=os.path.join(tempfile.mkdtemp(), "wyrd.db"))
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import app as A

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

SAME = {"Sec-Fetch-Site": "same-origin"}
BIRTH = {"name": "Freya", "full_name": "", "date": "1990-05-17", "time": "14:30", "place_id": "",
         "lat": "51.5", "lon": "-0.13", "tz": "Europe/London", "place_label": "London, England"}

admin = A.app.test_client()
with admin.session_transaction() as s:
    s["admin"] = True; s["admin_at"] = time.time()

# ---- generating a reading in the admin ----
r = admin.post("/admin/reading", data=BIRTH, headers=SAME)
link = r.headers.get("Location", "")
check("generating a reading opens it at its own link", r.status_code == 303 and link.startswith("https://example/gift/"))
path = link.removeprefix("https://example")

page = admin.get(path).get_data(as_text=True)
check("you see the reading there", "Freya" in page and "London, England" in page)
check("with a note, for you only, that this is the link to send", "This page's address is the link to send" in page)
check("and its Save as PDF and Copy link buttons", "window.print()" in page and "location.href" in page)

# ---- the person it's for, on another device ----
them = A.app.test_client()
r = them.get(path); seen = r.get_data(as_text=True)
check("the link opens for someone who isn't signed in", r.status_code == 200 and "Freya" in seen and "1990-05-17" in seen)
check("it reads like a paid reading: no admin note", "admin" not in seen.lower().split("<footer")[0].split("</header>")[0]
      and "link to send" not in seen and "no payment taken" not in seen)
check("and isn't called a gift", "A gift from" not in seen)
r = them.get(path + "?pdf=1")
check("its PDF link opens the reading with the save-as-PDF window", r.status_code == 200 and 'get("pdf") === "1"' in r.get_data(as_text=True))

# ---- what isn't allowed ----
check("a stranger can't generate one", them.post("/admin/reading", data=BIRTH, headers=SAME).status_code == 404)
check("a changed link opens nothing", them.get(path[:-3] + "xyz").status_code == 404)
r = admin.post("/admin/reading", data={**BIRTH, "date": "1990-02-31"}, headers=SAME)
check("bad details stay in the admin with the reason", r.status_code == 400 and "doesn&#x27;t exist" in r.get_data(as_text=True))

# ---- an old copied admin address ----
r = them.get("/admin/reading")
check("an old admin-address link explains itself instead of an error", r.status_code == 410 and "own link" in r.get_data(as_text=True))
check("and sends you back to the admin", admin.get("/admin/reading").status_code == 302)

# ---- gift links are as they were ----
r = admin.post("/admin/gift/reading", data=BIRTH, headers=SAME)
import re
g = re.search(r'href="https://example(/gift/[^"]+)"', r.get_data(as_text=True)).group(1)
check("a gift link still says it's a gift", "A gift from" in them.get(g).get_data(as_text=True))

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
