"""The divisional charts (vargas), the same arithmetic as static/vargas.js (tests/vargas_check.py
proves it), and the thread from Rashi to Dharma for the paid reading: a planet in the D1, its
navamsa sign, the gate it lights in the Dharma Design, and the centre that gate feeds."""
import json, math, os, re
from . import engine as E, bodygraph as BG, rave as RV

SIGNS = E.SIGNS
LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
ELEMENT = ["Fire", "Earth", "Air", "Water"]
BODIES = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇", "Earth": "⊕"}
NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60]


def sign(lon, n):
    L = E.norm(lon); s = math.floor(L / 30); d = L - s * 30; odd = s % 2 == 0; mode = s % 3; el = s % 4
    part = math.floor(d / (30 / n))
    frm = lambda start: (start + part) % 12
    if n == 1: return s
    if n == 2: return (4 if d < 15 else 3) if odd else (3 if d < 15 else 4)
    if n == 3: return (s + 4 * part) % 12
    if n == 4: return (s + 3 * part) % 12
    if n == 7: return frm(s if odd else s + 6)
    if n == 9: return frm([0, 9, 6, 3][el])
    if n == 10: return frm(s if odd else s + 8)
    if n in (12, 60): return frm(s)
    if n in (16, 45): return frm([0, 4, 8][mode])
    if n == 20: return frm([0, 8, 4][mode])
    if n == 24: return frm(4 if odd else 3)
    if n == 27: return frm([0, 3, 6, 9][el])
    if n == 30:
        if odd: return 0 if d < 5 else 10 if d < 10 else 8 if d < 18 else 2 if d < 25 else 6
        return 1 if d < 5 else 5 if d < 12 else 11 if d < 20 else 9 if d < 25 else 7
    if n == 40: return frm(0 if odd else 6)
    return math.floor(E.norm(L * n) / 30)          # cyclical: D5, D6, D8, D11


EXALT = {"Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6}
OWN = {"Sun": {4}, "Moon": {3}, "Mercury": {2, 5}, "Venus": {1, 6}, "Mars": {0, 7}, "Jupiter": {8, 11}, "Saturn": {9, 10}}
# dignity is a ladder: exalted, own sign, a friend's, a neutral's, an enemy's, debilitated; friend, neutral
# and enemy by the natural friendships (naisargika maitri, BPHS ch. 3). static/vargas.js keeps the same ladder.
KIN = {"Sun": ({"Moon", "Mars", "Jupiter"}, {"Venus", "Saturn"}), "Moon": ({"Sun", "Mercury"}, set()),
       "Mars": ({"Sun", "Moon", "Jupiter"}, {"Mercury"}), "Mercury": ({"Sun", "Venus"}, {"Moon"}),
       "Jupiter": ({"Sun", "Moon", "Mars"}, {"Mercury", "Venus"}), "Venus": ({"Mercury", "Saturn"}, {"Sun", "Moon"}),
       "Saturn": ({"Mercury", "Venus"}, {"Sun", "Moon", "Mars"})}
RANK = {"exalted": 5, "own sign": 4, "friend's sign": 3, "neutral sign": 2, "enemy's sign": 1, "debilitated": 0, "": 2}


def dignity_in(b, s):
    if b not in EXALT: return ""
    if EXALT[b] == s: return "exalted"
    if (EXALT[b] + 6) % 12 == s: return "debilitated"
    if s in OWN[b]: return "own sign"
    friends, enemies = KIN[b]
    return "friend's sign" if LORD[s] in friends else "enemy's sign" if LORD[s] in enemies else "neutral sign"


def ordinal(n): return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(os.path.join(HERE, "lib", "vargas.json"), encoding="utf-8"))           # the words, shared with static/vargas.js
KA = json.load(open(os.path.join(HERE, "lib", "karakas.json"), encoding="utf-8"))
HOUSE_LIFE = json.load(open(os.path.join(HERE, "lib", "register_ext.json"), encoding="utf-8"))["HOUSE_LIFE"]


def fill(t, **o):
    return re.sub(r"\{(\w+)\}", lambda m: str(o.get(m.group(1), "")), t or "")


def thread(C):
    """From Rashi to Dharma: the reading's version of WyrdVargas.thread, from the same words."""
    if not C.get("dharma"): return ""
    DA, BA = BG.analyse(C["dharma"]), BG.analyse(C["natal"])
    DP, NP = C["dharma"]["personality"], C["natal"]["personality"]
    unknown = bool(C.get("unknownTime"))
    asc_s = math.floor(E.norm(C["ascS"]) / 30)
    house = lambda s: None if unknown else (s - asc_s) % 12 + 1
    live_gates = {g for ch in DA["live"] for g in ch}
    rows = []
    for b in BODIES:
        s1, s9 = sign(C["sid"][b], 1), sign(C["sid"][b], 9)
        d1, d9 = dignity_in(b, s1), dignity_in(b, s9)
        g = DP[b]; k = RV.CENTRE_OF[g["gate"]]
        move = "rises" if RANK[d9] > RANK[d1] else "falls" if RANK[d9] < RANK[d1] else "holds" if s1 == s9 else ""
        rows.append(dict(b=b, s1=s1, s9=s9, d1=d1, d9=d9, g=g, k=k, live=g["gate"] in live_gates, move=move))
    lab = lambda k: RV.CENTRES[k][0]
    step = lambda r: f'{GLYPH[r["b"]]} {r["b"]} ({SIGNS[r["s1"]]} → {SIGNS[r["s9"]]}' + (f', {r["d9"]}' if r["d9"] else "") + ")"
    tr = "".join(
        f'<tr{" class=hi" if r["s1"] == r["s9"] else ""}><td>{GLYPH[r["b"]]} {r["b"]}</td>'
        f'<td>{SIGNS[r["s1"]]}{(" · " + ordinal(house(r["s1"])) + " house") if house(r["s1"]) else ""}{" · " + r["d1"] if r["d1"] else ""}</td>'
        f'<td>{SIGNS[r["s9"]]}{" · " + r["d9"] if r["d9"] else ""}{" ↑" if r["move"] == "rises" else " ↓" if r["move"] == "falls" else ""}</td>'
        f'<td>{r["g"]["gate"]}.{r["g"]["line"]}</td><td>{lab(r["k"])}{" · in a channel" if r["live"] else ""}</td>'
        f'<td>{NP[r["b"]]["gate"]}.{NP[r["b"]]["line"]}</td></tr>' for r in rows)
    ripen = "".join("<p>" + fill(W["RIPEN"], glyph=GLYPH[r["b"]], planet=r["b"], matter=W["PLANET"][r["b"]], s1=SIGNS[r["s1"]],
                                 fruit=(f'stays in {SIGNS[r["s9"]]} and deepens into ' if r["s1"] == r["s9"] else f'ripens in {SIGNS[r["s9"]]}, into ')
                                 + re.sub(r"^it ripens into ", "", W["FRUIT"][r["s9"]])) + "</p>" for r in rows)
    eg = next((r for r in rows if r["move"] == "falls" and r["d9"] != "debilitated"), None)
    standing = lambda d, s: fill(W["STANDING"].get(d, d), lord=("the " if LORD[s] in ("Sun", "Moon") else "") + LORD[s])
    ladder = (f'<p>{W["LADDER"]}</p>' + (f'<p>{fill(W["LADDER_EG"], glyph=GLYPH[eg["b"]], planet=eg["b"], s1=SIGNS[eg["s1"]], s9=SIGNS[eg["s9"]], p1=standing(eg["d1"], eg["s1"]), p9=standing(eg["d9"], eg["s9"]), steps=W["STEPS"][RANK[eg["d1"]] - RANK[eg["d9"]]])}</p>' if eg else ""))
    vargo = [r for r in rows if r["s1"] == r["s9"]]
    rise = [r for r in rows if r["move"] == "rises"]; fall = [r for r in rows if r["move"] == "falls"]
    lines = [fill(W["VARGOTTAMA"], list=", ".join(f'{GLYPH[r["b"]]} {r["b"]} in {SIGNS[r["s1"]]}' for r in vargo)) if vargo else W["VARGOTTAMA_NONE"]]
    if rise: lines.append(fill(W["RISE"], list=", ".join(step(r) for r in rise)))
    if fall: lines.append(fill(W["FALL"], list=", ".join(step(r) for r in fall)))
    ak = C["karaka"]["Atmakaraka"]; kar = sign(C["sid"][ak], 9)
    lines.append(fill(W["KARAKAMSA"], glyph=GLYPH.get(ak, ""), planet=ak, sign=SIGNS[kar], wish=(lambda w: w[:1].upper() + w[1:])(KA["KARAKAMSA"][kar].split(": ", 1)[-1])))
    if not unknown:
        a9 = sign(C["ascS"], 9); l9 = LORD[a9]; h = house(sign(C["sid"][l9], 1))
        lines.append(fill(W["NAV_RISING"], sign=SIGNS[a9], glyph=GLYPH[l9], lord=l9, house=ordinal(h), life=HOUSE_LIFE[h - 1]))
    e1, e9 = [0] * 4, [0] * 4
    for r in rows: e1[r["s1"] % 4] += 1; e9[r["s9"] % 4] += 1
    t1, t9 = ELEMENT[e1.index(max(e1))], ELEMENT[e9.index(max(e9))]
    counts = ", ".join(f"{x} {e1[i]}→{e9[i]}" for i, x in enumerate(ELEMENT))
    lines.append(fill(W["ELEMENT_HOLD"], el=t1, counts=counts) if t1 == t9 else fill(W["ELEMENT_SHIFT"], e1=t1, e9=t9, counts=counts))
    # every body the Dharma Design is cast from (the nine, the outer three, the Earth), at birth and at the design moment
    des = {b: E.norm(l - C["ay"]) for b, l in C["tropDes"].items()}
    sides = []
    for side, src, col in (("", C["sid"], C["dharma"]["personality"]), ("design ", des, C["dharma"]["design"])):
        for b in BODIES + ["Uranus", "Neptune", "Pluto", "Earth"]:
            l = E.norm(src["Sun"] + 180) if b == "Earth" else src.get(b)
            g = col.get(b)
            if l is None or not g: continue
            sides.append(dict(b=b, side=side, s1=sign(l, 1), s9=sign(l, 9), g=g, k=RV.CENTRE_OF[g["gate"]], live=g["gate"] in live_gates))
    feeds = []
    for k in RV.CENTRES:
        if k not in DA["defined"]: continue
        frm = [r for r in sides if r["k"] == k and r["live"]]
        if frm:
            feeds.append(f'<li><b>{lab(k)}</b> ← ' + ", ".join(f'{GLYPH.get(r["b"], "⊕")} {r["side"]}{r["b"]} ({SIGNS[r["s1"]]} → {SIGNS[r["s9"]]}, gate {r["g"]["gate"]}.{r["g"]["line"]})' for r in frm)
                         + ("" if k in BA["defined"] else f' · <em>{W["OPEN_AT_BIRTH"]}</em>') + "</li>")
    n = len(DA["defined"])
    body = (f'<p>{fill(W["CULMINATE"], n=n, centres="centre" if n == 1 else "centres")}</p><ul>{"".join(feeds)}</ul>' if feeds else f'<p>{W["CULMINATE_NONE"]}</p>')
    return f"""<h3 class="rd-tier">From Rashi to Dharma</h3>
      <p>{W["THREAD_INTRO"]} <b>{W["THREAD_CHAIN"]}</b></p>
      <div class="rd-tw"><table><tr><th>Planet</th><th>Rashi (D1)</th><th>Navamsha (D9)</th><th>Dharma gate</th><th>Centre</th><th>Birth gate</th></tr>{tr}</table></div>
      <p class="rd-note">{W["THREAD_NOTE"]}</p>
      <h4>{W["LADDER_H"]}</h4>{ladder}
      <h3 class="rd-tier">{W["RIPEN_H"]}</h3>{ripen}
      <h3 class="rd-tier">{W["INTERLOCK_H"]}</h3>{"".join("<p>" + x + "</p>" for x in lines)}
      <h3 class="rd-tier">{W["CULMINATE_H"]}</h3>{body}
      <p class="rd-kenning">{W["CLOSE"]}</p>"""
