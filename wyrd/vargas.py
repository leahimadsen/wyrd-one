"""The divisional charts (vargas), the same arithmetic as static/vargas.js (tests/vargas_check.py
proves it), and the thread from Rashi to Dharma for the paid reading: a planet in the D1, its
navamsa sign, the gate it lights in the Dharma Design, and the centre that gate feeds."""
import math
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
RANK = {"exalted": 3, "own sign": 2, "": 1, "debilitated": 0}


def dignity_in(b, s):
    if b not in EXALT: return ""
    if EXALT[b] == s: return "exalted"
    if (EXALT[b] + 6) % 12 == s: return "debilitated"
    if s in OWN[b]: return "own sign"
    return ""


def ordinal(n): return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def thread(C):
    """From Rashi to Dharma: the reading's version of WyrdVargas.thread."""
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
    tr = "".join(
        f'<tr{" class=hi" if r["s1"] == r["s9"] else ""}><td>{GLYPH[r["b"]]} {r["b"]}</td>'
        f'<td>{SIGNS[r["s1"]]}{(" · " + ordinal(house(r["s1"])) + " house") if house(r["s1"]) else ""}{" · " + r["d1"] if r["d1"] else ""}</td>'
        f'<td>{SIGNS[r["s9"]]}{" · " + r["d9"] if r["d9"] else ""}{" ↑" if r["move"] == "rises" else " ↓" if r["move"] == "falls" else ""}</td>'
        f'<td>{r["g"]["gate"]}.{r["g"]["line"]}</td><td>{lab(r["k"])}{" · in a channel" if r["live"] else ""}</td>'
        f'<td>{NP[r["b"]]["gate"]}.{NP[r["b"]]["line"]}</td></tr>' for r in rows)
    vargo = [r for r in rows if r["s1"] == r["s9"]]
    rise = [r for r in rows if r["move"] == "rises"]; fall = [r for r in rows if r["move"] == "falls"]
    ak = C["karaka"]["Atmakaraka"]; kar = sign(C["sid"][ak], 9)
    lines = []
    lines.append(f'<p><b>Holding steady (vargottama):</b> {", ".join(GLYPH[r["b"]] + " " + r["b"] + " in " + SIGNS[r["s1"]] for r in vargo)}. '
                 "The same sign in the life and in its ripening: what these planets are at birth is what they become, and the gates they light "
                 "in your Dharma Design are fed by that one sign twice over.</p>" if vargo else
                 "<p>No planet holds its sign from Rashi to navamsa: every planet ripens into something other than what it starts as.</p>")
    if rise: lines.append(f'<p><b>Ripening upward:</b> {", ".join(GLYPH[r["b"]] + " " + r["b"] + " (" + SIGNS[r["s1"]] + " → " + SIGNS[r["s9"]] + (", " + r["d9"] if r["d9"] else "") + ")" for r in rise)}. '
                          "What is ordinary or hard-won in the life matures into strength.</p>")
    if fall: lines.append(f'<p><b>Ripening slowly:</b> {", ".join(GLYPH[r["b"]] + " " + r["b"] + " (" + SIGNS[r["s1"]] + " → " + SIGNS[r["s9"]] + (", " + r["d9"] if r["d9"] else "") + ")" for r in fall)}. '
                          "Strong in the life, these take longer to bear their fruit; the work they ask comes later.</p>")
    lines.append(f"<p><b>The soul's direction (karakamsa):</b> your Soul-Planet, {GLYPH.get(ak, '')} {ak}, ripens in <b>{SIGNS[kar]}</b>, ruled by {LORD[kar]}. "
                 "In Jyotish this is the sign the soul is travelling toward.</p>")
    if not unknown:
        a9 = sign(C["ascS"], 9); l9 = LORD[a9]
        lines.append(f"<p><b>The ripening's own rising:</b> your navamsa rises in <b>{SIGNS[a9]}</b>. Its lord, {GLYPH[l9]} {l9}, stands in your Rashi's "
                     f"{ordinal(house(sign(C['sid'][l9], 1)))} house: that is the part of life where the ripening is worked out.</p>")
    e1, e9 = [0] * 4, [0] * 4
    for r in rows: e1[r["s1"] % 4] += 1; e9[r["s9"] % 4] += 1
    t1, t9 = ELEMENT[e1.index(max(e1))], ELEMENT[e9.index(max(e9))]
    lines.append((f"<p><b>The element holds:</b> {t1} leads in both the Rashi and the navamsa " if t1 == t9 else
                  f"<p><b>The element shifts</b> from {t1} in the Rashi to {t9} in the navamsa ")
                 + f"({', '.join(f'{x} {e1[i]}→{e9[i]}' for i, x in enumerate(ELEMENT))}).</p>")
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
                         + ("" if k in BA["defined"] else " · <em>open at birth: a current the life grows into</em>") + "</li>")
    body = (f"<p>Your Dharma Design defines {len(DA['defined'])} centre{'s' if len(DA['defined']) != 1 else ''}. "
            f"Each is fed by planets whose navamsa gates sit in a live channel there; “design” planets come from the design moment, read the same way.</p><ul>{''.join(feeds)}</ul>" if feeds else
            "<p>Your Dharma Design completes no channel: its currents run through single gates, each one open-ended, met by other people and by the sky.</p>")
    return f"""<h3 class="rd-tier">From Rashi to Dharma</h3>
      <p>Your Rashi (D1) is the life as it is lived, in the sidereal zodiac. Multiply every position by nine and you have the navamsa (D9), the chart of
      what the life ripens into. Your Dharma Design is built from exactly these positions, laid on the gate wheel, so one thread runs through all three:
      a planet in your Rashi, its navamsa sign, the gate it lights in your Dharma Design, and the centre that gate feeds.</p>
      <div class="rd-tw"><table><tr><th>Planet</th><th>Rashi (D1)</th><th>Navamsa (D9)</th><th>Dharma gate</th><th>Centre</th><th>Birth gate</th></tr>{tr}</table></div>
      <p class="rd-note">The birth-moment planets. The design side of the Dharma Design runs the same thread from the design moment. ↑ gains dignity in the navamsa; ↓ loses it.</p>
      <h3 class="rd-tier">How they interlock</h3>{''.join(lines)}
      <h3 class="rd-tier">Where it culminates in the body</h3>{body}"""
