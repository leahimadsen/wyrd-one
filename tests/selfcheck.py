"""Run on the server after deploy:  python tests/selfcheck.py
Checks Skyfield/DE440 against the console's own (approximate) ephemeris.
Agreement within the console's known error proves frames, time scales and
ayanamsa are wired correctly; a frame or time-scale mistake shows up as
degrees, not arcminutes."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd.ephemeris import Ephemeris
import config

TOL = {"Sun": .02, "Moon": .1, "Mercury": .05, "Venus": .05, "Mars": .05, "Jupiter": .2,
       "Saturn": .3, "Uranus": .1, "Neptune": .1, "Pluto": .1, "Rahu": .02, "Ketu": .02}
ref = json.load(open(os.path.join(os.path.dirname(__file__), "reference_positions.json")))
eph = Ephemeris(config.DATA_DIR, config.EPHEMERIS_FILE)
d = lambda a, b: abs((a - b + 180) % 360 - 180)
bad = 0
for r in ref:
    jd = r["jd"]; p = eph.positions(jd)
    for b, tol in TOL.items():
        if d(p[b], r["positions"][b]) > tol: bad += 1; print(f"  {r['input'][:3]} {b}: {p[b]:.4f} vs {r['positions'][b]:.4f}")
    ay = eph.ayanamsa(jd)
    if abs(ay - r["ayanamsa"]) > 0.02: bad += 1; print(f"  ayanamsa {ay:.5f} vs {r['ayanamsa']:.5f}")
    a, m = eph.angles(jd, r["input"][4], r["input"][5])
    if d(a, r["asc"]) > .1 or d(m, r["mc"]) > .1: bad += 1; print(f"  angles {a:.3f},{m:.3f} vs {r['asc']:.3f},{r['mc']:.3f}")
ay2000 = eph.ayanamsa(2451545.0)
print(f"Lahiri at J2000: {ay2000:.5f} deg (expected about 23.857)")
if abs(ay2000 - 23.857) > 0.01: bad += 1
print("SELF-CHECK", "PASSED" if not bad else f"FAILED ({bad} problems)")
sys.exit(1 if bad else 0)
