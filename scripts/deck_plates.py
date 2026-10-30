"""Turn The Völva's engraved deck cards into plates the site can draw.

Each card is drawn on the design canvas as a 1080 × 1920 story card. Its
engraving is one <svg viewBox="0 0 380 360"> whose look comes from the card's
style sheet (.ink, .tint, .wash ...). This script lifts that engraving out and
makes it stand alone:

  * every class rule is written onto the elements as attributes, applying the
    rules the way a browser does (later and more specific rules win, and an
    author rule beats a presentation attribute), so no style sheet is needed;
  * every id gets the placeholder prefix "@@", which static/deck.js swaps for a
    prefix of its own each time it draws a card, so two cards on one page never
    share an id;
  * the card's own words are kept too (its numeral, title and fact columns), so
    the site prints exactly what was approved on the canvas.

Usage:
    python3 scripts/deck_plates.py <folder of .dc.html cards>

Each plate is written to static/deck/plates/<card>.json as { label, words, svg }, beside the plates
drawn by scripts/deck_art/build.py for the other ten signs.

File names say which card each is: Aries-B2 is the Buddhist card of Aries's
first decan, Taurus-N7 the Nordic card of Taurus's third, Aries-V04 the Asura
void at station IV."""
import html, json, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PROPS = ["fill", "fill-opacity", "stroke", "stroke-width", "stroke-opacity", "stroke-linejoin", "stroke-linecap",
         "stroke-dasharray", "opacity", "font-family", "font-size", "font-style", "letter-spacing"]


def card_id(stem):
    m = re.fullmatch(r"(\w+)-([BN])(\d+)", stem)
    if m:
        s, kind, n = SIGNS.index(m[1]), m[2].lower(), int(m[3])
        decan = 3 * s + (n - 2) % 3              # each sign's three minors run 2-4, 5-7 or 8-10
        return f"{kind}{decan:02d}"
    m = re.fullmatch(r"\w+-V(\d+)", stem)
    if m: return f"v{int(m[1]):03d}"
    return None


def rules(css):
    """[(classes, specificity, order, {prop: value})] for every 'svg .a.b{...}' rule."""
    out = []
    for i, m in enumerate(re.finditer(r"svg((?:\s*\.[\w-]+)+)\s*\{([^}]*)\}", css)):
        cls = re.findall(r"\.([\w-]+)", m[1])
        decl = {k.strip(): v.strip() for k, v in (d.split(":", 1) for d in m[2].split(";") if ":" in d)}
        out.append((set(cls), len(cls), i, decl))
    return out


def resolve(el, R):
    cls = set((el.get("class") or "").split())
    if cls:
        hits = sorted((r for r in R if r[0] <= cls), key=lambda r: (r[1], r[2]))
        for _, _, _, decl in hits:
            for k, v in decl.items():
                if k in PROPS: el.set(k, v)
        del el.attrib["class"]
    style = el.get("style")
    if style:                                     # an inline style beats everything
        for d in style.split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                if k.strip() in PROPS: el.set(k.strip(), v.strip())
        del el.attrib["style"]
    for c in el: resolve(c, R)


def prefix_ids(s):
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    for i in sorted(ids, key=len, reverse=True):
        s = s.replace(f'id="{i}"', f'id="@@{i}"').replace(f"url(#{i})", f"url(#@@{i})").replace(f'href="#{i}"', f'href="#@@{i}"')
    return s


def text_of(frag):
    return html.unescape(re.sub(r"<[^>]+>", "", frag)).strip()


def words(src):
    """The card's own words, in the order they're set: numeral, title block and the three fact columns."""
    body = src[src.find('<div class="card"'):]
    body = re.sub(r"<svg.*?</svg>", "", body, flags=re.S)
    lines = []
    for m in re.finditer(r'<div style="([^"]*)">((?:(?!<div).)*?)</div>', body, flags=re.S):
        t = text_of(m[2])
        if not t: continue
        st = m[1]
        size = float(re.search(r"font-size: ([\d.]+)px", st)[1]) if "font-size" in st else None
        lines.append({"t": t, "size": size, "italic": "italic" in st, "sc": "Fell English SC" in st,
                      "black": "Unifraktur" in st, "color": (re.search(r"color: (#[0-9a-f]{6})", st) or [None, None])[1]})
    return lines


def main(folder):
    cards = {}
    for f in sorted(Path(folder).glob("*.dc.html")):
        cid = card_id(f.name.split(".")[0])
        if not cid: continue
        src = f.read_text(encoding="utf-8")
        css = re.search(r"<style>(.*?)</style>", src, re.S)[1]
        m = re.search(r'<svg viewBox="0 0 380 360"[^>]*aria-label="([^"]*)"[^>]*>.*?</svg>\s*</div>', src, re.S)
        label = html.unescape(m[1])
        svg = re.search(r'<svg viewBox="0 0 380 360".*?</svg>(?=\s*</div>)', src, re.S)[0]
        root = ET.fromstring(svg.replace("&", "&amp;").replace("&amp;amp;", "&amp;"))
        resolve(root, rules(css))
        inner = "".join(ET.tostring(c, encoding="unicode") for c in root)
        inner = re.sub(r"\s+", " ", inner).replace("> <", "><").replace("ns0:", "")
        inner = prefix_ids(inner)
        ws = words(src)
        cards[cid] = {"label": label, "svg": inner, "words": ws, "source": f.name}
    order = sorted(cards)
    out = Path(__file__).resolve().parent.parent / "static" / "deck" / "plates"
    out.mkdir(parents=True, exist_ok=True)
    for cid in order:
        c = cards[cid]
        (out / f"{cid}.json").write_text(json.dumps({"label": c["label"], "words": c["words"], "svg": c["svg"]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(cards)} plates: {', '.join(order)}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
