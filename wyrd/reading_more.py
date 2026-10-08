"""The fuller reading: every planet in both zodiacs, the runes and when they
wake, the body's centres and channels and what feeds them, and where a person
works and lives best.

Interpretive sentences come from lib/corpus.json (Saga Devi's register) and
lib/register_ext.json (drafted for her to edit). This file chooses and lays out."""
import html, json, math, os
from . import engine as E
from . import rave as RV

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C0 = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
X = json.load(open(os.path.join(HERE, "lib", "register_ext.json"), encoding="utf-8"))
REG, NAKS, DEEP, HOUSES, GATE_NAME = C0["REGISTER"], C0["NAKSHATRA"], C0["NAK_DEEP"], C0["HOUSES"], C0["GATE_NAME"]
esc = html.escape

GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
         "Uranus": "♅", "Neptune": "♆", "Pluto": "♇", "Rahu": "☊", "Ketu": "☋", "Earth": "⊕", "Ascendant": "↑"}
ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]
LORD_OF_SIGN = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
EXALT = {"Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6, "Rahu": 1, "Ketu": 7}
OWN = {"Sun": {4}, "Moon": {3}, "Mercury": {2, 5}, "Venus": {1, 6}, "Mars": {0, 7}, "Jupiter": {8, 11}, "Saturn": {9, 10}}
CENTRE_KEYS = list(RV.CENTRES)
ORD = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def sign_i(l): return math.floor(E.norm(l) / 30)
def deg(l):
    d = E.norm(l) % 30; m = round((d % 1) * 60)
    return f"{int(d) + (m == 60)}°{0 if m == 60 else m:02d}′"
def lon(l): return f"{E.SIGNS[sign_i(l)]} {deg(l)}"
def pada_of(l): return math.floor((E.norm(l) % E.NAK_ARC) / (E.NAK_ARC / 4)) + 1
def aim_of(l): return X["AIMS"][(E.nak_index(l) * 4 + pada_of(l) - 1) % 4]
def first(t, n=1):
    import re
    t = re.sub(r"<[^>]+>", "", t or "").strip()
    return " ".join(re.split(r"(?<=[.?!])\s+", t)[:n])
def pair(k, v): return f'<div class="rd-pair"><em>{k}</em><span>{v}</span></div>'
def gate_title(g): return REG.get(str(g), {}).get("t") or GATE_NAME.get(str(g), "")


def rune_at(l, asc):
    """The rune a sidereal longitude stands in: two to a whole-sign house, as on the console's wheel."""
    h = E.house_of(l, asc)
    half = "egress" if E.norm(l) % 30 >= 15 else "ingress"
    g, name, gloss = HOUSES[h - 1][half]
    return {"glyph": g, "name": name, "gloss": gloss, "house": h, "half": half}


def dignity(b, s):
    if b in EXALT and EXALT[b] == s: return "exalted"
    if b in EXALT and (EXALT[b] + 6) % 12 == s: return "debilitated"
    if s in OWN.get(b, ()): return "own"
    return None


def positions(C):
    """Every body's sidereal and tropical longitude, plus the design-side sidereal ones."""
    ay = C["ay"]
    sid_des = {b: E.norm(l - ay) for b, l in C["tropDes"].items()}
    sid_des["Earth"] = E.norm(sid_des["Sun"] + 180)
    sid = dict(C["sid"]); sid["Earth"] = E.norm(sid["Sun"] + 180)
    return sid, sid_des


# ---------------- the planets, in both zodiacs ----------------
def planets(C):
    out = [f'<p class="rd-kenning">{X["FRAMES"]["sidereal"]}</p><p class="rd-kenning">{X["FRAMES"]["tropical"]}</p><p>{X["FRAMES"]["both"]}</p>']
    N = C["natal"]
    for b in ORDER:
        s, t = C["sid"][b], C["trop"][b]
        si, ti = sign_i(s), sign_i(t)
        S, T, P = X["SIGNS"][si], X["SIGNS"][ti], X["PLANETS"][b]
        h = E.house_of(s, C["ascS"]); nk = E.nak_index(s); nak = NAKS[nk]; aim = aim_of(s); r = rune_at(s, C["ascS"])
        dg = dignity(b, si)
        if si == ti: agree = X["AGREE"]["same"].format(sign=S["sign"])
        elif S["element"] == T["element"]: agree = X["AGREE"]["element"].format(sid=S["sign"], trop=T["sign"], element=S["element"])
        else: agree = X["AGREE"]["differ"].format(sid=S["sign"], trop=T["sign"], e1=S["element"], e2=T["element"])
        gp, gd = N["personality"].get(b), N["design"].get(b)
        gates = ""
        if gp:
            gates += pair("Gate, conscious", f'{gp["gate"]}.{gp["line"]} {esc(gate_title(gp["gate"]))}: {esc(first(REG.get(str(gp["gate"]), {}).get("l")))}')
        if gd:
            gates += pair("Gate, unconscious", f'{gd["gate"]}.{gd["line"]} {esc(gate_title(gd["gate"]))}')
        out.append(f"""<div class="rd-entry"><h3>{GLYPH[b]} {b} <span class="rd-side p">{lon(s)} sidereal · {lon(t)} tropical</span></h3>
          <div class="rd-hdr">{P["governs"]}</div>
          <div class="rd-gifts"><div class="light"><h5>In your karma and reality · sidereal</h5>
            <p>{P["sid"]} In {S["sign"]}: {S["karma"]}. It works in your {ORD(h)} house, the house of {X["HOUSE_LIFE"][h - 1]}.</p>
            <p>Its star is <b>{nak[0]}</b>, pada {pada_of(s)}, ruled by {nak[1]}: {nak[6]} {aim["says"]}</p></div>
          <div class="dark"><h5>In your experience · tropical</h5>
            <p>{P["trop"]} In tropical {T["sign"]}, {T["felt"]}.</p><p>{agree}</p></div></div>
          {f'<p class="rd-kenning">{X["DIGNITY"][dg]}</p>' if dg else ""}
          {pair("Rune", f'{r["glyph"]} {r["name"]}, {r["gloss"]}. {X["RUNES"][r["name"]]["means"]}')}
          {gates}
          {pair("At its best", P["light"])}{pair("Watch for", P["shadow"])}</div>""")
    return "".join(out)


# ---------------- the runes and when they wake ----------------
def runes(C, dasha):
    asc = C["ascS"]
    holders = {}
    for b in ORDER + ["Ascendant"]:
        l = asc if b == "Ascendant" else C["sid"][b]
        holders.setdefault(rune_at(l, asc)["name"], []).append(b)
    ak = C["karaka"]["Atmakaraka"]; cur, curA = dasha["cur"]["lord"], dasha["curA"]["lord"]
    weight = {"Ascendant": 3, ak: 3, "Moon": 2, "Sun": 2}
    def score(name):
        return sum(weight.get(b, 1) + (2 if b == cur else 0) + (1 if b == curA else 0) for b in holders[name])
    ranked = sorted(holders, key=lambda n: -score(n))
    born = C["jd"]
    def wakes(name):
        b0 = holders[name][0]
        r = rune_at(asc if b0 == "Ascendant" else C["sid"][b0], asc)
        sign = (sign_i(asc) + r["house"] - 1) % 12
        lords = [b for b in holders[name] if b in dict(E.DASHA)] + [LORD_OF_SIGN[sign]]
        lords = list(dict.fromkeys(lords))
        rows = []
        for m in dasha["maha"]:
            if m["lord"] not in lords: continue
            age = max(0, int((m["from"] - born) / E.YEAR))
            state = "now" if m["now"] else ("past" if m["past"] else "ahead")
            rows.append(f'<tr{" class=hi" if m["now"] else ""}><td>{GLYPH[m["lord"]]} {m["lord"]} mahadasha</td><td>age {age}–{int((m["to"] - born) / E.YEAR)}</td><td>{state}</td></tr>')
        sub = [a for a in dasha["antars"] if a["lord"] in lords]
        subs = ", ".join(f'{a["lord"]} {E_year(a["from"])}–{E_year(a["to"])}{" (now)" if a["now"] else ""}' for a in sub)
        return lords, rows, subs
    out = [f"""<p>Twenty-four runes ring your chart, two to each house. A rune is lit when a planet or your Ascendant stands in it.
      These are the ones lit in your chart, the strongest first. A rune is strongest when it holds your Ascendant, your soul-planet,
      your Sun or Moon, or the lord of the period you are in now.</p>
      <p>A rune wakes when the period of a planet standing in it begins, and when the period of the lord of its sign begins.
      Those are the years it shapes your life most.</p>"""]
    for i, name in enumerate(ranked):
        R = X["RUNES"][name]; lords, rows, subs = wakes(name)
        held = ", ".join(f"{GLYPH[b]} {b}" for b in holders[name])
        if i < 4:
            out.append(f"""<div class="rd-entry"><h3>{rune_glyph(name)} {name}
              <span class="rd-side {'p' if i == 0 else 'd'}">{'your keynote rune' if i == 0 else 'a ruling rune'}</span></h3>
              <div class="rd-hdr">Holds {held}</div><p>{R["means"]}</p>
              <div class="rd-gifts"><div class="light"><h5>Lit well</h5><p>{R["light"]}</p></div><div class="dark"><h5>Lit badly</h5><p>{R["shadow"]}</p></div></div>
              {pair("Wakes with", ", ".join(lords))}
              {f'<div class="rd-tw"><table><tr><th>Period</th><th>Years</th><th></th></tr>{"".join(rows)}</table></div>' if rows else ""}
              {pair("Within this period", subs) if subs else ""}
              <div class="rd-ask">{R["call"]}</div></div>""")
        else:
            out.append(pair(f"{rune_glyph(name)} {name}", f'holds {held}. {R["means"]} Wakes with {", ".join(lords)}.'))
    return "".join(out)


def rune_glyph(name):
    for h in HOUSES:
        for half in ("ingress", "egress"):
            if h[half][1] == name: return h[half][0]
    return ""


def E_year(jd):
    from datetime import datetime, timedelta
    return (datetime(2000, 1, 1, 12) + timedelta(days=jd - 2451545.0)).year


# ---------------- the body: centres, channels, and what feeds them ----------------
def body(C):
    N = C["natal"]; sid, sid_des = positions(C)
    live, centres = RV.defines(N)
    out = ["""<p>Your body has nine centres. A defined centre runs on its own steady energy; an open centre takes in and
      amplifies the energy around it. Neither is better. Knowing which is which tells you what is yours and what you are carrying for others.</p>"""]
    rows = []
    for k in CENTRE_KEYS:
        name = RV.CENTRES[k][0]; c = X["CENTRES"][name]; on = name in centres
        rows.append(f"""<div class="rd-body"><h5>{name} · {"defined" if on else "open"}</h5>
          <p><b>{c["does"]}</b> {c["body"]}</p><p>{c["defined"] if on else c["open"]}</p></div>""")
    out.append("".join(rows))
    if not live:
        out.append("<p>No channel is complete at birth: every centre is open, and your energy is a mirror of the people and places around you. Choose them well.</p>")
        return "".join(out)
    out.append("""<h3 class="rd-tier">Your channels and what feeds them</h3>
      <p>A channel is a steady current between two centres. Each of its gates is carried by a planet, and that planet stands
      in one of the twenty-seven mansions, in one of its four padas. The mansion is what feeds the gate: the part of the body
      it rules, the quality of energy it brings, and the aim of its pada.</p>""")
    carriers = {}
    for side, pos in (("personality", sid), ("design", sid_des)):
        for b, g in N[side].items():
            if not isinstance(g, dict) or b not in pos: continue
            carriers.setdefault(g["gate"], []).append((side, b, pos[b]))
    for a, b in live:
        ca, cb = RV.CENTRES[RV.CENTRE_OF[a]][0], RV.CENTRES[RV.CENTRE_OF[b]][0]
        feeds = []
        for g in (a, b):
            for side, pl, l in carriers.get(g, []):
                nk = E.nak_index(l); n = NAKS[nk]; aim = aim_of(l)
                feeds.append(f"""<li><b>Gate {g} {esc(gate_title(g))}</b>, carried by your {"design " if side == "design" else ""}{pl},
                  fed from <b>{n[0]} pada {pada_of(l)}</b> ({aim["aim"]}), which rules the {n[5].lower()}. {n[6]}</li>""")
        out.append(f"""<div class="rd-entry"><h3>Channel {a}–{b} <span class="rd-side p">{ca} to {cb}</span></h3>
          <div class="rd-hdr">{esc(gate_title(a))} · {esc(gate_title(b))}</div>
          <p>{first(REG.get(str(a), {}).get("e"))} {first(REG.get(str(b), {}).get("e"))}</p>
          <ul>{"".join(feeds)}</ul></div>""")
    aims = {}
    for g, cs in carriers.items():
        for _, _, l in cs: aims[aim_of(l)["aim"]] = aims.get(aim_of(l)["aim"], 0) + 1
    top = max(aims, key=aims.get)
    out.append(f'<h3 class="rd-tier">The energy you run on</h3><p>Most of your gates are fed through <b>{top}</b> padas. {next(a["says"] for a in X["AIMS"] if a["aim"] == top)}</p>')
    return "".join(out)


# ---------------- where you thrive ----------------
def thrive(C):
    s = C["sid"]; asc = C["ascS"]
    moon, sun, ak = E.nak_index(s["Moon"]), E.nak_index(s["Sun"]), E.nak_index(asc)
    gana = NAKS[moon][4]
    els = {}
    for b in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        e = X["SIGNS"][sign_i(s[b])]["element"]; els[e] = els.get(e, 0) + 1
    e = X["SIGNS"][sign_i(asc)]["element"]; els[e] = els.get(e, 0) + 2
    strong = max(els, key=els.get); missing = [k for k in ("fire", "earth", "air", "water") if k not in els]
    tenth = (sign_i(asc) + 9) % 12; in10 = [b for b in ORDER if E.house_of(s[b], asc) == 10]
    lord10 = LORD_OF_SIGN[tenth]; l10 = s[lord10]
    D = DEEP
    return f"""
      <p>Where your chart says you work and live best. These are the settings in which your energy runs clean.</p>
      <h3 class="rd-tier">The culture you belong in</h3>
      <p>Your Moon's mansion, {NAKS[moon][0]}, is of the {gana} temperament. {X["GANA"].get(gana, "")}</p>
      <h3 class="rd-tier">The places</h3>
      <p>Your chart leans {strong}. {X["ELEMENTS"][strong]}</p>
      {f'<p>It has no {" or ".join(missing)} among the visible planets. Bring it in on purpose: {" ".join(X["ELEMENTS"][m] for m in missing)}</p>' if missing else ""}
      <h3 class="rd-tier">The work</h3>
      {pair("Your tenth house", f'{E.SIGNS[tenth]}: {X["SIGNS"][tenth]["karma"]}.')}
      {pair("Planets there", ", ".join(f"{GLYPH[b]} {b}" for b in in10) or "none: the house is run by its lord")}
      {pair("Its lord", f'{GLYPH[lord10]} {lord10} in your {ORD(E.house_of(l10, asc))} house, the house of {X["HOUSE_LIFE"][E.house_of(l10, asc) - 1]}')}
      <div class="rd-body"><h5>Your mind works best in · Moon in {NAKS[moon][0]}</h5><p>{X["SETTING"][moon]}</p><p>{D[moon][12]}</p></div>
      <div class="rd-body"><h5>Your purpose works best in · Sun in {NAKS[sun][0]}</h5><p>{X["SETTING"][sun]}</p><p>{D[sun][12]}</p></div>
      <div class="rd-body"><h5>You are seen best in · rising in {NAKS[ak][0]}</h5><p>{X["SETTING"][ak]}</p><p>{D[ak][12]}</p></div>
      <div class="rd-repair"><h5>Where it goes wrong</h5><p>{D[moon][13]}</p></div>"""


# ---------------- the clock, with each period's planet ----------------
def periods(C, dasha):
    rows = []
    born = C["jd"]
    for m in dasha["maha"]:
        b = m["lord"]; l = C["sid"][b]; r = rune_at(l, C["ascS"])
        rows.append(f"""<tr{" class=hi" if m["now"] else ""}><td>{GLYPH[b]} {b}</td><td>{E_year(m["from"])}–{E_year(m["to"])}</td>
          <td>age {max(0, int((m["from"] - born) / E.YEAR))}</td><td>{E.SIGNS[sign_i(l)]}, {ORD(E.house_of(l, C["ascS"]))} house: {X["HOUSE_LIFE"][E.house_of(l, C["ascS"]) - 1]}</td>
          <td>{r["glyph"]} {r["name"]}</td></tr>""")
    return f"""<p>Each period of your life is ruled by one planet. Its themes come forward: the house it stands in becomes the
      life's busiest room, and the rune it stands in wakes.</p>
      <div class="rd-tw"><table><tr><th>Period</th><th>Years</th><th>Begins</th><th>Brings forward</th><th>Wakes</th></tr>{"".join(rows)}</table></div>"""
