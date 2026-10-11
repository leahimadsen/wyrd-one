"""The deeper reading together: the thirty years, the sky's appointments, the old match,
how two bodygraphs meet, the numbers side by side, and the longer story.

    python tests/together_deeper_check.py

Needs node (the old match is checked against static/kuta.js); no ephemeris: the sky's
appointments are found on a pretend sky whose planets move at their mean rates."""
import json, os, random, re, subprocess, sys, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import engine as E, together, together_more as M

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- the sky's appointments, on a pretend sky ----
NOW = 2461325.0                                        # October 2026
PERIOD = {"Saturn": 29.457, "Jupiter": 11.862}
class Sky:
    """Saturn and Jupiter at their mean rates from 0° at NOW, the node backwards; no ayanamsa."""
    def lon(self, jd):
        t = (jd - NOW) / E.YEAR
        p = {b: E.norm(360 * t / y) for b, y in PERIOD.items()}
        p["Rahu"] = E.norm(-360 * t / 18.6); p["Ketu"] = E.norm(p["Rahu"] + 180)
        return p
    def positions(self, jd): return self.lon(jd)
    def ayanamsa(self, jd): return 0.0
class SkyMany(Sky):
    def positions_many(self, jds, bodies=None): return [(self.lon(j), 0.0) for j in jds]

natal = {"sid": {"Saturn": 90.0, "Jupiter": 180.0, "Rahu": 270.0, "Moon": 15.0}}
for eph, how in ((Sky(), "one moment at a time"), (SkyMany(), "many at once")):
    marks = M.sky_marks(eph, natal, NOW)
    years = {k: [round((a - NOW) / E.YEAR, 1) for kk, a, b in marks if kk == k] for k in M.T["MARKS"]}
    sat_ret = 29.457 * 90 / 360                          # Saturn reaches 90° after a quarter of its round
    check(f"Saturn return found when Saturn reaches its birth place ({how})", any(abs(y - (sat_ret - 0.12)) < 0.3 for y in years["saturn_return"]))
    check(f"Saturn opposition at 270° ({how})", any(abs(y - (29.457 * 270 / 360 - 0.12)) < 0.3 for y in years["saturn_opposition"]))
    check(f"Jupiter returns twice in thirty years ({how})", len(years["jupiter_return"]) == 3 and abs(years["jupiter_return"][0] - (11.862 / 2 - 0.05)) < 0.2)
    check(f"the node comes round every 18.6 years: twice in thirty ({how})", len(years["nodal_return"]) == 2 and abs(years["nodal_return"][0] - 18.6 / 4) < 0.2 and abs(years["nodal_return"][1] - (18.6 / 4 + 18.6)) < 0.2)
    check(f"Sade Sati: Saturn crossing the signs around the Moon ({how})", any(kk == "sade_sati" for kk, a, b in marks))
check("in time order", marks == sorted(marks, key=lambda m: m[1]))

# ---- pretend people ----
SID = {b: (i * 41.7) % 360 for i, b in enumerate(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])}
def person(name, asc, moon, ak, gates, date="1990-05-17", full_name="", born=2448029.0):
    C = {"ascS": asc, "sid": dict(SID, Moon=moon), "karaka": {"Atmakaraka": ak}, "jd": born,
         "natal": {"personality": {f"b{i}": {"gate": g, "line": 1} for i, g in enumerate(gates)}, "design": {}}}
    p = {"name": name, "C": C, "dasha": E.dasha_tree(C, NOW), "date": date, "full_name": full_name}
    p["marks"] = M.sky_marks(SkyMany(), C, NOW)
    return p
A = person("Freya", 10, 100, "Venus", (26, 10, 20, 7, 31, 30), full_name="Freya Ann Test")
B = person("Odin", 200, 250, "Saturn", (44, 10, 20, 41, 9, 52), date="1987-11-02", full_name="Odin Borson", born=2447102.0)
for p, s in ((A, 3), (B, 7)): p["shuku"] = {"index": s, "kanji": "", "read": ""}
html = together.build([A, B])

# ---- the thirty years ----
sec = html[html.index("<h2>The Seasons You Share</h2>"):html.index("<h2>The Questions</h2>")]
end = NOW + 30 * E.YEAR
cuts = {m["from"] for p in (A, B) for m in p["dasha"]["maha"] if NOW < m["from"] < end}
check("a chapter for every long-guest change, and one to begin", sec.count('<h3 class="rd-tier">') - 2 == len(cuts) + 1)
subs = sum(1 for p in (A, B) for s in M._antars(p["dasha"], NOW, end))
check("every sub-period in the thirty years is a dated turn", sec.count("sub-period begins") == subs and subs >= 20)
check("each chapter says where each guest lands in the other's chart", sec.count("sits in Odin's") >= len(cuts) and sec.count("sits in Freya's") >= len(cuts))
check("the sky's appointments are written out", "The sky's own appointments" in sec and "Saturn" in sec)
rows = re.findall(r"<tr(?: class=hi)?><td>(\d{4})", sec)
check("thirty years, one row each", len(rows) == 30 and int(rows[-1]) - int(rows[0]) == 29)
check("years to watch are marked and listed", "Years to watch" in sec and (sec.count("◆") == len(re.search(r"Years to watch:</b> ([^<]*)", sec).group(1).split(",")) or "one at a time" in sec))
check("no blank left unfilled", not re.findall(r"\{[a-z_]+\}", html))

# ---- the old match, against kuta.js ----
random.seed(5)
pairs = [(random.uniform(0, 360), random.uniform(0, 360)) for _ in range(1000)]
js = open(os.path.join(ROOT, "static", "kuta.js"), encoding="utf-8").read()
prog = f"""const window = {{ Wyrd: {{ helpers: {{ norm: x => ((x % 360) + 360) % 360 }} }} }}; const Wyrd = window.Wyrd; {js}
process.stdout.write(JSON.stringify({json.dumps(pairs)}.map(([a, b]) => window.WyrdKuta.read(a, b))));"""
browser = json.loads(subprocess.run(["node"], input=prog, capture_output=True, text=True, check=True).stdout)
server = [M.kuta(a, b, together.FRIENDS, together.ENEMIES) for a, b in pairs]
check("the old match scores exactly as the free page, 1000 random pairs of Moons",
      all(s["rows"] == j["rows"] and s["facts"] == j["facts"] and s["total"] == j["total"] for s, j in zip(server, browser)))
km = html[html.index("<h2>The Old Match</h2>"):html.index("<h2>How Your Bodies Meet</h2>")]
check("all eight measures written out", all(f"<h5>{k} ·" in km for k in M.MAX))

# ---- how your bodies meet ----
hd = html[html.index("<h2>How Your Bodies Meet</h2>"):html.index("<h2>Your Numbers Together</h2>")]
check("electromagnetic: 26 with 44 lights between you", "26 (" in hd and "44 (" in hd and "Electromagnetic" in hd)
check("companionship: both carry 10 to 20", "Companionship" in hd and "10 (" in hd)
check("dominance: Freya carries 7 to 31 and Odin neither gate", "7 (" in hd and "Freya's whole" in hd)
check("dominance the other way: Odin carries 9 to 52", "Odin's whole" in hd)
X = person("Ana", 10, 100, "Venus", (9, 52)); Y = person("Bo", 200, 250, "Saturn", (52,))
cm = M.bodies(dict(X, name="Ana"), dict(Y, name="Bo"))[0]
check("compromise: Ana carries 9 to 52 and Bo only gate 52", "Compromise" in cm and "Ana's whole" in cm and "Dominance" not in cm)
check("electromagnetic: 30 with 41", "30 (" in hd and "41 (" in hd)
check("types and the shared field", "Together your two bodies make one field" in hd)

# ---- the numbers side by side ----
nm = html[html.index("<h2>Your Numbers Together</h2>"):html.index("<h2>The Seasons You Share</h2>")]
check("every number side by side, names included", all(k in nm for k in ("Life path", "Birthday", "Expression", "Soul urge", "Personality")))
check("each pairing says how its planets get on", nm.count("By Stavefall the planets") + nm.count("You share the number") + nm.count("By both seatings") >= 5)

# ---- the longer story ----
pr = html[:html.index("Who Sits at the Table</h2>")]
check("each person's gift, from their Moon's mansion", "Freya got" in pr and "Odin got" in pr)
check("Skuld's appointment book names the next guest", "The next guest due is" in pr)
check("the shared errand, from the bond", "under both your names" in pr)

# ---- the full name rides through the payment ----
os.environ.update(STRIPE_SECRET_KEY="sk_test_fake", SECRET_KEY="k" * 40)
sys.modules["wyrd.ephemeris"] = types.SimpleNamespace(Ephemeris=lambda *a: object())
import app as site
b = {"name": "Freya", "full_name": "Freya Ann Test", "date": "1990-05-17", "time": "14:30", "lat": 51.5, "lon": -0.13, "tz": "Europe/London", "place_label": "London"}
packed = site.pack_person(b, site.birth_from(b))
check("the full name is kept with the payment, within Stripe's limits", site.unpack_person(packed)["full_name"] == "Freya Ann Test" and len(packed) <= 500)

print("TOGETHER DEEPER CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
