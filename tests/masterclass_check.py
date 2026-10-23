"""The free masterclass: the Substack sign-up at /masterclass, and the guide the welcome email links to.

    WYRD_DEV_NODE_EPH=1 python tests/masterclass_check.py      (no Skyfield needed)
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import app as A
from wyrd import masterclass as MC

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

web = A.app.test_client()
A.config.MASTERCLASS_PATH = ""
r = web.get("/masterclass"); land = r.get_data(as_text=True)
check("the sign-up page opens and is indexed", r.status_code == 200 and 'content="index, follow"' in land)
check("it signs people up to The Web of Wyrd on Substack", 'src="https://thewebofwyrd.substack.com/embed"' in land and "https://thewebofwyrd.substack.com/subscribe" in land)
check("a button subscribes on Substack, on the sign-up page",
      land.count('class="btn-buy mc-sub" href="https://thewebofwyrd.substack.com/subscribe"') == 1)
check("it lists what's inside", all(t in land for t in MC.contents()))
check("with no path set, it links straight to the guide", 'href="/masterclass/guide"' in land)
g = web.get("/masterclass/guide"); guide = g.get_data(as_text=True)
check("the guide opens at /masterclass/guide", g.status_code == 200)
check("the guide is kept out of search", "noindex" in g.headers.get("X-Robots-Tag", "") and 'content="noindex, nofollow"' in guide
      and "Disallow: /masterclass/" in web.get("/robots.txt").get_data(as_text=True))
check("the guide ends with the subscribe button", 'class="btn-buy mc-sub" href="https://thewebofwyrd.substack.com/subscribe"' in guide)
check("it saves as a PDF", "window.print()" in guide and "@media print" in open(os.path.join(A.HERE, "static", "plans.css"), encoding="utf-8").read())
check("it teaches every lesson, the worked stations and the worksheet",
      all(f'id="{i}"' in guide for i in ("before", "rotors", "inside-out", "voids", "worked", "mistakes", "yours", "close")) and guide.count('class="mc-worked"') == 2)
for W in MC.T["WORKED"]:
    check(f"station {W['station']:03d}'s cards are the wheel's", W["cards"] == MC.cards_at(W["station"]))
    words = " ".join(t for _, t in W["steps"])
    check(f"station {W['station']:03d}'s reading names those cards", all(c in words for c in W["cards"]["buddhist"] + W["cards"]["nordic"]))
check("the words are a draft for The Völva to edit", MC.T["_note"].startswith("DRAFT for The Völva to edit"))

A.config.MASTERCLASS_PATH = "lantern-7q"
land = web.get("/masterclass").get_data(as_text=True)
check("with a path set, the sign-up page no longer links to the guide", "/masterclass/lantern-7q" not in land and "/masterclass/guide" not in land)
check("the guide moves to the path, and the old address closes",
      web.get("/masterclass/lantern-7q").status_code == 200 and web.get("/masterclass/guide").status_code == 404)

check("search engines are told of the sign-up page", "/masterclass<" in web.get("/sitemap.xml").get_data(as_text=True))
check("Learn and the Mandala lesson link to it",
      'href="/masterclass"' in web.get("/learn").get_data(as_text=True) and 'href="/masterclass"' in web.get("/learn/mandala").get_data(as_text=True))
check("the Mandala page links to it", 'href="/masterclass"' in open(os.path.join(A.HERE, "static", "mandala.html"), encoding="utf-8").read())

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
