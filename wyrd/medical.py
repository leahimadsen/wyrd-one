"""The Body's Old Map: medical astrology, in the paid reading.

The maps the console reads each say something different about the body, so they
are laid onto one figure, the Planetary Ladder's seven stations from crown to
root, and read together:

  the sign       the body you were given (sidereal, Kalapurusha: Aries at the head)
  the house      where your life lands in your body (the same figure from the rising sign)
  the mansion    the fine detail (the Brihat Samhita's list)
  the centre     how energy moves there (the bodygraph: defined or open)
  the tropical   how the body feels to live in (the Western figure)
  the planet     what kind of thing: heat, bone, nerves
  the dosha      the temperament of the whole, each with its home on the ladder
  the period     when

The words are in lib/medical.json. grid() is also in static/medical.js for the free
chart's body map; tests/medical_check.py keeps the two equal."""
import json, math, os

from . import engine as E
from . import rave as RV
from .reading_more import dignity, ORD, E_year, LORD_OF_SIGN, the

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "medical.json"), encoding="utf-8"))
_C = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
DEEP = _C["NAK_DEEP"]
COLOUR = [b["hex"] for b in _C["BIFROST"]]        # the chakra colours, crown violet down to root red, as on the ladder
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋", "AC": "AC"}
HARD = {6, 8, 12}
DOSHAS = ("Vata", "Pitta", "Kapha")
ZONE = {z["key"]: z for z in T["ZONES"]}
KEYS = [z["key"] for z in T["ZONES"]]
LENSES = ("sign", "house", "mansion", "centre")
STATION_ZONE = {"the crown": "crown", "the brow": "brow", "the throat": "throat", "the heart": "heart",
                "the solar plexus": "solar", "the sacrum": "sacrum", "the root": "root"}


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def cap(s): return s[0].upper() + s[1:]
def low(s): return s[0].lower() + s[1:]
def sign_i(l): return math.floor(E.norm(l) / 30)
def part_of_sign(i): return T["SIGN"][E.SIGNS[i]]["part"]
def zones_of_sign(i): return [z["key"] for z in T["ZONES"] if E.SIGNS[i] in z["signs"]]
def zone_of_nak(l): return T["NAK_ZONE"][E.nak_index(l)]
def zname(k): return low(ZONE[k]["name"])
def znames(ks): return " and ".join([zname(ks[0])] + [zname(k)[4:] for k in ks[1:]])     # "the heart and solar plexus"
def listing(xs): return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def defined_centres(C):
    return RV.defines(C["natal"])[1] if C.get("natal") else []


def grid(C, defined, unknown=False):
    """For each station, which planets land there by each map (AC is the rising sign),
    and whether its bodygraph centres are defined. The same as grid() in static/medical.js."""
    g = {z["key"]: {"sign": [], "house": [], "mansion": [], "trop": [], "centre": [[c, c in defined] for c in z["centre"]]} for z in T["ZONES"]}
    def put(col, zs, b):
        for k in zs: g[k][col].append(b)
    if not unknown: put("sign", zones_of_sign(sign_i(C["ascS"])), "AC")
    for b in NINE:
        l = C["sid"][b]
        put("sign", zones_of_sign(sign_i(l)), b)
        if not unknown: put("house", zones_of_sign((sign_i(l) - sign_i(C["ascS"])) % 12), b)
        put("mansion", [zone_of_nak(l)], b)
        put("trop", zones_of_sign(sign_i(C["trop"][b])), b)
    return g


def weight(g):
    """How much each station carries, every map together. A sign or house that covers several
    stations shares its weight between them; the rising sign counts three, the Moon two,
    a mansion half, a defined centre one. Returns the totals and each map's share."""
    share = {}
    for row in g.values():
        for col in ("sign", "house"):
            for b in row[col]: share[(col, b)] = share.get((col, b), 0) + 1
    w, parts = {}, {}
    for k, row in g.items():
        p = {"sign": sum((3 if b == "AC" else 2 if b == "Moon" else 1) / share[("sign", b)] for b in row["sign"]),
             "house": sum(1 / share[("house", b)] for b in row["house"]),
             "mansion": 0.5 * len(row["mansion"]),
             "centre": sum(1 for _, on in row["centre"] if on) / len(row["centre"])}
        w[k] = sum(p.values()); parts[k] = p
    return w, parts


def trop_weight(g):
    share = {}
    for row in g.values():
        for b in row["trop"]: share[b] = share.get(b, 0) + 1
    return {k: sum((2 if b == "Moon" else 1) / share[b] for b in row["trop"]) for k, row in g.items()}


def mansion_dosha(l):
    word = DEEP[E.nak_index(l)][5]
    return next((d for d in DOSHAS if d in word), None)


def facts(C):
    """Per planet: sign, house, the body part and stations each gives, and whether it's under strain or strong."""
    asc = C["ascS"]; rows = []
    for b in NINE:
        l = C["sid"][b]; s = sign_i(l); h = E.house_of(l, asc); dg = dignity(b, l)
        strain = dg == "debilitated" or h in HARD
        strong = dg in ("exalted", "own", "root") and not strain
        rows.append({"body": b, "sign": E.SIGNS[s], "part": part_of_sign(s), "zones": zones_of_sign(s), "house": h,
                     "house_part": part_of_sign(h - 1), "mansion": E.NAK[E.nak_index(l)], "nak_part": T["NAK"][E.nak_index(l)],
                     "dignity": dg, "strain": strain, "strong": strong})
    return rows


def doshas(C):
    """The three doshas: each planet by its lean, the rising sign's ruler and the Moon twice, and the Moon's mansion."""
    t = dict.fromkeys(DOSHAS, 0.0)
    lord = LORD_OF_SIGN[sign_i(C["ascS"])]
    for b in NINE:
        k = 2 if b in (lord, "Moon") else 1
        for d, v in T["PLANET"][b]["dosha"].items(): t[d] += v * k
    md = mansion_dosha(C["sid"]["Moon"])
    if md: t[md] += 1
    total = sum(t.values())
    return {d: round(100 * v / total) for d, v in t.items()}


def _antars(dasha, now, n=6):
    out = []
    for m in dasha["maha"]:
        if m["to"] <= now: continue
        out += [a for a in E.sub_periods(m["lord"], m["from"], m["years"]) if a["from"] > now]
        if len(out) >= n: break
    return out[:n]


def cell(bs): return " ".join(GLYPH[b] for b in bs)


def figure(g, w, unknown=False, planets=True):
    """The body diagram: the engraving, the ladder down its middle, a mark on each station sized by its weight,
    and to the side the planets that land there by sign (and by house, when the birth time is known)."""
    F = T["FIGURE"]; W, H = F["w"], F["h"]; X0 = W + 40; top = max(w.values()) or 1
    pts = [F["at"][k] for k in KEYS]; heavy = sorted(w.values())[-2]
    grad = "".join(f'<stop offset="{i / 6:.3f}" stop-color="{c}"/>' for i, c in enumerate(COLOUR))
    has = os.path.exists(os.path.join(HERE, F["src"].lstrip("/")))      # until the engraving is added, the ladder stands alone
    out = [f'<defs><linearGradient id="mf-bow" x1="0" y1="{pts[0][1]}" x2="0" y2="{pts[-1][1]}" gradientUnits="userSpaceOnUse">{grad}</linearGradient></defs>',
           f'<image href="{F["src"]}" x="0" y="0" width="{W}" height="{H}"/>' if has else "",
           f'<polyline class="mf-ladder" stroke="url(#mf-bow)" points="{" ".join(f"{x},{y}" for x, y in pts)}"/>']
    for i, k in enumerate(KEYS):
        x, y = F["at"][k]; r = 6 + 12 * w[k] / top; ly = 40 + i * (H * 0.62 / 6)
        on = ([b for b in g[k]["sign"]] + ([] if unknown else [b for b in g[k]["house"] if b not in g[k]["sign"]])) if planets else []
        c = COLOUR[i]; hi = w[k] >= heavy
        out.append(f'<path class="mf-lead" stroke="{c}" d="M{x + r},{y} L{X0 - 10},{ly}"/>'
                   + (f'<circle class="mf-ring" stroke="{c}" cx="{x}" cy="{y}" r="{r + 6:.1f}"/>' if hi else "")
                   + f'<circle class="mf-dot{" hi" if hi else ""}" fill="{c}" cx="{x}" cy="{y}" r="{r:.1f}"/>'
                   f'<text class="mf-name" fill="{c}" x="{X0}" y="{ly - 4}">{ZONE[k]["name"].replace("The ", "")}{" ◆" if hi else ""}</text>'
                   + ((f'<text class="mf-pl" x="{X0}" y="{ly + 22}">' + ("".join(f'<tspan x="{X0}" dy="{0 if j == 0 else 30}">{cell(on[j:j + 5])}</tspan>' for j in range(0, len(on), 5)) or "·") + '</text>') if planets else ""))
    cap = F["caption"] if has else F["caption"].split(" Engraving")[0]
    return (f'<figure class="mf"><svg viewBox="0 0 {X0 + 230} {H}" role="img" aria-label="Your seven stations on the body">{"".join(out)}</svg>'
            + (f'<figcaption>{cap}</figcaption>' if planets else "") + '</figure>')


def free(C):
    """The free chart's body map: the figure with the stations sized, no planets, and one plain line."""
    unknown = C.get("unknownTime"); g = grid(C, defined_centres(C), unknown); w, _ = weight(g)
    a, b = sorted(KEYS, key=lambda k: -w[k])[:2]
    line = fill(T["FREE"]["line"], first=f"your {zname(a)[4:]}", first_parts=ZONE[a]["parts"], second=f"your {zname(b)[4:]}", second_parts=ZONE[b]["parts"])
    return {"figure": figure(g, w, unknown, planets=False), "line": line, "note": T["FREE"]["note"],
            "full": figure(g, w, unknown), "memberNote": T["FREE"]["member"]}          # members see the planets on each station


def body(C, dasha, asks):
    """The section's HTML."""
    unknown = C.get("unknownTime"); rows = facts(C); by = {r["body"]: r for r in rows}
    g = grid(C, defined_centres(C), unknown)
    w, parts = weight(g); order = sorted(KEYS, key=lambda k: -w[k])

    key = "".join(f"<dt>{a}</dt><dd>{cap(b)}</dd>" for a, b in T["LENSES"])
    centres = lambda row: ", ".join(f"{c} {'●' if on else '○'}" for c, on in row["centre"]) if C.get("natal") else "—"
    trs = "".join(f"<tr{' class=hi' if k in order[:2] else ''}><th><span class=mf-sw style='background:{COLOUR[KEYS.index(k)]}'></span>{ZONE[k]['name']}<br><small>{ZONE[k]['parts']}</small></th>"
                  f"<td>{cell(g[k]['sign'])}</td><td>{'—' if unknown else cell(g[k]['house'])}</td><td>{cell(g[k]['mansion'])}</td>"
                  f"<td>{centres(g[k])}</td><td>{cell(g[k]['trop'])}</td></tr>" for k in KEYS)
    table = (f'<div class="rd-tw"><table class="rd-zones"><tr><th>Station</th><th>Sign</th><th>House</th><th>Mansion</th><th>Centre</th><th>Tropical</th></tr>{trs}</table></div>'
             f'<p class="rd-note">{T["TABLE_NOTE"]}</p>')

    # where it gathers, and which maps agree
    def agree(k):
        ls = [T["LENS_NAME"][l] for l in LENSES if parts[k][l] >= 0.5]
        if not ls: return ""
        return fill(T["AGREE_ONE"] if len(ls) == 1 else T["AGREE"], lenses=cap(listing(ls)))
    gather = "".join(f'<div class="rd-body"><h5>{ZONE[k]["name"]} · {ZONE[k]["parts"]}</h5><p>{agree(k)} {ZONE[k]["line"]}</p></div>' for k in order[:2])
    tw = trop_weight(g); tt = max(KEYS, key=lambda k: tw[k])
    trop_line = "" if tt in order[:2] else f'<p class="rd-kenning">{fill(T["WEIGHT_TROP"], zone=zname(tt), parts=ZONE[tt]["parts"])}</p>'
    rising = "" if unknown else f'<p>{fill(T["RISING"], sign=E.SIGNS[sign_i(C["ascS"])], zone=znames(zones_of_sign(sign_i(C["ascS"]))))}</p>'

    # each planet: what it looks after, where it sits, and the thread to the station it feeds
    def line(r):
        P = T["PLANET"][r["body"]]; st = T["STATION"][r["body"]]
        ladder = fill(T["LADDER_SAME"] if STATION_ZONE.get(st) in r["zones"] else T["LADDER_OTHER"], station=st, zone=znames(r["zones"]))
        how = P["strain"] if r["strain"] else P["light"] if r["strong"] else T["NEUTRAL"]
        return "<p>" + fill(T["PLANET_LINE"], planet=f"<b>{GLYPH[r['body']]} {cap(the(r['body']))}</b>", rules=P["rules"], sign=r["sign"],
                            place=fill(T["PLACE_SAME"] if r["part"] == znames(r["zones"]) else T["PLACE"], part=r["part"], zone=znames(r["zones"])),
                            plain=P["plain"], ladder=ladder, how=how) + "</p>"
    marked = [r for r in rows if r["strain"] or r["strong"]]
    quiet = [r for r in rows if not (r["strain"] or r["strong"])]
    tag = lambda r: f' <span class="rd-side p">{T["STRAIN_TAG"] if r["strain"] else T["STRONG_TAG"]}</span>'
    planets = (f'<p>{T["STRAIN"]}</p>' + "".join(line(r).replace("</b>", "</b>" + tag(r), 1) for r in marked)) if marked else f'<p>{T["STRAIN_NONE"]}</p>'
    if quiet:
        planets += f'<h3 class="rd-tier">{T["QUIET_H"]}</h3><ul>' + "".join("<li>" + fill(T["QUIET_ROW"], planet=f"<b>{GLYPH[r['body']]} {cap(the(r['body']))}</b>",
                   sign=r["sign"], short=T["PLANET"][r["body"]]["short"], zone=znames(r["zones"])) + "</li>" for r in quiet) + "</ul>"

    # doshas, and where each lives on the ladder
    ds = doshas(C); lead = max(ds, key=ds.get)
    bars = "".join(f'<tr><td>{d}</td><td><b>{ds[d]}%</b></td><td>{T["DOSHA"][d]["is"]}</td></tr>' for d in DOSHAS)
    home = listing([zname(k) for k in KEYS if ZONE[k]["dosha"] == lead])
    dosha = (f'<p>{T["DOSHA_INTRO"]}</p><div class="rd-tw"><table>{bars}</table></div>'
             f'<p>{T["DOSHA"][lead]["line"]} {fill(T["DOSHA_HOME"], dosha=lead, zones=home)}</p>')

    # the health houses
    houses = ""
    if not unknown:
        asc_i = sign_i(C["ascS"])
        for h in (1, 6, 8, 12):
            lord = LORD_OF_SIGN[(asc_i + h - 1) % 12]
            inside = [the(r["body"]) for r in rows if r["house"] == h]
            in_it = fill(T["HOUSE_IN"], planets=cap(listing(inside)), verb="are" if len(inside) > 1 else "is") if inside else ""
            houses += "<p>" + fill(T["HOUSE_LINE"], house_says=cap(T["HOUSES"][str(h)]), lord=the(lord), where=ORD(by[lord]["house"]), in_it=in_it) + "</p>"
        houses = f'<h3 class="rd-tier">{T["HOUSES_H"]}</h3>{houses}'

    # the body in time
    now = dasha["now"]; m, a = dasha["cur"], dasha["curA"]
    sh = lambda b: T["PLANET"][b]["short"]; zn = lambda b: znames(by[b]["zones"])
    if m["lord"] == a["lord"]:
        when = fill(T["TIME_SAME"], maha=the(m["lord"]), maha_name=the(m["lord"]), to=E_year(a["to"]), maha_short=sh(m["lord"]), maha_zone=zn(m["lord"]))
    else:
        when = fill(T["TIME_NOW"], maha=the(m["lord"]), maha_name=the(m["lord"]), antar=the(a["lord"]), to=E_year(a["to"]),
                    maha_short=sh(m["lord"]), maha_zone=zn(m["lord"]), antar_short=sh(a["lord"]), antar_zone=zn(a["lord"]))
    nxt = "".join("<li>" + fill(T["TIME_ROW"], **{"from": E_year(x["from"]), "lord": f"{GLYPH[x['lord']]} {cap(the(x['lord']))}",
                                                   "rules": sh(x["lord"]), "zone": zn(x["lord"])}) + "</li>" for x in _antars(dasha, now))

    asks.append(("The body", fill(T["ASK"], zone=zname(order[0]), parts=ZONE[order[0]]["parts"]), False))
    return f"""<p>{T["INTRO"]}</p><p class="rd-note">{T["NOTE"]}</p>
      <h3 class="rd-tier">{T["LENSES_H"]}</h3><dl class="rd-lenses">{key}</dl>
      {table}
      <h3 class="rd-tier">{T["WEIGHT_H"]}</h3>{figure(g, w, unknown)}{rising}<p>{T["WEIGHT"]}</p>{gather}{trop_line}
      <h3 class="rd-tier">{T["STRAIN_H"]}</h3>{planets}
      <h3 class="rd-tier">{T["DOSHA_H"]}</h3>{dosha}
      {houses}
      <h3 class="rd-tier">{T["TIME_H"]}</h3><p>{when}</p><p>{T["TIME_NEXT"]}</p><ul>{nxt}</ul>"""
