"""The Two Designs and The Walk: how the Birth Design and the Dharma Design work together, and the walk
from one into the other, by practice, over a life and over a year.

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
check("all six lines, and how each learns", set(T["LINE"]) == set(T["LINE_SHORT"]) == set(T["LINE_HOW"]) == {str(i) for i in range(1, 7)})
check("every authority has its words", set(T["AUTH"]) == {"Emotional", "Sacral", "Splenic", "Ego manifested", "Ego projected", "Self-projected", "Outer", "Lunar"})
check("the band in words, for the seam, the echo and the magenta point", set(T["BAND"]) == {"Seam", "Echo", "magenta"})
check("no ascent: the dharma is walked further, not climbed to", not re.search(r"\b(higher self|ascen\w*|climb to)\b", json.dumps(T, ensure_ascii=False), re.I))
meds = {g: DH.medicines(r["r"]) for g, r in DH.REG.items()}
check("every gate in the register gives its medicines, flood and freeze (the three told otherwise are read whole)",
      all({k for k, _ in m} == {"Flood", "Freeze"} for g, m in meds.items() if g not in ("14", "25", "53")) and not any(meds[g] for g in ("14", "25", "53")))
check("a medicine read out whole: gate 2", meds["2"] == [("Flood", "Medicine is the dark gift: institute the drought."),
      ("Freeze", "Medicine is the light gift: ask what form the life is already proposing, then water only that.")])
check("a medicine inside its sentence: gate 31's flood", ("Flood", "Medicine is the dark gift in miniature — vacate one claimed seat.") in meds["31"])
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
    N, Dh = C["natal"], C["dharma"]
    have_n, have_d = RV.gates(N), RV.gates(Dh)
    live_n, _ = RV.defines(N); live_d, _ = RV.defines(Dh)
    M = DH.meet(N, Dh)
    bridges = {(a, b) for a, b in RV.CHANNELS if (a, b) not in live_n and (a, b) not in live_d and {a, b} <= have_n | have_d
               and (a in have_d or b in have_d) and (a in have_n or b in have_n)}
    check(f"chart {i + 1}: the bridges are the channels neither design completes and both reach", {c for c, _, _ in M["bridges"]} == bridges)
    check(f"chart {i + 1}: each bridge has one end only at birth and one only in the dharma",
          all(b in have_n and b not in have_d and d in have_d and d not in have_n for _, b, d in M["bridges"]))
    check(f"chart {i + 1}: keel, bridge halves and reach share out the dharma gates, once each",
          sorted(M["keel"] + M["halves"] + M["reach"]) == sorted(have_d))
    MORE.reset()
    two = DH.two_designs(C)
    found = {tuple(map(int, m)) for m in re.findall(r'<div class="rd-entry tw-ch"><h4>Channel (\d+)–(\d+)', two)}
    check(f"chart {i + 1}: the bridges and what the dharma builds are read", found == bridges | {c for c in live_d if c not in live_n})
    check(f"chart {i + 1}: both designs drawn on one body", two.count('class="bg-fig bg-k"') == 1 and two.count("k-bridge k-under") == len(bridges))
    check(f"chart {i + 1}: the Pentagram Cross holds", "72.000000° ✓" in two)
    asks = []
    walk = DH.walk(C, dasha, reading.activation, asks)
    cards = [int(g) for g in re.findall(r'<div class="rd-entry wk-gate"><h4>Gate (\d+)\.', walk)]
    cross = {Dh[s][b]["gate"] for s, b, _ in DH.CROSS}
    check(f"chart {i + 1}: every dharma gate the walk asks for has its card once (the keel is trusted, not practised)",
          len(cards) == len(set(cards)) and set(cards) == (have_d - have_n) | cross)
    check(f"chart {i + 1}: the four cross gates carry their gifts and medicines", walk.count('<p class="rd-med">') >= 2 * len(cross) - 2)
    life = re.search(r'<table class="wk-life">(.*?)</table>', walk, re.S).group(1)
    in_life = [int(g) for g in re.findall(r"<b>(\d+)</b>", life)]
    check(f"chart {i + 1}: over a life, every dharma gate under the period that opens it, once", sorted(in_life) == sorted(have_d))
    yr = re.search(r'<table class="wk-year">(.*?)</table>', walk, re.S).group(1)
    in_year = [int(g) for g in re.findall(r"<b>(\d+)</b>", yr)]
    starts = [DH.sun_days(g)[0].timetuple().tm_yday for g in in_year]
    check(f"chart {i + 1}: over a year, every dharma gate on the calendar, in order", sorted(in_year) == sorted(have_d) and starts == sorted(starts))
    check(f"chart {i + 1}: the dharma cross's questions are gathered", sum(1 for lab, _, _ in asks if lab.startswith("Dharma ")) == len(cross))
    txt = re.sub(r"<[^>]+>", "", two + walk)
    check(f"chart {i + 1}: nothing left unfilled", not re.search(r"\{(?!SEC:)", txt) and not re.search(r"\bNone\b(?! of them)", txt))
    check(f"chart {i + 1}: no period past a long life", not any(int(a) > 90 for a in re.findall(r"Opens at (\d+)", txt)))

# the whole reading: the two designs, then the walk, then the path, each step at birth and as it matures
C = E.cast(eph, 1988, 9, 23, 6.6667, 64.1466, -21.9426)
body = reading.build(C, E.dasha_tree(C, C["jd"] + 365.25 * 38), {"name": "", "date": "1988-09-23"})
heads = re.findall(r'<section class="rd-sec[^"]*" id="[^"]+">\s*<div class="rd-num">[^<]*</div>\s*<h2>(.*?)</h2>', body)
check("the reading reads the Two Designs, then the Walk, then the Path of Dharma",
      heads.index("The Two Designs") + 1 == heads.index("The Walk") == heads.index("The Path of Dharma") - 1)
check("the old gate-by-gate sections are gone", "The Dharma Gates" not in heads and "The Dharma Weave" not in heads)
path = body[body.index("<h2>The Path of Dharma</h2>"):body.index("<h2>The Numbers")]
check("every step of the path is read at birth and as it matures", path.count('class="rd-gate ripe"') == path.count('class="rd-step"') == 11)
check("sections that name each other are numbered", not re.search(r"\{\{?SEC:", re.sub(r"<script.*?</script>", "", body, flags=re.S)))

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
