"""The Dharma Gates: every gate the Dharma Design holds, read one by one, and how to wake it.

The words come from lib/dharma.json (a gate's practice, each channel, each centre, each line);
the gates' names and 'In short' lines from lib/corpus.json and lib/gate_short.json. This file
only finds what a chart holds and sets it out:

  the four ways a gate wakes        practice, its line, its other half, its time
  channels the Dharma completes     both gates in the Dharma Design
  channels the two designs make     one gate at birth, one in the Dharma: the bridges
  gate by gate                      under each centre, from the Head down
"""
import html, json, math, os
from datetime import date, timedelta

from . import engine as E
from . import rave as RV
from . import reading_more as MORE

HERE = os.path.dirname(__file__)
T = json.load(open(os.path.join(HERE, "..", "lib", "dharma.json"), encoding="utf-8"))
REG = json.load(open(os.path.join(HERE, "..", "lib", "corpus.json"), encoding="utf-8"))["REGISTER"]
SHORT = json.load(open(os.path.join(HERE, "..", "lib", "gate_short.json"), encoding="utf-8"))["GATES"]
GLYPH = MORE.GLYPH
esc = html.escape
ORDER = ["Sun", "Earth", "Moon", "Rahu", "Ketu", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
CROSS = {("personality", "Sun"), ("personality", "Earth"), ("design", "Sun"), ("design", "Earth")}

title = lambda g: REG.get(str(g), {}).get("t", "")
centre = lambda g: RV.CENTRES[RV.CENTRE_OF[g]][0]
key = lambda a, b: f"{min(a, b)}-{max(a, b)}"


def carriers(rave):
    """gate -> [(side, body, line)], bodies in the usual order."""
    out = {}
    for side in ("personality", "design"):
        for b in ORDER:
            v = rave[side].get(b)
            if isinstance(v, dict): out.setdefault(v["gate"], []).append((side, b, v["line"]))
    return out


def _sun_lon(d):
    """The Sun's tropical longitude at noon on a date: the low-precision solar formula, good to a few arcminutes."""
    n = (d - date(2000, 1, 1)).days
    L, g = 280.460 + 0.9856474 * n, math.radians(357.528 + 0.9856003 * n)
    return E.norm(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))


def sun_week(gate, year=2027):
    """The days each year the Sun stands in a gate, as '22–27 March'."""
    days = [date(year, 1, 1) + timedelta(days=i) for i in range(365)]
    inside = [E.gate_of(_sun_lon(d))["gate"] == gate for d in days]
    if not any(inside): return ""
    start = next(i for i in range(365) if inside[i] and not inside[i - 1])
    end = start
    while inside[(end + 1) % 365]: end += 1
    a, b = days[start], days[end % 365]
    if a.month == b.month: return f"{a.day}–{b.day} {a.strftime('%B')}"
    return f"{a.day} {a.strftime('%B')} – {b.day} {b.strftime('%B')}"


def _who(cs):
    parts = []
    for side, b, line in cs:
        parts.append(f"{GLYPH.get(b, '')} {'design ' if side == 'design' else ''}{b} <small>(line {line}, {'unconscious' if side == 'design' else 'conscious'})</small>")
    return ", ".join(parts)


def _channel(a, b, note):
    c = T["CHANNELS"][key(a, b)]
    return f"""<div class="rd-entry dh-ch"><h3>Channel {a}–{b} · {esc(c["name"])} <span class="rd-side p">{centre(a)} to {centre(b)}</span></h3>
      <div class="rd-hdr">{esc(title(a))} · {esc(title(b))} · {note}</div>
      <p>{esc(c["what"])}</p>
      <div class="rd-body"><h5>{T["LIVE"]}</h5><p>{esc(c["live"])}</p></div></div>"""


def body(C, dasha, activation):
    N, Dh = C["natal"], C["dharma"]
    have_n, have_d = RV.gates(N), RV.gates(Dh)
    live_n, cen_n = RV.defines(N)
    live_d, cen_d = RV.defines(Dh)
    cd = carriers(Dh); cn = carriers(N)
    out = [f"<p>{p}</p>" for p in T["INTRO"]]

    out.append(f'<h3 class="rd-tier">{T["WAYS_TITLE"]}</h3><div class="dh-ways">' +
               "".join(f'<div><b>{esc(k)}</b><p>{esc(v)}</p></div>' for k, v in T["WAYS"]) + "</div>")

    # ---- channels ----
    out.append(f'<h3 class="rd-tier">{T["CH_DHARMA_TITLE"]}</h3>')
    if live_d:
        out.append(f"<p>{T['CH_DHARMA_INTRO']}</p>")
        out += [_channel(a, b, T["REPEATS"] if (a, b) in live_n else T["NEW"]) for a, b in live_d]
    else:
        out.append(f"<p>{T['CH_DHARMA_NONE']}</p>")
    bridges = [ch for ch in RV.CHANNELS if ch not in live_n and ch not in live_d and set(ch) <= (have_n | have_d)
               and any(g in have_d for g in ch) and any(g in have_n for g in ch)]
    out.append(f'<h3 class="rd-tier">{T["CH_BRIDGE_TITLE"]}</h3>')
    if bridges:
        out.append(f"<p>{T['CH_BRIDGE_INTRO']}</p>")
        for a, b in bridges:
            side = lambda g: "both" if g in have_n and g in have_d else ("birth" if g in have_n else "dharma")
            out.append(_channel(a, b, f"gate {a} from {side(a)}, gate {b} from {side(b)}"))
    else:
        out.append(f"<p>{T['CH_BRIDGE_NONE']}</p>")

    # ---- gate by gate, under each centre ----
    out.append(f'<h3 class="rd-tier">{T["GATES_TITLE"]}</h3><p>{T["GATES_INTRO"]}</p>')
    for ck, (cname, gates) in RV.CENTRES.items():
        mine = [g for g in sorted(have_d, key=lambda g: (g not in have_n, g)) if RV.CENTRE_OF[g] == ck]
        if not mine: continue
        dd, dn = cname in cen_d, cname in cen_n
        status = (T["CENTRES"][cname]["grow"] if dd and not dn else T["CENTRES"][cname]["release"] if dn and not dd
                  else T["CENTRE_SAME_DEF"] if dd else T["CENTRE_SAME_OPEN"])
        out.append(f'<div class="dh-centre"><h4>{cname} <small>{"defined" if dd else "open"} in the Dharma</small></h4><p>{esc(status)}</p></div>')
        for g in mine:
            out.append(_gate(g, cd[g], have_n, have_d, C, dasha, activation))
    out.append(f'<p class="rd-note">{T["BW"]}</p>')
    return "".join(out)


def _gate(g, cs, have_n, have_d, C, dasha, activation):
    G = T["GATES"].get(str(g), {})
    side0, body0, line0 = next((c for c in cs if c[0] == "personality"), cs[0])
    repeats = g in have_n
    design_only = all(s == "design" for s, _, _ in cs)
    in_cross = any((s, b) in CROSS for s, b, _ in cs)
    lines = []
    for ln in dict.fromkeys(l for _, _, l in cs):
        lines.append(MORE.once(("dh-line", ln), T["LINE"][str(ln)], T["LINE_SHORT"][str(ln)]))
    halves = []
    for a, b in RV.CHANNELS:
        if g not in (a, b): continue
        p = b if g == a else a
        name = T["CHANNELS"][key(a, b)]["name"]
        if p in have_d: halves.append(T["PARTNER_DHARMA"].format(a=a, b=b, name=name))
        elif p in have_n: halves.append(T["PARTNER_BIRTH"].format(g=p, t=esc(title(p)), name=name))
        else: halves.append(MORE.once(("dh-open",), *T["PARTNER_OPEN"]).format(g=p, t=esc(title(p))))
    act = activation(g, line0, C, dasha)
    if act and act["state"] == "ahead" and _age(act, C, dasha) > 90:
        act = dict(act, text=T["LATE"].format(lord=act["lord"]))
    week = sun_week(g)
    do = (f"""<div class="rd-body dh-do"><h5>{T["DO"]}</h5><p>{esc(G["do"])}</p><p class="rd-how">{" ".join(lines)}</p>
          <p>{esc(T["SIGN"].format(sign=G["sign"]))}</p></div>""" if G.get("ok") else "")
    return f"""<div class="rd-entry dh-gate"><h3>Gate {g}.{line0} · {esc(title(g))}
        <span class="rd-side {'d' if design_only else 'p'}">{T["REPEATS"] if repeats else T["NEW"]}</span></h3>
      <div class="rd-hdr">{T["CARRIED"].format(who=_who(cs))}</div>
      {f'<p class="rd-short"><b>In short:</b> {esc(SHORT[str(g)]["short"])}</p>' if SHORT.get(str(g), {}).get("ok") else ""}
      {f'<p class="rd-note">{T["IN_CROSS"]}</p>' if in_cross else ""}
      {do}
      {f'<p class="rd-how">{MORE.once(("dh-design",), *T["DESIGN_ONLY"])}</p>' if design_only else ""}
      <div class="dh-foot"><p>{" ".join(halves)}</p>
      {f'<div class="rd-opens {act["state"].split()[0]}">{GLYPH.get(act["lord"], "⊕")} {act["text"]}</div>' if act else ""}
      {f'<p class="rd-how">{MORE.once(("dh-sun",), *T["SUN_WEEK"]).format(when=week)}</p>' if week else ""}</div></div>"""


def _age(act, C, dasha):
    row = next((r for r in dasha["maha"] if r["lord"] == act["lord"]), None)
    return (row["from"] - C["jd"]) / E.YEAR if row else 0
