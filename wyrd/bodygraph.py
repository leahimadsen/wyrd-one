"""The bodygraph as a drawing for the paid reading: the nine centres, every
channel, the live ones lit, and the direction energy runs along each live
channel (from the centre farther from the throat toward the nearer, so it
rises from the motors to expression). Arrows show the direction on paper;
on screen, light moves along the channels too.

Also the plain facts of a design: type, authority, definition."""
import math
from . import rave as RV

MOTORS = ("heart", "solar", "sacral", "root")
POS = {"head": (200, 46), "ajna": (200, 118), "throat": (200, 200), "g": (200, 292), "heart": (268, 322),
       "spleen": (78, 382), "solar": (322, 382), "sacral": (200, 410), "root": (200, 500)}
SHAPE = {"head": "up", "ajna": "down", "throat": "sq", "g": "dia", "heart": "heart", "spleen": "right",
         "solar": "left", "sacral": "sq", "root": "sq"}


def analyse(rave):
    have = RV.gates(rave)
    live = [c for c in RV.CHANNELS if c[0] in have and c[1] in have]
    defined = {RV.CENTRE_OF[g] for c in live for g in c}
    adj = {k: set() for k in RV.CENTRES}
    for a, b in live:
        adj[RV.CENTRE_OF[a]].add(RV.CENTRE_OF[b]); adj[RV.CENTRE_OF[b]].add(RV.CENTRE_OF[a])
    dist, q = {"throat": 0}, ["throat"]
    while q:
        c = q.pop(0)
        for n in adj[c]:
            if n not in dist: dist[n] = dist[c] + 1; q.append(n)
    seen, parts = set(), 0
    for c in defined:
        if c in seen: continue
        parts += 1; st = [c]
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); st.extend(adj[x])
    m2t = "throat" in defined and any(m in dist and dist[m] > 0 for m in MOTORS)
    typ = ("Reflector" if not defined else ("Manifesting Generator" if m2t else "Generator") if "sacral" in defined
           else "Manifestor" if m2t else "Projector")
    auth = ("Lunar" if not defined else "Emotional" if "solar" in defined else "Sacral" if "sacral" in defined
            else "Splenic" if "spleen" in defined else ("Ego manifested" if "heart" in dist else "Ego projected") if "heart" in defined
            else "Self-projected" if "g" in defined and "throat" in adj["g"] else "Outer")
    defn = ["No definition", "Single definition", "Split definition", "Triple split", "Quadruple split"][min(parts, 4)]
    return {"live": live, "defined": defined, "dist": dist, "type": typ, "authority": auth, "definition": defn,
            "motors": [m for m in MOTORS if m in dist and dist[m] > 0 and m in defined]}


def _shape(k):
    x, y = POS[k]; h = 16 if k == "heart" else 26
    s = SHAPE[k]
    if s == "up": return f"M{x},{y-h} L{x+h},{y+h} L{x-h},{y+h} Z"
    if s == "down": return f"M{x},{y+h} L{x+h},{y-h} L{x-h},{y-h} Z"
    if s == "dia": return f"M{x},{y-h} L{x+h},{y} L{x},{y+h} L{x-h},{y} Z"
    if s == "heart": return f"M{x-h},{y+h*.8} L{x},{y-h} L{x+h},{y+h*.8} Z"
    if s == "right": return f"M{x+h},{y} L{x-h},{y-h} L{x-h},{y+h} Z"
    if s == "left": return f"M{x-h},{y} L{x+h},{y-h} L{x+h},{y+h} Z"
    return f"M{x-h},{y-h} L{x+h},{y-h} L{x+h},{y+h} L{x-h},{y+h} Z"


def svg(A, tone, label):
    """One bodygraph. tone: 'birth' (gold) or 'dharma' (violet)."""
    live = {tuple(c) for c in A["live"]}
    bundles = {}
    for ch in RV.CHANNELS:
        k = tuple(sorted((RV.CENTRE_OF[ch[0]], RV.CENTRE_OF[ch[1]])))
        bundles.setdefault(k, []).append(ch)
    lines, arrows, sparks = [], [], []
    for (c1, c2), chs in bundles.items():
        (x1, y1), (x2, y2) = POS[c1], POS[c2]
        L = math.hypot(x2 - x1, y2 - y1); nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        for i, ch in enumerate(chs):
            o = (i - (len(chs) - 1) / 2) * 7
            a, b = (x1 + nx * o, y1 + ny * o), (x2 + nx * o, y2 + ny * o)
            on = tuple(ch) in live
            if on:
                d1, d2 = A["dist"].get(c1, 99), A["dist"].get(c2, 99)
                ty = POS["throat"][1]                                     # run toward the throat: along the circuit,
                if d1 < d2 or (d1 == d2 and abs(y1 - ty) < abs(y2 - ty)): a, b = b, a   # else toward its place (body.js runsFrom)
            lines.append(f'<line class="bg-ch{" on" if on else ""}" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
            if on:
                mx, my = a[0] + (b[0] - a[0]) * .56, a[1] + (b[1] - a[1]) * .56
                ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                arrows.append(f'<path class="bg-arrow" d="M-5,-4.5 L5,0 L-5,4.5 Z" transform="translate({mx:.1f},{my:.1f}) rotate({ang:.0f})"/>')
                dur = max(1.2, math.hypot(b[0] - a[0], b[1] - a[1]) / 38)
                for j in range(2):
                    sparks.append(f'<circle class="bg-spark" r="3"><animateMotion dur="{dur:.2f}s" begin="{j * dur / 2:.2f}s" repeatCount="indefinite" '
                                  f'path="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}"/></circle>')
    centres = []
    for k in POS:
        on = k in A["defined"]
        cls = "bg-c" + (" on" if on else "") + (" motor" if k in MOTORS else "")
        x, y = POS[k]
        centres.append(f'<g class="{cls}"><path d="{_shape(k)}"/><text x="{x}" y="{y + (4 if k == "heart" else 5)}">{RV.CENTRES[k][0]}</text></g>')
    return (f'<figure class="bg-fig bg-{tone}"><svg viewBox="0 0 400 560" role="img" aria-label="{label}: defined centres filled; '
            f'arrows show the way energy runs along each live channel">'
            f'<g>{"".join(lines)}</g><g>{"".join(arrows)}</g><g class="bg-sparks">{"".join(sparks)}</g><g>{"".join(centres)}</g></svg>'
            f'<figcaption><b>{label}</b><br>{A["type"]} · {A["authority"]} authority · {A["definition"]}</figcaption></figure>')
