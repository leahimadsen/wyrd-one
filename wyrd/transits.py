"""Today's sky laid over the natal chart.

For every moving body: which natal house it is crossing (whole sign from the
sidereal Ascendant), which gate and line it is in, whether that is a gate the
person carries, what natal points it sits on, and whether it is retrograde.
All facts; the client names them with the house colours and gate titles."""
from . import engine as E

ORB = {"Sun": 2.0, "Moon": 4.0, "Mercury": 2.0, "Venus": 2.0, "Mars": 2.0, "Jupiter": 2.5,
       "Saturn": 2.5, "Uranus": 2.0, "Neptune": 2.0, "Pluto": 2.0, "Rahu": 1.5, "Ketu": 1.5}
MOVING = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Rahu", "Ketu"]

def _sep(a, b):
    return abs((a - b + 180) % 360 - 180)

def transits(eph, chart, now_jd):
    ay = eph.ayanamsa(now_jd)
    trop = eph.positions(now_jd)
    later = eph.positions(now_jd + 0.5)
    sid = {b: E.norm(l - ay) for b, l in trop.items()}

    carried = {}                      # gate -> what in the natal chart holds it (the dharma layer stays in the paid reading)
    for side in ("personality", "design"):
        for body, g in chart["natal"][side].items():
            carried.setdefault(g["gate"], []).append(f"{side} {body}")

    points = dict(chart["sid"]); points["Ascendant"] = chart["ascS"]; points["Midheaven"] = chart["mcS"]
    natal_moon_sign = int(E.norm(chart["sid"]["Moon"]) // 30)
    moon_nak = E.nak_index(chart["sid"]["Moon"])

    rows = []
    for b in MOVING:
        g = E.gate_of(trop[b])
        motion = (later[b] - trop[b] + 540) % 360 - 180
        hits = [{"point": p, "orb": round(_sep(sid[b], l), 2)}
                for p, l in points.items() if _sep(sid[b], l) <= ORB[b] and not (p == b and b in ("Rahu", "Ketu"))]
        hits.sort(key=lambda h: h["orb"])
        rows.append({
            "body": b, "trop": trop[b], "sid": sid[b],
            "house": E.house_of(sid[b], chart["ascS"]),
            "gate": g["gate"], "line": g["line"],
            "carried": carried.get(g["gate"], []),
            "on": hits,
            "retro": bool(b not in ("Sun", "Moon", "Rahu", "Ketu") and motion < 0),
            "inMoonMansion": E.nak_index(sid[b]) == moon_nak,
        })
    sat_from_moon = (int(E.norm(sid["Saturn"]) // 30) - natal_moon_sign) % 12 + 1
    return {"jd": now_jd, "ay": ay, "rows": rows,
            "sadeSati": sat_from_moon in (12, 1, 2), "saturnFromMoon": sat_from_moon}
