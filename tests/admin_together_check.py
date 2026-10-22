"""A reading together, made in the admin: synastry for two to nine people, no checkout, at a link anyone can open.

    WYRD_DEV_NODE_EPH=1 python tests/admin_together_check.py      (no Skyfield needed)

Nothing here talks to Stripe or sends email."""
import os, re, sys, tempfile, time
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
PLACE = {"lat": "51.5", "lon": "-0.13", "tz": "Europe/London", "place_id": "", "place_label": "London, England"}
NAMES = ["Freya", "Odin", "Frigg", "Baldr", "Sif", "Tyr", "Idunn", "Bragi", "Hel"]

def form(n, **over):
    """n people, as the admin form posts them: p1_name, p1_date, ..."""
    d = {}
    for i in range(1, n + 1):
        d.update({f"p{i}_name": NAMES[i - 1], f"p{i}_full_name": "", f"p{i}_date": f"{1980 + i}-0{(i % 9) + 1}-1{i % 9}",
                  f"p{i}_time": f"{8 + i}:15", **{f"p{i}_{k}": v for k, v in PLACE.items()}})
    d.update(over)
    return d

admin = A.app.test_client()
with admin.session_transaction() as s:
    s["admin"] = True; s["admin_at"] = time.time()
them = A.app.test_client()

# ---- the form ----
r = admin.get("/admin/together")
check("the admin sees the form", r.status_code == 200 and "A reading together" in r.get_data(as_text=True) and 'action="/admin/together"' in r.get_data(as_text=True))
check("and it's linked from the admin page", "/admin/together" in admin.get("/admin").get_data(as_text=True))
check("a stranger can't see it", them.get("/admin/together").status_code == 404)

# ---- two people ----
r = admin.post("/admin/together", data=form(2), headers=SAME)
link = r.headers.get("Location", "")
check("two people open a reading at its own link", r.status_code == 303 and link.startswith("https://example/together/"))
path = link.removeprefix("https://example")
mine = admin.get(path).get_data(as_text=True)
check("you see both of them in the reading", "Freya" in mine and "Odin" in mine)
check("it is the whole reading together (the old match, the bodies, the numbers)",
      all(s in mine for s in ("The Old Match", "How Your Bodies Meet", "Your Numbers Together", "The Questions")))
check("you get a note that this address is the link to send", "link to send" in mine)

r = them.get(path); seen = r.get_data(as_text=True)
check("the link opens for someone who isn't signed in", r.status_code == 200 and "Freya" in seen and "Odin" in seen)
check("it reads like a paid reading: no admin note", "link to send" not in seen and "no payment taken" not in seen)
check("it isn't cached or indexed", r.headers.get("Cache-Control") == "no-store" and "noindex" in r.headers.get("X-Robots-Tag", ""))

# ---- an unknown birth time, and a name left blank ----
r = admin.post("/admin/together", data=form(2, p2_time="", p2_unknown="1", p2_name=""), headers=SAME)
check("an unknown birth time is allowed", r.status_code == 303)
page = them.get(r.headers["Location"].removeprefix("https://example")).get_data(as_text=True)
check("and a blank name becomes Person 2", "Person 2" in page)

# ---- nine people, the most ----
r = admin.post("/admin/together", data=form(9), headers=SAME)
loc = r.headers.get("Location", "")
check("nine people fit in one link", r.status_code == 303 and len(loc) < 4000)
page = them.get(loc.removeprefix("https://example")).get_data(as_text=True)
check("and all nine are in the reading", all(n in page for n in NAMES))

# ---- what isn't allowed ----
check("one person isn't a reading together", admin.post("/admin/together", data=form(1), headers=SAME).status_code == 400)
check("an empty form isn't either", admin.post("/admin/together", data={}, headers=SAME).status_code == 400)
r = admin.post("/admin/together", data=form(3, p2_date="1990-02-31"), headers=SAME)
check("bad details stay in the admin and name the person", r.status_code == 400 and "Odin" in r.get_data(as_text=True)
      and "doesn&#x27;t exist" in r.get_data(as_text=True))
check("a stranger can't generate one", them.post("/admin/together", data=form(2), headers=SAME).status_code == 404)
check("a form from another site is refused", admin.post("/admin/together", data=form(2), headers={"Sec-Fetch-Site": "cross-site"}).status_code == 404)
check("a changed link opens nothing", them.get(path[:-3] + "xyz").status_code == 404)
check("an invented link opens nothing", them.get("/together/nope").status_code == 404)

# ---- the two kinds of link stay apart ----
BIRTH = {"name": "Freya", "full_name": "", "date": "1990-05-17", "time": "14:30", "place_id": "", **PLACE}
g = re.search(r'href="https://example(/gift/[^"]+)"', admin.post("/admin/gift/reading", data=BIRTH, headers=SAME).get_data(as_text=True)).group(1)
check("a gift link can't open as a reading together", them.get(g.replace("/gift/", "/together/")).status_code == 404)
check("a reading-together link can't open as a gift", them.get(path.replace("/together/", "/gift/")).status_code == 404)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
