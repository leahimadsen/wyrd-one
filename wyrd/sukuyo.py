"""Sukuyō (宿曜): the Japanese reading of the twenty-seven lunar mansions.

A person's birth shuku comes from the old Japanese lunisolar calendar, not from
the Moon's measured position: each lunar month opens on a fixed shuku, and the
shuku advances one per day of the month. So the work here is rebuilding that
calendar for any date:

  * months begin on the (Japan-time) day of each new moon
  * a month is numbered by the principal solar term (chūki) it contains:
    the month holding the winter solstice is the 11th
  * in a year with thirteen months, the first month without a chūki is the leap
    month and repeats the number before it

Then two people's shuku give their relation by the 三九の秘法 (sanku hihō)."""
import math
from datetime import date, timedelta
from functools import lru_cache

from . import engine as E

JST = 9 / 24
norm = E.norm

# the twenty-seven shuku, in order (the 28-mansion 牛 is left out, as in Sukuyō)
SHUKU = [("昴", "Bō", "Krittika"), ("畢", "Hitsu", "Rohini"), ("觜", "Shi", "Mrigashira"), ("参", "Shin", "Ardra"),
         ("井", "Sei", "Punarvasu"), ("鬼", "Ki", "Pushya"), ("柳", "Ryū", "Ashlesha"), ("星", "Sei", "Magha"),
         ("張", "Chō", "Purva Phalguni"), ("翼", "Yoku", "Uttara Phalguni"), ("軫", "Shin", "Hasta"), ("角", "Kaku", "Chitra"),
         ("亢", "Kō", "Swati"), ("氐", "Tei", "Vishakha"), ("房", "Bō", "Anuradha"), ("心", "Shin", "Jyeshtha"),
         ("尾", "Bi", "Mula"), ("箕", "Ki", "Purva Ashadha"), ("斗", "To", "Uttara Ashadha"), ("女", "Jo", "Shravana"),
         ("虚", "Kyo", "Dhanishta"), ("危", "Ki", "Shatabhisha"), ("室", "Shitsu", "Purva Bhadrapada"), ("壁", "Heki", "Uttara Bhadrapada"),
         ("奎", "Kei", "Revati"), ("婁", "Rō", "Ashwini"), ("胃", "I", "Bharani")]
IDX = {k: i for i, (k, _, _) in enumerate(SHUKU)}
# the shuku on which each lunar month opens (month 1 .. 12)
MONTH_START = [IDX[k] for k in ["室", "奎", "胃", "畢", "参", "鬼", "張", "角", "氐", "心", "斗", "虚"]]

# 三九の秘法: the relation of another's shuku to one's own, by how many shuku on it lies
RING = ["命", "栄", "衰", "安", "危", "成", "壊", "友", "親",
        "業", "栄", "衰", "安", "危", "成", "壊", "友", "親",
        "胎", "栄", "衰", "安", "危", "成", "壊", "友", "親"]
PAIR = {"命": "命", "業": "業胎", "胎": "業胎", "栄": "栄親", "親": "栄親", "友": "友衰", "衰": "友衰",
        "安": "安壊", "壊": "安壊", "危": "危成", "成": "危成"}
READ = {"命": "Mei", "業": "Gyō", "胎": "Tai", "栄": "Ei", "親": "Shin", "友": "Yū", "衰": "Sui",
        "安": "An", "壊": "Kai", "危": "Ki", "成": "Sei", "業胎": "Gyōtai", "栄親": "Eishin", "友衰": "Yūsui",
        "安壊": "Ankai", "危成": "Kisei"}
EN = {"命": "Life", "業": "Karma", "胎": "Womb", "栄": "Prosperity", "親": "Intimacy", "友": "Friendship", "衰": "Decline",
      "安": "Peace", "壊": "Destruction", "危": "Danger", "成": "Completion"}


def relation(a, b):
    """How b stands to a, and the pair they make. Distance is near, middle or far."""
    k = (b - a) % 27
    me, them = RING[k], RING[(a - b) % 27]
    m = min(k, 27 - k)
    dist = None if PAIR[me] in ("命", "業胎") else "near" if m <= 4 else "far" if m <= 8 else "middle"
    return {"pair": PAIR[me], "pairRead": READ[PAIR[me]], "toA": me, "toB": them, "distance": dist, "offset": k}


# ---------- the calendar ----------
def _jd_day(jd):
    """The Japan-time calendar date (as an ordinal) of an instant."""
    return math.floor(jd + JST + 0.5)


def _wrap(d):
    return (d + 540) % 360 - 180


def _sun_moon(eph, jds):
    """Sun and Moon longitudes for many instants: one vectorised call where the ephemeris allows."""
    many = getattr(eph, "positions_many", None)
    if many:
        try:
            return [p for p, _ in many(jds, bodies=("Sun", "Moon"))]
        except TypeError:
            return [p for p, _ in many(jds)]
    return [eph.positions(j) for j in jds]


@lru_cache(maxsize=64)
def _year_events(eph, jd_start, days):
    """New moons and solar-term (every 30° of the Sun) instants in a window: daily samples
    find the day, hourly samples inside it pin the instant to a minute or so."""
    jds = [jd_start + i for i in range(days + 1)]
    rows = _sun_moon(eph, jds)
    found = []                                                   # (kind, day index, degree)
    for i in range(days):
        a, b = rows[i], rows[i + 1]
        if _wrap(a["Moon"] - a["Sun"]) < 0 <= _wrap(b["Moon"] - b["Sun"]):
            found.append(("moon", i, 0))
        k0, k1 = int(a["Sun"] // 30), int(b["Sun"] // 30)
        if k0 != k1:
            found.append(("term", i, k1 * 30))
    hours = [jds[i] + h / 24 for _, i, _ in found for h in range(25)]
    fine = _sun_moon(eph, hours) if hours else []
    moons, terms = [], []
    for n, (kind, i, deg) in enumerate(found):
        seg = fine[n * 25:(n + 1) * 25]
        f = (lambda p: _wrap(p["Moon"] - p["Sun"])) if kind == "moon" else (lambda p, deg=deg: _wrap(p["Sun"] - deg))
        for h in range(24):
            f0, f1 = f(seg[h]), f(seg[h + 1])
            if f0 < 0 <= f1 or (f0 == 0):
                jd = jds[i] + (h + (-f0 / (f1 - f0) if f1 != f0 else 0)) / 24
                (moons if kind == "moon" else terms).append(jd if kind == "moon" else (jd, deg))
                break
    return moons, terms


def lunar_date(eph, y, m, d):
    """(month, day, leap) of the old Japanese calendar for a civil date."""
    target_day = date(y, m, d).toordinal() + 1721425                 # the civil day as a Julian day number
    moons, terms = _year_events(eph, target_day - 400.5, 800)        # far enough either side to hold two winter solstices
    starts = [_jd_day(j) for j in moons]                             # first day of each lunation
    # the chūki (principal solar terms: the Sun at a multiple of 30°) falling in each lunation
    chuki = []
    for i in range(len(starts) - 1):
        chuki.append([deg for jd, deg in terms if starts[i] <= _jd_day(jd) < starts[i + 1]])
    # the lunation holding the target
    li = max(i for i in range(len(starts) - 1) if starts[i] <= target_day)
    # month 11 holds the winter solstice (Sun at 270°); find the two around the target
    elevens = [i for i, c in enumerate(chuki) if 270 in c]
    prev11 = max(i for i in elevens if i <= li) if any(i <= li for i in elevens) else None
    if prev11 is None:
        raise ValueError("date outside the computed window")
    nxt = [i for i in elevens if i > prev11]
    leap_year = bool(nxt) and nxt[0] - prev11 == 13
    month, leap_used, label = 11, False, {}
    for i in range(prev11, (nxt[0] if nxt else len(chuki))):
        if i == prev11:
            label[i] = (11, False); continue
        if leap_year and not leap_used and not chuki[i]:
            label[i] = (month, True); leap_used = True; continue
        month = month % 12 + 1
        label[i] = (month, False)
    mo, leap = label[li]
    return mo, target_day - starts[li] + 1, leap


@lru_cache(maxsize=2048)
def birth_shuku(eph, y, m, d):
    mo, day, leap = lunar_date(eph, y, m, d)
    i = (MONTH_START[mo - 1] + day - 1) % 27
    k, read, nak = SHUKU[i]
    return {"index": i, "kanji": k, "read": read, "mansion": nak, "lunarMonth": mo, "lunarDay": day, "leap": leap}
