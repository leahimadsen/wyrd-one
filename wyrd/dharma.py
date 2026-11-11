"""The Two Designs and The Walk: how a person's Birth Design and Dharma Design work together, and how
they walk from one into the other by practice.

The words come from lib/dharma.json (drafted for The Völva to rewrite); each gate's name, 'In short' line,
gifts and medicine from the register (lib/corpus.json, lib/gate_short.json). This file only sorts what a
chart holds and sets it out:

  meet()          how the two designs meet: the keel (gates and channels both hold), the bridges (a channel
                  with one end in each design), what the dharma builds (channels and centres it adds), what it
                  loosens (centres it leaves open), and the reach (the rest of its gates)
  two_designs()   the section: both designs side by side and drawn on one body, the four meetings, the two
                  crosses, every body birth beside dharma
  walk()          the section: how the walk works; your walk step by step (stand in the Birth Design, cross
                  the bridges, wake the dharma cross, reach, loosen); over a life, by the clock's periods;
                  over a year, by the Sun's days in each gate
"""
import html, json, math, os, re
from datetime import date, timedelta

from . import engine as E
from . import rave as RV
from . import bodygraph as BG
from . import reading_more as MORE

HERE = os.path.dirname(__file__)
T = json.load(open(os.path.join(HERE, "..", "lib", "dharma.json"), encoding="utf-8"))
_CORPUS = json.load(open(os.path.join(HERE, "..", "lib", "corpus.json"), encoding="utf-8"))
REG, GATE_NAME = _CORPUS["REGISTER"], _CORPUS["GATE_NAME"]
SHORT = json.load(open(os.path.join(HERE, "..", "lib", "gate_short.json"), encoding="utf-8"))["GATES"]
GLYPH = MORE.GLYPH
esc = html.escape
ORDER = ["Sun", "Earth", "Moon", "Rahu", "Ketu", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
CROSS = [("personality", "Sun", "Sun"), ("personality", "Earth", "Earth"), ("design", "Sun", "design Sun"), ("design", "Earth", "design Earth")]
KEY_OF = {name: k for k, (name, _) in RV.CENTRES.items()}
WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]

title = lambda g: REG.get(str(g), {}).get("t") or GATE_NAME.get(str(g), "")
centre = lambda g: RV.CENTRES[RV.CENTRE_OF[g]][0]
key = lambda a, b: f"{min(a, b)}-{max(a, b)}"


def short(g):
    s = SHORT.get(str(g), {})
    return s["short"] if s.get("ok") else ""


def num(n): return WORDS[n] if n < len(WORDS) else str(n)


def count(forms, n):
    """forms: [none, one, many with {k}]."""
    return forms[min(n, 2)].replace("{k}", num(n))


def cap(s): return s[:1].upper() + s[1:]


def carriers(rave):
    """gate -> [(side, body, line)], bodies in the usual order."""
    out = {}
    for side in ("personality", "design"):
        for b in ORDER:
            v = rave[side].get(b)
            if isinstance(v, dict): out.setdefault(v["gate"], []).append((side, b, v["line"]))
    return out


# ---------------- the Sun's days in each gate ----------------
def _sun_lon(d):
    """The Sun's tropical longitude at noon on a date: the low-precision solar formula, good to a few arcminutes."""
    n = (d - date(2000, 1, 1)).days
    L, g = 280.460 + 0.9856474 * n, math.radians(357.528 + 0.9856003 * n)
    return E.norm(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))


def sun_days(gate, year=2027):
    """The first and last day each year the Sun stands in a gate, or None."""
    days = [date(year, 1, 1) + timedelta(days=i) for i in range(365)]
    inside = [E.gate_of(_sun_lon(d))["gate"] == gate for d in days]
    if not any(inside): return None
    start = next(i for i in range(365) if inside[i] and not inside[i - 1])
    end = start
    while inside[(end + 1) % 365]: end += 1
    return days[start], days[end % 365]


def sun_week(gate, year=2027, fmt="%B"):
    """The days each year the Sun stands in a gate, as '22–27 March'."""
    span = sun_days(gate, year)
    if not span: return ""
    a, b = span
    if a.month == b.month: return f"{a.day}–{b.day} {a.strftime(fmt)}"
    return f"{a.day} {a.strftime(fmt)} – {b.day} {b.strftime(fmt)}"


# ---------------- how the two designs meet ----------------
def meet(N, Dh):
    """Sort the two designs. bridges: [(channel, birth gate, dharma gate)], a channel neither design completes,
    one end held only at birth and the other only in the dharma. Centres are by name, in body order."""
    gn, gd = RV.gates(N), RV.gates(Dh)
    live_n, cen_n = RV.defines(N)
    live_d, cen_d = RV.defines(Dh)
    bridges = []
    for a, b in RV.CHANNELS:
        if (a, b) in live_n or (a, b) in live_d: continue
        if a in gn and b in gd: bridges.append(((a, b), a, b))
        elif b in gn and a in gd: bridges.append(((a, b), b, a))
    halves = {d for _, _, d in bridges}
    return {"gn": gn, "gd": gd, "live_n": live_n, "live_d": live_d, "cen_n": cen_n, "cen_d": cen_d,
            "keel": sorted(gn & gd), "keel_ch": [c for c in live_d if c in live_n], "grown_ch": [c for c in live_d if c not in live_n],
            "bridges": bridges, "halves": sorted(halves), "reach": sorted(gd - gn - halves),
            "cen_keel": [c for c in cen_d if c in cen_n], "cen_grown": [c for c in cen_d if c not in cen_n],
            "cen_loose": [c for c in cen_n if c not in cen_d]}


def overlay(M):
    """Both designs drawn on one body: gold birth only, violet dharma only, white both, and the bridges."""
    chs = {c: "birth" for c in M["live_n"]}
    chs.update({c: "keel" if c in M["live_n"] else "dharma" for c in M["live_d"]})
    chs.update({c: "bridge" for c, _, _ in M["bridges"]})
    cens = {KEY_OF[n]: "keel" if n in M["cen_d"] else "birth" for n in M["cen_n"]}
    cens.update({KEY_OF[n]: "dharma" for n in M["cen_grown"]})
    K = T["FIG_KEY"]
    key_ = "".join(f'<span><i class="k-{k}"></i>{K[k]}</span>' for k in ("birth", "dharma", "keel", "bridge"))
    return (f'<div class="bg-pair">{BG.plate(chs, cens, T["FIG_LABEL"])}</div>'
            f'<p class="bg-key">{key_}</p>')


def _chips(gates):
    return " · ".join(f"<b>{g}</b> {esc(title(g))}" for g in gates)


def _channel_name(c):
    x = T["CHANNELS"][key(*c)]
    return f"{c[0]}–{c[1]}, {esc(x['name'])}"


# ---------------- the section: The Two Designs ----------------
def two_designs(C):
    N, Dh = C["natal"], C["dharma"]
    M = meet(N, Dh)
    band = T["BAND"]["magenta" if Dh.get("mauve") else Dh["band"]]
    l1, l2 = Dh["profile"].split("/")
    out = [f"<p>{p}</p>" for p in T["TWO_INTRO"]]
    if C.get("unknownTime"): out.append(f'<p class="rd-note">{T["UNKNOWN"]}</p>')
    out.append(f"""<p class="rd-kenning">{T["CROSS_LAW"]}</p>
      {MORE.pair("Birth Design profile", f"{N['profile']} · the equipment as issued")}
      {MORE.pair("Dharma Design profile", f"{Dh['profile']} · {band}")}
      {MORE.pair("The law", f"{Dh['suns']['gap']:.6f}° {'✓' if Dh['suns']['holds'] else '✗'}")}
      <p class="rd-kenning">{T["NUMBERS"]}</p>
      <p>{T["PROFILE"].replace("{l1}", T["LINE_HOW"][l1]).replace("{l2}", T["LINE_HOW"][l2])}</p>""")

    # at a glance, and drawn on one body
    glance = (T["GLANCE"].replace("{n}", str(len(M["gd"])))
              .replace("{keel}", cap(count(T["GLANCE_KEEL"], len(M["keel"]))))
              .replace("{bridge}", count(T["GLANCE_BRIDGE"], len(M["halves"])))
              .replace("{reach}", count(T["GLANCE_REACH"], len(M["reach"])))
              .replace("{grown}", count(T["GLANCE_GROWN"], len(M["grown_ch"])))
              .replace("{made}", count(T["GLANCE_MADE"], len(M["bridges"]))))
    out.append(f'<p class="rd-glance">{glance.strip()}</p>{overlay(M)}<p class="rd-note">{T["FIG"]}</p>')

    # the keel
    out.append(f'<h3 class="rd-tier">{T["KEEL_H"]}</h3>')
    if M["keel"]:
        out.append(f'<p>{T["KEEL"]}</p>{MORE.pair(T["KEEL_GATES"], _chips(M["keel"]))}'
                   + (MORE.pair(T["KEEL_CHANNELS"], "; ".join(_channel_name(c) for c in M["keel_ch"])) if M["keel_ch"] else "")
                   + (MORE.pair(T["KEEL_CENTRES"], ", ".join(M["cen_keel"])) if M["cen_keel"] else ""))
    else:
        out.append(f'<p>{T["KEEL_NONE"]}</p>')

    # the bridges
    out.append(f'<h3 class="rd-tier">{T["BRIDGE_H"]}</h3>')
    if M["bridges"]:
        out.append(f'<p>{T["BRIDGE"]}</p>')
        for c, gb, gd in M["bridges"]:
            x = T["CHANNELS"][key(*c)]
            row = T["BRIDGE_ROW"].format(gb=gb, tb=esc(title(gb)), gd=gd, td=esc(title(gd)))
            out.append(f"""<div class="rd-entry tw-ch"><h4>Channel {c[0]}–{c[1]} · {esc(x["name"])} <span class="rd-side p">{centre(c[0])} to {centre(c[1])}</span></h4>
              <p>{row} {esc(x["what"])}</p></div>""")
    else:
        out.append(f'<p>{T["BRIDGE_NONE"]}</p>')

    # what the dharma builds
    out.append(f'<h3 class="rd-tier">{T["GROW_H"]}</h3>')
    if M["grown_ch"] or M["cen_grown"]:
        out.append(f'<p>{T["GROW"]}</p>')
        for c in M["grown_ch"]:
            x = T["CHANNELS"][key(*c)]
            out.append(f"""<div class="rd-entry tw-ch"><h4>Channel {c[0]}–{c[1]} · {esc(x["name"])} <span class="rd-side p">{centre(c[0])} to {centre(c[1])}</span></h4>
              <p>{esc(x["what"])} <span class="rd-how">{esc(x["live"])}</span></p></div>""")
        out += [f'<p class="tw-cen"><b>{n}.</b> {esc(T["CENTRES"][n]["grow"])}</p>' for n in M["cen_grown"]]
    if not M["grown_ch"]:
        out.append(f'<p>{T["GROW_NONE"]}</p>')

    # what the dharma loosens
    out.append(f'<h3 class="rd-tier">{T["RELEASE_H"]}</h3>')
    out.append(f'<p>{T["RELEASE"]}</p>' + "".join(f'<p class="tw-cen"><b>{n}.</b> {esc(T["CENTRES"][n]["release"])}</p>' for n in M["cen_loose"])
               if M["cen_loose"] else f'<p>{T["RELEASE_NONE"]}</p>')

    # the two crosses
    rows = []
    for side, body, pos in CROSS:
        a, d = N[side][body], Dh[side][body]
        same = a["gate"] == d["gate"]
        s = short(d["gate"])
        rows.append(f"<tr{' class=hi' if same else ''}><td>{GLYPH[body]} {pos}</td><td>{a['gate']}.{a['line']} {esc(title(a['gate']))}</td>"
                    f"<td>{d['gate']}.{d['line']} {esc(title(d['gate']))}{f'<br><small>{esc(s)}</small>' if s else ''}</td>"
                    f"<td>{T['CROSS_HOLDS'] if same else T['CROSS_RIPENS']}</td></tr>")
    out.append(f"""<h3 class="rd-tier">{T["CROSS_H"]}</h3><p>{T["CROSS"]}</p>
      <div class="rd-tw"><table><tr><th></th><th>Birth</th><th>Dharma</th><th></th></tr>{"".join(rows)}</table></div>""")

    # every body, birth beside dharma
    rows = []
    for b in ORDER:
        for side, lab in (("personality", ""), ("design", "design ")):
            a, d = N[side].get(b), Dh[side].get(b)
            if not (a and d): continue
            same = a["gate"] == d["gate"]
            rows.append(f"<tr{' class=hi' if same else ''}><td>{GLYPH.get(b, '')} {lab}{b}</td><td>{a['gate']}.{a['line']}</td>"
                        f"<td>{d['gate']}.{d['line']} {esc(title(d['gate']))}</td><td>{'repeats' if same else ''}</td></tr>")
    out.append(f"""<h3 class="rd-tier">{T["TABLE_H"]}</h3><p>{T["TABLE"]}</p>
      <div class="rd-tw"><table><tr><th>Body</th><th>Birth</th><th>Dharma</th><th></th></tr>{"".join(rows)}</table></div>""")
    return "".join(out)


# ---------------- the section: The Walk ----------------
def medicines(r):
    """The register's flood and freeze, each with its medicine: [("Flood"|"Freeze", medicine sentence)]."""
    text = re.sub(r"<[^>]+>", "", r or "")
    out = []
    for part in re.split(r"(?<=[.!?])\s+(?=(?:Flood|Freeze)\b)", text):
        kind = re.match(r"(Flood|Freeze)", part)
        med = re.search(r"\b[Mm]edicine\b.*", part)
        if kind and med:
            m = med.group(0).strip()
            out.append((kind.group(1), m[0].upper() + m[1:]))
    return out


def _gifts(R):
    if not R.get("l"): return ""
    l, d = R["l"], R["d"]
    return f"""<div class="rd-gifts"><div class="light"><h5>{T["LIGHT"]}</h5><p>{l}</p></div>
        <div class="dark"><h5>{T["DARK"]}</h5><p>{d}</p></div></div>"""


def _who(cs):
    return ", ".join(f"{GLYPH.get(b, '')} {'design ' if side == 'design' else ''}{b} <small>(line {line}, {'unconscious' if side == 'design' else 'conscious'})</small>"
                     for side, b, line in cs)


def _when(g, line, C, dasha, activation):
    act = activation(g, line, C, dasha)
    if not act: return None
    row = next((r for r in dasha["maha"] if r["lord"] == act["lord"]), None)
    age = (row["from"] - C["jd"]) / E.YEAR if row else 0
    late = act["state"] == "ahead" and age > 90
    if late: act = dict(act, text=T["LATE"].format(lord=act["lord"]))
    return dict(act, row=row, late=late, sort=(0 if act["state"] == "running now" else 1 if act["state"] == "open" else 3 if late else 2,
                                               row["from"] if row else 0))


def card(g, cd, M, C, dasha, activation, full=False, lead=""):
    """One dharma gate, ready to practise: what it is in short, its practice and how its line learns it, how you'll know
    it's waking, its other half and when it opens. full (the dharma cross): its two gifts and their medicines too."""
    R, G = REG.get(str(g), {}), T["GATES"].get(str(g), {})
    cs = cd[g]
    side0, body0, line0 = next((c for c in cs if c[0] == "personality"), cs[0])
    w = _when(g, line0, C, dasha, activation)
    repeats = g in M["gn"]
    design_only = all(s == "design" for s, _, _ in cs)
    lines = " ".join(MORE.once(("wk-line", ln), T["LINE"][str(ln)], T["LINE_SHORT"][str(ln)]) for ln in dict.fromkeys(l for _, _, l in cs))
    meds = ""
    if full and R.get("r"):
        ms = medicines(R["r"])                  # a gate whose repair isn't told flood-then-freeze is read whole
        meds = ("".join(f'<p class="rd-med"><b>{T["FLOOD"] if k == "Flood" else T["FREEZE"]}</b> {m}</p>' for k, m in ms) if ms
                else f'<div class="rd-repair"><h5>{T["REPAIR"]}</h5><p>{R["r"]}</p></div>')
    half = ""
    if not full and g in M["reach"]:
        for a, b in RV.CHANNELS:
            if g not in (a, b): continue
            p = b if g == a else a
            if p in M["gd"]: half = T["HALF_DHARMA"].format(a=a, b=b, name=esc(T["CHANNELS"][key(a, b)]["name"])); break
        else:
            p = next((b if g == a else a) for a, b in RV.CHANNELS if g in (a, b))
            half = MORE.once(("wk-open",), T["HALF_OPEN"].format(g=p, t=esc(title(p))), "")
    s = short(g)
    do = (f'<p><b>{T["PRACTICE"]}.</b> {esc(G["do"])} <span class="rd-how">{lines}</span></p>'
          f'<p class="rd-how">{esc(T["SIGN"].format(sign=G["sign"]))}</p>') if G.get("ok") else f'<p class="rd-how">{lines}</p>'
    return f"""<div class="rd-entry wk-gate"><h4>Gate {g}.{line0} · {esc(title(g))}
        <span class="rd-side {'d' if design_only else 'p'}">{T["REPEATS"] if repeats else T["NEW"]}</span></h4>
      <div class="rd-hdr">{T["CARRIED"].format(who=_who(cs))} · {centre(g)}</div>
      {f'<p class="dh-lead">{lead}</p>' if lead else ""}
      {f'<p class="rd-short"><b>In short:</b> {esc(s)}</p>' if s else ""}
      {_gifts(R) if full else ""}{meds}{do}
      {f'<p class="rd-how">{MORE.once(("wk-design",), *T["DESIGN_ONLY"])}</p>' if design_only else ""}
      {f'<p class="rd-how">{half}</p>' if half else ""}
      {f'<div class="rd-opens {w["state"].split()[0]}">{GLYPH.get(w["lord"], "⊕")} {w["text"]}</div>' if w else ""}</div>"""


def walk(C, dasha, activation, asks):
    N, Dh = C["natal"], C["dharma"]
    M = meet(N, Dh)
    A, D = BG.analyse(N), BG.analyse(Dh)
    cd = carriers(Dh)
    out = [f'<p>{T["WALK_INTRO"]}</p>',
           f'<h3 class="rd-tier">{T["HOW_H"]}</h3><div class="dh-ways">'
           + "".join(f'<div><b>{esc(k)}</b><p>{esc(v)}</p></div>' for k, v in T["HOW"]) + "</div>",
           f'<h3 class="rd-tier">{T["LOOKS_H"]}</h3><p>{T["LOOKS"]}</p>',
           f'<h3 class="rd-tier">{T["STEPS_H"]}</h3>']
    done = set()

    # first: stand in the Birth Design
    same = (A["type"], A["authority"]) == (D["type"], D["authority"])
    out.append(f"""<div class="wk-step"><h4>{T["GROUND_H"]}</h4>
      <p>{T["GROUND"].format(type=A["type"], authority=A["authority"].lower(), auth=T["AUTH"][A["authority"]])}</p>
      <p>{(T["GROUND_DHARMA_SAME"] if same else T["GROUND_DHARMA"]).format(dtype=D["type"], dauth=D["authority"].lower())}</p>
      {f'<p>{T["GROUND_KEEL"].format(gates=_chips(M["keel"]))}</p>' if M["keel"] else f'<p>{T["KEEL_NONE"]}</p>'}</div>""")

    # second: cross the bridges
    cross = list(dict.fromkeys(Dh[side][body]["gate"] for side, body, _ in CROSS))
    if M["bridges"]:
        out.append(f'<div class="wk-step"><h4>{T["BRIDGE_STEP_H"]}</h4><p>{T["BRIDGE_STEP"]}</p></div>')
        for c, gb, gd in M["bridges"]:
            x = T["CHANNELS"][key(*c)]
            out.append(f'<p class="wk-bridge"><b>Channel {c[0]}–{c[1]} · {esc(x["name"])}.</b> {T["BRIDGE_LIVE"].format(gb=gb)} '
                       f'{esc(x["live"])}</p>')
            if gd in cross:
                out.append(f'<p class="rd-how">{T["BRIDGE_IN_CROSS"].format(gd=gd)}</p>'); continue
            if gd in done: continue
            done.add(gd)
            out.append(card(gd, cd, M, C, dasha, activation))

    # third: wake the dharma cross
    out.append(f'<div class="wk-step"><h4>{T["CROSS_STEP_H"]}</h4><p>{T["CROSS_STEP"]}</p></div>')
    for side, body, pos in CROSS:
        g = Dh[side][body]["gate"]
        if g in done: continue
        done.add(g)
        same_pos = next((p for s, b, p in CROSS if N[s][b]["gate"] == g), None)
        lead = T["CROSS_SAME"].replace("{pos}", same_pos) if same_pos else ""
        out.append(card(g, cd, M, C, dasha, activation, full=True, lead=lead))
        R = REG.get(str(g), {})
        if R.get("a"):
            asks.append((f"Dharma {pos} · gate {g}.{Dh[side][body]['line']}", R["a"], side == "design"))

    # fourth: reach, in the order the clock opens the gates
    rest = [g for g in M["reach"] if g not in done]
    out.append(f'<div class="wk-step"><h4>{T["REACH_H"]}</h4><p>{T["REACH"] if rest else T["REACH_NONE"]}</p></div>')
    def when_key(g):
        side0, body0, line0 = next((c for c in cd[g] if c[0] == "personality"), cd[g][0])
        w = _when(g, line0, C, dasha, activation)
        return w["sort"] if w else (4, 0)
    for g in sorted(rest, key=lambda g: (when_key(g), g)):
        done.add(g)
        out.append(card(g, cd, M, C, dasha, activation))

    # all the way: loosen
    out.append(f'<div class="wk-step"><h4>{T["LOOSEN_H"]}</h4>'
               + ("".join(f'<p class="tw-cen"><b>{n}.</b> {esc(T["CENTRES"][n]["release"])}</p>' for n in M["cen_loose"])
                  if M["cen_loose"] else f'<p>{T["LOOSEN_NONE"]}</p>') + "</div>")

    out.append(life(M, cd, C, dasha, activation))
    out.append(year(M))
    out.append(f'<div class="rd-ask">{T["ASK"]}</div>')
    asks.append(("The Walk", T["ASK"], False))
    return "".join(out)


def life(M, cd, C, dasha, activation):
    """Every dharma gate under the period of the clock that opens it."""
    by, late = {}, []
    for g in sorted(M["gd"]):
        side0, body0, line0 = next((c for c in cd[g] if c[0] == "personality"), cd[g][0])
        w = _when(g, line0, C, dasha, activation)
        if not w or not w["row"]: continue
        if w["late"]: late.append(g); continue
        by.setdefault(id(w["row"]), (w["row"], []))[1].append(g)
    rows = []
    for r in dasha["maha"]:
        if id(r) not in by: continue
        gates = by[id(r)][1]
        a0 = max(0, int((r["from"] - C["jd"]) / E.YEAR)); a1 = int((r["to"] - C["jd"]) / E.YEAR)
        y0, y1 = MORE.E_year(max(r["from"], C["jd"])), MORE.E_year(r["to"])
        state = T["LIFE_NOW"] if r["now"] else ""
        rows.append(f'<tr{" class=hi" if r["now"] else ""}><td>{GLYPH[r["lord"]]} {r["lord"]}{" · " + state if state else ""}</td>'
                    f'<td>{y0}–{y1}<br><small>age {a0}–{a1}</small></td><td>{_chips(gates)}</td></tr>')
    if late:
        rows.append(f'<tr><td colspan="2"><small>{T["LIFE_LATE"]}</small></td><td>{_chips(late)}</td></tr>')
    return (f'<h3 class="rd-tier">{T["LIFE_H"]}</h3><p>{T["LIFE"]}</p>'
            f'<div class="rd-tw"><table class="wk-life"><tr><th>Period</th><th>When</th><th>Gates it opens</th></tr>{"".join(rows)}</table></div>')


def year(M):
    """Every dharma gate on the calendar, by the days the Sun stands in it."""
    rows = []
    for g in M["gd"]:
        span = sun_days(g)
        if span: rows.append((span[0].timetuple().tm_yday, g))
    trs = "".join(f"<tr><td>{sun_week(g, fmt='%b')}</td><td><b>{g}</b> {esc(title(g))}</td><td>{centre(g)}</td></tr>" for _, g in sorted(rows))
    return (f'<h3 class="rd-tier">{T["YEAR_H"]}</h3><p>{T["YEAR"]}</p>'
            f'<div class="rd-tw"><table class="wk-year"><tr><th>Days</th><th>Gate</th><th>Centre</th></tr>{trs}</table></div>'
            f'<p class="rd-note">{T["BW"]}</p>')
