"""The Current Between You: two people's Birth and Dharma Designs read four to four.

    python tests/circuit_check.py

Pretend designs check each kind of current exactly; two real charts (cast with the console's built-in
ephemeris, so it needs node) check the section in the reading together."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import engine as E, circuit as CX, together, together_more as TM

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

def rave(*gs): return {"personality": {f"b{i}": {"gate": g, "line": 1} for i, g in enumerate(gs)}, "design": {}}
def person(name, birth, dharma): return {"name": name, "C": {"natal": rave(*birth), "dharma": rave(*dharma)}}

# Freya: born with 26, 11, 10, 5, 6; growing into 2, 23, 20, 42, 53
# Odin:  born with 44, 14, 5;            growing into 56, 43, 15, 6, 42, 53
A = person("Freya", (26, 11, 10, 5, 6), (2, 23, 20, 42, 53))
B = person("Odin", (44, 14, 5), (56, 43, 15, 6, 42, 53))
X = CX.currents(A, B)
chs = lambda k: {c for c, _, _ in X[k]}
check("between the bodies: Freya's 26 and Odin's 44", chs("body") == {(26, 44)})
check("Freya's body feeds Odin's dharma: her 11 completes his 56", X["ab"] == [((11, 56), 11, 56)])
check("Odin's body feeds Freya's dharma: his 14 completes her 2", X["ba"] == [((2, 14), 2, 14)])
check("between the dharmas: her 23 meets his 43", X["dd"] == [((23, 43), 23, 43)])
check("not a feed when the grower carries the other end already: 5–15 is Odin's own bridge", (5, 15) not in chs("ab"))
check("each person's own bridges are counted: Freya's 10–20, Odin's 5–15", X["own_a"] == 1 and X["own_b"] == 1)
check("the same current in both dharmas: 42–53", X["kin"] == [(42, 53)])
check("what each already is for the other: Freya was born with 6, which Odin's dharma reaches for", X["ex_b"] == [6] and X["ex_a"] == [])
check("a loop when each feeds the other", CX.shape(X) == ("loop", None))
Y = CX.currents(B, A)
check("the same both ways round", {c for c, _, _ in Y["ab"]} == chs("ba") and {c for c, _, _ in Y["ba"]} == chs("ab")
      and {c for c, _, _ in Y["dd"]} == chs("dd") and {c for c, _, _ in Y["body"]} == chs("body"))
check("one way when only one feeds", CX.shape(CX.currents(person("a", (11,), ()), person("b", (), (56,)))) == ("one", "ab"))
check("quiet when nothing runs", CX.shape(CX.currents(person("a", (1,), (3,)), person("b", (4,), (5,)))) == ("none", None))
svg = CX.diagram(A, B, X)
check("the circuit drawn with its six wires and four designs", svg.count('class="cx-wire') == 6 and svg.count('class="cx-node') == 4)
check("each wire numbered with its channels", sorted(int(n) for n in re.findall(r'class="cx-n"[^>]*>(\d+)<', svg)) == [1, 1, 1, 1, 1, 1])

# two real people, in the reading together
from tests.verify_engine import NodeEph
eph = NodeEph()
NOW = E.julian_day(2026, 11, 10, 12)
P = []
for name, args, day in (("Sigrun", (1988, 9, 23, 6.6667, 64.1466, -21.9426), "1988-09-23"), ("Halvard", (1986, 3, 2, 20.25, 59.9139, 10.7522), "1986-03-02")):
    C = E.cast(eph, *args)
    P.append({"name": name, "C": C, "dasha": E.dasha_tree(C, NOW), "date": day, "shuku": None, "marks": []})
X = CX.currents(P[0], P[1])
check("between the bodies, the same channels How Your Bodies Meet calls electromagnetic", len(X["body"]) == TM.bodies(P[0], P[1])[1])
html = together.build(P)
heads = re.findall(r"<h2>(.*?)</h2>", html)
check("the reading together reads the current right after the bodies", heads.index("The Current Between You") == heads.index("How Your Bodies Meet") + 1)
sec = html[html.index("<h2>The Current Between You</h2>"):html.index("<h2>Your Numbers Together</h2>")]
check("every feed and dharma channel read once", len(re.findall(r'<div class="rd-entry tw-ch"><h4>Channel', sec)) == len(X["ab"]) + len(X["ba"]) + len(X["dd"]) + len(X["kin"]))
check("the circuit and where it runs in the body, drawn", 'class="cx-fig' in sec and 'class="bg-fig bg-k"' in sec)
check("sections named by number", "section V" in sec and "{SEC:" not in html)
check("its question gathered at the end", together.T["CIRCUIT_ASK"] in html[html.index("<h2>The Questions</h2>"):])
check("nothing left unfilled", not re.search(r"\{[a-z_]+\}", re.sub(r"<[^>]+>", "", sec)))
P3 = P + [dict(P[0], name="Third")]
h3 = together.build(P3)
s3 = h3[h3.index("<h2>The Current Between You</h2>"):]
check("a table of three: one line a pair", len(re.findall(r"<p><b>[^<]+ and [^<]+</b>:", s3[:s3.index("</section>")])) == 3)

print("CIRCUIT CHECK PASSED" if not bad else f"CIRCUIT CHECK FAILED ({bad})")
sys.exit(1 if bad else 0)
