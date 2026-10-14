"""The Wyrd Mandala's card glyphs draw in every browser, and its cards name their decan.

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

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
