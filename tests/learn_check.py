"""The free learning pages: every lunar mansion reads in full.

    python tests/learn_check.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd import pages as P

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

SECTIONS = ["What it's about", "What it's good for", "Where it goes wrong", "What it rules, and what rules it",
            "The body and the face it gives", "Its four padas", "Its question"]
pages = {s: P.nakshatra("https://example", s) for s, _ in P.NAKS}
check("all twenty-seven mansions have a page", len(pages) == 27 and all(pages.values()))
text = {s: html.unescape(re.sub(r"<[^>]+>", " ", p[2])) for s, p in pages.items()}
check("every page has every section", all(all(h in p[2] for h in SECTIONS) for p in pages.values()))
check("no blank left unfilled", not any(re.search(r"\{[a-z_\[\]0-9\"']+\}", t) for t in text.values()))
check("each page reads at length, not just placements", all(len(t.split()) > 450 for t in text.values()))
check("the four padas, each with its navamsa sign and aim", all(p[2].count("<tr><td>") == 4 for p in pages.values()))
check("the dark gift and the distortion are told apart", all("a choice, made knowing" in t and "(unconscious)" in t for t in text.values()))
gates = [g for p in pages.values() for g in re.findall(r'href="/learn/gates/(\d+)"', p[2])]
check("every gate of the wheel is linked from the mansion it falls in", set(map(int, gates)) == set(P.GATES))
idx = P.learn_index("https://example")[2]
check("the learn index gives each mansion's gist", all(P.C["NAKSHATRA"][i][6] in html.unescape(idx) for _, i in P.NAKS))

print("LEARN CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
