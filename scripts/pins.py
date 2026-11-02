"""Pinterest pins for the 27 nakshatra pages, and the file Pinterest takes to post them all at once.

Each pin is a 1000 x 1500 plate in the site's manuscript look (her paper, knot corners, blackletter, Fell type),
carrying only what the mansion's page already says: its place among the 27, its gist, deity, ruling planet,
symbol and question. The images are written to static/pins/<mansion>.jpg, so Pinterest can fetch them from the
live site once they are merged.

    WYRD_DEV_NODE_EPH=1 python3 scripts/pins.py [where to write pinterest.csv]

The CSV follows Pinterest's bulk upload (Title, Media URL, Pinterest board, Thumbnail, Description, Link,
Publish date, Keywords). The board must exist on the account first, with exactly the name in BOARD."""
import csv, html, os, sys, tempfile, threading
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ.setdefault("WYRD_DB_PATH", os.path.join(tempfile.mkdtemp(), "wyrd.db"))
from wyrd.pages import C, NAKS, ORD27

SITE = "https://wyrdconsole.com"
BOARD = "The 27 Nakshatras"
OUT = os.path.join(ROOT, "static", "pins")
e = html.escape

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@import url('/static/fonts/wyrd90.css');
html,body{{margin:0;width:1000px;height:1500px;overflow:hidden}}
body{{background:#eee8db url(/static/look/paper.jpg) repeat;color:#1d1712;font-family:'IM Fell English',Georgia,serif;position:relative}}
.bar{{position:absolute;left:0;right:0;top:0;height:12px;background:linear-gradient(90deg,#e0201b,#ff7a00,#ffd400,#3fc12a,#13b8c9,#2a55e0,#6a35e0,#c22fd0)}}
.frame{{position:absolute;inset:52px 46px 262px;border:4px double #1d1712;box-shadow:8px 8px 0 rgba(29,23,18,.16);
        display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 64px 48px;box-sizing:border-box}}
.kt{{position:absolute;top:-6px;right:-6px;width:260px;opacity:.9}}
.kb{{position:absolute;bottom:-6px;left:-6px;width:260px;opacity:.9}}
.ord{{font-family:'IM Fell English SC',serif;color:#4b1d9e;font-size:34px;letter-spacing:.06em;margin:0}}
h1{{font-family:'UnifrakturMaguntia',serif;font-weight:400;font-size:{size}px;line-height:1.02;margin:26px 0 6px}}
.nak{{font-family:'IM Fell English SC',serif;font-size:44px;letter-spacing:.32em;margin:0 0 34px;padding-left:.32em}}
.gist{{font-style:italic;font-size:41px;line-height:1.32;margin:0 0 34px;max-width:780px}}
.rule{{width:220px;height:0;border-top:3px double #1d1712;margin:0 0 34px}}
dl{{display:grid;grid-template-columns:auto auto;gap:12px 26px;font-size:34px;margin:0 0 36px;text-align:left}}
dt{{font-family:'IM Fell English SC',serif;color:#4b1d9e}} dd{{margin:0}}
.ask{{font-style:italic;font-size:35px;line-height:1.36;color:#4b1d9e;max-width:780px;margin:0}}
.go{{position:absolute;left:46px;right:46px;bottom:52px;background:#4b1d9e;color:#fff;border:6px outset #b39cf5;
     font-family:'Space Mono',monospace;text-align:center;padding:30px 20px 32px}}
.go b{{display:block;font-weight:400;font-size:40px;letter-spacing:.02em}}
.go span{{display:block;font-size:30px;margin-top:10px;opacity:.92}}
</style></head><body><div class="bar"></div>
<div class="frame"><img class="kt" src="/static/look/knot-tr.png" alt=""><img class="kb" src="/static/look/knot-bl.png" alt="">
<p class="ord">The {ord} lunar mansion</p>
<h1>{name}</h1><p class="nak">Nakshatra</p>
<p class="gist">{gist}</p><div class="rule"></div>
<dl><dt>Deity</dt><dd>{deity}</dd><dt>Ruled by</dt><dd>{ruler}</dd><dt>Symbol</dt><dd>{symbol}</dd></dl>
<p class="ask">{ask}</p></div>
<div class="go"><b>What is your nakshatra?</b><span>Find it free at wyrdconsole.com</span></div>
</body></html>"""


def rows():
    for s, i in NAKS:
        n, g = C["NAKSHATRA"][i], C["ENGINE"][i]
        yield s, i, n, g


def plate(n, i, g):
    name = n[0]
    size = 168 if len(name) <= 9 else 136 if len(name) <= 13 else 112
    return PAGE.format(size=size, ord=ORD27[i], name=e(name), gist=e(n[6]), deity=e(n[2]), ruler=e(n[1]), symbol=e(n[3]), ask=e(g[10]))


def description(n, g):
    d = (f"{n[0]} nakshatra in Vedic astrology: {n[6]} Deity: {n[2]}. Ruled by {n[1]}. Symbol: {n[3]}. "
         f"Its question: {g[10]} Read {n[0]} in full, then find your own nakshatra free at The Wyrd Console.")
    return d[:500]


def main():
    import app as A
    from werkzeug.serving import make_server
    import logging; logging.getLogger("werkzeug").setLevel(logging.ERROR)
    tmp = tempfile.mkdtemp()
    A.app.add_url_rule("/_pin/<s>", "pin_preview", lambda s: open(os.path.join(tmp, s + ".html"), encoding="utf-8").read())
    srv = make_server("127.0.0.1", 8797, A.app, threaded=True); threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.makedirs(OUT, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1000, "height": 1500})
        for s, i, n, g in rows():
            open(os.path.join(tmp, s + ".html"), "w", encoding="utf-8").write(plate(n, i, g))
            pg.goto(f"http://127.0.0.1:8797/_pin/{s}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
            over = pg.evaluate("""() => { const f = document.querySelector('.frame'), a = document.querySelector('.ask'), go = document.querySelector('.go');
                const o = document.querySelector('.ord'); return a.getBoundingClientRect().bottom > f.getBoundingClientRect().bottom - 20 || o.getBoundingClientRect().top < f.getBoundingClientRect().top + 20 || o.getClientRects().length > 1 || o.offsetHeight > 60; }""")
            if over: print("  too tight:", s)
            pg.screenshot(path=os.path.join(OUT, s + ".jpg"), type="jpeg", quality=86)
        b.close()
    srv.shutdown()
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tmp, "pinterest.csv")
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
        for s, i, n, g in rows():
            w.writerow([f"{n[0]} Nakshatra: Meaning, Deity and Ruler"[:100], f"{SITE}/static/pins/{s}.jpg", BOARD, "",
                        description(n, g), f"{SITE}/learn/nakshatras/{s}?utm_source=pinterest&utm_medium=social", "",
                        f"{n[0].lower()} nakshatra, nakshatra meaning, vedic astrology, jyotish, lunar mansion, birth star, {n[2].lower()}"])
    print("pins:", OUT, "\ncsv:", dest)


if __name__ == "__main__":
    main()
