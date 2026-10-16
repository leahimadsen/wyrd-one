"""The rune wheel on the Runes page: the twenty-four runes in their ring, two to each house from the rising
sign, oriented like every wheel in the console, with the chart's activated runes lit on it.

    python tests/runes_wheel_check.py
"""
import json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()
runes, css = read("static", "runes.js"), read("static", "design.css")

check("the wheel stands on the Runes page, after the opening words and before the runes' readings", "${wheel(C, L)}\n    ${L.map(card).join(\"\")}" in runes)
check("oriented like every wheel in the console: house 1 at one o'clock, clockwise", "HOUSE_ONE_ANGLE" in runes and "ONE + norm(norm(l) - cusp)" in runes)
check("every rune card can be reached from the wheel", 'id="rn-${r.name}"' in runes and 'getElementById("rn-" + g.dataset.rune)' in runes)
check("lit runes take their house's colour, the strongest three their rank", ".rw-rune.lit .rw-cell" in css and "rw-rank" in runes and "L.slice(0, 3)" in runes)

if shutil.which("node"):
    js = r"""
global.window = global; global.matchMedia = () => ({ matches: false, addEventListener(){} }); global.addEventListener = () => {};
global.document = { addEventListener(){}, getElementById: () => null, querySelector: () => null, querySelectorAll: () => [], hidden: false, documentElement: { style: {} } };
global.IntersectionObserver = class { observe(){} }; global.requestAnimationFrame = () => 0; global.localStorage = { getItem: () => null, setItem(){} };
const fs = require("fs"); eval(fs.readFileSync(%r, "utf8") + "\nwindow.Wyrd = Wyrd;"); global.WyrdCommon = { esc: s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])) };
eval(fs.readFileSync(%r, "utf8"));
const R = window.WyrdRunes;
/* a chart with the Ascendant at 10° sidereal Leo: house 1 is Leo, so Fehu is 0-15° Leo */
const C = { ascS: 130, sid: { Sun: 125, Moon: 140, Mercury: 160, Venus: 300, Mars: 10, Jupiter: 45, Saturn: 250, Rahu: 200, Ketu: 20, Uranus: 260, Neptune: 265, Pluto: 210 }, karaka: { Atmakaraka: "Sun" } };
const L = R.lit(C), svg = R.wheel(C, L);
const lit = [...svg.matchAll(/class="rw-rune lit[^"]*" data-rune="(\w+)"/g)].map(m => m[1]);
console.log(JSON.stringify({ L: L.map(r => r.name), lit, cells: (svg.match(/class="rw-cell"/g) || []).length, houses: (svg.match(/class="rw-house"/g) || []).length,
  ranks: (svg.match(/class="rw-rank-n">\d/g) || []).length, planets: (svg.match(/class="rw-pl"/g) || []).length, asc: svg.includes("rw-asc"),
  fehu: R.runeAt(C, 132).name, othala: R.runeAt(C, 115).name,
  unknown: R.wheel({ ...C, unknownTime: true }, R.lit({ ...C, unknownTime: true })).includes("rw-asc") }));
""" % (os.path.join(ROOT, "static", "viz.js"), os.path.join(ROOT, "static", "runes.js"))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    o = json.loads(r.stdout or "{}") if r.returncode == 0 else {}
    if not o: print(r.stderr[:600])
    check("twenty-four rune cells in twelve house cells", o.get("cells") == 24 and o.get("houses") == 12)
    check("the wheel lights exactly the runes the page reads", sorted(o.get("lit", [])) == sorted(o.get("L", [])) and len(o.get("lit", [])) > 0)
    check("the three strongest carry their rank", o.get("ranks") == 3)
    check("every planet stands on it, and the Ascendant line when the time is known", o.get("planets") == 12 and o.get("asc") is True and o.get("unknown") is False)
    check("counted from the rising sign: Fehu opens house 1, Othala closes house 12", o.get("fehu") == "Fehu" and o.get("othala") == "Othala")

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
