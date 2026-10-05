"""Local birth time -> UT, using the IANA zone of the birthplace and the
offset in force at that instant (historical DST and all)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def to_ut(y, mo, d, hh, mi, tz):
    local = datetime(y, mo, d, hh, mi, tzinfo=ZoneInfo(tz))
    u = local.astimezone(timezone.utc)
    offset_min = round(local.utcoffset().total_seconds() / 60)
    return {"y": u.year, "mo": u.month, "d": u.day,
            "h": u.hour + u.minute / 60 + u.second / 3600,
            "offset_min": offset_min,
            "label": f"UTC{'+' if offset_min >= 0 else '-'}{abs(offset_min)//60:02d}:{abs(offset_min)%60:02d}"}
