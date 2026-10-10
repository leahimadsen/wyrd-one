"""Turn The Völva's mandala sheet (lib/wyrd-mandala-108.csv) into static/mandala.json and static/mandala/wyrd-mansions.js."""
import csv, json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(HERE, "lib", "wyrd-mandala-108.csv"), encoding="utf-8")))
assert len(rows) == 108, "the mandala has 108 padas"
# The cards follow one rule, the 36 decans (Golden Dawn): number 2-10 through each three signs,
# suit by the sign's element, ruler in Chaldean order from Mars, trump by sign. Two decks read it:
#   the Buddhist deck (the sheet's inner names) on the sidereal ring: emanating;
#   the Nordic deck (the sheet's outer names) on the true tropical ring, sidereal + ayanamsa: receiving.
# The sheet's own card columns were laid on a mirrored tropical chassis; only their names are kept.
import re
SIGNS = "Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces".split()
SUIT = ["Wands", "Shields", "Swords", "Cups"]                 # fire, earth, air, water
CHALDEAN = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]
inner_suit, inner_trump, outer_trump = {}, {}, {}
for r in rows:   # the names each deck gives, checked against the rule wherever the mirrored chassis is unambiguous
    num, suit = re.match(r"(\d+) of (\w+)", r["minor_card_outer"]).groups()
    inner_suit.setdefault(suit, re.match(r"\d+ of (.+)", r["minor_card_inner"]).group(1))
    assert inner_suit[suit] == re.match(r"\d+ of (.+)", r["minor_card_inner"]).group(1)
    inner_trump.setdefault(r["trump_outer"], r["trump_inner"]); assert inner_trump[r["trump_outer"]] == r["trump_inner"]
    d, m, sg = re.match(r"(\d+)°(\d+)′ (\w+)", r["tropical_under_chassis"]).groups()
    mid = (SIGNS.index(sg) * 30 + int(d) + int(m) / 60 - 5 / 3) % 360
    if abs(mid % 10 - 5) < 4.9:
        k = int(mid // 10); outer_trump[k // 3] = r["trump_outer"]
        assert (int(num), suit, r["decan_ruler"]) == (2 + k % 9, SUIT[(k // 3) % 4], CHALDEAN[k % 7]), (r["pada"], k)
assert len(outer_trump) == 12 and len(inner_suit) == 4
decans = []
for k in range(36):
    suit, tr = SUIT[(k // 3) % 4], outer_trump[k // 3]
    decans.append({"sign": SIGNS[k // 3], "n": 2 + k % 9, "ruler": CHALDEAN[k % 7],
                   "nordic": {"minor": f"{2 + k % 9} of {suit}", "trump": tr},
                   "buddhist": {"minor": f"{2 + k % 9} of {inner_suit[suit]}", "trump": inner_trump[tr]}})
padas = [{"nak": r["nakshatra"], "pada": int(r["nak_pada"]), "void": r["asura_void"] or ""} for r in rows]
GATE = {"at": 0, "buddhist": "The Fool", "reading": "The Great Departure: the going-forth that begins with nothing",
        "note": "The Fool belongs to no sign and no decan. It stands at the gate itself, 0° sidereal Aries, where the Buddhist ring begins."}
json.dump({"_note": "The Völva's mandala. decans: the 36 decan cards, index = floor(longitude / 10); the Buddhist deck reads them at the "
                    "sidereal longitude, the Nordic deck at the true tropical longitude. padas: the 108 sidereal padas from Ashwini 1 at 0°, "
                    "with their asura voids. gate: the card at the opening of the wheel. Made from lib/wyrd-mandala-108.csv by scripts/mandala.py.",
           "decans": decans, "padas": padas, "gate": GATE},
          open(os.path.join(HERE, "static", "mandala.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("static/mandala.json: 36 decans, 108 padas")

# The Wyrd Mandala room (static/mandala/): the 27 mansions' short texts, taken from the corpus
# (lib/corpus.json: NAKSHATRA, ENGINE, NAK_DEEP), and the sheet's cards for each pada.
corpus = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
mansions = []
for i in range(27):
    n, e, d = corpus["NAKSHATRA"][i], corpus["ENGINE"][i], corpus["NAK_DEEP"][i]
    syl = d[9].split()
    assert len(syl) == 4, n[0]
    mansions.append({"name": n[0], "symbol": n[3], "gana": n[4], "line": n[6],
                     "shakti": e[1], "power": e[2], "above": e[3], "below": e[4], "result": e[5],
                     "core": e[6], "question": e[10], "syllables": syl})
cards = {"decans": decans, "voids": [p["void"] for p in padas], "gate": GATE}
# The correspondence tables, gathered from the rest of the console so the mandala reads the same sources:
# gates and hexagrams (viz.js, body.js, corpus), runes and house colours (corpus HOUSES, register RUNES),
# the Planetary Ladder of realms (viz.js), Sukuyō (wyrd/sukuyo.py), the mansions' attributes (corpus NAK_DEEP).
import sys
sys.path.insert(0, HERE)
from wyrd.sukuyo import SHUKU
src = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
viz, body = src("static", "viz.js"), src("static", "body.js")
gate_order = [int(x) for x in re.search(r"const GATE_ORDER = \[([\d,\s]+)\]", viz).group(1).split(",")]
assert sorted(gate_order) == list(range(1, 65))
gate_centre = {}
for label, gates in re.findall(r'label:"(\w+)",\s*gates:\[([\d,]+)\]', body):
    for g in gates.split(","): gate_centre[int(g)] = label
assert len(gate_centre) == 64
ladder = {}
for m in re.finditer(r'\{ id:"(\w+)", world:"([^"]+)", station:"([^"]+)".*?band:"(#[0-9a-f]+)".*?operator:"([^"]+)", opGloss:"([^"]+)",\s*feeder:"(\w+)", hz:([\d.]+), hd:"([^"]+)", bifrost:"([^"]+)"', viz, re.S):
    i, world, station, band, op, gloss, feeder, hz, hd, bif = m.groups()
    ladder[feeder] = {"world": world, "station": station, "band": band, "operator": op, "opGloss": gloss, "hz": float(hz), "hd": hd, "bifrost": bif}
assert len(ladder) == 7, ladder.keys()
reg = json.load(open(os.path.join(HERE, "lib", "register_ext.json"), encoding="utf-8"))
learn = json.load(open(os.path.join(HERE, "lib", "learn_ext.json"), encoding="utf-8"))
shuku = {n: [k, r] for k, r, n in SHUKU}
ref = {
    "gateOrder": gate_order, "gateStart": 302, "gateCentre": gate_centre,
    "gateName": corpus["GATE_NAME"], "hexagram": {g: v.get("t", "") for g, v in corpus["REGISTER"].items()},
    "houses": [{"color": h["color"], "hex": h["hex"], "phase": h["phase"], "ingress": h["ingress"], "egress": h["egress"]} for h in corpus["HOUSES"]],
    "runes": {k: v["means"] for k, v in reg["RUNES"].items()},
    "aettir": [a["name"] for a in learn["AETTIR"]],
    "signs": [{"element": x["element"], "mode": x["mode"]} for x in reg["SIGNS"]],
    "ladder": ladder,
    "numSeat": [None, "Sun", "Moon", "Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Rahu", "Ketu"],
    "nak": [{"star": d[1], "gana": d[2], "yoni": d[3], "guna": d[4], "dosha": d[5], "varna": d[6], "aim": d[7], "direction": d[8],
             "body": corpus["NAKSHATRA"][i][5], "shuku": shuku[corpus["NAKSHATRA"][i][0]]} for i, d in enumerate(corpus["NAK_DEEP"])],
}
cards["ref"] = ref
with open(os.path.join(HERE, "static", "mandala", "wyrd-mansions.js"), "w", encoding="utf-8") as f:
    f.write("/* Generated by scripts/mandala.py from lib/corpus.json and lib/wyrd-mandala-108.csv. Do not edit by hand. */\n")
    f.write("window.WYRD_MANSIONS = " + json.dumps({"mansions": mansions, "cards": cards}, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("static/mandala/wyrd-mansions.js: 27 mansions, 36 decans")
