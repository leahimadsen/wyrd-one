"""The fuller reading: every planet in both zodiacs, the runes and when they
wake, the body's centres and channels and what feeds them, and where a person
works and lives best.

Interpretive sentences come from lib/corpus.json (The Völva's register) and
lib/register_ext.json (drafted for her to edit). This file chooses and lays out."""
import html, json, math, os
from . import engine as E
from . import rave as RV

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C0 = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
X = json.load(open(os.path.join(HERE, "lib", "register_ext.json"), encoding="utf-8"))
PL = json.load(open(os.path.join(HERE, "lib", "placements.json"), encoding="utf-8"))
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


def star_lord(l): return E.DASHA[E.nak_index(l) % 9][0]
def the(p): return f"the {p}" if p in ("Sun", "Moon") else p


def woven(C, b, l):
    """How the planets that rule this one's star and sign lend it their energy."""
    asc = C["ascS"]; si = sign_i(l); nak = NAKS[E.nak_index(l)][0]
    lord = star_lord(l); sl = LORD_OF_SIGN[si]
    who = "your rising sign" if b == "Ascendant" else f"your {b}"
    if lord == b:
        star = X["WEAVE"]["self"].format(b=b)
    else:
        ll = C["sid"][lord]; ln = E.nak_index(ll)
        star = (f"{who[0].upper() + who[1:]} stands in {nak}, a star ruled by {the(lord)}. Your {lord} sits in <b>{NAKS[ln][0]}</b> in sidereal "
                f"{E.SIGNS[sign_i(ll)]}, your {ORD(E.house_of(ll, asc))} house. So {the(lord)} lends {X['PLANETS'][lord]['lends']} to {who}, "
                f"and it arrives coloured by {NAKS[ln][0]}: {NAKS[ln][6]}")
    if sl == b:
        sign = f"It also sits in its own sign, {E.SIGNS[si]}: here it is the host, not a guest."
    else:
        sp = C["sid"][sl]
        sign = (f"{E.SIGNS[si]} is ruled by {the(sl)}, and your {sl} in {E.SIGNS[sign_i(sp)]}, your {ORD(E.house_of(sp, asc))} house, "
                f"sets the climate {who} lives in: {X['PLANETS'][sl]['lends']}.")
    return f'<div class="rd-body"><h5>Woven in · what feeds it</h5><p>{star}</p><p>{sign}</p></div>'


def web(C):
    """Who lends to whom across the whole chart."""
    asc = C["ascS"]; fed = {}
    rows = []
    for b in ORDER:
        l = C["sid"][b]; lord = star_lord(l); fed.setdefault(lord, []).append(b)
        ll = C["sid"][lord]
        rows.append(f"<tr><td>{GLYPH[b]} {b}</td><td>{NAKS[E.nak_index(l)][0]}</td><td>{GLYPH[lord]} {lord}</td>"
                    f"<td>{NAKS[E.nak_index(ll)][0]}, {E.SIGNS[sign_i(ll)]}, {ORD(E.house_of(ll, asc))} house</td></tr>")
    most = max(len(v) for v in fed.values())
    hubs = [k for k in fed if len(fed[k]) == most]
    selfr = [b for b in ORDER if star_lord(C["sid"][b]) == b]
    lines = []
    if len(hubs) == 1 and most >= 2:
        hub = hubs[0]
        lines.append(X["WEAVE"]["hub"].format(b=hub, n=most) + f" It feeds your {', '.join(fed[hub])}.")
    elif most >= 2:
        lines.append(f"Your chart has several feeders of equal weight: " + "; ".join(f"{k} feeds your {' and '.join(fed[k])}" for k in hubs)
                     + ". No single planet runs the web; the life is carried by these together.")
    if selfr:
        lines.append(f"Self-fuelled: {', '.join(selfr)}. These run on their own star and steady the rest.")
    starved = [p for p, _ in E.DASHA if p not in fed]
    if starved:
        lines.append(f"Lending to none of your planets: {', '.join(starved)}. " + ("Its" if len(starved) == 1 else "Their")
                     + " energy works through " + ("its" if len(starved) == 1 else "their") + " own house and sign rather than through other planets.")
    return f"""<h3 class="rd-tier">The web · who feeds whom</h3><p>{X["WEAVE"]["intro"]}</p>
      {"".join(f"<p>{x}</p>" for x in lines)}
      <div class="rd-tw"><table><tr><th>Planet</th><th>Its star</th><th>Fed by</th><th>Where the feeder stands</th></tr>{"".join(rows)}</table></div>"""


# ---------------- the planets, in both zodiacs ----------------
def planets(C):
    out = [f'<p class="rd-kenning">{X["FRAMES"]["sidereal"]}</p><p class="rd-kenning">{X["FRAMES"]["tropical"]}</p><p>{X["FRAMES"]["both"]}</p>']
    out.append(web(C))
    N = C["natal"]
    for b in ORDER:
        s, t = C["sid"][b], C["trop"][b]
        si, ti = sign_i(s), sign_i(t)
        S, T, P = X["SIGNS"][si], X["SIGNS"][ti], X["PLANETS"][b]
        h = E.house_of(s, C["ascS"]); nk = E.nak_index(s); nak = NAKS[nk]; aim = aim_of(s); r = rune_at(s, C["ascS"])
        dg = dignity(b, si)
        shift = PL["SAME"] if si == ti else PL["SHIFT"][ti]
        tail = lambda line: line.split(": ", 1)[-1]
        felt = "" if si == ti else (f'<p><b>Your {b}, felt:</b> {tail(PL["PIS"][b][ti])}<br>'
                                    f'<b>Your {b}, lived:</b> {tail(PL["PIS"][b][si])}</p>')
        gp, gd = N["personality"].get(b), N["design"].get(b)
        gates = ""
        if gp:
            gates += pair("Gate, conscious", f'{gp["gate"]}.{gp["line"]} {esc(gate_title(gp["gate"]))}: {esc(first(REG.get(str(gp["gate"]), {}).get("l")))}')
        if gd:
            gates += pair("Gate, unconscious", f'{gd["gate"]}.{gd["line"]} {esc(gate_title(gd["gate"]))}')
        out.append(f"""<div class="rd-entry"><h3>{GLYPH[b]} {b} <span class="rd-side p">tropical {lon(t)} → sidereal {lon(s)}</span></h3>
          <div class="rd-hdr">{P["governs"]}</div>
          <div class="rd-gifts"><div class="light"><h5>How it feels · tropical {T["sign"]}</h5>
            <p>{PL["SIGN_TROP"][ti]}</p><p><b>{PL["PIS"][b][ti]}</b></p><p>{P["trop"]}</p></div>
          <div class="dark"><h5>What it brings · sidereal {S["sign"]}</h5>
            <p>{PL["SIGN_SID"][si]}</p><p><b>{PL["PIS"][b][si]}</b></p>
            <p>{P["sid"]} It works in your {ORD(h)} house, the house of {X["HOUSE_LIFE"][h - 1]}.</p>
            <p>Its star is <b>{nak[0]}</b>, pada {pada_of(s)}, ruled by {nak[1]}: {nak[6]} {aim["says"]}</p></div></div>
          <div class="rd-repair"><h5>{"The shift · " + T["sign"] + " into " + S["sign"] if si != ti else "One sign in both zodiacs · " + S["sign"]}</h5><p>{shift}</p>{felt}</div>
          {woven(C, b, s)}
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
def diagrams(C):
    """Both bodygraphs side by side: the birth design and the Dharma design, with how the energy runs in each."""
    from . import bodygraph as BG
    A = BG.analyse(C["natal"]); D = BG.analyse(C["dharma"]) if C.get("dharma") else None
    name = lambda k: RV.CENTRES[k][0]
    def route(R):
        if "throat" not in R["defined"]: return "Your throat is open: energy reaches expression through others and through the moment."
        if R["motors"]: return f'Energy rises from your {" and ".join(name(m) for m in R["motors"])} and surfaces at your throat as voice and action.'
        return "Your throat is defined, but no motor reaches it: what you say and do is moved by the energy around you."
    figs = BG.svg(A, "birth", "Your birth design") + (BG.svg(D, "dharma", "Your Dharma design") if D else "")
    return f"""<h3 class="rd-tier">Your two bodygraphs</h3>
      <p>The same nine centres, drawn twice: as you were born, and as your Dharma design ripens. Filled centres are defined.
      Lit lines are your live channels, and the arrows show which way the energy runs along each one: up from the motors
      toward the throat, where it becomes voice and action.</p>
      <div class="bg-pair">{figs}</div>
      <p><b>Birth design:</b> {route(A)}</p>{f"<p><b>Dharma design:</b> {route(D)}</p>" if D else ""}"""


def body(C):
    N = C["natal"]; sid, sid_des = positions(C)
    live, centres = RV.defines(N)
    out = ["""<p>Your body has nine centres. A defined centre runs on its own steady energy; an open centre takes in and
      amplifies the energy around it. Neither is better. Knowing which is which tells you what is yours and what you are carrying for others.</p>"""]
    out.append(diagrams(C))
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


def rising(C):
    """The Ascendant in both zodiacs: how you meet the world, and what the world hands you on arrival."""
    s, t = C["ascS"], C["ascT"]
    si, ti = sign_i(s), sign_i(t)
    shift = PL["SAME"] if si == ti else PL["SHIFT"][ti]
    return f"""<div class="rd-gifts"><div class="light"><h5>How you meet the world · tropical {E.SIGNS[ti]} rising</h5>
        <p>{PL["SIGN_TROP"][ti]}</p></div>
      <div class="dark"><h5>What the world hands you · sidereal {E.SIGNS[si]} rising</h5><p>{PL["SIGN_SID"][si]}</p></div></div>
      <div class="rd-repair"><h5>{"The shift · " + E.SIGNS[ti] + " into " + E.SIGNS[si] if si != ti else "One sign in both zodiacs"}</h5><p>{shift}</p></div>
      {woven(C, "Ascendant", s)}"""


# ---------------- the Engine, fleshed out ----------------
MX = json.load(open(os.path.join(HERE, "lib", "matrix.json"), encoding="utf-8"))
ENG = C0["ENGINE"]


def engine_more(C, dasha):
    """More of the Moon's mansion: its full profile, the Moon's phase, what feeds it, the life's first period, the nine-star cycle."""
    m = C["sid"]["Moon"]; mi = E.nak_index(m); D = DEEP[mi]; n = NAKS[mi]; aim = aim_of(m); h = E.house_of(m, C["ascS"])
    phase = MX["PHASE"][int(E.norm(m - C["sid"]["Sun"]) // 45)]
    first_p = dasha["maha"][0]
    groups = {}
    for k in range(27): groups.setdefault(((k - mi) % 27) % 9, []).append(NAKS[k][0])
    taras = "".join(f'<tr{" class=hi" if i in (1, 3, 5, 7, 8) else ""}><td>{t["name"]} <small>({t["means"]})</small></td><td>{", ".join(groups[i])}</td><td>{t["says"]}</td></tr>'
                    for i, t in enumerate(MX["TARA"]))
    return f"""
      <h3 class="rd-tier">The star in full</h3>
      {pair("Stars", D[1])}{pair("Temperament", D[2])}{pair("Animal", D[3])}{pair("Qualities", D[4])}
      {pair("Constitution", D[5])}{pair("Class", D[6])}{pair("Aim of the mansion", D[7])}{pair("Motion", D[8])}
      {pair("Sounds", D[9])}{pair("The body", n[5])}
      <h3 class="rd-tier">Where the engine runs</h3>
      <p>Your Moon is in pada {pada_of(m)} of {n[0]}. {aim["says"]}</p>
      <p>It works in your {ORD(h)} house, the house of {X["HOUSE_LIFE"][h - 1]}. {MX["MOON_HOUSE"][h - 1]}</p>
      <div class="rd-body"><h5>The Moon you were born under · {phase["name"]}</h5><p>{phase["says"]}</p></div>
      {woven(C, "Moon", m)}
      <h3 class="rd-tier">The clock it starts</h3>
      <p>Your Moon's mansion sets the order of your whole life's periods. You were born in the <b>{first_p["lord"]}</b> period,
      with {dasha["balance"]:.1f} of its {first_p["years"]} years still to run, because the Moon had already crossed
      {dasha["through"] * 100:.0f}% of {n[0]}. Every period after follows from that.</p>
      <h3 class="rd-tier">The nine kinds of star</h3><p>{MX["TARA_INTRO"]}</p>
      <div class="rd-tw"><table><tr><th>Kind</th><th>Mansions</th><th>For you</th></tr>{taras}</table></div>"""


# ---------------- the Matrix: Saturn and the Moon ----------------
def matrix(C, dasha):
    asc = C["ascS"]; s = C["sid"]["Saturn"]; m = C["sid"]["Moon"]
    si = sign_i(s); h = E.house_of(s, asc); ni = E.nak_index(s); n = NAKS[ni]; e = ENG[ni]
    mh = E.house_of(m, asc); from_moon = (sign_i(s) - sign_i(m)) % 12
    looks = [((h - 1 + k) % 12) + 1 for k in (2, 6, 9)]
    born = C["jd"]
    sat = [x for x in dasha["maha"] if x["lord"] == "Saturn"]
    sat_rows = "".join(f'<li>Saturn period: {E_year(x["from"])}–{E_year(x["to"])}, age {max(0, int((x["from"] - born) / E.YEAR))} to {int((x["to"] - born) / E.YEAR)}'
                       f'{" (running now)" if x["now"] else ""}</li>' for x in sat)
    sat_sub = [a for a in dasha["antars"] if a["lord"] == "Saturn"]
    by = E_year(born)
    returns = ", ".join(f"{by + round(29.46 * k)} (age {round(29.46 * k)})" for k in (1, 2, 3))
    return f"""
      <p>{MX["INTRO"]}</p>
      <h3 class="rd-tier">How your matrix is built · Saturn in {E.SIGNS[si]}, {ORD(h)} house</h3>
      <p><b>{MX["SATURN_SIGN"][si]}</b></p>
      <p>{MX["SATURN_HOUSE"][h - 1]}</p>
      <div class="rd-body"><h5>Its star · {n[0]}, pada {pada_of(s)}</h5>
        <p>{n[6]} The power of this star is {e[1]}, {e[2]}. {e[6]}</p><p>{aim_of(s)["says"]}</p></div>
      {woven(C, "Saturn", s)}
      <h3 class="rd-tier">Where it presses</h3>
      <p>{MX["SATURN_LOOKS"]}</p>
      <ul>{"".join(f"<li>Your {ORD(x)} house: {X['HOUSE_LIFE'][x - 1]}.</li>" for x in looks)}</ul>
      <h3 class="rd-tier">The world from the Moon</h3><p>{MX["MOON_INTRO"]}</p>
      <p>{MX["MOON_HOUSE"][mh - 1]}</p>
      <p>Your Moon is in {NAKS[E.nak_index(m)][0]} in sidereal {E.SIGNS[sign_i(m)]}: {X["SIGNS"][sign_i(m)]["karma"]}; {X["SIGNS"][sign_i(m)]["felt"]}.</p>
      <h3 class="rd-tier">Saturn and the Moon together</h3>
      <p><b>{MX["SATURN_FROM_MOON"][from_moon]}</b></p>
      <h3 class="rd-tier">When the matrix is rebuilt</h3>
      <p>{MX["RETURNS"]} Your Saturn returns fall around {returns}.</p>
      <ul>{sat_rows or "<li>No Saturn period falls in the 120-year cycle shown.</li>"}</ul>
      {f'<p>Inside your current period, the Saturn sub-period runs {E_year(sat_sub[0]["from"])}–{E_year(sat_sub[0]["to"])}{" and is running now" if sat_sub[0]["now"] else ""}: the matrix is reviewed then.</p>' if sat_sub else ""}"""


# ---------------- the karakas in depth ----------------
KA = json.load(open(os.path.join(HERE, "lib", "karakas.json"), encoding="utf-8"))


def karakas_more(C, dasha):
    asc = C["ascS"]; K = C["karaka"]; born = C["jd"]
    nav = lambda l: sign_i(E.varga(l, 9))
    out = [f'<h3 class="rd-tier">Your cabinet, one by one</h3><p>{KA["INTRO"]}</p>']
    for role, b in K.items():
        R = KA["ROLES"][role]; l = C["sid"][b]; si = sign_i(l); h = E.house_of(l, asc); ni = E.nak_index(l); n = NAKS[ni]
        periods = "; ".join(f'{E_year(m["from"])}–{E_year(m["to"])} ' + ("(from birth)" if m["from"] <= born else f'(age {int((m["from"] - born) / E.YEAR)})')
                            + (" · now" if m["now"] else "")
                            for m in dasha["maha"] if m["lord"] == b and (m["from"] - born) / E.YEAR < 100)
        extra = ""
        if role == "Atmakaraka":
            extra = (f'<div class="rd-body"><h5>Karakamsa · {E.SIGNS[nav(l)]}</h5><p>{KA["KARAKAMSA_INTRO"]} {KA["KARAKAMSA"][nav(l)]}</p></div>'
                     + woven(C, b, l))
        elif role == "Amatyakaraka":
            extra = pair("The work", KA["WORK"][si] + (" It holds the same sign in the navamsa, so this is doubly true." if nav(l) == si
                                                         else f' In the navamsa: {KA["WORK"][nav(l)].split(": ", 1)[-1]}'))
        elif role == "Darakaraka":
            extra = pair("The partner", KA["PARTNER"][si] + (" It holds the same sign in the navamsa, so this is doubly true." if nav(l) == si
                                                               else f' In the navamsa, deeper in the bond: {KA["PARTNER"][nav(l)].split(": ", 1)[-1]}'))
        out.append(f"""<div class="rd-entry"><h3>{role} · {GLYPH[b]} {b} <span class="rd-side p">{deg(l)} into {E.SIGNS[si]}</span></h3>
          <div class="rd-hdr">{R["rules"]}</div>
          <p>{R["asks"]}</p>
          <p><b>{KA["ROLE_PLANET"][role][b]}</b></p>
          <p>It stands in sidereal {E.SIGNS[si]}, your {ORD(h)} house, the house of {X["HOUSE_LIFE"][h - 1]}: this part of your life plays out there. Its star is {n[0]}, pada {pada_of(l)}: {n[6]}</p>
          {extra}
          {pair("In your life", R["people"])}
          {pair("Its periods", periods or "its period falls after age 100")}</div>""")
    ak, amk, dk = C["sid"][K["Atmakaraka"]], C["sid"][K["Amatyakaraka"]], C["sid"][K["Darakaraka"]]
    close = lambda a, b: (sign_i(a) - sign_i(b)) % 12 in (0, 6)
    notes = [KA["PAIR_AK_AMK"]] if close(ak, amk) else []
    if close(ak, dk): notes.append(KA["PAIR_AK_DK"])
    if notes: out.append('<h3 class="rd-tier">How the cabinet works together</h3>' + "".join(f"<p>{x}</p>" for x in notes))
    return "".join(out)
