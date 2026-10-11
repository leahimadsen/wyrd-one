"""The bond in words: the paid writing about two people, for the reading together.

Free Compare shows a bond's facts (its Sukuyō relation by name, the contacts,
which houses). The meaning, in words, lives in lib/bond.json and is only ever
sent inside a paid reading together. The arithmetic here matches compare.js
and synastry.js, so the reading and the free page always agree."""
import json, os, re

from . import engine as E
from . import sukuyo as SK

B = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "bond.json"), encoding="utf-8"))
ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
WEIGHT = {"Sun": 3, "Moon": 3, "Venus": 2.5, "Mars": 2, "Mercury": 1.5, "Saturn": 2, "Jupiter": 1.5, "Rahu": 1.2, "Ketu": 1.2}
HARMONICS = [(1, 0, "Conjunction", 8), (2, 180, "Opposition", 8), (3, 120, "Trine", 7), (4, 90, "Square", 7), (6, 60, "Sextile", 5)]
HEAVY = {"Saturn", "Mars", "Rahu", "Ketu"}
ROLE = {"Sun": "will", "Moon": "need", "Mercury": "speech", "Venus": "affection", "Mars": "drive", "Jupiter": "faith",
        "Saturn": "duty", "Rahu": "hunger", "Ketu": "the already-known"}
FLAVOUR = {"conj": "fused: the two poles share a body", "soft": "flowing: each provisions the other", "hard": "in friction: each tests the other"}
ORD = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def aspect(a, b):
    d = abs(E.norm(a - b))
    if d > 180: d = 360 - d
    for n, deg, name, orb in HARMONICS:
        if abs(d - deg) <= orb: return {"n": n, "name": name, "orb": abs(d - deg)}
    return None


def contacts(A, B_):
    """Every close contact between two charts' nine, strongest first (as compare.js)."""
    out = []
    for p in ORDER:
        for q in ORDER:
            x = aspect(A["C"]["sid"][p], B_["C"]["sid"][q])
            if not x or x["orb"] > (6 if x["n"] == 1 else 5): continue
            f = "conj" if x["n"] == 1 else "soft" if x["n"] in (3, 6) else "hard"
            w = (WEIGHT[p] + WEIGHT[q]) * (1.4 - x["orb"] / 10) * (1.15 if x["n"] == 1 else 1)
            out.append({"p": p, "q": q, "x": x, "f": f, "w": w})
    return sorted(out, key=lambda c: -c["w"])


def _names(c, A, B_):
    return lambda s: re.sub(r"the (\w+) person", lambda m: "one of you" if c["p"] == c["q"] else
                                          A["name"] if m.group(1) == c["p"] else B_["name"] if m.group(1) == c["q"] else m.group(0), s)


def _entry(c):
    key = f'{c["p"]}-{c["q"]}' if ORDER.index(c["p"]) <= ORDER.index(c["q"]) else f'{c["q"]}-{c["p"]}'
    return B["PAIRS"].get(key)


def contact_text(c, A, B_):
    e, fill = _entry(c), _names(c, A, B_)
    if e:
        return f'{fill(e["core"])} {fill(e[c["f"]])}' + (f' <em class="cp-ask">{fill(e["ask"])}</em>' if e.get("ask") else "")
    return f'{A["name"]}\'s {c["p"]} ({ROLE[c["p"]]}) meets {B_["name"]}\'s {c["q"]} ({ROLE[c["q"]]}), {FLAVOUR[c["f"]]}.'


def relation(A, B_):
    a, b = A.get("shuku"), B_.get("shuku")
    return SK.relation(a["index"], b["index"]) if a and b else None


def life(h, who):
    return B["LIFE"][h - 1].replace("their", f"{who}'s", 1)


def pair(A, B_, full=True):
    """The bond between two people, in words. A and B_ carry an escaped "name", "C" and "shuku"."""
    cs, R = contacts(A, B_), relation(A, B_)
    asks, out = [], []
    house = lambda P, Q, b: E.house_of(P["C"]["sid"][b], Q["C"]["ascS"])

    if R:
        t = B["SUKUYO"][R["pair"]]
        out.append(f'<h3 class="rd-tier">Sukuyō · {R["pairRead"]} ({R["pair"]})</h3><p>{t["text"]}</p>'
                   + (f'<p>{B["DISTANCE"][R["distance"]]}</p>' if R.get("distance") else ""))
        if t.get("ask"): asks.append(t["ask"])

    # what the bond is for, its higher and lower paths (as synastry.js paths())
    soft = [c for c in cs if c["f"] == "soft" or (c["f"] == "conj" and c["p"] not in HEAVY and c["q"] not in HEAVY)][:4]
    hard = [c for c in cs if c["f"] == "hard" or (c["f"] == "conj" and (c["p"] in HEAVY or c["q"] in HEAVY))][:4]
    gifts = [f'{P["name"]}\'s {b} ({ROLE[b]}) blesses {life(house(P, Q, b), Q["name"])}' for P, Q in ((A, B_), (B_, A))
             for b in ("Jupiter", "Venus", "Sun") if house(P, Q, b) in (1, 5, 7, 9, 10, 11)]
    weights = [f'{P["name"]}\'s {b} ({ROLE[b]}) presses on {life(house(P, Q, b), Q["name"])}' for P, Q in ((A, B_), (B_, A))
               for b in ("Saturn", "Mars", "Rahu") if house(P, Q, b) in (1, 4, 7, 8, 12)]
    bond = B["BOND"].get(R["pair"]) if R else None
    li = lambda xs: "<ul>" + "".join(f"<li>{x}.</li>" for x in xs) + "</ul>" if xs else ""
    flow = lambda c: f'{A["name"]}\'s {c["p"]} ({ROLE[c["p"]]}) and {B_["name"]}\'s {c["q"]} ({ROLE[c["q"]]}) flow: ' + (
        f'you share the same {ROLE[c["p"]]}, and it is easy between you' if c["p"] == c["q"] else f'{ROLE[c["p"]]} and {ROLE[c["q"]]} feed each other')
    grind = lambda c: f'{A["name"]}\'s {c["p"]} ({ROLE[c["p"]]}) and {B_["name"]}\'s {c["q"]} ({ROLE[c["q"]]}) grind: ' + (
        f'under stress your two kinds of {ROLE[c["p"]]} compete' if c["p"] == c["q"] else f'under stress, {ROLE[c["p"]]} and {ROLE[c["q"]]} fight for the same ground')
    out.append(f"""<h3 class="rd-tier">What this bond is for</h3>{f'<p>By the lunar mansions, {bond["high"]}</p>' if bond else ""}{li(gifts)}
      <h3 class="rd-tier">The higher path</h3><p>Grown well, this bond lifts both of you toward your higher purpose.</p>{li([flow(c) for c in soft])}
      <h3 class="rd-tier">The lower path</h3><p>{f'Left unconscious, {bond["low"]}' if bond else "Left unconscious, the frictions below run the bond instead of the bond running them."}</p>
      {li([grind(c) for c in hard] + [f"{w}: heavy, and lasting. Name it before it hardens" for w in weights])}
      <h3 class="rd-tier">Weaving the two</h3><p>{bond["weave"] + " " if bond else ""}The higher path does not cancel the lower one; it uses it. Every friction above is also where you can grow most, if both of you agree to work on it.</p>""")
    asks += [_names(c, A, B_)(_entry(c)["ask"]) for c in hard if _entry(c) and _entry(c).get("ask")]

    top = cs[:6 if full else 3]
    if top:
        out.append('<h3 class="rd-tier">The contacts between you, in words</h3><ol class="rd-contacts">' + "".join(
            f'<li><h5>{A["name"]}\'s {c["p"]} · {B_["name"]}\'s {c["q"]} · {c["x"]["name"].lower()} <small>orb {c["x"]["orb"]:.1f}°</small></h5>'
            f'<p>{contact_text(c, A, B_)}</p></li>' for c in top) + "</ol>")
    else:
        out.append("<p>No close contacts between the main planets: a bond that works through the houses rather than the aspects.</p>")

    if full:
        rows = lambda P, Q: "".join(f'<li><b>{P["name"]}\'s {b}</b> in {Q["name"]}\'s {ORD(house(P, Q, b))} house: '
                                    f'{P["name"]} {B["IN_HOUSE"][b]} {life(house(P, Q, b), Q["name"])}.</li>' for b in ORDER)
        out.append(f'<h3 class="rd-tier">Your planets in each other\'s houses, in words</h3><ul>{rows(A, B_)}</ul><ul>{rows(B_, A)}</ul>')
    return "".join(out), list(dict.fromkeys(asks))
