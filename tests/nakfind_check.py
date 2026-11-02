"""The nakshatra finder at /nakshatra-calculator: the page is found by search, the answer matches the chart engine,
an unknown birth time is handled honestly, and birth details never reach an address or an indexed page.

    WYRD_DEV_NODE_EPH=1 python tests/nakfind_check.py      (no Skyfield needed)
"""
import html, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
import app as A
from wyrd import engine as E, nakfind as N, pages as P

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

text = lambda h: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)))
c = A.app.test_client()
NY = {"place_id": "", "lat": "40.7128", "lon": "-74.006", "tz": "America/New_York", "place_label": "New York, United States"}

# the page people search for
r = c.get("/nakshatra-calculator"); h = r.get_data(as_text=True)
check("the page opens", r.status_code == 200)
check("its title answers the search", "<title>What Is My Nakshatra? Free Nakshatra Calculator" in h)
check("it is indexed", 'content="index, follow"' in h)
check("the form posts, so birth details stay out of the address", 'method="post" action="/nakshatra-calculator"' in h)
check("it carries its questions for search (FAQPage)", '"FAQPage"' in h and h.count('"@type": "Question"') == len(N.FAQ))
check("it lists all 27 mansions, each linked", all(f'href="/learn/nakshatras/{s}"' in h for s, _ in P.NAKS))
check("the place picker is wired", "/static/common.js" in h and "placeSearch" in h)

# linked from where people and crawlers already go
check("in the sitemap", "/nakshatra-calculator" in P.sitemap("https://example"))
check("from Learn", 'href="/nakshatra-calculator"' in P.learn_index("https://example")[2])
check("from every mansion page", all('href="/nakshatra-calculator"' in P.nakshatra("https://example", s)[2] for s, _ in P.NAKS))
check("from the first page", 'href="/nakshatra-calculator"' in P.home_explore())

# a known birth time: the same answer as the full chart
births = [("1990-03-14", "06:30"), ("1985-11-02", "23:10"), ("2001-07-19", "12:00"), ("1972-01-30", "03:45"), ("2015-12-25", "18:20")]
same = rune_same = rising_same = noindex = True
for date, time in births:
    r = c.post("/nakshatra-calculator", data={**NY, "date": date, "time": time}); h = r.get_data(as_text=True)
    b = A.birth_from({**NY, "date": date, "time": time})
    ch = A.cast_for(b)
    m = ch["sid"]["Moon"]; i = int(m // (360 / 27)); pada = int((m - i * 360 / 27) // (360 / 108)) + 1
    same &= r.status_code == 200 and f"Your Moon is in {P.C['NAKSHATRA'][i][0]}, pada {pada}" in text(h)
    cusp = int(ch["ascS"] // 30) * 30; ri = int(E.norm(m - cusp) // 15)        # as deck.js person() and the Runes page
    rune_same &= f"The rune of your Moon: {P.RUNES[ri][1]} {P.RUNES[ri][2]}" in text(h)
    a = ch["ascS"]; ai = int(a // (360 / 27))
    rising_same &= f"Your rising nakshatra is {P.C['NAKSHATRA'][ai][0]}" in text(h)
    noindex &= 'content="noindex, nofollow"' in h and date not in r.request.url
check("the Moon's mansion and pada match the chart engine", same)
check("the rune of the Moon matches the card and the Runes page", rune_same)
check("the rising nakshatra matches the chart engine", rising_same)
check("an answer is never indexed, and the date is never in the address", noindex)
check("the answer offers the full chart, carrying the birth only in the page", '"date": "2015-12-25"' in h and "WyrdCommon.cast" in h)

# an unknown time: honest about days when the Moon changes mansion
def moon_at(date, minute):
    y, mo, d = map(int, date.split("-"))
    u = A.to_ut(y, mo, d, minute // 60, minute % 60, NY["tz"])
    jd = E.julian_day(u["y"], u["mo"], u["d"], u["h"])
    return int(N._sid(A.EPH, jd, "Moon") // (360 / 27))
import datetime as dt
d0 = dt.date(1990, 3, 1); change = still = None
for k in range(40):
    s = (d0 + dt.timedelta(days=k)).isoformat()
    if moon_at(s, 0) != moon_at(s, 1439): change = change or s
    else: still = still or s
r = c.post("/nakshatra-calculator", data={**NY, "date": still, "unknown_time": "1"}); t = text(r.get_data(as_text=True))
check("a day with one mansion names it outright", f"Your Moon is in {P.C['NAKSHATRA'][moon_at(still, 0)][0]}" in t and "all day" in t)
check("without a time there is no pada, rising or rune", ", pada" not in t and "rising nakshatra is" not in t and "The rune of your Moon:" not in t)
r = c.post("/nakshatra-calculator", data={**NY, "date": change, "unknown_time": "1"}); t = text(r.get_data(as_text=True))
a, b2 = moon_at(change, 0), moon_at(change, 1439)
check("a day the Moon changes mansion gives both", t.count("Your Moon may be in") >= 2 and P.C["NAKSHATRA"][a][0] in t and P.C["NAKSHATRA"][b2][0] in t)
seg = N.day_segments(A.EPH, "Moon", lambda m: (lambda u: E.julian_day(u["y"], u["mo"], u["d"], u["h"]))(
    A.to_ut(*map(int, change.split("-")), m // 60, m % 60, NY["tz"])))
class Batched:                      # the live ephemeris's one-call lookup, played by the dev one
    def __init__(s, eph): s.eph = eph
    def positions(s, jd): return s.eph.positions(jd)
    def ayanamsa(s, jd): return s.eph.ayanamsa(jd)
    def positions_many(s, jds, bodies=None): return [(s.eph.positions(j), s.eph.ayanamsa(j)) for j in jds]
to_jd = lambda m: (lambda u: E.julian_day(u["y"], u["mo"], u["d"], u["h"]))(A.to_ut(*map(int, change.split("-")), m // 60, m % 60, NY["tz"]))
check("the batched lookup finds the same change as the stepwise one", N.day_segments(Batched(A.EPH), "Moon", to_jd) == seg)
cut = seg[1][1]
check("and the minute of the change is right", moon_at(change, cut - 1) == a and moon_at(change, cut) != a and N.clock(cut) in t)

# mistakes come back as the page, with a reason
r = c.post("/nakshatra-calculator", data={**NY, "date": "1990-02-30", "time": "10:00"})
check("an impossible date is refused kindly", r.status_code == 400 and "doesn't exist" in text(r.get_data(as_text=True)))
r = c.post("/nakshatra-calculator", data={"date": "1990-03-14", "time": "10:00"})
check("no birthplace is refused kindly", r.status_code == 400 and "birthplace" in r.get_data(as_text=True))

print("NAKFIND CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
