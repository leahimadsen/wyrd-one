"""Data the free chart shows beside the cast: retrograde motion, the panchanga
of the birth day, and Placidus house cusps for comparison with whole signs.

Kept apart from engine.cast so the cast stays identical to the console's."""
import math
from datetime import date, timedelta

from . import engine as E
from . import sukuyo

D2R, R2D = math.pi / 180, 180 / math.pi
norm = E.norm

TITHI = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami",
         "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi"]
YOGA = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula",
        "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
KARANA_MOVING = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
VARA = [("Somavara", "Moon"), ("Mangalavara", "Mars"), ("Budhavara", "Mercury"), ("Guruvara", "Jupiter"),
        ("Shukravara", "Venus"), ("Shanivara", "Saturn"), ("Ravivara", "Sun")]   # Python weekday(): Monday = 0
NO_RETRO = ("Sun", "Moon")


def retrograde(eph, jd):
    """Bodies moving backwards at birth. The mean nodes always are."""
    now, later = eph.positions(jd), eph.positions(jd + 0.5)
    out = {}
    for b, l in now.items():
        if b in NO_RETRO:
            continue
        out[b] = (later[b] - l + 540) % 360 - 180 < 0
    return out


def _sunrise_jd(jd_local_noon_ut, lat, lon_e):
    """NOAA-style sunrise equation, good to a minute or two. None near the poles."""
    n = round(jd_local_noon_ut - 2451545.0 + lon_e / 360)
    j = n - lon_e / 360
    M = (357.5291 + 0.98560028 * j) % 360
    C = 1.9148 * math.sin(M * D2R) + 0.02 * math.sin(2 * M * D2R) + 0.0003 * math.sin(3 * M * D2R)
    lam = (M + C + 180 + 102.9372) % 360
    transit = 2451545.0 + j + 0.0053 * math.sin(M * D2R) - 0.0069 * math.sin(2 * lam * D2R)
    dec = math.asin(math.sin(lam * D2R) * math.sin(23.4397 * D2R))
    cw = (math.sin(-0.833 * D2R) - math.sin(lat * D2R) * math.sin(dec)) / (math.cos(lat * D2R) * math.cos(dec))
    if abs(cw) > 1:
        return None
    return transit - math.acos(cw) * R2D / 360


def panchanga(chart, birth):
    """The five limbs of the birth day. `birth` is app.birth_from()'s dict."""
    sun, moon = chart["sid"]["Sun"], chart["sid"]["Moon"]
    gap = norm(moon - sun)
    t = int(gap // 12)                       # 0..29
    paksha = "Shukla" if t < 15 else "Krishna"
    name = TITHI[t % 15] if t % 15 < 14 else ("Purnima" if t == 14 else "Amavasya")
    k = int(gap // 6)                        # 0..59
    karana = "Kimstughna" if k == 0 else KARANA_MOVING[(k - 1) % 7] if k < 57 else ["Shakuni", "Chatushpada", "Naga"][k - 57]
    yoga = YOGA[int(norm(sun + moon) // (360 / 27))]

    # the Vedic day runs sunrise to sunrise
    local_h = birth["hh"] + birth["mi"] / 60
    jd = chart["jd"]
    rise = _sunrise_jd(jd + (12 - local_h) / 24, chart["lat"], chart["lon"])
    day = date(birth["y"], birth["mo"], birth["d"])
    before_sunrise = rise is not None and jd < rise
    if before_sunrise:
        day -= timedelta(days=1)
    vara, lord = VARA[day.weekday()]
    sunrise_local = None
    if rise is not None:
        mins = round(((rise - jd) * 24 + local_h) * 60)
        sunrise_local = f"{(mins // 60) % 24:02d}:{mins % 60:02d}"
    return {"tithi": t + 1, "tithiName": name, "paksha": paksha, "yoga": yoga, "karana": karana,
            "vara": vara, "varaLord": lord, "beforeSunrise": before_sunrise, "sunrise": sunrise_local,
            "nakshatra": E.nak_of(moon)}


def placidus(chart):
    """Placidus cusps 1-12, tropical. None above the polar circles, where the system fails."""
    lat = chart["lat"]
    T = (chart["jd"] - 2451545.0) / 36525.0
    eps = (23.4392911 - 0.0130042 * T) * D2R
    mc = chart["mcT"] * D2R
    ramc = math.atan2(math.sin(mc) * math.cos(eps), math.cos(mc)) * R2D
    tlat = math.tan(lat * D2R)

    def cusp(offset, frac, above):
        ra = norm(ramc + offset)
        for _ in range(60):
            lam = math.atan2(math.sin(ra * D2R), math.cos(ra * D2R) * math.cos(eps))
            dec = math.asin(math.sin(eps) * math.sin(lam))
            x = tlat * math.tan(dec)
            if abs(x) > 1:
                return None
            ad = math.asin(x) * R2D                     # ascensional difference
            new = norm(ramc + frac * (90 + ad)) if above else norm(ramc + 180 - frac * (90 - ad))
            if abs((new - ra + 540) % 360 - 180) < 1e-7:
                break
            ra = new
        return norm(math.atan2(math.sin(ra * D2R), math.cos(ra * D2R) * math.cos(eps)) * R2D)

    c11, c12 = cusp(30, 1 / 3, True), cusp(60, 2 / 3, True)
    c2, c3 = cusp(120, 2 / 3, False), cusp(150, 1 / 3, False)
    if None in (c11, c12, c2, c3) or abs(lat) > 66:
        return None
    asc, mcT = chart["ascT"], chart["mcT"]
    first = [asc, c2, c3, norm(mcT + 180), norm(c11 + 180), norm(c12 + 180)]
    return first + [norm(c + 180) for c in first]


def placidus_house(cusps, lon):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if norm(lon - a) < norm(b - a):
            return i + 1
    return 12


def extras(eph, chart, birth):
    cusps = placidus(chart)
    try:
        shuku = sukuyo.birth_shuku(eph, birth["y"], birth["mo"], birth["d"])     # by the civil birth date
    except Exception:
        shuku = None
    return {
        "sukuyo": shuku,
        "retro": retrograde(eph, chart["jd"]),
        "panchanga": panchanga(chart, birth),
        "placidus": None if cusps is None else {
            "cusps": cusps,
            "houses": {b: placidus_house(cusps, l) for b, l in chart["trop"].items()},
        },
    }
