"""The free introduction to the Wyrd Mandala at /learn/mandala, and the ways to it.

    WYRD_DEV_NODE_EPH=1 python tests/mandala_learn_check.py      (no Skyfield needed)
"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
import app as A

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

web = A.app.test_client()
r = web.get("/learn/mandala"); page = r.get_data(as_text=True)
check("the page opens", r.status_code == 200)
check("it teaches the instrument: rotors, rings, decks, voids, reading a station, things to try",
      all(f'id="{s}"' in page for s in ("rotors", "rings", "decks", "voids", "station", "try", "course")))
check("the rings are named from the centre out, with a key drawn as the wheel draws them",
      page.index("The field") < page.index("The sidereal signs") < page.index("The tropical signs") and 'class="ml-fig"' in page)
check("it sends the reader to the Mandala itself", page.count('href="/mandala"') >= 2)
T = json.load(open(os.path.join(A.HERE, "lib", "mandala_learn.json"), encoding="utf-8"))
check("the words are a draft for The Völva to edit", T["_note"].startswith("DRAFT for The Völva to edit"))
check("the course shows only its module titles and a line each", len(T["COURSE"]) >= 6 and all(len(x) == 2 and len(x[1]) < 120 for x in T["COURSE"]))
check("the course is marked as coming, and for the Order", "The course is coming" in page and 'href="/membership"' in page)
check("no open seat left: the void at station 90 is named Narakasura", "open seat" not in page and "never been named" not in page and "The void at station 90 is Narakasura" in page)
check("the voids are taught in depth: what an asura is, where they dwell, the spacing, the mansions, the names",
      all(k in page for k in ("Brihadaranyaka Upanishad 1.3.1", "patalas", "Sumeru", "fourth, the seventh and the ninth", "gandanta", "Devi Mahatmya", "Bhagavata Purana 10.59")))
check("the borrowed word is flagged: Grant's tunnels lend the image, not the lineage", "Nightside of Eden" in page and "claim no descent" in page)
check("a diagram of one sign's nine padas, and a table of all thirty-six by sign",
      'aria-labelledby="mlv"' in page and page.count('<tr><th scope="row">') == 12 and page.count('<td data-n="') == 36)
check("the table names station 90 Narakasura, in Dhanishta's second pada", '<td data-n="Ninth"><b>Narakasura</b><small>090 · Dhanishta 2</small></td>' in page)
check("the Learn page links to it", 'href="/learn/mandala"' in web.get("/learn").get_data(as_text=True))
check("the Mandala page links to it", 'href="/learn/mandala"' in open(os.path.join(A.HERE, "static", "mandala.html"), encoding="utf-8").read())
check("search engines are told of it", "/learn/mandala" in web.get("/sitemap.xml").get_data(as_text=True))

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
