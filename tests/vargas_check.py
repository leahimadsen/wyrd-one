"""The divisional charts: the Python (wyrd/vargas.py) and the browser (static/vargas.js) agree on
every division for random longitudes, the navamsa is the x9 the Dharma Design is cast from, and
a few hand-worked cases come out as Parashara gives them."""
import json, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd import vargas as V, engine as E

JS = r"""
const fs = require("fs"), vm = require("vm");
const norm = d => ((d % 360) + 360) % 360;
const ctx = { Math, Object, Set, console, window: {} }; ctx.window = ctx;
ctx.Wyrd = { helpers: { norm, GLYPH: {} } }; ctx.WyrdCommon = { esc: s => s };
vm.createContext(ctx); vm.runInContext(fs.readFileSync(process.argv[1] + "/static/vargas.js", "utf8"), ctx);
const L = JSON.parse(fs.readFileSync(0, "utf8"));
console.log(JSON.stringify(L.map(l => ctx.WyrdVargas.VARGAS.map(v => ctx.WyrdVargas.sign(l, v[0])))));
"""
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(9)
lons = [random.uniform(0, 360) for _ in range(3000)] + [k * 0.5 for k in range(720)]     # and every half-degree boundary
js = json.loads(subprocess.run(["node", "-e", JS, root], input=json.dumps(lons), capture_output=True, text=True, check=True).stdout)
bad = 0
for l, row in zip(lons, js):
    py = [V.sign(l, n) for n in V.NUMBERS]
    if py != row: bad += 1; print("MISMATCH", l, py, row) if bad < 5 else None
    if V.sign(l, 9) != int(E.norm(9 * l) // 30): bad += 1; print("D9 is not x9", l)
cases = [(15.5, 2, 3), (14.9, 2, 4), (45.0, 2, 4), (3.0, 30, 0), (33.0, 30, 1), (35.0, 9, 10), (40.0, 10, 1 + 8 + 3), (12.0, 3, 4), (95.0, 7, 3 + 6 + 1)]
for l, n, want in cases:
    got = V.sign(l, n) % 12
    if got != want % 12: bad += 1; print("CASE", l, n, "got", E.SIGNS[got], "want", E.SIGNS[want % 12])
print(f"{len(lons)} longitudes x {len(V.NUMBERS)} divisions: " + ("VARGAS CHECK PASSED" if not bad else f"VARGAS CHECK FAILED ({bad})"))
sys.exit(1 if bad else 0)
