"""The Wyrd Mandala: its card glyphs draw in every browser, its cards name their decan, its rings carry the
console's colours, and the Asura voids and both decks' trumps are on the wheel.

    python tests/mandala_check.py
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok
read = lambda f: open(os.path.join(ROOT, "static", "mandala", f), encoding="utf-8").read()
glyphs, css, data, mand = read("wyrd-glyphs.js"), read("wyrd-mandala.css"), read("wyrd-data.js"), read("wyrd-mandala.js")

# A <use> copy is styled as a copy: since Chrome 144 (and in Firefox) a rule like ".wm .g-card" doesn't
# reach inside it, and the glyphs drew solid black. They carry their own styling instead.
used = set(c for m in re.findall(r'class="(g-[^"]*)"', glyphs) for c in m.split())
style = dict(re.findall(r'"(g-[a-z]+)": "([^"]+)"', glyphs))
check("every class the drawn glyphs use has its own styling", used and used <= set(style))
check("the card body is filled and outlined, so it never falls back to solid black", "fill:var(--wm-paper)" in style.get("g-card", "") and "stroke:currentColor" in style.get("g-card", ""))
check("the symbols are written with that styling on their shapes", "styled(g.svg)" in glyphs)
check("no stylesheet rule tries to reach inside the copies", not re.search(r"\.g-(card|frame|em|thin|dot|rom|num)\b", css))

# "ruled by" is the decan's ruler, so the card says which decan
check("each card names its decan beside its ruler", 'decan: third(mid)' in data and "decan: third(l)" in data and "${x.decan} decan" in mand)

# the palette: the console's twelve house colours round the wheel, Aries red to Pisces magenta
viz = open(os.path.join(ROOT, "static", "viz.js"), encoding="utf-8").read()
house = re.findall(r'hex:"(#[0-9a-f]{6})"', viz)[:12]
hue = re.findall(r'"(#[0-9a-f]{6})"', mand[mand.index("const HUE"):mand.index("];", mand.index("const HUE"))])
check("the wheel's twelve colours are the console's house colours, in order", len(house) == 12 and hue == house)
check("every ring's sectors carry their sign's colour", all(re.search(re.escape(cls) + r'[^\n]*tint\(', mand) for cls in ('class="z-sec', 'class="n-sec', 'class="p-sec', 'class="t-sec', 'class="tz-sec tz-dec', 'class="tz-sec ${s.index')))
check("the mansions, which cross the signs, take the colour where their middle stands", "tint(hueAt((k.start + k.end) / 2))" in mand)
check("the tropical rings take the tropical sign's colour, so the ayanamsa shows as a shift in colour", "tint(hueOf(Math.floor(k / 3)))" in mand and 'data-tsign="${s.index}"${tint(hueOf(s.index))}' in mand)
check("the fills are mixed from each sector's own colour", all(f".wm .{c} {{ fill: color-mix(in srgb, var(--h" in css for c in ("z-sec", "n-sec", "p-sec", "t-sec", "tz-sec", "tz-dec")))
check("the console's theme is deep night with gold for the chosen", '--wm-paper: #0b0722' in css and '--wm-rubric: #ffcf5a' in css)

# the Asura voids, the tunnels: drawn on the wheel now, not only in the record
mans = read("wyrd-mansions.js"); M = __import__("json").loads(mans[mans.index("{"):mans.rindex("}") + 1])
check("thirty-six voids in the data, every one named; station 90's is Narakasura", sum(1 for v in M["cards"]["voids"] if v) == 36 and "UNNAMED" not in M["cards"]["voids"] and M["cards"]["voids"][89] == "Narakasura")
check("the voids are the fourth, seventh and ninth pada of every sidereal sign", [i + 1 for i, v in enumerate(M["cards"]["voids"]) if v] == [9 * k + n for k in range(12) for n in (4, 7, 9)])
check("each void is a dark pada with a mouth ringed in mauve", '${voidOf(s) ? " p-void" : ""}' in mand and 'class="void-mouth"' in mand and ".wm .p-sec.p-void" in css)
check("no open seat left in the wheel", "open seat" not in mand and "UNNAMED" not in mand)
check("the key names them", "Asura void: the tunnels, thirty-six dark padas on a 3-2-4 spacing" in mand)
check("hovering a void names it", '" · Asura void: " + esc(voidOf(s))' in mand)

# the major arcana: the Buddhist trump on the sidereal signs, as the tropical ring carries the Nordic
check("the sidereal sign ring carries each sign's Buddhist trump", 'class="z-trump"' in mand and "dec[s.index * 3].buddhist.trump" in mand)
check("and the tropical ring still carries the Nordic", "dec[s.index * 3].nordic.trump" in mand)

# both decks as cards: the Nordic minors and every trump carry glyphs, and the Fool stands at the gate
check("the Nordic ring draws a card in each decan, in place of its name", 'card("N" + String(k + 1).padStart(2, "0")' in mand and 'class="nd-name"' not in mand)
check("the sidereal signs carry the Buddhist trump's card, the tropical signs the Nordic's", 'card("MB" + String(s.index + 1)' in mand and 'card("MN" + String(s.index + 1)' in mand)
check("the Fool's card stands at the gate", 'card("MB00"' in mand)
check("the record shows each deck's card and trump as glyphs", 'glyph(x.glyph, x.minor)}${glyph(x.major, x.trump)' in mand and 'glyph("MB00", c.gate.buddhist)' in mand)
check("the record's cards are small, with their size written on them, so no browser stretches them to the column",
      'class="c-glyph" width="${CW}" height="${CH}"' in mand and "const CW = 28" in mand and ".wm .c-glyph { display: block; flex: none; width: 28px; height: 42px;" in css)
check("each pair sits side by side, with its name and detail beside it", 'class="c-row"' in mand and ".wm .c-row { display: grid; grid-template-columns: auto minmax(0, 1fr)" in css and ".wm .c-pair { display: flex;" in css)
for page in ("mandala.html", "chart.html"):
    html = open(os.path.join(ROOT, "static", page), encoding="utf-8").read()
    check(f"{page} asks for this deploy's Mandala files by version, so an old stylesheet can't sit beside new scripts",
          all(re.search(rf'/static/mandala/{re.escape(f)}\?v=\d+"', html) for f in ("wyrd-mandala.css", "wyrd-mansions.js", "wyrd-data.js", "wyrd-glyphs.js", "wyrd-mandala.js")))
import shutil, subprocess, json as _json
if shutil.which("node"):
    js = """global.window = global; const fs = require("fs"), d = %r;
for (const f of ["wyrd-mansions.js", "wyrd-data.js", "wyrd-glyphs.js"]) eval(fs.readFileSync(d + f, "utf8"));
const G = window.WyrdGlyphs, p2 = n => String(n).padStart(2, "0"), has = c => c.filter(x => G.get(x)).length;
console.log(JSON.stringify({ N: has(Array.from({length:36}, (_, i) => "N" + p2(i + 1))), MB: has(Array.from({length:12}, (_, i) => "MB" + p2(i + 1))),
  MN: has(Array.from({length:12}, (_, i) => "MN" + p2(i + 1))), fool: !!G.get("MB00"),
  drawn: Array.from({length:12}, (_, i) => G.get("MB" + p2(i + 1)).svg + G.get("MN" + p2(i + 1)).svg).every(s => s.includes("g-em")),
  iv: G.get("MN01").svg.includes(">IV<"), ii: G.get("N01").svg.includes(">II<"), st: window.WYRD.stations[8].cards,
  ex: window.WYRD.TRUMP_EXALT, mx: Array.from({length:7}, (_, i) => G.get("MX" + p2(i + 1))).map(g => g ? [g.name, g.svg.includes("g-em"), (g.svg.match(/>([IVXL]+)</) || [])[1]] : null) }));""" % os.path.join(ROOT, "static", "mandala", "")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True); o = _json.loads(r.stdout or "{}")
    check("thirty-six Nordic minor cards, twelve trumps a deck, and the Fool, all registered", o.get("N") == 36 and o.get("MB") == 12 and o.get("MN") == 12 and o.get("fool"))
    check("every trump has its own emblem drawn", o.get("drawn") is True)
    check("the Nordic trumps carry Waite's numbers (the Emperor is IV), the minors their own (2 of Wands is II)", o.get("iv") and o.get("ii"))
    st = o.get("st", {})
    check("a station knows its cards' glyphs: station 9's Nordic card is Taurus's third decan, 7 of Shields", st.get("nordic", [{}])[0].get("glyph") == "N06" and st["nordic"][0]["minor"] == "7 of Shields" and st["buddhist"]["major"] == "MB01")
    # the seven planetary trumps, each deck on its own rotor: the Nordic at the Western exaltation on the tropical ring
    ex = {x["planet"]: x for x in o.get("ex", [])}
    WEST = {"Sun": 19, "Moon": 33, "Mercury": 165, "Venus": 357, "Mars": 298, "Jupiter": 105, "Saturn": 201}     # 19° Aries … 21° Libra
    JYOTISH = {"Sun": 10, "Moon": 33, "Mercury": 165, "Venus": 357, "Mars": 298, "Jupiter": 95, "Saturn": 200}   # Parashara
    GD = {"Sun": "The Sun", "Moon": "The High Priestess", "Mercury": "The Magician", "Venus": "The Empress", "Mars": "The Tower", "Jupiter": "Wheel of Fortune", "Saturn": "The World"}
    check("seven planetary trumps, the Golden Dawn's, one to each planet", {p: x["nordic"] for p, x in ex.items()} == GD)
    check("the Nordic deck's sit at the Western exaltation degrees (tropical)", {p: x["trop"] for p, x in ex.items()} == WEST)
    check("and the sidereal degrees are Parashara's, the same the record's exaltation rows use", {p: x["sid"] for p, x in ex.items()} == JYOTISH
          and "const EXALT = { Sun: 10, Moon: 33, Mars: 298, Mercury: 165, Jupiter: 95, Venus: 357, Saturn: 200 }" in data)
    mx = o.get("mx", [])
    check("each has its card drawn, with Waite's number (the Magician I … the World XXI)", len(mx) == 7 and all(m and m[1] for m in mx)
          and {m[0]: m[2] for m in mx if m} == {"The Sun": "XIX", "The High Priestess": "II", "The Magician": "I", "The Empress": "III", "The Tower": "XVI", "Wheel of Fortune": "X", "The World": "XXI"})
check("the planetary trumps stand outside the rim at their degree on the tropical ring, with a hairline in", 'card("MX" + String(i + 1).padStart(2, "0"), r + 38, a' in mand
      and "norm(x.trop - AY())" in mand and 'class="ex-tick"' in mand and ".wm .ex-tick" in css)
check("the rim's degree numbers make way for them, and so does the selected station's code", "if (ex.some(a =>" in mand and "steps aside from a planetary trump" in mand)
check("a station holding an exaltation shows its trump in the record", "exaltIn(s, ay.degrees)" in mand and "Exaltation · tropical ring" in mand)
check("the key explains them", "planetary trumps, each at its planet's exaltation" in mand)
if shutil.which("node"):
    js = """global.window = global; const fs = require("fs"), d = %r;
for (const f of ["wyrd-mansions.js", "wyrd-data.js"]) eval(fs.readFileSync(d + f, "utf8"));
const W = window.WYRD, ay = W.FRAME.ayanamsa.degrees, n = x => ((x %% 360) + 360) %% 360;
console.log(JSON.stringify(W.TRUMP_EXALT.map(x => [x.planet, W.stations.filter(s => n(x.trop - n(s.zodiacStart + ay)) < s.zodiacEnd - s.zodiacStart).map(s => s.id)])));""" % os.path.join(ROOT, "static", "mandala", "")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True); held = dict(_json.loads(r.stdout or "[]"))
    check("each exaltation falls in exactly one station (2026: the Sun's 19° Aries in station 107)", len(held) == 7 and all(len(v) == 1 for v in held.values()) and held.get("Sun") == [107])

# the record without its annotations: no status badges, no counts beside the sections
check("no status badges in the record", "badge(" not in mand and 'class="prov' not in mand and "how it is held" not in mand)
check("no counts beside the sections", "<small>${rows.length}</small>" not in mand)
check("the page no longer promises them", "how it is held" not in open(os.path.join(ROOT, "static", "mandala.html"), encoding="utf-8").read())

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
