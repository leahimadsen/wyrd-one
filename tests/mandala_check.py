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
check("thirty-six voids in the data, one of them unnamed", sum(1 for v in M["cards"]["voids"] if v) == 36 and M["cards"]["voids"].count("UNNAMED") == 1)
check("each void is a dark pada with a mouth ringed in mauve", '${voidOf(s) ? " p-void" : ""}' in mand and 'class="void-mouth"' in mand and ".wm .p-sec.p-void" in css)
check("the unnamed void reads as the open seat", '"the unnamed void, the open seat"' in mand)
check("the key names them", "Asura void: the tunnels, thirty-six dark padas on a 3-2-4 spacing" in mand)
check("hovering a void names it", '" · Asura void: " + esc(voidOf(s))' in mand)

# the major arcana: the Buddhist trump on the sidereal signs, as the tropical ring carries the Nordic
check("the sidereal sign ring carries each sign's Buddhist trump", 'class="z-trump"' in mand and "dec[s.index * 3].buddhist.trump" in mand)
check("and the tropical ring still carries the Nordic", "dec[s.index * 3].nordic.trump" in mand)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
