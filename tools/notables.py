"""Work out the sky of every person in lib/notables.json and write it back into the file.

    python tools/notables.py

Uses the console's own ephemeris (lib/engine.js, through Node), which runs for any date in history.
For each person it finds, over their local birth day widened by two hours either side:
  sun      the sidereal (Lahiri) sign of the Sun
  sun_nak  the lunar mansion the Sun stood in, when it held one mansion all day
  trop     the tropical sign of the Sun, the one most people know as their "star sign"
  moon     the sidereal sign of the Moon, only when it held one sign all day
A field is left out when the day itself decides it, or when the person is marked 'unsure'.
"""
import json, os, subprocess

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(HERE, "lib", "notables.json")
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKS = [n[0] for n in json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))["NAKSHATRA"]]
MARGIN = 2 / 24          # two hours either side of the local day


def jd(y, m, d, cal):
    """Julian day at 0h UT of a calendar date, Julian ('J') or Gregorian ('G')."""
    if m <= 2: y, m = y - 1, m + 12
    b = 0 if cal == "J" else 2 - y // 100 + (y // 100) // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


class Console:
    def __init__(self):
        self.p = subprocess.Popen(["node", os.path.join(HERE, "tests", "node_eph.js")], cwd=os.path.join(HERE, "tests"),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def ask(self, f, j):
        self.p.stdin.write(json.dumps({"f": f, "jd": j}) + "\n"); self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())

    def at(self, j):
        p, a = self.ask("positions", j), self.ask("ay", j)
        return {"sun_t": p["Sun"] % 360, "sun_s": (p["Sun"] - a) % 360, "moon_s": (p["Moon"] - a) % 360}

    def close(self):
        self.p.stdin.close(); self.p.wait()


def sky(eng, person):
    y, m, d = person["born"]
    start = jd(y, m, d, person["cal"]) - person["utc"] / 24        # local midnight, in UT
    lo, hi = eng.at(start - MARGIN), eng.at(start + 1 + MARGIN)
    same = lambda k, size: int(lo[k] // size) == int(hi[k] // size)
    out = {}
    if same("sun_s", 30): out["sun"] = SIGNS[int(lo["sun_s"] // 30)]
    if same("sun_t", 30): out["trop"] = SIGNS[int(lo["sun_t"] // 30)]
    if not person.get("unsure"):
        if same("sun_s", 40 / 3): out["sun_nak"] = NAKS[int(lo["sun_s"] // (40 / 3))]
        if same("moon_s", 30): out["moon"] = SIGNS[int(lo["moon_s"] // 30)]
    return out


def main():
    doc = json.load(open(PATH, encoding="utf-8"))
    eng = Console()
    try:
        for p in doc["PEOPLE"]:
            p["sky"] = sky(eng, p)
    finally:
        eng.close()
    json.dump(doc, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    on_cusp = [p["name"] for p in doc["PEOPLE"] if "sun" not in p["sky"]]
    print(f"{len(doc['PEOPLE'])} people worked out." + (f" Born the day the Sun changed sign, so left off the sign pages: {', '.join(on_cusp)}" if on_cusp else ""))


if __name__ == "__main__":
    main()
