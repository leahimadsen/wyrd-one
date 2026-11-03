"""Old Style dates: a birth recorded in the Julian calendar is cast for its true day.

The conversion matches births whose two dates history gives; an Old Style birth casts exactly the sky of its
New Style day; the marker survives every route a birth travels (checkout, readings together, stored births,
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
SPB = {"lat": 59.9386, "lon": 30.3141, "tz": "Europe/Moscow", "place_label": "Saint Petersburg, Russia", "place_id": None}
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
check("stored births keep it (members' charts, loved ones, clients, gifts)", "cal" in A.BIRTH_KEYS)
check("the checkout keeps it", A.keep_cal({}, d) == {"cal": "J"} and A.keep_cal({}, {**d, "cal": ""}) == {})
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
src = js[js.index("const OLD_STYLE"):js.index("/* The calendar choice")]
out = subprocess.run(["node", "-e", src + """
const p = (cc, tz) => ({ cc, tz });
console.log(JSON.stringify({
  ns: ["1870-04-10", "1900-02-28", "1900-03-01", "1918-01-31", "1867-10-06"].map(newStyle),
  ru1899: !!oldStyleFor(p("RU", "Europe/Moscow"), "1899-04-10"), ru1918: !!oldStyleFor(p("RU", "Europe/Moscow"), "1918-02-14"),
  gr1920: !!oldStyleFor(p("GR", "Europe/Athens"), "1920-05-01"), fi1899: !!oldStyleFor(p("FI", "Europe/Helsinki"), "1899-04-10"),
  us1899: !!oldStyleFor(p("US", "America/New_York"), "1899-04-10"), ak1860: !!oldStyleFor(p("US", "America/Sitka"), "1860-01-01"),
  none: oldStyleFor(null, "1899-04-10") }));"""], capture_output=True, text=True)
b = json.loads(out.stdout or "{}")
check("the browser converts as the server does",
      b.get("ns") == [OS.new_style({"date": x, "cal": "J"}) for x in ["1870-04-10", "1900-02-28", "1900-03-01", "1918-01-31", "1867-10-06"]])
check("the form asks for Russia in 1899 and Greece in 1920", b.get("ru1899") and b.get("gr1920"))
check("it stops asking on the day a country changed", b.get("ru1918") is False)
check("it doesn't ask where the Gregorian calendar was already kept (Finland, New York)", b.get("fi1899") is False and b.get("us1899") is False)
check("Russian Alaska is found by its time zone", b.get("ak1860") is True)

print("\nPASSED" if not bad else f"\n{bad} FAILED")
sys.exit(1 if bad else 0)
