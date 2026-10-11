"""The Body's Old Map: medical astrology, in the paid reading.

Signs on the body (Kalapurusha, Aries at the head and Pisces at the feet), the same
figure counted by house from the rising sign, the mansions' body parts (the
Brihat Samhita's list), the organs each planet rules, the doshas, the health
houses, and which parts of the body the periods bring forward. The words are in
lib/medical.json; what the free chart shows comes from the same tables
(static/medical.js holds a copy, and tests/medical_check.py keeps them equal)."""
import json, math, os

from . import engine as E
from .reading_more import dignity, ORD, E_year, LORD_OF_SIGN, the

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "medical.json"), encoding="utf-8"))
DEEP = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))["NAK_DEEP"]
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"}
HARD = {6, 8, 12}
DOSHAS = ("Vata", "Pitta", "Kapha")


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def cap(s): return s[0].upper() + s[1:]
def sign_i(l): return math.floor(E.norm(l) / 30)
def part_of_sign(i): return T["SIGN"][E.SIGNS[i]]["part"]


def mansion_dosha(l):
    """The Moon's mansion's dosha, from the corpus (a word like 'Vata')."""
    word = DEEP[E.nak_index(l)][5]
    return next((d for d in DOSHAS if d in word), None)


def facts(C):
    """Per planet: sign, house, the body part each gives, and whether it's under strain or strong."""
    asc = C["ascS"]; rows = []
    for b in NINE:
        l = C["sid"][b]; s = sign_i(l); h = E.house_of(l, asc); dg = dignity(b, l)
        strain = dg == "debilitated" or h in HARD
        strong = dg in ("exalted", "own", "root") and not strain
        rows.append({"body": b, "sign": E.SIGNS[s], "part": part_of_sign(s), "house": h, "house_part": part_of_sign(h - 1),
                     "mansion": E.NAK[E.nak_index(l)], "nak_part": T["NAK"][E.nak_index(l)],
                     "trop": E.SIGNS[sign_i(C["trop"][b])] if b in C.get("trop", {}) else None,
                     "dignity": dg, "strain": strain, "strong": strong})
    return rows


def weight(C, rows, zodiac="sid"):
    """Which parts of the body the chart comes back to: the rising sign counts three, the Moon two,
    every planet one by its sign and one by its house (the house counted from the rising sign)."""
    w = [0.0] * 12
    asc = C["ascS"] if zodiac == "sid" else E.norm(C["ascS"] + C.get("ay", 0))
    w[sign_i(asc)] += 3
    for r in rows:
        l = C["sid"][r["body"]] if zodiac == "sid" else C["trop"][r["body"]]
        w[sign_i(l)] += 2 if r["body"] == "Moon" else 1
        if zodiac == "sid": w[r["house"] - 1] += 1
    return w


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
        for a in E.sub_periods(m["lord"], m["from"], m["years"]):
            if a["from"] > now: out.append(a)
        if len(out) >= n: break
    return out[:n]


def body(C, dasha, asks):
    """The section's HTML."""
    rows = facts(C); unknown = C.get("unknownTime")
    by = {r["body"]: r for r in rows}

    table = "".join(f"<tr><td>{GLYPH[r['body']]} {r['body']}</td><td>{r['sign']} · {r['part']}</td>"
                    f"<td>{'—' if unknown else ORD(r['house']) + ' · ' + r['house_part']}</td><td>{r['mansion']} · {r['nak_part']}</td>"
                    f"<td>{(r['trop'] + ' · ' + T['SIGN'][r['trop']]['part']) if r['trop'] else '—'}</td></tr>" for r in rows)
    table = (f'<div class="rd-tw"><table><tr><th>Planet</th><th>Sign</th><th>House</th><th>Mansion</th><th>Tropical</th></tr>{table}</table></div>'
             f'<p class="rd-note">{T["TABLE_NOTE"]}</p>')

    # where the weight falls
    w = weight(C, rows); top = sorted(range(12), key=lambda i: -w[i])[:3]
    top = [i for i in top if w[i] > 0]
    weigh = "".join(f'<div class="rd-body"><h5>{E.SIGNS[i]} · {T["SIGN"][E.SIGNS[i]]["parts"]}</h5><p>{T["SIGN"][E.SIGNS[i]]["line"]}</p></div>' for i in top)
    wt = weight(C, rows, "trop"); tt = max(range(12), key=lambda i: wt[i])
    trop_line = "" if tt in top else f'<p class="rd-kenning">{fill(T["WEIGHT_TROP"], part=T["SIGN"][E.SIGNS[tt]]["parts"])}</p>'
    rising = "" if unknown else f'<p>{fill(T["RISING"], sign=E.SIGNS[sign_i(C["ascS"])])}</p>'

    # each planet and what it looks after
    def line(r):
        P = T["PLANET"][r["body"]]; name = cap(the(r["body"]))
        how = P["strain"] if r["strain"] else P["light"] if r["strong"] else T["NEUTRAL"]
        return "<p>" + fill(T["PLANET_LINE"], planet=f"<b>{GLYPH[r['body']]} {name}</b>", rules=P["rules"], sign=r["sign"], part=r["part"],
                            house=ORD(r["house"]), station=fill(T["STATION_LINE"], station=T["STATION"][r["body"]]),
                            plain=P["plain"], how=how) + "</p>"
    planets = "".join(line(r) for r in rows)
    strained = [r for r in rows if r["strain"]]
    strain = (f'<p>{T["STRAIN"]}</p><ul>' + "".join("<li>" + fill(T["STRAIN_ROW"], planet=f"<b>{GLYPH[r['body']]} {cap(the(r['body']))}</b>", sign=r["sign"],
              house=ORD(r["house"]), weak=T["STRAIN_WEAK"] if r["dignity"] == "debilitated" else "", short=T["PLANET"][r["body"]]["short"], part=r["part"]) + "</li>"
              for r in strained) + "</ul>" if strained else f'<p>{T["STRAIN_NONE"]}</p>')

    # doshas
    ds = doshas(C); lead = max(ds, key=ds.get)
    bars = "".join(f'<tr><td>{d}</td><td><b>{ds[d]}%</b></td><td>{T["DOSHA"][d]["is"]}</td></tr>' for d in DOSHAS)
    dosha = (f'<p>{T["DOSHA_INTRO"]}</p><div class="rd-tw"><table>{bars}</table></div><p>{T["DOSHA"][lead]["line"]}</p>')

    # the health houses
    houses = ""
    if not unknown:
        asc_i = sign_i(C["ascS"])
        for h in (1, 6, 8, 12):
            lord = LORD_OF_SIGN[(asc_i + h - 1) % 12]
            inside = [the(r["body"]) for r in rows if r["house"] == h]
            in_it = "" if not inside else fill(T["HOUSE_IN"], planets=cap(" and ".join([", ".join(inside[:-1]), inside[-1]] if len(inside) > 1 else inside)),
                                                 verb="are" if len(inside) > 1 else "is")
            houses += "<p>" + fill(T["HOUSE_LINE"], house_says=cap(T["HOUSES"][str(h)]), lord=the(lord), where=ORD(by[lord]["house"]), in_it=in_it) + "</p>"
        houses = f'<h3 class="rd-tier">{T["HOUSES_H"]}</h3>{houses}'

    # the body in time
    now = dasha["now"]; m, a = dasha["cur"], dasha["curA"]
    sh = lambda b: T["PLANET"][b]["short"]
    if m["lord"] == a["lord"]:
        when = fill(T["TIME_SAME"], maha=the(m["lord"]), maha_name=the(m["lord"]), to=E_year(a["to"]), maha_short=sh(m["lord"]), maha_part=by[m["lord"]]["part"])
    else:
        when = fill(T["TIME_NOW"], maha=the(m["lord"]), maha_name=the(m["lord"]), antar=the(a["lord"]), to=E_year(a["to"]),
                    maha_short=sh(m["lord"]), maha_part=by[m["lord"]]["part"], antar_short=sh(a["lord"]), antar_part=by[a["lord"]]["part"])
    nxt = "".join("<li>" + fill(T["TIME_ROW"], **{"from": E_year(x["from"]), "lord": f"{GLYPH[x['lord']]} {cap(the(x['lord']))}",
                                                   "rules": T["PLANET"][x["lord"]]["short"], "part": by[x["lord"]]["part"]}) + "</li>"
                  for x in _antars(dasha, now))

    asks.append(("The body", fill(T["ASK"], part=T["SIGN"][E.SIGNS[top[0]]]["parts"]), False))
    return f"""<p>{T["INTRO"]}</p><p class="rd-note">{T["NOTE"]}</p>{table}
      <h3 class="rd-tier">{T["WEIGHT_H"]}</h3>{rising}<p>{T["WEIGHT"]}</p>{weigh}{trop_line}
      <h3 class="rd-tier">Your planets and what they look after</h3>{planets}
      <h3 class="rd-tier">{T["STRAIN_H"]}</h3>{strain}
      <h3 class="rd-tier">{T["DOSHA_H"]}</h3>{dosha}
      {houses}
      <h3 class="rd-tier">{T["TIME_H"]}</h3><p>{when}</p><p>{T["TIME_NEXT"]}</p><ul>{nxt}</ul>"""
