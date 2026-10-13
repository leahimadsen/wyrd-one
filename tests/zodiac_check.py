"""The zodiac pages: the overview and every sign read in full, and the people born under each.

    python tests/zodiac_check.py
"""
import html, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd import pages as P, zodiac as Z

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

SECTIONS = ["At a glance", "What it brings, and how it feels", "rising", "Every planet in", "in the deeper charts", "Its mansions",
            "Its stars", "How the old traditions drew it", "Born under"]
pages = {s: P.sign("https://example", s) for s, _ in P.SIGNS}
check("all twelve signs have a page", len(pages) == 12 and all(pages.values()))
text = {s: html.unescape(re.sub(r"<[^>]+>", " ", p[2])) for s, p in pages.items()}
check("every page has every section", all(all(h in p[2] for h in SECTIONS) for p in pages.values()))
check("no blank left unfilled", not any(re.search(r"\{[a-z_\[\]0-9\"']+\}|None|\bnan\b", t) for t in text.values()))
check("each page reads at length", all(len(t.split()) > 1200 for t in text.values()))
check("an unknown sign is not a page", P.sign("https://example", "ophiuchus") is None)

# every link a sign page makes goes somewhere real
naks, runes = {s for s, _ in P.NAKS}, {r[0] for r in P.RUNES}
links = [u for p in pages.values() for u in re.findall(r'href="(/learn/[^"#]+)', p[2])]
def real(u):
    m = re.match(r"/learn/(nakshatras|runes|signs|gates)/(.+)$", u)
    if not m: return u in ("/learn", "/learn/signs")
    kind, s = m.groups()
    return (s in naks if kind == "nakshatras" else s in runes if kind == "runes" else s in dict(P.SIGNS) if kind == "signs" else int(s) in P.GATES)
check("every link on the sign pages resolves", all(real(u) for u in links))

# the mansions tile the zodiac: 108 padas, nine to a sign
check("nine padas to every sign", all(sum(len(p) for _, p, _, _ in Z.mansions_in(i)) == 9 for i in range(12)))
gates = [g for i in range(12) for g in Z.gates_in_tropical(i)]
check("every gate falls in exactly one tropical sign", sorted(gates) == sorted(P.GATES))

# dignities match the readings' own tables
EXALT, OWN, ROOT = Z._dignity()
check("each sign has a ruler", all(any(i in OWN[b] for b in Z.SEVEN) for i in range(12)))
check("Aries: Mars rules, the Sun is exalted, Saturn falls",
      all(k in text["aries"] for k in ("♂︎ Mars", "the Sun, at its peak at 10°", "Saturn, at its lowest at 20°")))

# the people
N = Z.N["PEOPLE"]
check("every person has a sky worked out", all(isinstance(p.get("sky"), dict) and "sun" in p["sky"] for p in N))
check("every sign has at least eight people with the Sun there", all(len(Z.people(s, "sun")) >= 8 for s in Z.SIGNS))
check("no one marked unsure is given a Moon", not any(p.get("unsure") and p["sky"].get("moon") for p in N))
check("sidereal Sun is the tropical sign or the one before it",
      all("trop" not in p["sky"] or Z.SIGNS.index(p["sky"]["trop"]) - Z.SIGNS.index(p["sky"]["sun"]) in (0, 1, -11) for p in N))
check("every person appears on their Sun sign's page", all(p["name"] in html.unescape(pages[P.slug(p["sky"]["sun"])][2]) for p in N if p["sky"].get("sun")))
if shutil.which("node"):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
    import notables as T
    eng = T.Console()
    try:
        again = [T.sky(eng, p) == p["sky"] for p in N]
    finally:
        eng.close()
    check("the stored skies match the console's engine", all(again))
else:
    print("  skip the stored skies against the console's engine (no node)")

# the overview
title, desc, body, ld = P.signs_index("https://example")
t = html.unescape(re.sub(r"<[^>]+>", " ", body))
check("the overview has the wheel, the dates, the elements and the rulers",
      all(k in body for k in ("<svg", "When the Sun is in each sign", "Elements and modes", "Rulers and dignities")))
check("the overview names this year's ayanamsa", Z.ayanamsa()[1] in t)
check("the overview links all twelve", all(f'/learn/signs/{s}"' in body for s, _ in P.SIGNS))
check("the learn index links the overview", 'href="/learn/signs"' in P.learn_index("https://example")[2])
check("the sitemap lists the overview", "/learn/signs<" in P.sitemap("https://example"))

print("ZODIAC CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
