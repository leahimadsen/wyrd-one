"""The paid reading's drawings: the chart flat and as a torus, and the Harmonic Body, drawn in the page with the
console's own code from the chart the reading carries.

    WYRD_DEV_NODE_EPH=1 python tests/reading_figs_check.py      (no Skyfield needed)
"""
import json, os, re, sys, tempfile
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
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()

page = A.app.test_client().get("/sample").get_data(as_text=True)
ids = re.findall(r'<section class="rd-sec[^"]*" id="([^"]+)"', page)
check("the chart comes first, drawn, before the Seat", ids[:3] == ["s-story", "s-the-chart", "s-the-seat"])
check("flat and as a torus, each on its night plate", 'data-fig="wheel"' in page and 'data-fig="torus"' in page and page.count('class="rd-plate') >= 3)
check("the torus can be read in either zodiac and its layers switched", "data-tz-zodiac" in page and "data-tz-layers" in page and "data-tz-cap" in page)
body = page[page.index('id="s-the-body"'):page.index('id="s-the-body-s-old-map"')]
check("the Body section ends with the Harmonic Body", "The Harmonic Body" in body and 'data-fig="harmonic"' in body)
old = re.search(r'<div class="rd-num">([IVXL]+)</div>\s*<h2>The Body.s Old Map</h2>', page)
check("it points to the old map by its number", bool(old) and f"read in full in section {old.group(1)}." in body)

m = re.search(r'<script type="application/json" id="rd-chart">(.*?)</script>', page, re.S)
D = json.loads(m.group(1)) if m else {}
check("the reading carries its chart for the drawings", all(k in D for k in ("sid", "trop", "ascS", "ay", "natal", "dharma", "tropDes", "bodyMap")))
check("with the stations' weights for the glow", len(D.get("bodyMap", {}).get("weights", {})) == 7 and len(D["bodyMap"]["heavy"]) == 2)
check("and nothing in it can close the script early", "</" not in m.group(1) if m else False)

order = [page.index(f'/static/{f}') for f in ("viz.js", "body.js", "wheel.js", "torus.js", "reading-figs.js")]
check("the console's drawings load before the page draws with them", order == sorted(order))
check("with their styles", "/static/map.css" in page and "/static/body.css" in page)
check("the Harmonic Body's station styles come with it, kept to the figure", ".rd-hb .station .core{" in page and ".rd-hb .station .lead{" in page and "html,body{height:100%" not in page)
check("the PDF waits for the drawings to build", 'document.querySelector("[data-fig]") ? 3200 : 600' in page)
check("the controls stay off the printed page", ".rd-plate .hb-ctl" in page and ".rd-plate .wx-bar" in page)

figs, body_js = read("static", "reading-figs.js"), read("static", "body.js")
check("the torus builds at once, so it prints whole, then turns only in view", "T.start();" in figs and "IntersectionObserver" in figs)
check("the Harmonic Body takes the reading's own introduction", "function mount(host, chart, opts = {})" in body_js and "opts.intro != null" in body_js and "intro: \"\"" in figs)
check("a reading without the chart draws nothing", 'if (!el) return;' in figs)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
