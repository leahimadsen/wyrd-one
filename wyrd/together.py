"""The Wyrd Reading Together: two to nine people, built around timing.

  Prologue                    the Norns seat you at one table
  I   Who Sits at the Table   each person's soul-planet, seat and current guest
  II  The Bond                each pair in words: Sukuyō, what it is for, the higher and lower
                              paths, the contacts, the houses (wyrd/bond.py, lib/bond.json)
  III What You Wake in Each Other   where each one's soul-planet and guest land in the others' houses
  IV  The Old Match           Ashtakoota, the eight measures in words (wyrd/together_more.py)
  V   How Your Bodies Meet    two bodygraphs: the channels between you, who conditions whom (couples)
  VI  Your Numbers Together   life paths and name numbers side by side, and how their planets get on
  VII The Seasons You Share   the next thirty years chapter by chapter, the sky's appointments, year by year
  VIII The Questions

Every sentence comes from lib/together.json (drafted for The Völva to rewrite)
and lib/register_ext.json; this file only chooses which lines the charts call for.
Free Compare shows the bond's facts; everything it means, in words, is here."""
import html, json, math, os

from . import engine as E
from . import bond as BOND
from . import together_more as MORE
from .reading import ENG
from .reading import section, pair, ROMAN, GLYPH
from .reading_more import X as REG_EXT, ORD, E_year, the

T = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "together.json"), encoding="utf-8"))
MAX_PEOPLE = 9
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

    # ---------- I · who sits at the table ----------
    rows = "".join(f"<tr><td>{p['name']}</td><td>{GLYPH[s]} {s}</td><td>{seat(p['C'])}{' (Sun)' if p['C'].get('unknownTime') else ''}</td>"
                   f"<td>{GLYPH[g]} {g} · until {E_year(p['dasha']['cur']['to'])}</td></tr>" for p, s, g in zip(P, soul, guest))
    out.append(section(0, T["TABLE_TITLE"], T["TABLE_SUB"], f"""<p>{T["TABLE_INTRO"]}</p>
      <div class="rd-tw"><table><tr><th>Who</th><th>Soul-planet</th><th>Seat</th><th>Guest now</th></tr>{rows}</table></div>"""))

    # ---------- II · the bond, pair by pair ----------
    pairs = [(i, k) for i in range(len(P)) for k in range(i + 1, len(P))]
    bond_asks, blocks = [], []
    for i, k in pairs:
        text, asks = BOND.pair(P[i], P[k], full=two)
        bond_asks += asks
        blocks.append(text if two else f'<h3 class="rd-tier">{fill(T["BOND_PAIR"], a=P[i]["name"], b=P[k]["name"])}</h3><div class="rd-pairbond">{text}</div>')
    out.append(section(0, T["BOND_TITLE"], T["BOND_SUB"], f'<p>{T["BOND_INTRO"]}</p>{"".join(blocks)}'))

    # ---------- III · what you wake in each other ----------
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

    # ---------- IV · the old match ----------
    match = MORE.old_match(P[0], P[1], FRIENDS, ENEMIES)[0] if two else \
        f'<p>{T["KUTA_INTRO"]}</p>' + "".join(MORE.old_match(P[i], P[k], FRIENDS, ENEMIES, short=True)[0] for i, k in pairs)
    out.append(section(0, T["KUTA_TITLE"], T["KUTA_SUB"], match))

    # ---------- V · how your bodies meet (couples: two bodygraphs read in full) ----------
    if two:
        out.append(section(0, T["HD_TITLE"], T["HD_SUB"], MORE.bodies(P[0], P[1])[0]))

    # ---------- VI · your numbers together ----------
    if all(p.get("date") for p in P):
        out.append(section(0, T["NUM_TITLE"], T["NUM_SUB"], MORE.numbers(P, season, now)))

    # ---------- VII · the seasons you share ----------
    now_rows = "".join(pair(f"{P[i]['name']} &amp; {P[k]['name']}",
                            f"{GLYPH[guest[i]]} {guest[i]} and {GLYPH[guest[k]]} {guest[k]}: <b>{S[season(guest[i], guest[k])]['label']}</b>")
                       for i, k in pairs)
    kinds = sorted({season(guest[i], guest[k]) for i, k in pairs}, key=list(S).index)
    now_text = "".join(f'<p><b>{S[x]["label"][0].upper() + S[x]["label"][1:]}.</b> {S[x]["text"]}</p>' for x in kinds)
    chapters, watch = MORE.seasons(P, season, S, now)
    out.append(section(0, T["SEASON_TITLE"], T["SEASON_SUB"], f"""{now_rows}{now_text}{chapters}"""))

    # ---------- V · the questions ----------
    qs = list(dict.fromkeys(bond_asks + T["ASKS"]))
    out.append(section(0, T["ASKS_TITLE"], T["ASKS_SUB"], '<ol class="rd-qs">' + "".join(f"<li><div>{q}</div></li>" for q in qs) + "</ol>"))

    for i in range(len(out)):
        out[i] = out[i].replace("{{N}}", ROMAN[i], 1)

    # ---------- the prologue: the table (told last, so it can point at what the book holds) ----------
    guests = [fill(T["GUEST_NOW"], lord=the(g), name=p["name"]) for p, g in zip(P, guest)]
    now_season = S[season(guest[0], guest[1])]["text"] if two else ""
    gifts = [fill(T["PROLOGUE_GIFT"], name=p["name"], shakti=ENG[E.nak_index(p["C"]["sid"]["Moon"])][2], mansion=ENG[E.nak_index(p["C"]["sid"]["Moon"])][0]) for p in P]
    nxt = min(((m["from"], i, m["lord"]) for i, p in enumerate(P) for m in p["dasha"]["maha"] if m["from"] > now), default=None)
    mark = min(((a, i, k) for i, p in enumerate(P) for k, a, b in p.get("marks", [])), default=None)
    book = fill(T["PROLOGUE_BOOK"], turn=fill(T["PROLOGUE_TURN"], lord=the(nxt[2]), name=P[nxt[1]]["name"], year=E_year(nxt[0])) if nxt else "",
                mark=fill(T["PROLOGUE_MARK"], year=E_year(mark[0]), what=MORE.fill(T["MARK_SHORT"][mark[2]], name=P[mark[1]]["name"])) if mark else "",
                year=watch[0] if watch else E_year(nxt[0]) if nxt else E_year(now)).replace("  ", " ")
    shared = [BOND.relation(P[i], P[k]) for i, k in pairs] if two else []
    errand = BOND.B["BOND"][shared[0]["pair"]]["high"] if shared and shared[0] else T["PROLOGUE_ERRAND_PLAIN"]
    story = [T["PROLOGUE_OPEN"],
             " ".join(fill(T["PROLOGUE_PERSON"], name=p["name"], sent=T["SENT"][s], wore=T["WORE"][seat(p["C"])]) for p, s in zip(P, soul)),
             fill(T["PROLOGUE_GIFTS"], gifts=names_line(gifts)),
             T["PROLOGUE_TABLE_TWO"] if two else fill(T["PROLOGUE_TABLE_MANY"], n=len(P)),
             fill(T["PROLOGUE_NOW"], guests=names_line(guests), season=now_season), book,
             fill(T["PROLOGUE_ERRAND"], errand=errand[0].upper() + errand[1:])]
    prologue = f"""<section class="rd-sec rd-story"><h2>{T["PROLOGUE_TITLE"]}</h2><div class="rd-sub">{T["PROLOGUE_SUB"]}</div>
      {"".join(f"<p>{x}</p>" for x in story)}<p class="rd-kenning">{T["PROLOGUE_CLOSE"]}</p></section>"""
    return prologue + "".join(out)
