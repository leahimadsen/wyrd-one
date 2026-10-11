"""The chara karakas in both zodiacs.

    python tests/karaka_check.py

The free chart ranks the tropical karakas in the browser (static/chart.js) and
the reading ranks them on the server (wyrd/engine.py); this checks the two
always agree, and that the ranking is the sidereal rule applied to the
tropical signs. Needs node; no ephemeris."""
import json, os, random, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import engine as E

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
sid = {"Sun": 10.5, "Moon": 29.0, "Mars": 3.2, "Mercury": 44.0, "Jupiter": 75.9, "Venus": 120.1, "Saturn": 200.0}
K = E.karakas(sid)
check("sidereal: furthest through its sign leads", K["Atmakaraka"] == "Moon" and K["Darakaraka"] == "Venus")
trop = {b: E.norm(l + 24) for b, l in sid.items()}
KT = E.karakas(trop)
check("tropical: the same rule on the tropical signs", KT["Atmakaraka"] == "Mars" and list(KT.values()) == sorted(SEVEN, key=lambda b: -E.deg_in(trop[b])))
check("seven seats, every planet once", sorted(KT.values()) == sorted(SEVEN) and list(KT) == E.KARAKA7)

# the browser's ranking, lifted from chart.js, run in node against the server's
src = open(os.path.join(ROOT, "static", "chart.js"), encoding="utf-8").read()
rank = re.search(r"const rank = (L => .*?);\n", src).group(1)
random.seed(7)
cases = [{b: random.uniform(0, 360) for b in SEVEN} for _ in range(1000)]
js = f"""const norm = x => ((x % 360) + 360) % 360; const SEVEN = {json.dumps(SEVEN)}; const rank = {rank};
process.stdout.write(JSON.stringify({json.dumps(cases)}.map(rank)));"""
browser = json.loads(subprocess.run(["node"], input=js, capture_output=True, text=True, check=True).stdout)
server = [list(E.karakas(c).values()) for c in cases]
check("browser and server rank alike, 1000 random charts", browser == server)

roles = json.loads(re.search(r"const ROLES = (\[.*?\]);", src).group(1))
check("the free table lists the roles in rank order, Atma first", roles == E.KARAKA7)

print("KARAKA CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
