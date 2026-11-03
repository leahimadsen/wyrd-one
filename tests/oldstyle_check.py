"""Old Style dates: a birth recorded in the Julian calendar is cast for its true day.

The conversion matches births whose two dates history gives; an Old Style birth casts exactly the sky of its
New Style day; Old Style applies only where and while the Julian calendar was kept; the marker survives every route a birth travels (checkout, readings together, stored births,
share links); readings show both dates; the numbers count by the New Style day; and a day that exists only in
the Julian calendar (29 February 1900) is accepted.

    WYRD_DEV_NODE_EPH=1 python tests/oldstyle_check.py      (no Skyfield needed)
"""
import html, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
import app as A
from wyrd import oldstyle as OS, numbers as NUM

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

text = lambda h: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)))

# ---- the conversion, against births history gives in both calendars ----
KNOWN = [("Vladimir Lenin", "1870-04-10", "1870-04-22"), ("Nicholas II", "1868-05-06", "1868-05-18"),
         ("Wassily Kandinsky", "1866-12-04", "1866-12-16"), ("Sergei Rachmaninoff", "1873-03-20", "1873-04-01"),
         ("Boris Pasternak", "1890-01-29", "1890-02-10"), ("Vladimir Nabokov", "1899-04-10", "1899-04-22"),
         ("Dmitri Shostakovich", "1906-09-12", "1906-09-25"), ("Nikos Kazantzakis", "1883-02-06", "1883-02-18")]
for who, o, n in KNOWN:
    check(f"{who}: {o} Old Style is {n}", OS.new_style({"date": o, "cal": "J"}) == n)
check("the offset grows to 13 days at the Julian leap day of 1900",
      OS.new_style({"date": "1900-02-28", "cal": "J"}) == "1900-03-12" and OS.new_style({"date": "1900-03-01", "cal": "J"}) == "1900-03-14")
check("Russia's last Old Style day is the day before its first New Style one", OS.new_style({"date": "1918-01-31", "cal": "J"}) == "1918-02-13")
check("a New Style date is left alone", OS.new_style({"date": "1899-04-10"}) == "1899-04-10")

# ---- the same sky ----
SPB = {"lat": 59.9386, "lon": 30.3141, "tz": "Europe/Moscow", "place_label": "Saint Petersburg, Russia", "place_id": None, "cc": "RU"}
old = A.birth_from({**SPB, "date": "1899-04-10", "time": "04:15", "cal": "J"})
new = A.birth_from({**SPB, "date": "1899-04-22", "time": "04:15"})
check("an Old Style birth is cast for its New Style day", (old["y"], old["mo"], old["d"]) == (1899, 4, 22) and old["ut"] == new["ut"])
check("the date as the record gives it is kept", old.get("os") == "1899-04-10" and "os" not in new)
co, cn = A.cast_for(old), A.cast_for(new)
check("every planet where it is on the New Style day", all(abs(co["trop"][k] - cn["trop"][k]) < 1e-9 for k in cn["trop"]))
naive = A.cast_for(A.birth_from({**SPB, "date": "1899-04-10", "time": "04:15"}))
moved = abs((naive["trop"]["Moon"] - cn["trop"]["Moon"] + 180) % 360 - 180)
check(f"read as New Style by mistake, the Moon would be {moved:.0f}° off", moved > 100)

leap = A.birth_from({**SPB, "date": "1900-02-29", "time": "12:00", "cal": "J"})
check("29 February 1900 Old Style is a real birth day (13 March 1900)", (leap["y"], leap["mo"], leap["d"]) == (1900, 3, 13))
try: A.birth_from({**SPB, "date": "1901-02-29", "time": "12:00", "cal": "J"}); check("a day no calendar had is refused", False)
except A.BadInput as e: check("a day no calendar had is refused", "Julian" in str(e))

# ---- only where and while the Julian calendar was kept ----
def cast_day(place, date, cal="J"):
    b = A.birth_from({**place, "date": date, "time": "12:00", "cal": cal})
    return "%04d-%02d-%02d" % (b["y"], b["mo"], b["d"]), b.get("os")
LON = {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "place_label": "London", "place_id": None, "cc": "GB"}
KGD = {"lat": 54.7104, "lon": 20.4522, "tz": "Europe/Kaliningrad", "place_label": "Kaliningrad", "place_id": None, "cc": "RU"}
SIT = {"lat": 57.0531, "lon": -135.33, "tz": "America/Sitka", "place_label": "Sitka", "place_id": None, "cc": "US"}
ATH = {"lat": 37.9838, "lon": 23.7275, "tz": "Europe/Athens", "place_label": "Athens", "place_id": None, "cc": "GR"}
check("not in London, which kept the Gregorian calendar: the date stands", cast_day(LON, "1899-04-10") == ("1899-04-10", None))
check("not in Russia after its change: a 1990 date stands", cast_day(SPB, "1990-04-10") == ("1990-04-10", None))
check("Russia's last Old Style day applies (31 January 1918)", cast_day(SPB, "1918-01-31") == ("1918-02-13", "1918-01-31"))
check("a day Russia skipped can't be Old Style (5 February 1918 stands)", cast_day(SPB, "1918-02-05") == ("1918-02-05", None))
check("Greece until its change in 1923", cast_day(ATH, "1923-02-15") == ("1923-02-28", "1923-02-15") and cast_day(ATH, "1924-01-01")[1] is None)
check("not in Kaliningrad, then Prussian, though it's in Russia now", cast_day(KGD, "1899-04-10") == ("1899-04-10", None))
check("Russian Alaska before 1867, not after", cast_day(SIT, "1860-01-01")[1] == "1860-01-01" and cast_day(SIT, "1870-01-01")[1] is None)
check("the country comes from the place index when only the place is given",
      A.place_cc(next(iter(A.PLACES.search("New York", 1)))["id"]) == "US" and A.place_cc("") is None and A.place_cc("x") is None)

# ---- the chart, through the site ----
c = A.app.test_client()
r = c.post("/api/chart", json={**SPB, "date": "1899-04-10", "time": "04:15", "cal": "J"}); j = r.get_json()
r2 = c.post("/api/chart", json={**SPB, "date": "1899-04-22", "time": "04:15"}); j2 = r2.get_json()
check("the chart opens", r.status_code == 200 and r2.status_code == 200)
check("the chart says which day it was cast for", j["born"] == {"date": "1899-04-22", "os": "1899-04-10"} and j2["born"]["os"] is None)
check("the chart's Moon is the New Style day's", abs(j["chart"]["trop"]["Moon"] - j2["chart"]["trop"]["Moon"]) < 1e-9)

# ---- the marker travels with the birth ----
d = {**SPB, "name": "Test", "date": "1899-04-10", "time": "04:15", "cal": "J"}
packed = A.unpack_person(A.pack_person(d, A.birth_from(d)))
check("a reading together keeps the Old Style marker", packed.get("cal") == "J" and packed["date"] == "1899-04-10")
check("a reading together without it adds nothing", "cal" not in A.unpack_person(A.pack_person({**d, "cal": None}, new)))
check("a reading together keeps no marker that didn't apply",
      "cal" not in A.unpack_person(A.pack_person({**LON, "date": "1899-04-10", "time": "12:00", "cal": "J"},
                                                 A.birth_from({**LON, "date": "1899-04-10", "time": "12:00", "cal": "J"}))))
check("stored births keep it, with the country (members' charts, loved ones, clients, gifts)", "cal" in A.BIRTH_KEYS and "cc" in A.BIRTH_KEYS)
check("what's stored keeps it when it applied", A.keep_cal({}, A.birth_from(d)) == {"cal": "J", "cc": "RU"})
stale = {**LON, "date": "1899-04-10", "time": "12:00", "cal": "J"}
check("and drops it when it didn't", "cal" not in A.keep_cal(dict(stale), A.birth_from(stale)))
check("a reading with a marker that didn't apply shows no Old Style date",
      "Old Style (" not in A.render_reading(stale).get_data(as_text=True) and "1899-04-10 · 12:00" in text(A.render_reading(stale).get_data(as_text=True)))
check("an email's birth line shows both dates", "1899-04-10 Old Style (1899-04-22 New Style)" in A.birth_lines(d)[0])
page = A.render_reading(d).get_data(as_text=True)
check("the reading shows both dates", "1899-04-10 Old Style (1899-04-22 New Style)" in text(page))
num = lambda h, label: (re.search(rf"<td>{label}</td><td><b>(\d+)</b>", h) or [None, None])[1]
check("the reading's numbers count by the New Style day (life path 8, birthday 22, not 5 and 1)",
      (num(page, "Life path"), num(page, "Birthday")) == ("8", "22") == tuple(str(NUM.of("1899-04-22")[k]) for k in ("life_path", "birthday")))
together = A.render_together({"kind": "together", "people": "2", "p1": A.pack_person(d, A.birth_from(d)),
                              "p2": A.pack_person({**SPB, "name": "Other", "date": "1901-06-01", "time": "12:00"}, new)}).get_data(as_text=True)
check("a reading together shows the Old Style date", "(1899-04-10 Old Style)" in text(together))

# ---- the finder hands an Old Style date on to the full chart ----
r = c.post("/nakshatra-calculator", data={"date": "1899-04-10", "time": "04:15", "cal": "J", "lat": "59.9386", "lon": "30.3141",
                                         "tz": "Europe/Moscow", "place_label": "Saint Petersburg, Russia", "place_id": ""})
h = r.get_data(as_text=True)
check("the finder answers an Old Style birth", r.status_code == 200 and "Your Moon is in" in h)

# ---- the browser's table and converter agree with the server ----
js = open(os.path.join(HERE, "static", "common.js"), encoding="utf-8").read()
src = js[js.index("/* old-style helpers"):js.index("/* end of the old-style helpers */")]
table = open(os.path.join(HERE, "static", "old-style.json"), encoding="utf-8").read()
out = subprocess.run(["node", "-e", f"let OLD_STYLE = {table}.PLACES;\n" + src + """
const p = (cc, tz) => ({ cc, tz }), ru = p("RU", "Europe/Moscow");
console.log(JSON.stringify({
  ns: ["1870-04-10", "1900-02-28", "1900-03-01", "1918-01-31", "1867-10-06"].map(newStyle),
  ru1899: !!oldStyleAsk(ru, "1899-04-10"), ru1918: !!oldStyleAsk(ru, "1918-02-14"), ru1990: !!oldStyleAsk(ru, "1990-04-10"),
  gr1920: !!oldStyleAsk(p("GR", "Europe/Athens"), "1920-05-01"), fi1899: !!oldStyleAsk(p("FI", "Europe/Helsinki"), "1899-04-10"),
  us1899: !!oldStyleAsk(p("US", "America/New_York"), "1899-04-10"), ak1860: !!oldStyleAsk(p("US", "America/Sitka"), "1860-01-01"),
  kgd1899: !!oldStyleAsk(p("RU", "Europe/Kaliningrad"), "1899-04-10"), none: !!oldStyleAsk(null, "1899-04-10"),
  skipped: [oldStyleAsk(ru, "1918-02-05") && true, oldStyleFits(ru, "1918-02-05"), oldStyleFits(ru, "1918-01-31")],
  lastOS: julianDate(jdnOf("1918-02-14") - 1) }));"""], capture_output=True, text=True)
b = json.loads(out.stdout or "{}")
check("the browser converts as the server does",
      b.get("ns") == [OS.new_style({"date": x, "cal": "J"}) for x in ["1870-04-10", "1900-02-28", "1900-03-01", "1918-01-31", "1867-10-06"]])
check("the form asks for Russia in 1899 and Greece in 1920", b.get("ru1899") and b.get("gr1920"))
check("it stops asking on the day a country changed", b.get("ru1918") is False)
check("it doesn't ask where the Gregorian calendar was already kept (Finland, New York)", b.get("fi1899") is False and b.get("us1899") is False)
check("Russian Alaska is found by its time zone", b.get("ak1860") is True)
check("it doesn't ask for Russia in 1990, nor for Kaliningrad, nor with no place",
      b.get("ru1990") is False and b.get("kgd1899") is False and b.get("none") is False)
check("a day Russia skipped is asked about but can't be Old Style; its last Old Style day can", b.get("skipped") == [True, False, True])
check("the form names Russia's last Old Style day (31 January 1918)", b.get("lastOS") == "1918-01-31")
check("the server reads the same table: every row applies in 1850 and none after its change",
      all(OS.applies(r.get("cc", [None])[0], (r.get("tz") or ["Europe/X"])[0], "1850-06-01") is r
          and OS.applies(r.get("cc", [None])[0], (r.get("tz") or ["Europe/X"])[0], r["until"]) is None for r in OS.PLACES))

print("\nPASSED" if not bad else f"\n{bad} FAILED")
sys.exit(1 if bad else 0)
