"""Now and next, the colour room and the bench: the year's daily sky the chart page scrubs
through is right, the calendar's events are unchanged by sharing it, and the page loads
the new rooms (and not the old ones).

    WYRD_DEV_NODE_EPH=1 python tests/now_check.py      (no Skyfield needed)
"""
import os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ["WYRD_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "wyrd.db")
import app as A
from wyrd import calendar as wcal

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

BIRTH = {"name": "Sample", "date": "1988-07-22", "time": "14:30", "lat": 40.7128, "lon": -74.006,
         "tz": "America/New_York", "place_label": "New York, United States"}
c = A.app.test_client()
r = c.post("/api/calendar", json=BIRTH)
check("the calendar answers", r.status_code == 200)
j = r.get_json()
T = j.get("track") or {}
check("it carries the year's track", set(T) == {"start", "ay", "lon"} and T["start"] == j["start"])
check("twelve bodies, a position for every day of the year and one more", sorted(T["lon"]) == sorted(wcal.TRACK) and all(len(v) == 367 for v in T["lon"].values()))
check("every position is a longitude", all(0 <= x < 360 for v in T["lon"].values() for x in v))

# the track is the sky: compare a few days with the ephemeris directly
worst = 0
for d in (0, 1, 120, 250, 366):
    jd = j["start"] + d
    p, ay = A.EPH.positions(jd), A.EPH.ayanamsa(jd)
    for b in wcal.TRACK:
        worst = max(worst, abs((p[b] - ay - T["lon"][b][d] + 540) % 360 - 180))
check(f"the track agrees with the ephemeris (worst {worst:.4f}°)", worst < 0.006)
check("one ayanamsa serves the year", abs(T["ay"] - A.EPH.ayanamsa(j["start"])) < 1e-3)

# sharing the day's samples changes nothing in the events
chart = A.cast_for(A.birth_from(BIRTH))
alone = A.plain(wcal.year_for(A.EPH, chart, j["start"]))
check("the events are the same as working the year out alone", len(alone) == len(j["events"]) and
      all(a["kind"] == b["kind"] and abs(a["jd"] - b["jd"]) < 1e-6 for a, b in zip(alone, j["events"])))
check("and they stay inside the year", all(j["start"] <= e["jd"] <= j["start"] + 366 for e in j["events"]))

# the page builds its retrograde lanes from the stations: they must alternate
ok = True
for body in wcal.STATIONS:
    turns = [e["turns"] for e in j["events"] if e["kind"] == "station" and e["body"] == body]
    ok &= all(a != b for a, b in zip(turns, turns[1:]))
check("each planet's stations alternate retrograde and direct", ok)
check("a second asking is answered from the cache, the same", c.post("/api/calendar", json=BIRTH).get_json() == j)

# the chart page loads the new rooms, not the old ones
page = open(os.path.join(ROOT, "static", "chart.html"), encoding="utf-8").read()
check("the chart page loads now.js, colour.js and bench.js", all(f'src="/static/{f}"' in page for f in ("now.js", "colour.js", "bench.js")))
check("and no longer transits.js or lands.js", "transits.js" not in page and "lands.js" not in page)
check("and the rooms' stylesheet", 'href="/static/rooms.css"' in page)
check("Now and next has its hosts", 'id="nowHost"' in page and 'id="calHost"' in page and 'id="coming"' in page)
sw = open(os.path.join(ROOT, "static", "sw.js"), encoding="utf-8").read()
check("the offline copy knows the new files", all(f"/static/{f}" in sw for f in ("now.js", "colour.js", "bench.js", "rooms.css")))
check("and drops the old ones", "transits.js" not in sw and "lands.js" not in sw)
js = open(os.path.join(ROOT, "static", "chart.js"), encoding="utf-8").read()
check("the rooms are built from the new modules", "WyrdNow.mount" in js and "WyrdColour.mount" in js and "WyrdBench.mount" in js)

# the new modules keep to their own click attributes, so viz.js's old handlers never catch them
OLD = ("data-hue", "data-graha", "data-house", "data-jump", "data-bench", "data-sound-pair", "data-bench-live", "data-tr", "data-f")
for f in ("now.js", "colour.js", "bench.js"):
    src = open(os.path.join(ROOT, "static", f), encoding="utf-8").read()
    # an attribute written into markup (a space before it), not a selector reaching the lab's own buttons
    check(f"{f} writes none of the old click attributes", not any(re.search(r"\s" + re.escape(a) + r"(?=[=\s>])", src) for a in OLD))
if shutil.which("node"):
    for f in ("now.js", "colour.js", "bench.js", "viz.js", "chart.js"):
        check(f"{f} parses", subprocess.run(["node", "--check", os.path.join(ROOT, "static", f)], capture_output=True).returncode == 0)

print("\nall good" if not bad else f"\n{bad} failed")
sys.exit(1 if bad else 0)
