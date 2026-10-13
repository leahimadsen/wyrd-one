"""What's coming: a year of sky events, and the ones that touch a birth chart.

The sky is sampled once a day and events are placed by straight-line
interpolation between samples, which is good to well under a day for every
body but the Moon (which is left out)."""
from . import engine as E

norm = E.norm
SIGNS = E.SIGNS
INGRESS = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Uranus", "Neptune", "Pluto"]
STATIONS = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
# which aspects each slow mover is followed through, to which birth points
ASPECTS = {
    "Mars":    [(0, "conjunction")],
    "Jupiter": [(0, "conjunction"), (180, "opposition"), (90, "square"), (270, "square"), (120, "trine"), (240, "trine")],
    "Saturn":  [(0, "conjunction"), (180, "opposition"), (90, "square"), (270, "square")],
    "Rahu":    [(0, "conjunction")],
    "Ketu":    [(0, "conjunction")],
    "Uranus":  [(0, "conjunction"), (180, "opposition"), (90, "square"), (270, "square")],
    "Neptune": [(0, "conjunction"), (180, "opposition"), (90, "square"), (270, "square")],
    "Pluto":   [(0, "conjunction"), (180, "opposition"), (90, "square"), (270, "square")],
}
TARGETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]


def wrap(d):
    return (d + 540) % 360 - 180


def samples(eph, jd0, days):
    jds = [jd0 + i for i in range(days + 1)]
    many = getattr(eph, "positions_many", None)
    if many:
        try:
            rows = many(jds)
            return [(jd, {b: norm(l - ay) for b, l in p.items()}) for jd, (p, ay) in zip(jds, rows)]
        except Exception:
            pass
    out = []
    for jd in jds:
        p, ay = eph.positions(jd), eph.ayanamsa(jd)
        out.append((jd, {b: norm(l - ay) for b, l in p.items()}))
    return out


def _cross(f0, f1, jd0):
    """jd where a quantity going f0 -> f1 over one day passes zero."""
    return jd0 + f0 / (f0 - f1) if f0 != f1 else jd0


def sky_events(S):
    """Sign ingresses (sidereal) and retrograde / direct stations."""
    ev = []
    for (j0, a), (j1, b) in zip(S, S[1:]):
        for body in INGRESS:
            s0, s1 = int(a[body] // 30), int(b[body] // 30)
            if s0 != s1:
                step = wrap(b[body] - a[body])
                edge = s1 * 30 if step > 0 else s0 * 30
                jd = _cross(wrap(a[body] - edge), wrap(b[body] - edge), j0)
                ev.append({"jd": jd, "kind": "ingress", "body": body, "sign": SIGNS[s1], "retro": step < 0})
                if body == "Rahu":
                    ev.append({"jd": jd, "kind": "ingress", "body": "Ketu", "sign": SIGNS[(s1 + 6) % 12], "retro": True})
    for body in STATIONS:
        for k in range(1, len(S) - 1):
            m0 = wrap(S[k][1][body] - S[k - 1][1][body]); m1 = wrap(S[k + 1][1][body] - S[k][1][body])
            if (m0 < 0) != (m1 < 0):
                ev.append({"jd": S[k][0], "kind": "station", "body": body, "turns": "retrograde" if m1 < 0 else "direct",
                           "sign": SIGNS[int(S[k][1][body] // 30)]})
    return ev


def natal_events(S, chart):
    ev = []
    pts = {b: chart["sid"][b] for b in TARGETS}
    if not chart.get("unknownTime"):
        pts["Ascendant"], pts["Midheaven"] = chart["ascS"], chart["mcS"]
    for body, asp in ASPECTS.items():
        for name, lon in pts.items():
            if name == body and body in ("Rahu", "Ketu"):
                continue
            for ang, aname in asp:
                for (j0, a), (j1, b) in zip(S, S[1:]):
                    f0, f1 = wrap(a[body] - lon - ang), wrap(b[body] - lon - ang)
                    if (f0 <= 0 < f1 or f1 <= 0 < f0) and abs(f0 - f1) < 10:
                        ev.append({"jd": _cross(f0, f1, j0), "kind": "transit", "body": body, "aspect": aname, "to": name,
                                   "retro": wrap(b[body] - a[body]) < 0})
    return ev


def sade_sati(sky, chart):
    """Saturn's seven and a half years over the birth Moon: entering the sign before it, the sign itself, the sign after, and leaving."""
    moon_sign = int(chart["sid"]["Moon"] // 30)
    out = []
    for e in sky:
        if e["kind"] == "ingress" and e["body"] == "Saturn":
            s = SIGNS.index(e["sign"]); rel = (s - moon_sign) % 12
            if rel == 11 and not e["retro"]: out.append({**e, "kind": "sadesati", "phase": "begins"})
            elif rel == 2 and not e["retro"]: out.append({**e, "kind": "sadesati", "phase": "ends"})
            elif rel in (0, 1) and not e["retro"]: out.append({**e, "kind": "sadesati", "phase": "deepens"})
    return out


TRACK = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]


def track(S, ay):
    """The daily sky as plain numbers, for the chart page to scrub through the year:
    each body's sidereal longitude at 0h UT on each day, to a hundredth of a degree.
    One ayanamsa serves the year (it moves about 0.014° in that time)."""
    return {"start": S[0][0], "ay": round(ay, 4),
            "lon": {b: [round(p[b], 2) for _, p in S] for b in TRACK}}


def year_for(eph, chart, jd0, days=365, S=None):
    if S is None:
        S = samples(eph, jd0, days)
    sky = sky_events(S)
    ev = sky + natal_events(S, chart) + sade_sati(sky, chart)
    ev.sort(key=lambda e: e["jd"])
    return ev


def today(eph, jd):
    """The sky now, for the public Today page: every body, plus the next 30 days of events."""
    p, later, ay = eph.positions(jd), eph.positions(jd + 0.5), eph.ayanamsa(jd)
    rows = []
    for b in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
        sid = norm(p[b] - ay); g = E.gate_of(p[b])
        rows.append({"body": b, "sid": sid, "trop": p[b], "nak": E.nak_of(sid), "gate": g["gate"], "line": g["line"],
                     "retro": b not in ("Sun", "Moon") and wrap(later[b] - p[b]) < 0})
    sun, moon = norm(p["Sun"] - ay), norm(p["Moon"] - ay)
    gap = norm(moon - sun); t = int(gap // 12)
    from .extras import TITHI, YOGA, KARANA_MOVING
    k = int(gap // 6)
    karana = "Kimstughna" if k == 0 else KARANA_MOVING[(k - 1) % 7] if k < 57 else ["Shakuni", "Chatushpada", "Naga"][k - 57]
    panch = {"tithi": t + 1, "paksha": "Shukla" if t < 15 else "Krishna",
             "tithiName": TITHI[t % 15] if t % 15 < 14 else ("Purnima" if t == 14 else "Amavasya"),
             "yoga": YOGA[int(norm(sun + moon) // (360 / 27))], "karana": karana, "phase": gap}
    upcoming = [e for e in sky_events(samples(eph, jd, 30))]
    return {"jd": jd, "ay": ay, "rows": rows, "panchanga": panch, "upcoming": upcoming}
