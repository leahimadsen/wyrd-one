"""Place search over data/places.db (built by scripts/build_places.py)."""
import os, re, sqlite3, threading, unicodedata

def normalise(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"\bsainte\b", "ste", s)
    return " ".join(s.split())

class Places:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} missing — run scripts/build_places.py")
        self.path = path
        self.local = threading.local()

    def _db(self):
        if not hasattr(self.local, "db"):
            self.local.db = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, check_same_thread=False)
        return self.local.db

    def get(self, pid):
        r = self._db().execute("SELECT id,name,region,country,cc,lat,lon,tz,pop FROM places WHERE id=?",
                               (int(pid),)).fetchone()
        return self._row(r) if r else None

    @staticmethod
    def _row(r):
        pid, name, region, country, cc, lat, lon, tz, pop = r[:9]
        label = ", ".join(x for x in [name, region, country] if x and x != name)
        return {"id": pid, "name": name, "region": region, "country": country, "cc": cc,
                "lat": lat, "lon": lon, "tz": tz, "pop": pop, "label": f"{name}, {label}" if label else name}

    def search(self, q, limit=10):
        parts = [p for p in (q or "").split(",")]
        head = normalise(parts[0])
        tail = [normalise(p) for p in parts[1:] if normalise(p)]
        if len(head) < 2: return []
        hi = head[:-1] + chr(ord(head[-1]) + 1)
        rows = self._db().execute("""
            SELECT p.id,p.name,p.region,p.country,p.cc,p.lat,p.lon,p.tz,p.pop,p.rkey,
                   MAX(n.key = ?) AS exact, MAX(n.primary_name) AS prim
            FROM names n JOIN places p ON p.id = n.pid
            WHERE n.key >= ? AND n.key < ?
            GROUP BY p.id
            ORDER BY exact DESC, p.pop DESC
            LIMIT 400""", (head, head, hi)).fetchall()
        out = []
        for r in rows:
            rkey = " " + r[9] + " "
            if all((" " + t) in rkey for t in tail):
                out.append(self._row(r))
                if len(out) >= limit: break
        return out
