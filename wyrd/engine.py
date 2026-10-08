"""
The Wyrd engine — a line-for-line port of the console's cast() pipeline.

The ephemeris is injected (see ephemeris.py), so this file holds only the
doctrine: tropical gate wheel, sidereal mansions and houses, ayanamsa
restored before the x9 so the 88 degree arc cancels exactly, seven karakas,
Vimshottari from the Moon. tests/verify_engine.py proves it matches the
console's JavaScript output for the same planet positions.
"""
import math

def norm(d):
    return ((d % 360) + 360) % 360

def julian_day(y, m, d, h_ut):
    if m <= 2:
        y -= 1; m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5 + h_ut / 24

# ---- the gate wheel: gate 41 opens at 02 Aquarius (302 tropical) ----
GATE_ORDER = [41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,27,24,2,23,
              8,20,16,35,45,12,15,52,39,53,62,56,31,33,7,4,29,59,40,64,
              47,6,46,18,48,57,32,50,28,44,1,43,14,34,9,5,26,11,10,58,
              38,54,61,60]
GATE_START = 302
GATE_ARC = 360 / 64
LINE_ARC = GATE_ARC / 6

def gate_of(trop_lon):
    off = norm(trop_lon - GATE_START)
    gi = math.floor(off / GATE_ARC)
    within = off - gi * GATE_ARC
    line = math.floor(within / LINE_ARC) + 1
    return {"gate": GATE_ORDER[gi], "line": line, "intoLine": within - (line - 1) * LINE_ARC}

def D9(sid):
    return norm(9 * sid)

def varga(sid, n):
    return norm(n * sid)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAK = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
       "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
       "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
       "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
       "Uttara Bhadrapada","Revati"]
NAK_ARC = 360 / 27

def sign_of(l):   return SIGNS[math.floor(norm(l) / 30)]
def deg_in(l):    return norm(l) % 30
def nak_of(l):    return NAK[math.floor(norm(l) / (360 / 27))]
def nak_index(l): return math.floor(norm(l) / NAK_ARC)
def house_of(l, asc):
    return ((math.floor(norm(l) / 30) - math.floor(norm(asc) / 30) + 12) % 12) + 1

# ---- Vimshottari ----
DASHA = [["Ketu",7],["Venus",20],["Sun",6],["Moon",10],["Mars",7],
         ["Rahu",18],["Jupiter",16],["Saturn",19],["Mercury",17]]
YEAR = 365.2425

def vimshottari(moon_sid, jd_birth, jd_now):
    span = 360 / 27
    idx = math.floor(norm(moon_sid) / span)
    frac = (norm(moon_sid) % span) / span
    start = idx % 9
    elapsed = DASHA[start][1] * frac
    t = (jd_now - jd_birth) / 365.2425 + elapsed
    i = start
    while t >= DASHA[i][1]:
        t -= DASHA[i][1]; i = (i + 1) % 9
    maha, maha_yrs = DASHA[i]
    a, at = i, t
    while True:
        sub = maha_yrs * DASHA[a][1] / 120
        if at < sub: break
        at -= sub; a = (a + 1) % 9
    return {"maha": maha, "antar": DASHA[a][0], "into": t}

def sub_periods(lord, frm, years):
    i = next(k for k, d in enumerate(DASHA) if d[0] == lord)
    out, c = [], frm
    for k in range(9):
        l, y = DASHA[(i + k) % 9]
        ln = years * y / 120
        out.append({"lord": l, "from": c, "to": c + ln * YEAR, "years": ln})
        c += ln * YEAR
    return out

def dasha_tree(chart, now):
    moon = chart["sid"]["Moon"]
    moon_nak = math.floor(norm(moon) / NAK_ARC)
    through = (norm(moon) % NAK_ARC) / NAK_ARC
    first = DASHA[moon_nak % 9]
    balance = first[1] * (1 - through)
    maha = []
    c = chart["jd"] + balance * YEAR
    maha.append({"lord": first[0], "years": first[1], "from": chart["jd"] - first[1] * through * YEAR,
                 "to": c, "partial": True, "elapsedAtBirth": first[1] * through})
    i = next(k for k, d in enumerate(DASHA) if d[0] == first[0])
    for k in range(1, 10):
        l, y = DASHA[(i + k) % 9]
        maha.append({"lord": l, "years": y, "from": c, "to": c + y * YEAR}); c += y * YEAR
    def mark(rows):
        for r in rows:
            r["now"] = r["from"] <= now < r["to"]; r["past"] = now >= r["to"]
        return next((r for r in rows if r["now"]), rows[0])
    cur = mark(maha)
    antars = sub_periods(cur["lord"], cur["from"], cur["years"]); curA = mark(antars)
    praty = sub_periods(curA["lord"], curA["from"], curA["years"]); curP = mark(praty)
    return {"moonNak": moon_nak, "through": through, "balance": balance, "maha": maha,
            "antars": antars, "praty": praty, "cur": cur, "curA": curA, "curP": curP, "now": now}

# ---- karakas: seven, by decision. No Rahu, no Pitrikaraka. ----
KARAKA7 = ["Atmakaraka","Amatyakaraka","Bhratrikaraka","Matrikaraka",
           "Putrakaraka","Gnatikaraka","Darakaraka"]

def karakas(sid):
    rows = [{"body": k, "deg": deg_in(sid[k])}
            for k in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]]
    rows.sort(key=lambda r: -r["deg"])     # stable, like the console's sort
    return {KARAKA7[i]: r["body"] for i, r in enumerate(rows) if i < 7}

# ---- gate -> mansion ----
def gate_span(gate):
    if gate not in GATE_ORDER: return None
    a = norm(302 + GATE_ORDER.index(gate) * 5.625)
    return {"start": a, "end": norm(a + 5.625)}

def gate_mansion(gate, line):
    s = gate_span(gate)
    if not s: return None
    arc = 5.625 / 6
    lo = norm(s["start"] + (line - 1) * arc)
    hi = norm(lo + arc)
    a, b = nak_index(lo), nak_index(hi - 1e-9)
    return {"primary": a, "secondary": None if a == b else b, "seam": a != b}

BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
RAVE = BODIES + ["Rahu","Ketu"]

def design_jd(eph, jd_birth):
    target = norm(eph.sun_lon(jd_birth) - 88)
    jd = jd_birth - 88.5
    for _ in range(40):
        d = eph.sun_lon(jd) - target
        if d > 180: d -= 360
        if d < -180: d += 360
        if abs(d) < 1e-8: break
        jd -= d / 0.9856473
    return jd

def cast(eph, y, mo, d, h_ut, lat, lon_e, now_jd=None):
    jd = julian_day(y, mo, d, h_ut)
    ay = eph.ayanamsa(jd)
    trop = eph.positions(jd)
    sid = {k: norm(v - ay) for k, v in trop.items()}

    ascT, mcT = eph.angles(jd, lat, lon_e)
    ascS, mcS = norm(ascT - ay), norm(mcT - ay)

    # incarnate rave
    jd_des = design_jd(eph, jd)
    trop_des = eph.positions(jd_des)
    natal = {"personality": {b: gate_of(trop[b]) for b in RAVE},
             "design":      {b: gate_of(trop_des[b]) for b in RAVE}}
    natal["personality"]["Earth"] = gate_of(norm(trop["Sun"] + 180))
    natal["design"]["Earth"]      = gate_of(norm(trop_des["Sun"] + 180))
    natal["profile"] = f'{natal["personality"]["Sun"]["line"]}/{natal["design"]["Sun"]["line"]}'

    # dharma rave: the D9 of the TROPICAL positions at both moments, as the current console
    # casts it. The two Suns sit 88 deg apart, x9 = 792 deg, less two circles = 72 deg exactly.
    d9p = {b: D9(trop[b]) for b in RAVE}
    d9d = {b: D9(trop_des[b]) for b in RAVE}
    dharma = {"personality": {b: gate_of(l) for b, l in d9p.items()},
              "design":      {b: gate_of(l) for b, l in d9d.items()},
              "lonP": d9p, "lonD": d9d}
    dharma["personality"]["Earth"] = gate_of(norm(d9p["Sun"] + 180))
    dharma["design"]["Earth"]      = gate_of(norm(d9d["Sun"] + 180))
    dharma["profile"] = f'{dharma["personality"]["Sun"]["line"]}/{dharma["design"]["Sun"]["line"]}'

    # the Pentagram Cross: the two dharma Suns sit 72 apart
    gap = norm(d9p["Sun"] - d9d["Sun"])
    dharma["suns"] = {"p": d9p["Sun"], "d": d9d["Sun"], "gap": gap, "holds": abs(gap - 72) < 0.02}

    # seam or echo: the LAST 11.25 arcminutes of the line decides it
    into = dharma["personality"]["Sun"]["intoLine"]
    dharma["band"] = "Echo" if into > LINE_ARC - 0.1875 else "Seam"
    dharma["mauve"] = dharma["profile"] == "6/1"

    nav = {b: varga(sid[b], 9) for b in RAVE}
    return {
        "jd": jd, "jdDes": jd_des, "ay": ay, "tropDes": trop_des,
        "trop": trop, "sid": sid, "nav": nav, "navAsc": varga(ascS, 9),
        "ascT": ascT, "ascS": ascS, "mcT": mcT, "mcS": mcS,
        "natal": natal, "dharma": dharma,
        "karaka": karakas(sid),
        "dasha": vimshottari(sid["Moon"], jd, now_jd or jd),
        "moonNak": nak_of(sid["Moon"]),
        "lat": lat, "lon": lon_e,
    }
