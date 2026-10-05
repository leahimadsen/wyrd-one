"""Build data/places.db from GeoNames (free, CC BY 4.0 — credit "GeoNames" on the site).

    python scripts/build_places.py            # downloads cities500 (~10 MB zip), builds the index
    python scripts/build_places.py --src DIR  # use files already downloaded into DIR

cities500 = every populated place on Earth with 500+ people, plus every
administrative seat — about 200,000 places, each with its IANA time zone.
Alternate names (Bombay, München, Saint Louis...) are indexed too."""
import argparse, io, os, re, sqlite3, sys, unicodedata, urllib.request, zipfile

GEO = "https://download.geonames.org/export/dump/"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from wyrd.places import normalise

def fetch(src, name):
    path = os.path.join(src, name)
    if os.path.exists(path): return path
    url = GEO + (name.replace(".txt", ".zip") if name.startswith("cities") else name)
    print("downloading", url)
    data = urllib.request.urlopen(url, timeout=120).read()
    if url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z: z.extract(name, src)
    else:
        open(path, "wb").write(data)
    return path

LATIN = re.compile(r"^[A-Za-z0-9 .,'’()\-]+$")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(HERE, "data", "geonames"))
    ap.add_argument("--cities", default="cities500.txt")
    ap.add_argument("--out", default=os.path.join(HERE, "data", "places.db"))
    a = ap.parse_args()
    os.makedirs(a.src, exist_ok=True)

    countries = {}
    for line in open(fetch(a.src, "countryInfo.txt"), encoding="utf-8"):
        if line.startswith("#"): continue
        f = line.rstrip("\n").split("\t")
        if len(f) > 4: countries[f[0]] = f[4]
    admin1 = {}
    for line in open(fetch(a.src, "admin1CodesASCII.txt"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 1: admin1[f[0]] = f[1]

    tmp = a.out + ".tmp"
    if os.path.exists(tmp): os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.executescript("""
      CREATE TABLE places(id INTEGER PRIMARY KEY, name TEXT, region TEXT, country TEXT, cc TEXT,
                          lat REAL, lon REAL, tz TEXT, pop INTEGER, rkey TEXT);
      CREATE TABLE names(key TEXT, pid INTEGER, primary_name INTEGER);""")
    n = 0
    for line in open(fetch(a.src, a.cities), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 19 or not f[17]: continue
        gid, name, ascii_, alts = int(f[0]), f[1], f[2], f[3]
        cc, a1, pop, tz = f[8], f[10], int(f[14] or 0), f[17]
        region = admin1.get(f"{cc}.{a1}", "")
        country = countries.get(cc, cc)
        rkey = normalise(" ".join([region, country, cc, a1]))
        db.execute("INSERT INTO places VALUES(?,?,?,?,?,?,?,?,?,?)",
                   (gid, name, region, country, cc, float(f[4]), float(f[5]), tz, pop, rkey))
        keys = {normalise(name): 1, normalise(ascii_): 1}
        for alt in alts.split(",")[:60]:
            alt = alt.strip()
            if len(alt) > 3 and LATIN.match(alt) and not alt.isupper():
                keys.setdefault(normalise(alt), 0)
        for k, prim in keys.items():
            if k: db.execute("INSERT INTO names VALUES(?,?,?)", (k, gid, prim))
        n += 1
    db.execute("CREATE INDEX names_key ON names(key)")
    db.commit(); db.execute("VACUUM"); db.close()
    os.replace(tmp, a.out)
    print(f"{n} places indexed -> {a.out}")

if __name__ == "__main__":
    main()
