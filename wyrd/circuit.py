"""The Current Between You: two people's Birth and Dharma Designs read together, four designs to four.

A channel runs between two designs when one holds one end and the other holds the other. Between two people
there are four designs, so the currents come in kinds:

  body     birth to birth: one end in each Birth Design (as "electromagnetic" in How Your Bodies Meet)
  feed     one person's birth gate completes a gate the other holds only in their Dharma Design, which that
           other person does not carry at all: what one was born with feeds what the other is growing into
  dd       dharma to dharma: one end held only in each person's Dharma Design, neither able to complete it alone
  kin      a channel both Dharma Designs complete, each on its own
  example  a gate one was born with that the other holds only in their Dharma Design

The words come from lib/together.json (drafted for The Völva to rewrite) and the channel and gate texts from
lib/dharma.json and the register; this file only sorts the gates and draws the circuit."""
import html, json, math, os

from . import rave as RV
from . import bodygraph as BG
from . import dharma as DH

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "together.json"), encoding="utf-8"))
esc = html.escape
title = DH.title


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def gates(p):
    return RV.gates(p["C"]["natal"]), RV.gates(p["C"]["dharma"])


def currents(A, B):
    """Every channel that runs between two people's four designs, by kind:
    {"body": [(ch, a's gate, b's gate)], "ab": A's body into B's dharma, "ba": B's body into A's dharma,
     "dd": between the dharmas, "kin": [ch], "own_a"/"own_b": each person's own bridges (counted),
     "ex_a": gates B was born with that A's dharma reaches for, "ex_b": the other way}."""
    ab, ad = gates(A); bb, bd = gates(B)
    a_all, b_all = ab | ad, bb | bd
    out = {"body": [], "ab": [], "ba": [], "dd": []}
    for c in RV.CHANNELS:
        for x, y in (c, c[::-1]):                        # x: A's end, y: B's end
            if x in ab and x not in bb and y in bb and y not in ab:
                out["body"].append((c, x, y))
            elif x in ab and x not in b_all and y in bd and y not in bb:
                out["ab"].append((c, x, y))
            elif y in bb and y not in a_all and x in ad and x not in ab:
                out["ba"].append((c, x, y))
            elif x in ad and x not in ab and y in bd and y not in bb and x not in b_all and y not in a_all:
                out["dd"].append((c, x, y))
    live_a, _ = RV.defines(A["C"]["dharma"]); live_b, _ = RV.defines(B["C"]["dharma"])
    out["kin"] = [c for c in live_a if c in live_b]
    out["own_a"] = len(DH.meet(A["C"]["natal"], A["C"]["dharma"])["bridges"])
    out["own_b"] = len(DH.meet(B["C"]["natal"], B["C"]["dharma"])["bridges"])
    out["ex_a"] = sorted(bb & (ad - ab))
    out["ex_b"] = sorted(ab & (bd - bb))
    return out


def shape(X):
    fa, fb = len(X["ab"]), len(X["ba"])
    if fa and fb: return "loop", None
    if fa or fb: return "one", "ab" if fa else "ba"
    if X["dd"]: return "dharma", None
    if X["body"]: return "body", None
    return "none", None


# ---------------- the drawing: four designs as one circuit ----------------
W, H, NW, NH = 520, 300, 170, 58
NODE = {"Ad": (115, 58), "Bd": (405, 58), "Ab": (115, 242), "Bb": (405, 242)}


def _edge(c, d):
    """Where a line from node centre c toward d leaves the node's box."""
    dx, dy = d[0] - c[0], d[1] - c[1]
    t = min((NW / 2 + 6) / abs(dx) if dx else 9e9, (NH / 2 + 6) / abs(dy) if dy else 9e9)
    return c[0] + dx * t, c[1] + dy * t


def diagram(A, B, X):
    n = NODE; out, defs = [], []
    wires = [("Ab", "Bb", "body", len(X["body"]), False, .5), ("Ad", "Bd", "dd", len(X["dd"]), False, .5),
             ("Ab", "Bd", "feed", len(X["ab"]), True, .3), ("Bb", "Ad", "feed", len(X["ba"]), True, .3),
             ("Ab", "Ad", "own", X["own_a"], True, .5), ("Bb", "Bd", "own", X["own_b"], True, .5)]
    for i, (s, e, kind, k, arrow, at) in enumerate(wires):
        (x1, y1), (x2, y2) = _edge(n[s], n[e]), _edge(n[e], n[s])
        if not k:
            out.append(f'<line class="cx-wire off" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
            continue
        sw = 2 + 1.6 * min(k, 6)
        cls = kind
        if kind in ("feed", "own"):
            defs.append(f'<linearGradient id="cxg{i}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                        f'<stop offset="0" stop-color="#c9a35a"/><stop offset="1" stop-color="#9b84f0"/></linearGradient>')
        stroke = f' stroke="url(#cxg{i})"' if kind in ("feed", "own") else ""
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)); s_ = 5 + sw / 2
        L = math.hypot(x2 - x1, y2 - y1); cut = s_ * 1.2 if arrow else 0           # the line stops where its arrowhead starts
        ex, ey = x2 - (x2 - x1) * cut / L, y2 - (y2 - y1) * cut / L
        out.append(f'<line class="cx-wire {cls}"{stroke} stroke-width="{sw:.1f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
        if arrow:
            out.append(f'<path class="cx-tip" d="M{-s_ * 1.4:.1f},{-s_:.1f} L0,0 L{-s_ * 1.4:.1f},{s_:.1f} Z" transform="translate({x2:.1f},{y2:.1f}) rotate({ang:.0f})"/>')
        mx, my = x1 + (x2 - x1) * at, y1 + (y2 - y1) * at
        out.append(f'<text class="cx-n" x="{mx:.1f}" y="{my + 5:.1f}">{k}</text>')
    nodes = []
    for k_, (x, y) in n.items():
        who = A if k_[0] == "A" else B
        kind = "dharma" if k_[1] == "d" else "birth"
        nodes.append(f'<g class="cx-node {kind}"><rect x="{x - NW / 2}" y="{y - NH / 2}" width="{NW}" height="{NH}" rx="4"/>'
                     f'<text class="who" x="{x}" y="{y - 6}">{who["name"]}</text><text x="{x}" y="{y + 15}">{T["CIRCUIT_NODE"][kind]}</text></g>')
    K = T["CIRCUIT_KEY"]
    key = "".join(f'<span><i class="k-{k}"></i>{K[k]}</span>' for k in ("body", "feed", "dd", "own"))
    return (f'<figure class="cx-fig rd-plate"><svg viewBox="0 0 {W} {H}" role="img" aria-label="The four designs as a circuit">'
            f'<defs>{"".join(defs)}</defs><g>{"".join(out)}</g><g>{"".join(nodes)}</g></svg></figure>'
            f'<p class="bg-key">{key}</p><p class="rd-note">{T["CIRCUIT_FIG"]}</p>')


def body_plate(X):
    chs = {c: "body" for c, _, _ in X["body"]}
    chs.update({c: "feed" for c, _, _ in X["ab"] + X["ba"]})
    chs.update({c: "dd" for c, _, _ in X["dd"]})
    chs.update({c: "kin" for c in X["kin"]})
    if not chs: return ""
    used = [k for k in ("body", "feed", "dd", "kin") if k in chs.values()]
    K = T["CIRCUIT_KEY"]
    return (f'<div class="bg-pair">{BG.plate(chs, {}, T["CIRCUIT_BODY_LABEL"])}</div>'
            f'<p class="bg-key">{"".join(f"<span><i class=k-{k}></i>{K[k]}</span>" for k in used)}</p>')


# ---------------- the words ----------------
def _ch(c):
    x = DH.T["CHANNELS"][DH.key(*c)]
    return f'Channel {c[0]}–{c[1]} · {esc(x["name"])}', esc(x["what"])


def pair(A, B, X, two=True):
    """Two people, in full. A and B carry an escaped "name"."""
    out = []
    kind, way = shape(X)
    a, b = (A, B) if way != "ba" else (B, A)
    out.append(f'<p class="rd-glance">{fill(T["CIRCUIT_SHAPE"][kind], a=a["name"], b=b["name"])}</p>')
    out.append(diagram(A, B, X))
    if two:
        out.append(f'<p>{fill(T["CIRCUIT_BODY"], n=len(X["body"])) if X["body"] else T["CIRCUIT_BODY_NONE"]}</p>')
    for k, P, Q in (("ab", A, B), ("ba", B, A)):
        if not X[k]: continue
        out.append(f'<h3 class="rd-tier">{fill(T["CIRCUIT_FEED_H"], a=P["name"], b=Q["name"])}</h3><p>{fill(T["CIRCUIT_FEED"], a=P["name"], b=Q["name"])}</p>')
        for c, x, y in X[k]:
            ga, gb = (x, y) if k == "ab" else (y, x)              # the giver's gate, the grower's
            head, what = _ch(c)
            G = DH.T["GATES"].get(str(gb), {})
            do = f' <span class="rd-how">{fill(T["CIRCUIT_FEED_DO"], b=Q["name"], do=esc(G["do"]))}</span>' if G.get("ok") else ""
            out.append(f'<div class="rd-entry tw-ch"><h4>{head}</h4><p>{fill(T["CIRCUIT_FEED_ITEM"], a=P["name"], b=Q["name"], ga=ga, ta=esc(title(ga)), gb=gb, tb=esc(title(gb)))} '
                       f'{what}{do}</p></div>')
    if X["dd"]:
        out.append(f'<h3 class="rd-tier">{T["CIRCUIT_DD_H"]}</h3><p>{T["CIRCUIT_DD"]}</p>')
        for c, x, y in X["dd"]:
            head, what = _ch(c)
            out.append(f'<div class="rd-entry tw-ch"><h4>{head}</h4><p>{fill(T["CIRCUIT_DD_ITEM"], a=A["name"], b=B["name"], ga=x, ta=esc(title(x)), gb=y, tb=esc(title(y)))} {what}</p></div>')
    if X["kin"]:
        out.append(f'<h3 class="rd-tier">{T["CIRCUIT_KIN_H"]}</h3><p>{T["CIRCUIT_KIN"]}</p>')
        for c in X["kin"]:
            head, what = _ch(c)
            out.append(f'<div class="rd-entry tw-ch"><h4>{head}</h4><p>{what}</p></div>')
    out.append(body_plate(X))
    out.append(f'<h3 class="rd-tier">{T["CIRCUIT_EXAMPLE_H"]}</h3>')
    said = False
    for ex, P, Q in (("ex_a", A, B), ("ex_b", B, A)):     # Q was born with what P's dharma reaches for
        gs = X[ex]
        if not gs: continue
        said = True
        each = [f"gate {g} ({esc(title(g))})" for g in gs]
        chips = each[0] if len(each) == 1 else ", ".join(each[:-1]) + " and " + each[-1]
        Dh = P["C"]["dharma"]
        cross = [g for g in gs if g in {Dh[s][b]["gate"] for s, b, _ in DH.CROSS}]
        out.append(f'<p>{fill(T["CIRCUIT_EXAMPLE"][len(gs) > 1], a=P["name"], b=Q["name"], gates=chips)}'
                   + (" " + fill(T["CIRCUIT_EXAMPLE_CROSS"], g=cross[0], a=P["name"]) if cross else "") + "</p>")
    if not said:
        out.append(f'<p>{T["CIRCUIT_EXAMPLE_NONE"]}</p>')
    return "".join(out)


def body(P):
    """The section for two people in full, or for a table of three to nine, one line a pair."""
    out = [f'<p>{T["CIRCUIT_INTRO"]}</p>']
    if len(P) == 2:
        out.append(pair(P[0], P[1], currents(P[0], P[1])))
        return "".join(out)
    out.append(f'<p>{T["CIRCUIT_GROUP"]}</p>')
    for i in range(len(P)):
        for k in range(i + 1, len(P)):
            A, B = P[i], P[k]
            X = currents(A, B)
            kind, way = shape(X)
            a, b = (A, B) if way != "ba" else (B, A)
            out.append(f'<p>{fill(T["CIRCUIT_GROUP_PAIR"], a=A["name"], b=B["name"], fa=len(X["ab"]), fb=len(X["ba"]), dd=len(X["dd"]), shape=fill(T["CIRCUIT_SHAPE_SHORT"][kind], a=a["name"], b=b["name"]))}</p>')
    return "".join(out)
