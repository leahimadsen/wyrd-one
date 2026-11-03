"""Old Style dates: births recorded in the Julian calendar.

Russia, Greece, the Balkans, Turkey and a few others kept the old Julian calendar into the 1900s, so a birth
record of the time runs 12 days behind today's calendar (13 days from March 1900, when the Julian calendar kept
a leap day the Gregorian dropped). A chart cast from that date as written lands on the wrong day: the Moon some
160 degrees off, the Sun 12 degrees, every gate and mansion moved.

A birth whose `cal` is "J" is turned into its Gregorian (New Style) date before anything else touches it, so
the time zone, the ephemeris, the mansions and Sukuyo all see the one true day. The date as the record gives it
is kept for showing beside it, and the Stavefall numbers count that date: the date given, not the converted one.

Old Style applies only where and while the Julian calendar was kept: static/old-style.json lists the places
and the first Gregorian day in each. Outside that, a "J" is set aside and the date is read as New Style. Inside
it the choice is the person's, because modern sources often give the New Style date already. The forms read
the same table (common.js calendarChoice), so they only offer the choice where it can apply.
"""
import json, os
from datetime import date

PLACES = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "old-style.json"),
                        encoding="utf-8"))["PLACES"]

def region(cc, tz):
    """The row of old-style.json for a birthplace, or None where the Gregorian calendar was kept all along."""
    for r in PLACES:
        if (cc and cc in r.get("cc", ()) and tz not in r.get("notTz", ())) or (tz and tz in r.get("tz", ())):
            return r
    return None

def applies(cc, tz, new_style_date):
    """The row when a birth on this New Style day (YYYY-MM-DD) at this place fell in Julian-calendar years."""
    r = region(cc, tz)
    return r if r and new_style_date < r["until"] else None

def is_julian(d):
    return str((d or {}).get("cal", "")).strip().upper() in ("J", "JULIAN", "OS")

def julian_valid(y, m, d):
    """A real day of the Julian calendar, where every fourth year is a leap year (1900-02-29 included)."""
    if not 1 <= m <= 12 or d < 1: return False
    days = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return d <= days

def julian_day_number(y, m, d):
    """The Julian day number of a Julian-calendar date (Richards' algorithm)."""
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083

def to_gregorian(y, m, d):
    """The same day in the Gregorian calendar: (year, month, day)."""
    g = date.fromordinal(julian_day_number(y, m, d) - 1721425)
    return g.year, g.month, g.day

def new_style(meta):
    """The Gregorian date of a birth as YYYY-MM-DD, whichever calendar it was given in."""
    s = str((meta or {}).get("date", ""))
    if not is_julian(meta): return s
    try:
        y, m, d = (int(x) for x in s.split("-"))
        if not julian_valid(y, m, d): return s
        return "%04d-%02d-%02d" % to_gregorian(y, m, d)
    except ValueError:
        return s

def show(meta, long=False):
    """The birth date for a page or an email: as given, marked Old Style, with its New Style day when `long`."""
    s = str((meta or {}).get("date", ""))
    if not is_julian(meta): return s
    return f"{s} Old Style ({new_style(meta)} New Style)" if long else f"{s} O.S."
