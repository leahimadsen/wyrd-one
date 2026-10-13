"""The Dharma Gates: every gate the Dharma Design holds, read one by one, and how to wake it.

    python tests/dharma_check.py

Casts real charts with the console's built-in ephemeris (needs node), so no Skyfield."""
import json, os, random, re, sys
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import engine as E, rave as RV, dharma as DH, reading, reading_more as MORE
from tests.verify_engine import NodeEph

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

T = DH.T
check("a practice and a sign for every gate", set(T["GATES"]) == {str(g) for g in range(1, 65)} and all(v["do"] and v["sign"] for v in T["GATES"].values()))
check("every channel named, with what it does and how to live it",
      set(T["CHANNELS"]) == {DH.key(a, b) for a, b in RV.CHANNELS} and all(v["name"] and v["what"] and v["live"] for v in T["CHANNELS"].values()))
check("every centre, grown into and released", set(T["CENTRES"]) == {v[0] for v in RV.CENTRES.values()} and all(v["grow"] and v["release"] for v in T["CENTRES"].values()))
check("all six lines", set(T["LINE"]) == set(T["LINE_SHORT"]) == {str(i) for i in range(1, 7)})
check("the Sun's yearly days: gate 41 opens the wheel near 22 January", DH.sun_week(41).endswith("January") and DH.sun_week(41).startswith(("21", "22", "23")))
check("every gate gets five or six of the Sun's days", all(5 <= _n <= 7 for _n in [
      len([d for d in range(365) if E.gate_of(DH._sun_lon(date.fromordinal(date(2027, 1, 1).toordinal() + d)))["gate"] == g]) for g in range(1, 65)]))

eph = NodeEph()
random.seed(7)
for i in range(6):
    y, mo, d, h = random.randint(1950, 2010), random.randint(1, 12), random.randint(1, 28), random.uniform(0, 24)
    lat, lon = random.uniform(-50, 60), random.uniform(-170, 170)
    C = E.cast(eph, y, mo, d, h, lat, lon)
    dasha = E.dasha_tree(C, C["jd"] + 365.25 * 30)
    MORE.reset()
    html = DH.body(C, dasha, reading.activation, reading.repair)
    have_n, have_d = RV.gates(C["natal"]), RV.gates(C["dharma"])
    shown = [int(g) for g in re.findall(r'<div class="rd-entry dh-gate"><h3>Gate (\d+)\.', html)]
    check(f"chart {i + 1}: every dharma gate read once", sorted(shown) == sorted(have_d))
    check(f"chart {i + 1}: gates in body order, from the Head down",
          [list(RV.CENTRES).index(RV.CENTRE_OF[g]) for g in shown] == sorted(list(RV.CENTRES).index(RV.CENTRE_OF[g]) for g in shown))
    live_d, _ = RV.defines(C["dharma"]); live_n, _ = RV.defines(C["natal"])
    bridges = {(a, b) for a, b in RV.CHANNELS if (a, b) not in live_n and (a, b) not in live_d and {a, b} <= have_n | have_d
               and (a in have_d or b in have_d) and (a in have_n or b in have_n)}
    found = {tuple(map(int, m)) for m in re.findall(r'<div class="rd-entry dh-ch"><h3>Channel (\d+)–(\d+)', html)}
    check(f"chart {i + 1}: channels are the dharma's own and the bridges", found == set(live_d) | bridges)
    txt = re.sub(r"<[^>]+>", "", html)
    check(f"chart {i + 1}: nothing left unfilled", not re.search(r"\{(?!SEC:)", txt) and not re.search(r"\bNone\b(?! of them)", txt))
    check(f"chart {i + 1}: no period past a long life", not any(int(a) > 90 for a in re.findall(r"Opens at (\d+)", txt)))

print("DHARMA CHECK PASSED" if not bad else f"DHARMA CHECK FAILED ({bad})")
sys.exit(1 if bad else 0)
