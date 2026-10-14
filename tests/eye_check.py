"""Odin's Eye at the top of the chart page, the torus inside its shell, and the Harmonic Body
on the engraving.

    python tests/eye_check.py
"""
import json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import medical as M

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()

page, js, sw = read("static", "chart.html"), read("static", "chart.js"), read("static", "sw.js")
eye, body, viz = read("static", "eye.js"), read("static", "body.js"), read("static", "viz.js")

# the hub: the eye first, the torus when its shell is opened
check("the chart page loads eye.js and eye.css", 'src="/static/eye.js"' in page and 'href="/static/eye.css"' in page)
check("eye.js loads after viz.js and torus.js", page.index("/static/viz.js") < page.index("/static/eye.js") and page.index("/static/torus.js") < page.index("/static/eye.js"))
check("the hub window holds the eye, with the torus hidden behind it", 'id="eyeHost"' in page and re.search(r'class="map-core tz-core" hidden', page) is not None)
check("a switch between the eye and the opened shell", 'data-hub-view="eye"' in page and 'data-hub-view="shell"' in page)
check("the page mounts the eye and opens the torus only when asked", "WyrdEye.mount" in js and "if (shell && !TZ) mountTorus();" in js)
check("leaving the map stops both, coming back starts the one showing", "stopHub()" in js and "startHub()" in js)
check("the offline copy knows the eye", '"/static/eye.js"' in sw and '"/static/eye.css"' in sw)

# the eye itself
check("the seven Ladder worlds take their soul parts from the Harmonic Body's stations",
      "w.soul = s.operator" in eye and not re.search(r'soul:"(Önd|Hugr|Minni|Hamr|Óðr|Hamingja|Fylgja)"', eye))
check("Jötunheim keeps Sjálfr and Niflheim takes Lík", re.search(r'id:"jotunheim"[^}]*soul:"Sjálfr"', eye) and re.search(r'id:"niflheim"[^}]*soul:"Lík"', eye))
check("the ring's four quarters: Niflheim north, Jötunheim east, Muspelheim south, Vanaheim west",
      all(re.search(rf'id:"{w}"[^}}]*az:{d}\b', eye) for w, d in (("niflheim", 225), ("jotunheim", 315), ("muspelheim", 45), ("vanaheim", 135))))
check("the shell turns freely: the houses are not set by the compass", "let rot = 0" in eye and "+ rot" in eye and "ASC + 315" not in eye)
check("the runes and house colours come from the console's own table", "HOUSES.flatMap" in eye and "HOUSES.map(h => h.hex)" in eye)
check("only the living wood: no circuit, node graph or split drawings", not any(w in eye for w in ("circuit", "NODE_COL", '"split"', "octo(")))
check("no Veð anywhere in the eye", "Veð" not in eye and "ved" not in eye.lower().replace("moved", "").replace("removed", "").replace("curved", "").replace("saved", ""))
check("the eye's parts link to their rooms", all(h in eye for h in ('"#design/harmonic"', '"#mandala"', '"#chart"', "data-eye-open")))
check("the eye keeps to its own click attributes", not re.search(r"\sdata-(graha|house|hue|jump|bench|tr|f)(?=[=\s>])", eye))

# the Harmonic Body on the engraving
check("the Harmonic Body draws the engraving, not the Vitruvian figure", "anatomy-light.png" in body and 'class="fig"' not in body and "fig-muscle" not in body)
F = json.load(open(os.path.join(ROOT, "lib", "medical.json"), encoding="utf-8"))["FIGURE"]
at = dict(re.findall(r"(\w+): \[(\d+, \d+)\]", body[body.index("at: {"):body.index("feet:")]))
ids = ["asgard", "alfheim", "vanaheim", "midgard", "muspelheim", "nidavellir", "hel"]
check("its stations stand where the engraving marks them (lib/medical.json FIGURE.at)",
      all(at.get(i) == f"{F['at'][k][0]}, {F['at'][k][1]}" for i, k in zip(ids, M.KEYS)))
check("the same engraving, the same size", f"w: {F['w']}, h: {F['h']}" in body and F["src"].replace(".png", "-light.png") in body)
check("every use of the stations in the Harmonic Body goes through the moved ones", body.count("STATIONS") == 2)
check("the turning, the scan, the sound and the design overlays are all still there",
      all(k in body for k in ("bindDrag", "stepScan", "Sound.chord", "centresSVG", "torusSVG", "zodiacSVG", "data-hb-view")))

# the body map's weights travel to the Harmonic Body; the free card points there instead of drawing a second figure
import random
from wyrd import engine as E
for seed in (4, 11, 27):
    random.seed(seed)
    sid = {b: random.uniform(0, 360) for b in M.NINE[:7]}
    sid["Rahu"] = random.uniform(0, 360); sid["Ketu"] = E.norm(sid["Rahu"] + 180)
    C = {"sid": sid, "trop": {b: E.norm(l + 24.1) for b, l in sid.items()}, "ascS": random.uniform(0, 360), "ay": 24.1, "jd": 2450000.0}
    fr = M.free(C); w = fr.get("weights") or {}
    check(f"chart {seed}: the free body map carries a weight for every station, the heaviest at 1",
          set(w) == set(M.KEYS) and max(w.values()) == 1 and all(0 <= v <= 1 for v in w.values()))
    check(f"chart {seed}: and names its two heaviest", len(fr.get("heavy", [])) == 2 and all(w[k] >= sorted(w.values())[-2] for k in fr["heavy"]))
check("the Harmonic Body draws the weights as a glow round each station", "class=\"weight" in body and "BM.weights" in body)
check("the free body map card links to the Harmonic Body and no longer draws its own figure",
      '<p class="bm-free"' in js and "#design/harmonic" in js and "${BM.figure}" not in js)

# the Veð is gone from the console
check("no Veð left in viz.js", not any(k in viz for k in ("VED_WORLD", "vedOf", "Veð", "onDoorpost")))

if shutil.which("node"):
    for f in ("eye.js", "body.js", "viz.js", "chart.js"):
        check(f"{f} parses", subprocess.run(["node", "--check", os.path.join(ROOT, "static", f)], capture_output=True).returncode == 0)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
