"""The Body's Old Map: medical astrology in the reading and the body map on the free chart.

    python tests/medical_check.py

Pretend charts, so no ephemeris; needs node for the free chart's copy of the tables."""
import json, os, random, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import engine as E, medical as M

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

T = M.T
check("a body part for every sign", set(T["SIGN"]) == set(E.SIGNS))
check("the zodiac runs head to feet", T["SIGN"]["Aries"]["part"] == "the head" and T["SIGN"]["Pisces"]["part"] == "the feet")
check("a body part for every mansion", len(T["NAK"]) == 27 and T["NAK"][0] == "the knees" and T["NAK"][18] == "the feet")
check("every planet has its organs, dosha lean and three ways to read it",
      set(T["PLANET"]) == set(M.NINE) and all({"rules", "short", "dosha", "light", "strain", "plain"} <= set(v) and abs(sum(v["dosha"].values()) - 1) < 0.02 for v in T["PLANET"].values()))
check("every planet has its station on the ladder", set(T["STATION"]) == set(M.NINE))
check("seven stations, crown to root, as on the ladder", M.KEYS == ["crown", "brow", "throat", "heart", "solar", "sacrum", "root"])
check("every sign belongs to a station, in head-to-feet order",
      all(M.zones_of_sign(i) for i in range(12)) and all(M.KEYS.index(M.zones_of_sign(i)[0]) <= M.KEYS.index(M.zones_of_sign(i + 1)[0]) for i in range(11)))
check("every mansion's body part belongs to a station", len(T["NAK_ZONE"]) == 27 and set(T["NAK_ZONE"]) <= set(M.KEYS))
from wyrd import rave as RV
check("every bodygraph centre has its station", sorted(c for z in T["ZONES"] for c in z["centre"]) == sorted(v[0] for v in RV.CENTRES.values()))
check("every dosha has a home on the ladder", {z["dosha"] for z in T["ZONES"]} == set(M.DOSHAS))
check("every map is explained", [l[0] for l in T["LENSES"]] == ["The sign", "The house", "The mansion", "The centre", "The tropical sign", "The planet", "The dosha", "The period"])

# the free chart's copy of the tables, read in node
js = open(os.path.join(ROOT, "static", "medical.js"), encoding="utf-8").read()
out = subprocess.run(["node"], input="const window = {};" + js + "process.stdout.write(JSON.stringify(window.WyrdMedical));",
                     capture_output=True, text=True, check=True).stdout
MD = json.loads(out)
check("the free chart's body map uses the same tables", MD["SIGN"] == {k: v["part"] for k, v in T["SIGN"].items()} and MD["NAK"] == T["NAK"]
      and MD["NAK_ZONE"] == T["NAK_ZONE"] and [z["signs"] for z in MD["ZONES"]] == [z["signs"] for z in T["ZONES"]] and [z["centre"] for z in MD["ZONES"]] == [z["centre"] for z in T["ZONES"]])
src = open(os.path.join(ROOT, "static", "chart.js"), encoding="utf-8").read()
check("the free chart shows it, and points to the reading for the meaning", "WyrdMedical" in src and "The Body's Old Map" in src)
check("the page loads the tables", "/static/medical.js" in open(os.path.join(ROOT, "static", "chart.html"), encoding="utf-8").read())

# pretend charts
NOW = 2461325.0
def chart(seed, unknown=False):
    random.seed(seed)
    sid = {b: random.uniform(0, 360) for b in M.NINE[:7]}
    sid["Rahu"] = random.uniform(0, 360); sid["Ketu"] = E.norm(sid["Rahu"] + 180)
    ay = 24.1
    C = {"sid": sid, "trop": {b: E.norm(l + ay) for b, l in sid.items()}, "ascS": random.uniform(0, 360), "ay": ay, "jd": NOW - 30 * E.YEAR}
    if unknown: C["unknownTime"] = True
    return C, E.dasha_tree(C, NOW)

leftover, notes, ds_ok, texts = [], 0, True, []
for s in range(300):
    C, d = chart(s, unknown=s % 10 == 0); asks = []
    t = M.body(C, d, asks); texts.append(t)
    leftover += re.findall(r"\{[a-z_]+\}", t)
    notes += T["NOTE"] in t
    ds = M.doshas(C); ds_ok &= 98 <= sum(ds.values()) <= 102 and all(v >= 0 for v in ds.values())
    if not asks or asks[0][0] != "The body": leftover.append("no question")
check("300 charts, no blank left unfilled, each asks its question", not leftover)
check("every reading says it isn't medical advice", notes == 300)
check("the doshas always add up to the whole", ds_ok)
check("no 'The' in the middle of a sentence", not any(re.search(r"[a-z,] The (Sun|Moon)\b", re.sub("<[^>]+>", "", t)) for t in texts))

# a planet in its weakest sign, or in the 6th, 8th or 12th, is under strain
C, d = chart(1); C["ascS"] = 5.0; C["sid"]["Saturn"] = 5.0; C["sid"]["Sun"] = 185.0; C["sid"]["Mars"] = 155.0   # Mars in Virgo: the 6th
by = {r["body"]: r for r in M.facts(C)}
check("Saturn in Aries is in its weakest sign", by["Saturn"]["strain"] and by["Saturn"]["dignity"] == "debilitated")
check("the Sun in Libra too", by["Sun"]["strain"])
check("Mars in the 6th is under strain", by["Mars"]["house"] == 6 and by["Mars"]["strain"])
check("a planet's house gives the body part counted from the rising sign", by["Mars"]["house_part"] == "the belly")
C["sid"]["Jupiter"] = 95.0
check("Jupiter in Cancer, its best sign and not in a hard house, is strong", M.facts(C)[4]["strong"])
w, parts = M.weight(M.grid(C, []))
check("the rising sign counts three at its station", parts["crown"]["sign"] >= 1.5 and parts["brow"]["sign"] >= 1.5)

# the free chart and the reading lay the maps out alike
random.seed(11)
NAMES = [v[0] for v in RV.CENTRES.values()]
cases = []
for i in range(500):
    C, _ = chart(1000 + i, unknown=i % 7 == 0)
    cases.append((C, random.sample(NAMES, random.randint(0, 9)), bool(C.get("unknownTime"))))
prog = js + f"process.stdout.write(JSON.stringify({json.dumps([[c, d, u] for c, d, u in cases])}.map(([C, d, u]) => window.WyrdMedical.grid(C, d, u))));"
browser = json.loads(subprocess.run(["node"], input="const window = {};" + prog, capture_output=True, text=True, check=True).stdout)
server = [json.loads(json.dumps(M.grid(C, d, u))) for C, d, u in cases]
check("the free chart and the reading put every planet on the same station, 500 charts", browser == server)
C, d = chart(3); g = M.grid(C, ["G", "Heart"])
w, parts = M.weight(g)
check("all the weight is accounted for: rising 3, Moon 2, eight planets, nine houses, nine mansions at a half, a station with its centres defined",
      abs(sum(w.values()) - (3 + 2 + 8 + 9 + 4.5 + 1)) < 1e-9)   # G and Heart share the heart station: one between them
check("a defined centre adds to its station", parts["heart"]["centre"] == 1)

# the body diagram
C, d = chart(5); g = M.grid(C, ["Root"]); w, _ = M.weight(g); fig = M.figure(g, w)
check("the diagram marks all seven stations and names them", fig.count('class="mf-dot') == 7 and all(M.ZONE[k]["name"].replace("The ", "") in fig for k in M.KEYS))
check("every station on the diagram has a place on the figure", set(T["FIGURE"]["at"]) == set(M.KEYS))
check("the two heaviest stations stand out", fig.count('mf-dot hi') >= 2)

# the full reading carries it
src = open(os.path.join(ROOT, "wyrd", "reading.py"), encoding="utf-8").read()
check("the reading has the section, right after The Body", src.index("MEDICAL.body") > src.index("MORE.body(C)") and src.index("MEDICAL.body") < src.index("Where You Thrive\", \"culture"))

print("MEDICAL CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
