"""The deeper parts of the reading together: the thirty years chapter by chapter, the sky's
own appointments, the old eight-fold match, how two bodygraphs meet, and the numbers side by
side. Every sentence comes from lib/together.json (drafted for The Völva to rewrite) or the
register; this file only chooses which lines the charts call for."""
import json, math, os

from . import engine as E
from . import numbers as NUM
from . import rave as RV
from .bodygraph import analyse as hd
from .reading_more import X as REG_EXT, ORD, E_year, the

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "together.json"), encoding="utf-8"))
C_ = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"}
YEARS = 30


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def cap(s): return s[0].upper() + s[1:] if s else s


from .reading import jd_date as month          # "Mar 2031"


# ---------------- the sky's own appointments ----------------
def _sep(a, b): return abs((a - b + 180) % 360 - 180)


def _runs(jds, flags, gap):
    """Spans where flags hold, joining spans less than `gap` days apart (retrograde loops)."""
    spans = []
    for jd, f in zip(jds, flags):
        if not f: continue
        if spans and jd - spans[-1][1] <= gap: spans[-1][1] = jd
        else: spans.append([jd, jd])
    return spans


def sky_marks(eph, C, now, years=YEARS, step=10):
    """Saturn and Jupiter returns, Saturn's opposition, the nodal return and Sade Sati, in the
    next `years`, from the ephemeris (sidereal). [(kind, start_jd, end_jd)], in time order."""
    jds = [now + i * step for i in range(int(years * E.YEAR / step) + 1)]
    if hasattr(eph, "positions_many"):
        rows = eph.positions_many(jds, bodies=("Saturn", "Jupiter"))
    else:
        rows = [(eph.positions(jd), eph.ayanamsa(jd)) for jd in jds]
    sat = [E.norm(p["Saturn"] - ay) for p, ay in rows]
    jup = [E.norm(p["Jupiter"] - ay) for p, ay in rows]
    node = [E.norm(p["Rahu"] - ay) for p, ay in rows]
    n = C["sid"]; moon_sign = int(n["Moon"] // 30)
    out = []
    for kind, track, target, orb, gap in (("saturn_return", sat, n["Saturn"], 1.5, 400), ("saturn_opposition", sat, E.norm(n["Saturn"] + 180), 1.5, 400),
                                          ("jupiter_return", jup, n["Jupiter"], 1.5, 400), ("nodal_return", node, n["Rahu"], 1.0, 400)):
        out += [(kind, a, b) for a, b in _runs(jds, [_sep(x, target) <= orb for x in track], gap)]
    sade = [((int(x // 30) - moon_sign) % 12) in (11, 0, 1) for x in sat]
    out += [("sade_sati", a, b) for a, b in _runs(jds, sade, 500) if b - a > 2 * E.YEAR or (a > jds[0] and b < jds[-1])]
    return sorted(out, key=lambda m: m[1])


def when(a, b):
    ya, yb = E_year(a), E_year(b)
    return str(ya) if ya == yb else f"{ya}–{yb}"


# ---------------- the thirty years ----------------
def _guest(dasha, jd, level="maha"):
    rows = dasha["maha"]
    m = next((r for r in rows if r["from"] <= jd < r["to"]), rows[-1])
    if level == "maha": return m
    subs = E.sub_periods(m["lord"], m["from"], m["years"])
    return next((s for s in subs if s["from"] <= jd < s["to"]), subs[-1])


def _antars(dasha, a, b):
    """Every sub-period that begins between a and b."""
    out = []
    for m in dasha["maha"]:
        if m["to"] < a or m["from"] > b: continue
        out += [s for s in E.sub_periods(m["lord"], m["from"], m["years"]) if a < s["from"] <= b]
    return out


def seasons(P, season, labels, now):
    """The Seasons You Share: chapters, the sky's appointments, year by year, years to watch."""
    two, end = len(P) == 2, now + YEARS * E.YEAR
    life = REG_EXT["HOUSE_LIFE"]
    marks = [(i, k, a, b) for i, p in enumerate(P) for k, a, b in p.get("marks", [])]
    out = [f"<p>{T['SEASON_INTRO']}</p>"]

    # chapters: a new one whenever anyone's long guest changes
    cuts = sorted({now, end} | {m["from"] for p in P for m in p["dasha"]["maha"] if now < m["from"] < end})
    for a, b in zip(cuts, cuts[1:]):
        g = [_guest(p["dasha"], a + 1)["lord"] for p in P]
        if two:
            lab = season(g[0], g[1])
            head = fill(T["CHAPTER_TITLE"], **{"from": E_year(a), "to": E_year(b), "la": f"{GLYPH[g[0]]} {g[0]}", "lb": f"{GLYPH[g[1]]} {g[1]}"})
            body = [fill(T["CHAPTER_OPEN"], **{"from": E_year(a), "to": E_year(b), "la": the(g[0]), "lb": the(g[1]),
                                               "a": P[0]["name"], "b": P[1]["name"], "label": labels[lab]["label"]}) + " " + labels[lab]["text"]]
        else:
            head = f"{E_year(a)}–{E_year(b)} · " + ", ".join(f"{GLYPH[x]} {x}" for x in g)
            body = []
        for i, p in enumerate(P):
            body.append(fill(T["LORD_BOND"][g[i]], name=p["name"]))
            if two:
                o = P[1 - i]; h = E.house_of(p["C"]["sid"][g[i]], o["C"]["ascS"])
                body.append(fill(T["CHAPTER_LANDS"], a=p["name"], b=o["name"], lord=g[i], house=ORD(h), life=life[h - 1]))
        subs = sorted((s["from"], i, s["lord"]) for i, p in enumerate(P) for s in _antars(p["dasha"], a, b))
        lines = []
        for jd, i, lord in subs:
            if two:
                other = _guest(P[1 - i]["dasha"], jd + 1, "antar")["lord"]
                lines.append((jd, fill(T["SUB_LINE"], name=P[i]["name"], lord=lord, short=T["SUB_SHORT"][lord], label=labels[season(lord, other)]["label"])))
            else:
                lines.append((jd, fill(T["SUB_UNIT"], name=P[i]["name"], lord=lord, short=T["SUB_SHORT"][lord])))
        lines += [(ma, fill(T["MARK_SHORT"][k], name=P[i]["name"]) + ".") for i, k, ma, mb in marks if a <= ma < b]
        lis = "".join(f"<li><b>{month(jd)}</b> · {t}</li>" for jd, t in sorted(lines))
        out.append(f'<h3 class="rd-tier">{head}</h3>' + "".join(f"<p>{x}</p>" for x in body)
                   + (f'<h5>{T["CHAPTER_SUBS"]}</h5><ul class="rd-turns">{lis}</ul>' if lis else ""))

    # the sky's own appointments, written out
    if marks:
        out.append(f'<h3 class="rd-tier">{T["MARKS_TITLE"]}</h3>' + "".join(
            f'<p>{fill(T["MARKS"][k], name=P[i]["name"], when=when(ma, mb))}</p>' for i, k, ma, mb in sorted(marks, key=lambda m: m[2])))

    # year by year, and the years to watch
    y0 = E_year(now); rows, watch = [], []
    for y in range(y0, y0 + YEARS):
        mid = now + (y - y0 + 0.5) * E.YEAR
        gs = [_guest(p["dasha"], mid) for p in P]; ss = [_guest(p["dasha"], mid, "antar") for p in P]
        changes = sum(1 for p in P for m in p["dasha"]["maha"] if E_year(m["from"]) == y and m["from"] > now)
        subch = sum(1 for p in P for s in _antars(p["dasha"], now, end) if E_year(s["from"]) == y)
        yr_marks = [(i, k) for i, k, ma, mb in marks if E_year(ma) == y]
        hot = changes >= 2 or len(yr_marks) >= 2 or (changes and yr_marks) or (two and subch >= 3)
        if hot: watch.append(y)
        cells = "".join(f"<td>{GLYPH[g['lord']]}{GLYPH[s['lord']]}</td>" for g, s in zip(gs, ss))
        between = f"<td>{labels[season(gs[0]['lord'], gs[1]['lord'])]['label']}</td>" if two else ""
        sky = ", ".join(fill(T["MARK_SHORT"][k], name=P[i]["name"]) for i, k in yr_marks)
        rows.append(f'<tr{" class=hi" if hot else ""}><td>{y}{" ◆" if hot else ""}</td>{cells}{between}<td>{sky}</td></tr>')
    head = "".join(f"<th>{p['name']}</th>" for p in P) + ("<th>Between you</th>" if two else "")
    out.append(f'<h3 class="rd-tier">{T["YEARS_TITLE"]}</h3><p>{T["YEARS_INTRO"]}</p>'
               f'<div class="rd-tw"><table class="rd-years"><tr><th>Year</th>{head}<th>Sky</th></tr>{"".join(rows)}</table></div>'
               f'<p class="rd-kenning"><b>{T["WATCH_TITLE"]}:</b> {", ".join(map(str, watch)) if watch else T["WATCH_NONE"]}</p>')
    return "".join(out), watch


# ---------------- the old match: Ashtakoota, as static/kuta.js ----------------
NAK = 360 / 27
VARNA = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4]
VASHYA = {0: [4, 7], 1: [3, 6], 2: [5], 3: [7, 8], 4: [6], 5: [11, 2], 6: [5, 9], 7: [3], 8: [11], 9: [0, 10], 10: [0], 11: [9]}
YONI_OF = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
YONI = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"]
YONI_SCORE = [
    [4,2,2,3,2,2,2,1,0,1,3,3,2,1],[2,4,3,3,2,2,2,2,3,1,2,3,2,0],[2,3,4,2,1,2,1,3,3,1,2,0,3,1],[3,3,2,4,2,1,1,1,1,2,2,2,0,2],
    [2,2,1,2,4,2,1,2,2,1,0,2,1,1],[2,2,2,1,2,4,0,2,2,1,3,3,2,1],[2,2,1,1,1,0,4,2,2,2,2,2,1,2],[1,2,3,1,2,2,2,4,3,0,3,2,2,1],
    [0,3,3,1,2,2,2,3,4,1,2,2,2,1],[1,1,1,2,1,1,2,0,1,4,1,1,2,1],[3,2,2,2,0,3,2,3,2,1,4,2,2,1],[3,3,0,2,2,3,2,2,2,1,2,4,3,2],
    [2,2,3,0,1,2,1,2,2,2,2,3,4,2],[1,0,1,2,1,1,2,1,1,1,1,2,2,4]]
LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
GANA_SCORE = {"Deva": {"Deva": 6, "Manushya": 6, "Rakshasa": 1}, "Manushya": {"Deva": 5, "Manushya": 6, "Rakshasa": 0},
              "Rakshasa": {"Deva": 1, "Manushya": 0, "Rakshasa": 6}}
NADI = ["Adi", "Madhya", "Antya"]
MAX = {"Varna": 1, "Vashya": 2, "Tara": 3, "Yoni": 4, "Graha Maitri": 5, "Gana": 6, "Bhakoot": 7, "Nadi": 8}
VARNA_NAME = ["", "Shudra", "Vaishya", "Kshatriya", "Brahmin"]


def _load_gana():
    """The 27 birth stars' natures, read from static/kuta.js so the free page and the reading never drift."""
    import re
    src = open(os.path.join(HERE, "static", "kuta.js"), encoding="utf-8").read()
    return json.loads(re.search(r"const GANA = (\[.*?\]);", src).group(1))


GANA = _load_gana()

def _nadi(n): return [0, 1, 2, 2, 1, 0][n % 6]


def _rel(a, b, friends, enemies): return "friend" if b in friends[a] else "enemy" if b in enemies[a] else "neutral"


def kuta(ma, mb, friends, enemies):
    """One reading of the match, the first Moon in the first position (as kuta.js read())."""
    sa, sb, na, nb = int(E.norm(ma) // 30), int(E.norm(mb) // 30), int(E.norm(ma) // NAK), int(E.norm(mb) // NAK)
    d = (sb - sa + 12) % 12 + 1
    bh = d in (2, 12, 5, 9, 6, 8)
    la, lb = LORD[sa], LORD[sb]
    if la == lb: gm = 5
    else:
        x = "+".join(sorted([_rel(la, lb, friends, enemies), _rel(lb, la, friends, enemies)]))
        gm = {"friend+friend": 5, "friend+neutral": 4, "neutral+neutral": 3, "enemy+friend": 1, "enemy+neutral": .5, "enemy+enemy": 0}[x]
    ab, ba = sb in VASHYA.get(sa, []), sa in VASHYA.get(sb, [])
    tara = lambda f, t: ((t - f + 27) % 27 + 1) % 9 not in (3, 5, 7)
    rows = {"Varna": 1 if VARNA[sa] >= VARNA[sb] else 0, "Vashya": 2 if sa == sb or (ab and ba) else 1 if ab or ba else 0,
            "Tara": (1.5 if tara(nb, na) else 0) + (1.5 if tara(na, nb) else 0), "Yoni": YONI_SCORE[YONI_OF[na]][YONI_OF[nb]],
            "Graha Maitri": gm, "Gana": GANA_SCORE[GANA[na]][GANA[nb]], "Bhakoot": 0 if bh else 7, "Nadi": 0 if _nadi(na) == _nadi(nb) else 8}
    facts = {"Varna": f"{VARNA_NAME[VARNA[sa]]} · {VARNA_NAME[VARNA[sb]]}", "Vashya": "by Moon sign", "Tara": "counted both ways between your birth stars",
             "Yoni": f"{YONI[YONI_OF[na]]} · {YONI[YONI_OF[nb]]}", "Graha Maitri": f"{la} · {lb}", "Gana": f"{GANA[na]} · {GANA[nb]}",
             "Bhakoot": f"Moon signs {d} and {(14 - d) % 12 or 12} apart", "Nadi": f"{NADI[_nadi(na)]} · {NADI[_nadi(nb)]}"}
    return {"rows": rows, "facts": facts, "total": sum(rows.values())}


def _tier(k, v):
    m = MAX[k]; K = T["KUTA"][k]
    if v >= m * 0.75 or (k == "Yoni" and v >= 3): return K["full"]
    if v == 0 or (k == "Graha Maitri" and v <= 1): return K["none"]
    return K.get("part", K["full"] if v >= m / 2 else K["none"])


def old_match(A, B, friends, enemies, short=False):
    ab, ba = kuta(A["C"]["sid"]["Moon"], B["C"]["sid"]["Moon"], friends, enemies), kuta(B["C"]["sid"]["Moon"], A["C"]["sid"]["Moon"], friends, enemies)
    best = max(ab["total"], ba["total"])
    v = T["KUTA_VERDICT"]["strong" if best >= 28 else "workable" if best >= 18 else "demanding"]
    score = (f"<b>{ab['total']:g}</b> of 36" if ab["total"] == ba["total"] else
             f"<b>{ab['total']:g}</b> of 36 read from {A['name']}, <b>{ba['total']:g}</b> read from {B['name']}")
    if short: return f"<p>{A['name']} and {B['name']}: {score}, {v}.</p>", ab
    rows = "".join(f'<div class="rd-body"><h5>{k} · {ab["rows"][k]:g}{"" if ab["rows"][k] == ba["rows"][k] else f" / {ba["rows"][k]:g}"} of {MAX[k]}</h5>'
                   f'<p class="rd-kenning">{T["KUTA"][k]["about"]} · {ab["facts"][k]}</p><p>{_tier(k, max(ab["rows"][k], ba["rows"][k]))}</p></div>' for k in MAX)
    return f'<p>{T["KUTA_INTRO"]}</p><p class="rd-score">{score}: {v}.</p>{rows}', ab


# ---------------- how your bodies meet ----------------
def bodies(A, B):
    GN = C_["GATE_NAME"]; CEN = REG_EXT["CENTRES"]
    ra, rb = hd(A["C"]["natal"]), hd(B["C"]["natal"])
    ga, gb = RV.gates(A["C"]["natal"]), RV.gates(B["C"]["natal"])
    full = lambda g, c: c[0] in g and c[1] in g
    one = lambda g, c: (c[0] in g) != (c[1] in g)
    kinds = {"em": [], "comp": [], "dom": [], "promise": []}
    for c in RV.CHANNELS:
        if full(ga, c) and full(gb, c): kinds["comp"].append((c, None))
        elif full(ga, c) or full(gb, c):
            owner, other = (A, gb) if full(ga, c) else (B, ga)
            kinds["dom" if not (c[0] in other or c[1] in other) else "promise"].append((c, owner))
        elif one(ga, c) and one(gb, c) and not (c[0] in ga and c[0] in gb) and not (c[1] in ga and c[1] in gb): kinds["em"].append((c, None))
    union = {"personality": {f"g{i}": {"gate": g, "line": 1} for i, g in enumerate(sorted(ga | gb))}, "design": {}}
    rc = hd(union)
    ch = lambda c: fill(T["HD_CHANNEL"], g1=c[0], t1=GN.get(str(c[0]), ""), g2=c[1], t2=GN.get(str(c[1]), ""))
    out = [f'<p>{T["HD_INTRO"]}</p><p>{fill(T["HD_TYPES"], a=A["name"], b=B["name"], ta=ra["type"], tb=rb["type"], aa=ra["authority"].lower(), ab=rb["authority"].lower(), tc=rc["type"])}</p>']
    for k in ("em", "comp", "dom", "promise"):
        if not kinds[k]: continue
        items = "".join(f"<li>{ch(c)}{' · ' + fill(T['HD_OWNER'], name=o['name']) + ' whole' if o else ''}</li>" for c, o in kinds[k])
        out.append(f'<p>{T["HD_KIND"][k]}</p><ul>{items}</ul>')
    name = lambda k: RV.CENTRES[k][0]
    cond = [fill(T["HD_COND"], a=P["name"], b=Q["name"], centre=name(k), does=CEN[name(k)]["does"].rstrip(".").lower(), open=CEN[name(k)]["open"])
            for P, Q, rp, rq in ((A, B, ra, rb), (B, A, rb, ra)) for k in RV.CENTRES if k in rp["defined"] and k not in rq["defined"]]
    out.append(f'<h3 class="rd-tier">{T["HD_COND_TITLE"]}</h3>' + ("".join(f"<p>{x}</p>" for x in cond) if cond else f'<p>{T["HD_COND_NONE"]}</p>'))
    both_open = [name(k) for k in RV.CENTRES if k not in ra["defined"] and k not in rb["defined"]]
    if both_open: out.append(f'<p>{fill(T["HD_OPEN_BOTH"], centres=", ".join(both_open))}</p>')
    return "".join(out), len(kinds["em"])


# ---------------- your numbers together ----------------
def numbers(P, season, now):
    year = E_year(now)
    nums = [NUM.of(p["date"], p.get("full_name", ""), year) for p in P]
    kinds = [k for k in ("life_path", "birthday", "expression", "soul_urge", "personality") if all(k in n for n in nums)]
    label = {"life_path": "Life path", "birthday": "Birthday", "expression": "Expression", "soul_urge": "Soul urge", "personality": "Personality"}
    head = "".join(f"<th>{p['name']}</th>" for p in P)
    rows = "".join(f"<tr><td>{label[k]}</td>" + "".join(f"<td><b>{n[k]}</b></td>" for n in nums) + "</tr>" for k in kinds)
    out = [f'<p>{T["NUM_INTRO"]}</p><div class="rd-tw"><table><tr><th></th>{head}</tr>{rows}</table></div>']
    if not all("expression" in n for n in nums): out.append(f'<p class="rd-note">{T["NUM_NO_NAME"]}</p>')
    if len(P) == 2:
        for k in kinds:
            a, b = nums[0][k], nums[1][k]
            if NUM.root(a) == NUM.root(b):
                out.append(f'<h3 class="rd-tier">{label[k]}: {a} and {b}</h3><p>{T["NUM_PAIR_SAME"]}</p>'); continue
            pa, pb = NUM.planets(a), NUM.planets(b)
            ls, lv = season(pa["stavefall"], pb["stavefall"]), season(pa["vedic"], pb["vedic"])
            meaning = (f'By both seatings, {T["NUM_MEANING"][ls]}.' if ls == lv else
                       f'By Stavefall, {T["NUM_MEANING"][ls]}; by the Vedic seating, {T["NUM_MEANING"][lv]}.')
            out.append(f'<h3 class="rd-tier">{label[k]}: {a} and {b}</h3><p>{fill(T["NUM_PAIR"], sa=the(pa["stavefall"]), sb=the(pb["stavefall"]), va=the(pa["vedic"]), vb=the(pb["vedic"]), ls=T["NUM_LABEL"][ls], lv=T["NUM_LABEL"][lv])} {meaning}</p>')
    return "".join(out)
