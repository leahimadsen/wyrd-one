"""The free Sukuyō pages: the old calendar is right, the pages read in full, the finder works,
and nothing of the paid writing about a bond shows.

    WYRD_DEV_NODE_EPH=1 python tests/sukuyo_learn_check.py      (no Skyfield needed)
"""
import html, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
import app as A
from wyrd import sukuyo as SK, sukuyo_learn as L, bond as BOND

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# the old Japanese calendar: lunar new years, and leap months, as Japan keeps them
NEW_YEARS = [(1990, 1, 27), (2000, 2, 5), (2001, 1, 24), (2010, 2, 14), (2020, 1, 25), (2023, 1, 22), (2024, 2, 10), (2025, 1, 29)]
check("lunar new year falls on the first day of the first month", all(SK.lunar_date(A.EPH, *d) == (1, 1, False) for d in NEW_YEARS))
LEAPS = [((2014, 11, 5), 9), ((2020, 6, 5), 4), ((2023, 4, 5), 2), ((2017, 7, 5), 5)]     # 2017: Japan's leap month follows the 5th (China's the 6th)
check("leap months land where Japan's calendar puts them", all(SK.lunar_date(A.EPH, *d)[0] == m and SK.lunar_date(A.EPH, *d)[2] for d, m in LEAPS))
check("1 January 2000 is the 25th of the 11th month", SK.lunar_date(A.EPH, 2000, 1, 1) == (11, 25, False))
s = SK.birth_shuku(A.EPH, 1985, 3, 14)
check("a birth shuku is the month's opening shuku, moved on by the day", s["index"] == (SK.MONTH_START[s["lunarMonth"] - 1] + s["lunarDay"] - 1) % 27)

# the ring: each name in its place, and the six relations pair up both ways
check("the ring has Life, Karma and Womb at 0, 9 and 18", (SK.RING[0], SK.RING[9], SK.RING[18]) == ("命", "業", "胎"))
check("every relation reads the same from either side", all(SK.relation(a, b)["pair"] == SK.relation(b, a)["pair"] for a in range(27) for b in range(27)))
for p, v in L.T["PAIRS"].items():
    # the offsets, counted forward from you, at which another person makes this relation with you
    ks = {b for b in range(27) if SK.relation(0, b)["pair"] == p}
    nums = {int(n) for n in re.findall(r"\d+", v["how"])}
    either_way = nums | {(27 - n) % 27 for n in nums}           # "counting either way": forward, or the same number backward
    check(f"the page counts {p} right ({v['how']})", (ks == {0}) if p == "命" else either_way == ks)

# the overview
title, desc, body, ld = L.index_page("https://example")
t = html.unescape(re.sub(r"<[^>]+>", " ", body))
check("the overview teaches the source, the calendar, the ring and the six", all(h in body for h in ("Where it comes from", "comes from the calendar", "The three nines", "The six relations", "<svg")))
check("all twenty-seven shuku are listed, each beside its nakshatra", body.count('<td class="sk-kj">') == 27 and all(f"/learn/nakshatras/{L.slug(n)}" in body for _, _, n in SK.SHUKU))
check("it reads at length", len(t.split()) > 700)
paid = [v["text"][:60] for v in BOND.B["SUKUYO"].values()] + [v["ask"][:40] for v in BOND.B["SUKUYO"].values()]
check("none of the paid writing about a bond is on the page", not any(x in t for x in paid))

# the finder, through the site
c = A.app.test_client()
r = c.get("/learn/sukuyo"); check("the page is served", r.status_code == 200 and "<h1>Sukuyō</h1>" in r.get_data(as_text=True))
r = c.get("/learn/sukuyo/find?a=1985-03-14"); one = html.unescape(r.get_data(as_text=True))
check("one date gives its shuku and how it was found", r.status_code == 200 and "箕" in one and "day 23 of the first lunar month" in one)
r = c.get("/learn/sukuyo/find?a=1985-03-14&b=1987-11-02"); two = html.unescape(r.get_data(as_text=True))
rel = SK.relation(SK.birth_shuku(A.EPH, 1985, 3, 14)["index"], SK.birth_shuku(A.EPH, 1987, 11, 2)["index"])
check("two dates give the relation by name and distance", L.T["PAIRS"][rel["pair"]]["title"] in two and rel["distance"] in two)
check("the finder keeps the paid writing back too", not any(x in two for x in paid))
check("a bad date is turned back, not a crash", c.get("/learn/sukuyo/find?a=nonsense").status_code == 400 and c.get("/learn/sukuyo/find?a=1700-01-01").status_code == 400)
check("the learn index and the sitemap link it", 'href="/learn/sukuyo"' in A.pages.learn_index("https://x")[2] and "/learn/sukuyo<" in A.pages.sitemap("https://x"))

print("SUKUYO LEARN CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
