"""The gate entries in the reading: the 'In short' drafts and the distortion-and-repair layout.

    python tests/gates_check.py
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from wyrd import reading as R

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

REG = json.load(open(os.path.join(ROOT, "lib", "corpus.json"), encoding="utf-8"))["REGISTER"]
check("a draft 'In short' for all 64 gates", sorted(map(int, R.SHORT)) == list(range(1, 65)) and all(v["short"].strip() for v in R.SHORT.values()))
asks0 = []
check("all 64 approved and showing at the top of their gate",
      all(v["ok"] for v in R.SHORT.values()) and all("In short:" in R.register_entry(g, 1, "personality", "Sun", asks0) for g in range(1, 65)))
bare = lambda t: re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", t))
check("the repair layout keeps every word of the register", all(bare(R.repair(v["r"])) == bare(v["r"]) for v in REG.values()))
check("each medicine stands on its own line", all(R.repair(v["r"]).count('class="rd-med"') >= 1 for v in REG.values() if "Medicine" in v["r"]))
asks = []
gate = next(g for g, v in R.SHORT.items() if not v["ok"]) if any(not v["ok"] for v in R.SHORT.values()) else None
if gate:
    check("a line not yet approved doesn't appear", "In short:" not in R.register_entry(int(gate), 1, "personality", "Sun", asks))
    R.SHORT[gate]["ok"] = True
    check("an approved line appears at the top of its gate", R.SHORT[gate]["short"] in R.register_entry(int(gate), 1, "personality", "Sun", asks))
    R.SHORT[gate]["ok"] = False

print("GATES CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
