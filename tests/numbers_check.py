"""A person's numbers, on the server and in the browser.

    python tests/numbers_check.py

Worked examples by hand, the two planets for each number, the reading's
numbers section, and the browser's sums (static/numbers.js, run in node)
against the server's (wyrd/numbers.py) on 500 random births and names."""
import json, os, random, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import numbers as N, engine as E

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- birth-date numbers, worked by hand ----
check("1990-05-17: 5 + 8 + (1990 → 19 → 1) = 14 → life path 5", N.of("1990-05-17")["life_path"] == 5)
check("1980-01-01: 1 + 1 + 9 = 11, kept as a master", N.of("1980-01-01")["life_path"] == 11)
check("1980-04-09: 4 + 9 + 9 = 22, kept as a master", N.of("1980-04-09")["life_path"] == 22)
check("born on the 29th: birthday 11", N.of("1990-05-29")["birthday"] == 11)
check("born on the 17th: birthday 8", N.of("1990-05-17")["birthday"] == 8)
check("personal year 2026 for 17 May: 5 + 8 + 1 = 14 → 5", N.of("1990-05-17", year=2026)["personal_year"] == 5)
check("no year, no personal year", "personal_year" not in N.of("1990-05-17"))

# ---- name numbers ----
js = N.name_numbers("John Smith")
check("John Smith: expression 2 + 6 = 8", js["expression"] == 8)
check("John Smith: soul urge (O, I) 6 + 9 = 15 → 6", js["soul_urge"] == 6)
check("John Smith: personality (consonants) 5 + 6 = 11, a master", js["personality"] == 11)
check("Lynn: no other vowel, so Y is the vowel (7)", N.name_numbers("Lynn")["soul_urge"] == 7)
check("accents come off: José is Jose", N.name_numbers("José") == N.name_numbers("Jose"))
check("hyphens and apostrophes don't count", N.name_numbers("Mary-Anne O'Neil") == N.name_numbers("Mary Anne ONeil"))
check("no name, no name numbers", N.name_numbers("") == {} and N.name_numbers("李") == {})

# ---- the two planets ----
check("1: the Sun in both", N.planets(1)["stavefall"] == "Sun" and N.planets(1)["vedic"] == "Sun")
check("4: Jupiter (Stavefall, the heart) and Rahu (Vedic)", (N.planets(4)["stavefall"], N.planets(4)["station"], N.planets(4)["vedic"]) == ("Jupiter", "Heart", "Rahu"))
check("7: Mercury and Ketu", (N.planets(7)["stavefall"], N.planets(7)["vedic"]) == ("Mercury", "Ketu"))
check("a master sits on its root's planets: 11 on 2's, 22 on 4's, 33 on 6's",
      [N.planets(n)["root"] for n in (11, 22, 33)] == [2, 4, 6] and N.planets(22)["vedic"] == "Rahu")
viz = open(os.path.join(ROOT, "static", "viz.js"), encoding="utf-8").read()
check("Stavefall matches the console's own seating in viz.js",
      all(re.search(rf'\b{n}: {{ graha:"{g}"', viz) for n, (g, _) in N.STAVEFALL.items()))

# ---- the reading's section, from a pretend chart ----
from wyrd import reading_numbers as RN
SID = {b: (i * 41.7) % 360 for i, b in enumerate(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])}
C = {"ascS": 15.0, "sid": SID, "jd": 2448029.0}
d = E.dasha_tree({"sid": {"Moon": SID["Moon"]}, "jd": C["jd"]}, C["jd"] + 36 * E.YEAR)
asks = []
html = RN.body(C, d, {"date": "1990-05-17", "full_name": "Freya Ann Test"}, asks, year=2026)
check("every number shown with both planets", all(k in html for k in ("Life path", "Birthday", "Personal year", "Expression", "Soul urge", "Personality")))
check("life path 5's planets placed in the chart: Mars (Stavefall) and Mercury (Vedic)", "♂ Mars (your Stavefall seat" in html and "☿ Mercury (the Vedic planet of 5)" in html)
check("and on the clock", "Its period" in html)
check("its question joins the reading's questions", asks and asks[0][0] == "Life path 5")
check("no blank left unfilled", not re.findall(r"\{[a-z_]+\}", html))
no_name = RN.body(C, d, {"date": "1990-05-17"}, [], year=2026)
check("without a full name: asks for it, shows no name numbers", "Add your full name at birth" in no_name and "Soul urge" not in no_name)

# ---- the learn page and the glossary ----
from wyrd import pages
title, desc, body, ld = pages.numbers_learn("https://example")
check("the learn page shows all nine with both planets", all(f"<td><b>{n}</b></td>" in body for n in range(1, 10))
      and all(f"{N.STAVEFALL[n][0]} <span" in body for n in range(1, 10)) and "Rahu</td>" in body)
check("it teaches both seatings and the worked example", "Stavefall: the console" in body and "Vedic numerology" in body and "Life path 5" in body)
check("the shadows stay in the reading", not any(pages.NUMS["NUMBER"][str(n)]["shadow"] in body for n in (1, 5, 9, 11)))
check("it's in the sitemap and on the Learn page", "/learn/numbers" in pages.sitemap("https://x") and "/learn/numbers" in pages.learn_index("https://x")[2])
gl = open(os.path.join(ROOT, "static", "glossary.js"), encoding="utf-8").read()
check("every number term can be tapped for a definition",
      all(f"  {k}: [" in gl for k in ("stavefall", "vedicnum", "lifepath", "birthdaynum", "personalyear", "expression", "soulurge", "personalitynum", "masternum")))

# ---- the browser does the same sums ----
random.seed(3)
NAMES = ["John Smith", "Lynn", "José María Ñúñez", "Mary-Anne O'Neil", "", "Freya Ann Test", "Yvy", "Siobhán Ní Bhriain", "Bryn Wyn"]
cases = [{"date": f"{random.randint(1850, 2149)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
          "name": random.choice(NAMES), "year": random.randint(2020, 2040)} for _ in range(500)]
js_src = open(os.path.join(ROOT, "static", "numbers.js"), encoding="utf-8").read()
prog = f"""const window = {{}}; {js_src}
const N = window.WyrdNumbers, cases = {json.dumps(cases)};
process.stdout.write(JSON.stringify(cases.map(c => [N.of(c.date, c.name, c.year), [1,2,3,4,5,6,7,8,9,11,22,33].map(N.planets)])));"""
browser = json.loads(subprocess.run(["node"], input=prog, capture_output=True, text=True, check=True).stdout)
server = [[N.of(c["date"], c["name"], c["year"]), [N.planets(n) for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)]] for c in cases]
check("browser and server agree, 500 random births and names", browser == server)

print("NUMBERS CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
