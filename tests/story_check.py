"""The prologue: every chart gets a whole story, with no gaps and no unfilled blanks.

    python tests/story_check.py

Walks every rising sign, every Moon mansion and every soul-planet against a
pretend chart, so it needs no ephemeris."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd import engine as E, story
from wyrd.reading import ENG

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

S = story.S
check("a soul for every possible Atmakaraka", set(S["SOUL"]) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"})
check("a costume for every sign", set(S["COSTUME"]) == set(E.SIGNS))
check("a houseguest for every period", set(S["VISITOR"]) == {d[0] for d in E.DASHA})

def chart(asc, moon, ak, unknown=False, through=0.5):
    C = {"ascS": asc, "sid": {"Moon": moon}, "karaka": {"Atmakaraka": ak}, "jd": 2450000.0}
    if unknown: C["unknownTime"] = True
    now = C["jd"] + 30 * E.YEAR
    return C, E.dasha_tree({"sid": {"Moon": moon}, "jd": C["jd"]}, now)

texts, leftover = [], []
for si in range(12):
    for nk in range(27):
        ak = list(S["SOUL"])[(si + nk) % 7]
        C, d = chart(si * 30 + 5, nk * E.NAK_ARC + E.NAK_ARC / 2, ak)
        t = story.tell(C, d, "Freya Test", ENG)
        texts.append(t)
        leftover += re.findall(r"\{[a-z_]+\}", t)
check("every sign and mansion tells a story", len(texts) == 12 * 27 and all("Dressing room" in t or "dressing room" in t for t in texts))
check("no blank left unfilled", not leftover)
check("each story names its mansion and shakti", all(ENG[nk][0] in texts[si * 27 + nk] and ENG[nk][2] in texts[si * 27 + nk]
                                                     for si in range(12) for nk in range(27)))

C, d = chart(10, 100, "Saturn")
t = story.tell(C, d, "Freya Test", ENG)
check("the first name is used", "called you Freya" in t)
check("exactly one houseguest is in the house now", t.count(S["NOW"].strip()) == 1)
ages = [int(a) for a in re.findall(r"At (\d+) comes", t)]
check("houseguests arrive in order, within a lifetime", ages == sorted(ages) and ages[-1] <= S["UNTIL_AGE"])
check("no name, no naming", "called" not in story.tell(C, d, "", ENG) and "called" not in story.tell(C, d, "A sample chart", ENG))
check("names can't add HTML", "<script>" not in story.tell(C, d, "<script>x", ENG))
C, d = chart(10, 100, "Sun", unknown=True)
check("unknown birth time says the costume is read from the Sun", S["COSTUME_UNKNOWN"].strip() in story.tell(C, d, "", ENG))
C, d = chart(10, E.NAK_ARC * 0.999, "Sun")           # born at the very end of the first period
check("a period ending in the first year reads naturally", "until you were 0" not in story.tell(C, d, "", ENG)
      and "first birthday" in story.tell(C, d, "", ENG))

print("STORY CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
