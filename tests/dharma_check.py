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

# the free chart shows the Dharma Design's facts and picture; what it means is the reading's, and the Order's
src = lambda f: open(os.path.join(ROOT, "static", f), encoding="utf-8").read()
dz, vg, cj = src("design.js"), src("vargas.js"), src("chart.js")
check("a free chart gets the Dharma Design's facts, not its readout", "function locked(R, label)" in dz and "(open() ? readout : locked)(dharma" in dz)
check("the Birth Design is still read in full for everyone", 'readout(birth, "Your Birth Design")' in dz)
check("the Rashi-to-Dharma prose waits for the reading on a free chart", "${full ? `<h4>${w.RIPEN_H" in vg and 'class="dg-lock"' in vg)
check("members see both in full, even when membership arrives after the page is drawn",
      "full: () => MEMBER" in cj and "full: MEMBER" in cj and "DESIGN.redraw()" in cj and "full: true" in cj)

# dignity is a ladder: the Navamsha can step a planet down without debilitating it
from wyrd import vargas as VG
L = {"sid": {"Sun": 293.4, "Moon": 325.0, "Mercury": 289.2, "Venus": 261.5, "Mars": 267.5, "Jupiter": 138.6, "Saturn": 286.4}}   # Leah's Rashi
check("natural friendship alone, without a chart: Saturn in Venus's Taurus is a friend's sign", VG.dignity_in("Saturn", 1) == "friend's sign")
check("compound with the chart: Venus is also Saturn's temporary friend (12th from it), so a great friend's sign",
      VG.dignity_in("Saturn", 1, L) == "great friend's sign" and VG.RANK["own sign"] - VG.RANK["great friend's sign"] == 1)
check("natural friend, temporary enemy cancel to neutral: Jupiter in the Sun's Leo", VG.dignity_in("Jupiter", 4, L) == "neutral sign")
check("natural enemy, temporary enemy: Jupiter in Mercury's Virgo is a great enemy's sign", VG.dignity_in("Jupiter", 5, L) == "great enemy's sign")
check("only the sign of debilitation is debilitated", VG.dignity_in("Saturn", 0, L) == "debilitated" and VG.dignity_in("Jupiter", 9, L) == "debilitated")
check("the ladder runs exalted, own, great friend's, friend's, neutral, enemy's, great enemy's, debilitated",
      [k for k, _ in sorted(VG.RANK.items(), key=lambda kv: -kv[1]) if k] == ["exalted", "own sign", "great friend's sign", "friend's sign", "neutral sign", "enemy's sign", "great enemy's sign", "debilitated"])
vj = src("vargas.js")
check("the page keeps the same friendships and ladder as the reading",
      all(f'{b}: {{ friend: [{", ".join(chr(34) + x + chr(34) for x in sorted(VG.KIN[b][0], key=lambda x: ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"].index(x)))}]' in vj for b in VG.KIN)
      and all(f'"{k}": {v}' in vj for k, v in VG.RANK.items() if k) and "[2, 3, 4, 10, 11, 12]" in vj and "dignityIn(b, s9, C)" in vj)
check("the page and the reading both explain the ladder, with the person's own planet", "ladderEg" in vj and 'W["LADDER_EG"]' in open(os.path.join(ROOT, "wyrd", "vargas.py"), encoding="utf-8").read())
from wyrd import vargas as _v
check("every rung has its phrase", set(VG.RANK) - {""} <= set(_v.W["STANDING"]))

print("DHARMA CHECK PASSED" if not bad else f"DHARMA CHECK FAILED ({bad})")
sys.exit(1 if bad else 0)
