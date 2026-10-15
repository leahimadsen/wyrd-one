"""The sky behind Odin's Eye: real stars in their true places, seen as the sky is seen, and star maps
that say where each name comes from.

    python tests/sky_check.py
"""
import json, math, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()

data_js, sky, eye, page, sw = read("static", "sky-data.js"), read("static", "sky.js"), read("static", "eye.js"), read("static", "chart.html"), read("static", "sw.js")
D = json.loads(data_js[data_js.index("{"):data_js.rindex("}") + 1])

# ---- the data: real stars ----
mags = D["stars"][2::3]
check("about sixteen hundred stars, to magnitude 5", 1400 < len(mags) < 2000 and max(mags) <= 5.0)
KNOWN = {"Sirius": (101.29, -16.72), "Betelgeuse": (88.79, 7.41), "Rigel": (78.63, -8.20), "Vega": (279.23, 38.78),
         "Polaris": (37.95, 89.26), "Castor": (113.65, 31.89), "Aldebaran": (68.98, 16.51), "Deneb": (310.36, 45.28)}
check("the bright stars stand where the catalogues put them (J2000, within 0.1°)",
      all(abs(D["named"][n][0] - ra) < .1 and abs(D["named"][n][1] - dec) < .1 for n, (ra, dec) in KNOWN.items()))
check("the Milky Way's outline comes along", len(D["mw"]) > 40)
check("the data says where it comes from", "Hipparcos" in D["credit"] and "d3-celestial" in D["credit"] and "BSD" in D["credit"])
check("small enough to load with the page", os.path.getsize(os.path.join(ROOT, "static", "sky-data.js")) < 80_000)

# ---- the page loads it ----
check("the chart page loads the sky before the eye", page.index("/static/sky-data.js") < page.index("/static/sky.js") < page.index("/static/eye.js"))
check("the offline copy keeps the sky", '"/static/sky-data.js"' in sw and '"/static/sky.js"' in sw)

# ---- the eye uses it, and nothing made up ----
check("the made-up stars and corner constellations are gone", not any(k in eye for k in ("const CONST", "const BRIGHT", "const STARS", "of CONST", "of BRIGHT")))
check("the tree's seeded twigs and rocks are kept as they were", "for (let i = 0; i < 990; i++) rnd();" in eye)
check("the sky turns about the pole above Asgard", "WyrdSky.draw(ctx, POLES.above.at, skyAngle(time)" in eye)
check("nothing is written on the sky: no names, no tags", "fillText" not in sky and "label" not in sky.split("/* ---------------- drawing")[1])
check("a tap on a figure opens its record", 'choose("sky:" + f, false)' in eye and 'sel.startsWith("sky:")' in eye)
check("the record gives the stars and the source, and says what is composed",
      all(k in eye for k in ("<dt>The stars</dt>", "<dt>Its source</dt>", "keep their true places to one another", "composed for the drawing", "no source fixes the sky to the tree")))

# ---- the maps ----
figs = re.findall(r'\{ id: "(\w+)", kind: (NORSE|GREEK), name: "([^"]+)", gloss: "([^"]+)", tag: "([^"]+)", at: \[([\d.\-]+), ([\d.\-]+)\]', sky)
kinds = {f[0]: f[1] for f in figs}
check("twelve maps: five Norse, seven Greek", len(figs) == 12 and list(kinds.values()).count("NORSE") == 5)
check("each Norse name is tagged with how it is attested",
      {f[0]: f[4] for f in figs if f[1] == "NORSE"} == {"eyes": "Eddic", "wolf": "medieval Icelandic", "loki": "later Scandinavian", "distaff": "Swedish folk", "wagon": "Scandinavian folk"})
check("each Greek map says so, and where it is listed", all(f[4] == "Greek constellation" for f in figs if f[1] == "GREEK") and "Almagest" in sky)
check("star maps only: no knotwork left", not re.search(r"knot|plait|weave|woven|ribbon|strand|interlac", sky, re.I))
notes = dict(re.findall(r'id: "(\w+)"[^\n]*\n\s*stars: "[^"]*",\s*note: "([^"]+)"', sky))
check("Þjazi's eyes: Skáldskaparmál and Hárbarðsljóð, and the stars a modern reading",
      all(k in notes["eyes"] for k in ("Skáldskaparmál", "Hárbarðsljóð", "modern reading")))
check("the wolf's jaw: the 12th-century Icelandic glossary", "GKS 1812 4to" in notes["wolf"] and "12th-century" in notes["wolf"])
check("Lokabrenna: later tradition, not in the Eddas", "later tradition" in notes["loki"] and "not in the Eddas" in notes["loki"])
check("Frigg's distaff: a later Swedish folk name, beside the glossary's fishermen", "Swedish folk name" in notes["distaff"] and "fiskikarlar" in notes["distaff"])
ANCHOR = {"eyes": "Castor", "loki": "Sirius", "wolf": None, "distaff": "Alnilam", "wagon": "Megrez"}
check("each Norse map is drawn about its own star", all(abs(float(f[5]) - D["named"][ANCHOR[f[0]]][0]) < .1 and abs(float(f[6]) - D["named"][ANCHOR[f[0]]][1]) < .1
                                                       for f in figs if ANCHOR.get(f[0]) and ANCHOR[f[0]] in D["named"]))
check("every map has its constellation's IAU lines in the data", all(f"\"{iau}\"" in data_js for iau in re.findall(r'iau: "(\w+)"', sky)) and len(re.findall(r'iau: "(\w+)"', sky)) == 12)

# ---- the geometry, run as the browser runs it ----
if shutil.which("node"):
    check("sky.js parses", subprocess.run(["node", "--check", os.path.join(ROOT, "static", "sky.js")], capture_output=True).returncode == 0)
    js = """
global.window = {}; eval(require('fs').readFileSync(%r, 'utf8')); eval(require('fs').readFileSync(%r, 'utf8'));
const S = window.WyrdSky, R = 325, rad = Math.PI / 180;
const turn = ([x, y], th) => [x * Math.cos(th) - y * Math.sin(th), x * Math.sin(th) + y * Math.cos(th)];
const N = window.WYRD_SKY_DATA.named, th = -86 * rad;          /* Orion turned to stand below the pole */
const B = turn(S.at(...N.Betelgeuse), th), Rg = turn(S.at(...N.Rigel), th), Si = turn(S.at(...N.Sirius), th);
const figs = S.build(R), G = id => figs.find(g => g.f.id === id);
const boxes = figs.map(G => G.box), overlap = boxes.some((a, i) => boxes.some((b, j) => j > i && a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1));
const inside = boxes.every(b => b.x0 >= 0 && b.x1 <= 1000 && b.y0 >= 0 && b.y1 <= 1280);
const finite = figs.every(G => [...G.lines, ...G.marks].every(l => l.every(p => isFinite(p[0]) && isFinite(p[1]))) && G.stars.every(s => isFinite(s.x) && isFinite(s.y)));
const within = figs.every(G => [...G.lines, ...G.marks].every(l => l.every(p => p[0] >= G.box.x0 - 1 && p[0] <= G.box.x1 + 1 && p[1] >= G.box.y0 - 1 && p[1] <= G.box.y1 + 1)));
const lines = figs.map(G => G.lines.flat().length), starsIn = figs.map(G => G.stars.length);
/* every gold point of a Norse map stands on a catalogue star */
const onStars = figs.filter(G => G.f.kind === "norse").every(G => G.marks.flat().every(([x, y]) => G.stars.some(s => Math.hypot(s.x - x, s.y - y) < 1.5)));
const marked = figs.filter(G => G.marks.length).map(G => G.f.id);
const Bo = G("distaff").place(...N.Betelgeuse), Ro = G("distaff").place(...N.Rigel);
console.log(JSON.stringify({ B, Rg, Si, overlap, inside, finite, within, lines, starsIn, onStars, marked, Bo, Ro }));
""" % (os.path.join(ROOT, "static", "sky-data.js"), os.path.join(ROOT, "static", "sky.js"))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    out = json.loads(r.stdout or "{}") if r.returncode == 0 else {}
    if not out: print(r.stderr[:400])
    B, Rg, Si = out.get("B", [0, 0]), out.get("Rg", [0, 0]), out.get("Si", [0, 0])
    check("seen as the sky is seen: with Orion below the pole, Betelgeuse is up and to the left of Rigel", B[0] < Rg[0] and B[1] < Rg[1])
    check("and Sirius lies to the left of Orion (east), below it (south)", Si[0] < B[0] and Si[1] > B[1])
    check("every map builds, with every point finite", out.get("finite") is True)
    check("the maps are spread through the margins, no two in the same place", out.get("overlap") is False and out.get("inside") is True)
    check("each map's lines stay inside its own place", out.get("within") is True)
    check("every map draws its constellation's lines and shows its own real stars",
          len(out.get("lines", [])) == 12 and all(n >= 3 for n in out.get("lines", [])) and all(n >= 4 for n in out.get("starsIn", [])))
    check("each Norse map marks its named stars in gold, and every gold point is a real star",
          set(out.get("marked", [])) == {"eyes", "wolf", "loki", "distaff", "wagon"} and out.get("onStars") is True)
    Bo, Ro = out.get("Bo", [0, 0]), out.get("Ro", [0, 0])
    check("each map is north up with east to the left: in Frigg's distaff, Betelgeuse is up and left of Rigel", Bo[0] < Ro[0] and Bo[1] < Ro[1])

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
