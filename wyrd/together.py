"""The Wyrd Reading Together: two to nine people, built around timing.

  Prologue                    the Norns seat you at one table
  I   Who Sits at the Table   each person's soul-planet, seat and current guest
  II  What You Wake in Each Other   where each one's soul-planet and guest land in the others' houses
  III The Seasons You Share   how the guests get on now, and every change in the next thirty years
  IV  The Questions

Every sentence comes from lib/together.json (drafted for The Völva to rewrite)
and lib/register_ext.json; this file only chooses which lines the charts call for.
Free Compare (static/dynamics.js) covers the bond itself; this is the paid side."""
import html, json, math, os

from . import engine as E
from .reading import section, pair, ROMAN, GLYPH
from .reading_more import X as REG_EXT, ORD, E_year, the

T = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "together.json"), encoding="utf-8"))
MAX_PEOPLE = 9
AHEAD_YEARS = 30
esc = html.escape

# the natural friendships (naisargika maitri) of the seven; Rahu is read like Saturn, Ketu like Mars
FRIENDS = {"Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"},
           "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
           "Saturn": {"Mercury", "Venus"}}
ENEMIES = {"Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"},
           "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"}}
AS = {"Rahu": "Saturn", "Ketu": "Mars"}
SCORE = {2: "allies", 1: "friendly", 0: "polite", -1: "uneasy", -2: "odds"}


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def season(a, b):
    """How two period lords get on: same, allies, friendly, polite, uneasy or odds."""
    if a == b: return "same"
    x, y = AS.get(a, a), AS.get(b, b)
    view = lambda p, q: 0 if p == q else 1 if q in FRIENDS[p] else -1 if q in ENEMIES[p] else 0
    return SCORE[view(x, y) + view(y, x)]


def guest_at(dasha, jd):
    return next((m["lord"] for m in dasha["maha"] if m["from"] <= jd < m["to"]), dasha["cur"]["lord"])


def names_line(ns):
    return ns[0] if len(ns) == 1 else " and ".join(ns) if len(ns) == 2 else ", ".join(ns[:-1]) + " and " + ns[-1]


def seat(C): return E.SIGNS[math.floor(E.norm(C["ascS"]) / 30)]


def build(people):
    """people: [{"name", "C", "dasha"}], two to nine. Returns the reading's sections as HTML."""
    P = [dict(p, name=esc(p["name"])) for p in people]
    two, now = len(P) == 2, P[0]["dasha"]["now"]
    soul = [p["C"]["karaka"]["Atmakaraka"] for p in P]
    guest = [p["dasha"]["cur"]["lord"] for p in P]
    S = T["SEASONS"]
    out = []

    # ---------- the prologue: the table ----------
    guests = [fill(T["GUEST_NOW"], lord=the(g), name=p["name"]) for p, g in zip(P, guest)]
    now_season = S[season(guest[0], guest[1])]["text"] if two else ""
    story = [T["PROLOGUE_OPEN"],
             " ".join(fill(T["PROLOGUE_PERSON"], name=p["name"], sent=T["SENT"][s], wore=T["WORE"][seat(p["C"])]) for p, s in zip(P, soul)),
             T["PROLOGUE_TABLE_TWO"] if two else fill(T["PROLOGUE_TABLE_MANY"], n=len(P)),
             fill(T["PROLOGUE_NOW"], guests=names_line(guests), season=now_season)]
    prologue = f"""<section class="rd-sec rd-story"><h2>{T["PROLOGUE_TITLE"]}</h2><div class="rd-sub">{T["PROLOGUE_SUB"]}</div>
      {"".join(f"<p>{x}</p>" for x in story)}<p class="rd-kenning">{T["PROLOGUE_CLOSE"]}</p></section>"""

    # ---------- I · who sits at the table ----------
    rows = "".join(f"<tr><td>{p['name']}</td><td>{GLYPH[s]} {s}</td><td>{seat(p['C'])}{' (Sun)' if p['C'].get('unknownTime') else ''}</td>"
                   f"<td>{GLYPH[g]} {g} · until {E_year(p['dasha']['cur']['to'])}</td></tr>" for p, s, g in zip(P, soul, guest))
    out.append(section(0, T["TABLE_TITLE"], T["TABLE_SUB"], f"""<p>{T["TABLE_INTRO"]}</p>
      <div class="rd-tw"><table><tr><th>Who</th><th>Soul-planet</th><th>Seat</th><th>Guest now</th></tr>{rows}</table></div>"""))

    # ---------- II · what you wake in each other ----------
    life, lends = REG_EXT["HOUSE_LIFE"], {k: v["lends"] for k, v in REG_EXT["PLANETS"].items() if v.get("lends")}
    blocks = []
    for i, a in enumerate(P):
        lines = []
        for k, b in enumerate(P):
            if i == k: continue
            hs = E.house_of(a["C"]["sid"][soul[i]], b["C"]["ascS"]); hg = E.house_of(a["C"]["sid"][guest[i]], b["C"]["ascS"])
            lines.append(f'<p>{fill(T["WAKE_SOUL"], a=a["name"], b=b["name"], planet=the(soul[i]), house=ORD(hs), life=life[hs - 1], lends=lends[soul[i]])} '
                         f'{fill(T["WAKE_GUEST"], a=a["name"], b=b["name"], lord=the(guest[i]), house=ORD(hg), life=life[hg - 1])}</p>')
        blocks.append(f'<h3 class="rd-tier">What {a["name"]} wakes</h3>{"".join(lines)}')
    unknown = " ".join(fill(T["UNKNOWN_HOUSES"], name=p["name"]) for p in P if p["C"].get("unknownTime"))
    out.append(section(0, T["WAKE_TITLE"], T["WAKE_SUB"], f"""<p>{T["WAKE_INTRO"]}</p>
      {f'<p class="rd-note">{unknown}</p>' if unknown else ""}{"".join(blocks)}"""))

    # ---------- III · the seasons you share ----------
    pairs = [(i, k) for i in range(len(P)) for k in range(i + 1, len(P))]
    now_rows = "".join(pair(f"{P[i]['name']} &amp; {P[k]['name']}",
                            f"{GLYPH[guest[i]]} {guest[i]} and {GLYPH[guest[k]]} {guest[k]}: <b>{S[season(guest[i], guest[k])]['label']}</b>")
                       for i, k in pairs)
    kinds = sorted({season(guest[i], guest[k]) for i, k in pairs}, key=list(S).index)
    now_text = "".join(f'<p><b>{S[x]["label"][0].upper() + S[x]["label"][1:]}.</b> {S[x]["text"]}</p>' for x in kinds)
    changes = sorted((m["from"], i, m["lord"]) for i, p in enumerate(P) for m in p["dasha"]["maha"]
                     if now < m["from"] <= now + AHEAD_YEARS * E.YEAR)
    ahead = []
    for jd, i, lord in changes:
        if two:
            other = guest_at(P[1 - i]["dasha"], jd + 1)
            what = fill(T["SEASON_CHANGE_TWO"], name=P[i]["name"], lord=lord, label=S[season(lord, other)]["label"])
        else:
            what = fill(T["SEASON_CHANGE"], name=P[i]["name"], lord=lord)
        ahead.append(f"<tr><td>{E_year(jd)}</td><td>{GLYPH[lord]} {what}</td></tr>")
    out.append(section(0, T["SEASON_TITLE"], T["SEASON_SUB"], f"""<p>{T["SEASON_INTRO"]}</p>{now_rows}{now_text}
      <h3 class="rd-tier">{T["SEASON_AHEAD"]}</h3><p>{T["SEASON_AHEAD_INTRO"]}</p>
      <div class="rd-tw"><table><tr><th>Year</th><th>What changes</th></tr>{"".join(ahead)}</table></div>"""))

    # ---------- IV · the questions ----------
    out.append(section(0, T["ASKS_TITLE"], T["ASKS_SUB"], '<ol class="rd-qs">' + "".join(f"<li><div>{q}</div></li>" for q in T["ASKS"]) + "</ol>"))

    for i in range(len(out)):
        out[i] = out[i].replace("{{N}}", ROMAN[i], 1)
    return prologue + "".join(out)
