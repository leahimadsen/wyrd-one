"""Draw the Wyrd deck's engraved plates and write them for the site.

    python3 scripts/deck_art/build.py                 every sign drawn here
    python3 scripts/deck_art/build.py gemini cancer   just these
    python3 scripts/deck_art/build.py --sheet DIR     also a contact sheet of each sign, for checking by eye

Each sign's nine cards are drawn in scripts/deck_art/<sign>.py (Aries and Taurus were engraved on
the design canvas and come from scripts/deck_plates.py), and the 24 trumps of the zodiac in
trumps_buddhist.py and trumps_nordic.py. A plate is written to
static/deck/plates/<card>.json as { label, svg }, with the suit's colours written onto every shape
and every id marked "@@" so static/deck.js can make it unique on the page."""
import importlib, json, os, re, sys
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import lib
from deck_plates import rules, resolve, prefix_ids

OUT = os.path.join(ROOT, "static", "deck", "plates")
SIGN_FILES = ["gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces", "trumps_buddhist", "trumps_nordic"]


def finish(plate):
    """A Plate, made into the markup the site keeps."""
    inner = plate.svg()
    root = ET.fromstring(f"<svg>{inner}</svg>")
    resolve(root, rules(lib.css(plate.fam)))
    out = "".join(ET.tostring(ch, encoding="unicode") for ch in root)
    out = re.sub(r"\s+", " ", out).replace("> <", "><").replace("ns0:", "")
    return prefix_ids(out)


def cards_of(name):
    mod = importlib.import_module(name)
    return mod.CARDS          # {card id: function returning a Plate}


def write(cid, plate):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{cid}.json"), "w", encoding="utf-8") as fh:
        json.dump({"label": plate.label, "svg": finish(plate)}, fh, ensure_ascii=False, separators=(",", ":"))


def sheet(cards, path, cols=3, scale=1.1):
    """A contact sheet of plates, as one HTML page and its screenshot."""
    cells = []
    for k, (cid, plate) in enumerate(cards):
        svg = finish(plate).replace("@@", f"s{k}-")
        cells.append(f'<figure><svg viewBox="0 0 380 360" width="{380 * scale:.0f}" height="{360 * scale:.0f}">{svg}</svg><figcaption><b>{cid}</b> {plate.label}</figcaption></figure>')
    html = ("<!doctype html><meta charset=utf-8><style>body{margin:0;background:#bbb;font:12px Georgia}main{display:grid;grid-template-columns:repeat(%d,%dpx);gap:10px;padding:10px}"
            "figure{margin:0;background:#fff;padding:4px}figcaption{width:%dpx}</style><main>%s</main>") % (cols, 380 * scale + 8, 380 * scale, "".join(cells))
    with open(path, "w", encoding="utf-8") as fh: fh.write(html)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": int(cols * (380 * scale + 18) + 10), "height": 800})
            pg.goto("file://" + path); pg.wait_for_timeout(300); pg.screenshot(path=path.replace(".html", ".png"), full_page=True); b.close()
    except Exception as e:
        print("no screenshot:", e, file=sys.stderr)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheet_dir = None
    if "--sheet" in args:
        i = args.index("--sheet"); sheet_dir = args[i + 1]; del args[i:i + 2]
    names = args or SIGN_FILES
    for n in names:
        cards = [(cid, fn()) for cid, fn in cards_of(n).items()]
        for cid, plate in cards: write(cid, plate)
        if sheet_dir: sheet(cards, os.path.join(sheet_dir, f"{n}.html"))
        print(f"{n}: {', '.join(cid for cid, _ in cards)}")
