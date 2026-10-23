"""The free Sukuyō pages: /learn/sukuyo (what it is, the calendar, the 27 shuku, the ring of the three nines)
and /learn/sukuyo/find (a birth shuku, or two people's relation, from their birth dates).

Words are in lib/sukuyo_learn.json. Only the names of the relations are free; what each one means is the
paid writing in lib/bond.json and stays in the reading together."""
import html, json, math, os
from datetime import date

from . import sukuyo as SK

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "sukuyo_learn.json"), encoding="utf-8"))
e = html.escape
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]
# the six relations, coloured from The Völva's wheel of the houses, each by the house it is most like
PAIR_HOUSE = {"命": 1,     # Life: the self at the gate
              "業胎": 12,  # Karma and Womb: the seam, the hidden, what is carried in
              "栄親": 5,   # Prosperity and Intimacy: radiance, merit
              "友衰": 11,  # Friendship and Decline: the many, the friends
              "安壊": 8,   # Peace and Destruction: the depths, transformation
              "危成": 7}   # Danger and Completion: the other, the covenant
def _house_hex(n):
    from .pages import C
    return C["HOUSES"][n - 1]["hex"]
PAIR_COLOUR = {p: _house_hex(n) for p, n in PAIR_HOUSE.items()}


def slug(s):
    from .pages import slug as _s
    return _s(s)


def nak_link(name):
    return f'<a href="/learn/nakshatras/{slug(name)}">{e(name)}</a>'


def ring_svg():
    """The ring of the three nines, counted from your own shuku at the top."""
    cx = cy = 300
    def pt(r, k):
        a = math.radians(-90 + k * 360 / 27)
        return cx + r * math.cos(a), cy + r * math.sin(a)
    out = []
    for k in range(27):
        name = SK.RING[k]; pair = SK.PAIR[name]; col = PAIR_COLOUR[pair]
        a0, a1 = -90 + (k - .5) * 360 / 27, -90 + (k + .5) * 360 / 27
        p = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(270, a0), p(270, a1), p(196, a1), p(196, a0)
        out.append(f'<path d="M{x0:.1f},{y0:.1f} A270,270 0 0 1 {x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} A196,196 0 0 0 {x3:.1f},{y3:.1f} Z" '
                   f'fill="{col}" fill-opacity="{1 if name in ("命", "業", "胎") else .82}" class="sr-seg"/>')
        x, y = pt(244, k)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" class="sr-k">{name}</text>')
        x, y = pt(203, k)                       # the English name runs along the radius, inside the ring, never upside down
        ang = -90 + k * 360 / 27
        right = math.cos(math.radians(ang)) >= -1e-9
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" class="sr-en" text-anchor="{"end" if right else "start"}" '
                   f'transform="rotate({ang if right else ang + 180:.1f} {x:.1f} {y:.1f})">{e(SK.EN[name])}</text>')
        x, y = pt(286, k)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" class="sr-n">{k}</text>')
        m = min(k, 27 - k)
        dist = "" if name in ("命", "業", "胎") else "near" if m <= 4 else "far" if m <= 8 else "middle"
        if dist:
            x, y = pt(128, k)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ {"near": 5, "far": 2.2, "middle": 3.6}[dist] }" class="sr-d"/>')
    for k in (0, 9, 18):                      # the three nines open at Life, Karma and Womb
        (x0, y0), (x1, y1) = pt(140, k - .5), pt(300, k - .5)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="sr-cut"/>')
    out.append(f'<text x="{cx}" y="{cy - 16}" class="sr-mid">count from</text><text x="{cx}" y="{cy + 10}" class="sr-mid big">your shuku</text>'
               f'<text x="{cx}" y="{cy + 34}" class="sr-mid">at the top</text>')
    legend = "".join(f'<li><span class="sr-sw" style="background:{c}"></span><b>{p}</b> {e(T["PAIRS"][p]["title"].split(" · ")[1])}</li>' for p, c in PAIR_COLOUR.items())
    return (f'<figure class="sr-fig"><svg viewBox="0 0 600 600" role="img" aria-labelledby="srt"><title id="srt">The ring of the three nines: '
            f'the eleven names around the twenty-seven shuku, counted from your own</title>{"".join(out)}</svg>'
            f'<figcaption><ul class="sr-legend">{legend}</ul>Each name is coloured by the relation it belongs to, in the colours of the wheel of the houses. The dots near the middle mark the distance: '
            f'a large dot near, a middle one middle, a small one far. The lines mark where each of the three nines begins.</figcaption></figure>')


def jp_font(body):
    """Noto Serif JP, cut down to the kanji and kana the site uses (tools/fonts.py) and served from here, so they look the same everywhere."""
    chars = "".join(sorted({c for c in body if "\u3000" <= c <= "\u9fff"}))
    return '<link rel="stylesheet" href="/static/fonts/jp.css">' if chars else ""


def find_form(a="", b=""):
    lo, hi = SK_RANGE
    return f"""<form class="pg-form sk-find" method="post" action="/learn/sukuyo/find">
<label>A birth date <input type="date" name="a" required value="{e(a)}" min="{lo}-01-01" max="{hi}-12-31"></label>
<label>A second birth date (optional) <input type="date" name="b" value="{e(b)}" min="{lo}-01-01" max="{hi}-12-31"></label>
<button class="btn-cast" type="submit">Find the shuku</button></form>"""


SK_RANGE = (1851, 2148)          # the old calendar is rebuilt from a year either side of the date, inside the ephemeris


def index_page(base):
    from .pages import _crumbs, _cta
    month_of = {i: n + 1 for n, i in enumerate(SK.MONTH_START)}
    rows = "".join(f'<tr><td>{i + 1}</td><td class="sk-kj">{k}</td><td>{e(r)}</td><td>{nak_link(nak)}</td>'
                   f'<td>{"the " + ORD[month_of[i] - 1] + " month" if i in month_of else ""}</td></tr>' for i, (k, r, nak) in enumerate(SK.SHUKU))
    starts = "".join(f'<tr><td>{n + 1}</td><td><span class="sk-kj">{SK.SHUKU[i][0]}</span> {e(SK.SHUKU[i][1])}</td></tr>' for n, i in enumerate(SK.MONTH_START))
    pairs = "".join(f'<li><span class="sk-pk" style="color:{PAIR_COLOUR[p]}">{p}</span><span><b>{e(v["title"])}</b>, {e(v["short"])}. '
                    f'<span class="muted">{e(v["how"][:1].upper() + v["how"][1:])}.</span></span></li>' for p, v in T["PAIRS"].items())
    ps = lambda xs: "".join(f"<p>{e(x)}</p>" for x in xs)
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>Sukuyō</h1>
<p class="lede">{e(T["LEDE"])}</p>
<div class="cta sk-top"><p>{e(T["FIND"])}</p>{find_form()}</div>

<h2>Where it comes from</h2>{ps(T["ORIGIN"])}

<h2>The twenty-seven shuku</h2>
<p>{e(T["STARS"])}</p>
<div class="tw"><table class="sk-table"><tr><th></th><th>Shuku</th><th>Reading</th><th>Nakshatra of the same stars</th><th>Opens</th></tr>{rows}</table></div>

<h2>Your shuku comes from the calendar</h2>{ps(T["CALENDAR"])}
<p>{e(T["METHOD"])}</p>
<div class="tw"><table class="sk-table sk-months"><tr><th>Lunar month</th><th>Opens on</th></tr>{starts}</table></div>
<p class="muted">{e(T["JAPAN_TIME"])}</p>

<h2>The three nines</h2>{ps(T["RING"])}
{ring_svg()}

<h2>The six relations</h2>
<p>{e(T["PAIRS_INTRO"])}</p>
<ul class="sk-pairs">{pairs}</ul>
<p>{e(T["DISTANCE"])}</p>
<p class="note-box">{e(T["CTA"])} <a href="/reports">See the Reading Together</a>.</p>
{_cta()}"""
    body += jp_font(body)
    desc = ("Sukuyō (宿曜), the Japanese art of the lunar mansions: where it comes from, the 27 shuku, how your birth shuku is found from the "
            "old lunar calendar, and the six relations of the three nines. Find your shuku free.")
    return ("Sukuyō Astrology: the 27 Shuku and the Six Relations · Find Your Shuku · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), ("Sukuyō", "/learn/sukuyo")]))


def _parse(s):
    try:
        d = date.fromisoformat((s or "").strip())
    except ValueError:
        return None
    return d if SK_RANGE[0] <= d.year <= SK_RANGE[1] else None


def _card(eph, d, who):
    s = SK.birth_shuku(eph, d.year, d.month, d.day)
    open_i = SK.MONTH_START[s["lunarMonth"] - 1]
    leap = "the leap " if s["leap"] else "the "
    return s, f"""<div class="sk-card"><span class="sk-big">{s["kanji"]}</span><div>
<h3>{e(who)}: {e(s["read"])}</h3>
<p>Born {d.day} {MONTHS[d.month - 1]} {d.year}: day {s["lunarDay"]} of {leap}{ORD[s["lunarMonth"] - 1]} lunar month.
That month opens on <span class="sk-kj">{SK.SHUKU[open_i][0]}</span> {e(SK.SHUKU[open_i][1])}, and {s["lunarDay"] - 1} {"day" if s["lunarDay"] == 2 else "days"} on
from it is <span class="sk-kj">{s["kanji"]}</span> {e(s["read"])}.</p>
<p class="muted">Its stars are those of {nak_link(s["mansion"])}.</p></div></div>"""


def find_page(eph, a, b):
    """Returns (title, body) or None when the first date can't be read."""
    da, db = _parse(a), _parse(b) if b else None
    if not da:
        return None
    sa, card_a = _card(eph, da, "The first date" if db else "Your shuku")
    out = card_a
    if db:
        sb, card_b = _card(eph, db, "The second date")
        r = SK.relation(sa["index"], sb["index"])
        v = T["PAIRS"][r["pair"]]
        roles = ("You share one shuku: each of you is the other's 命, Life." if r["pair"] == "命" else
                 f'The second stands on the first one\'s <span class="sk-kj">{r["toA"]}</span> {e(SK.EN[r["toA"]])}; '
                 f'the first stands on the second one\'s <span class="sk-kj">{r["toB"]}</span> {e(SK.EN[r["toB"]])}.')
        out += card_b + f"""<div class="sk-rel" style="--pc:{PAIR_COLOUR[r["pair"]]}"><span class="sk-big">{r["pair"]}</span><div>
<h3>Together: {e(v["title"])}</h3><p><b>{e(v["short"][:1].upper() + v["short"][1:])}.</b> {roles}
{f' Distance: <b>{r["distance"]}</b>.' if r["distance"] else ""}</p></div></div>
<p class="note-box">{e(T["CTA"])} <a href="/chart#compare">Add both charts in Compare</a> to get it, or <a href="/reports">see the readings</a>.</p>"""
    else:
        out += '<p class="muted">Add a second birth date above to see how two people stand to each other.</p>'
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn/sukuyo">Sukuyō</a></p>
<h1>{"Two shuku" if db else "Your shuku"}</h1>
{out}
<h2>Try other dates</h2>{find_form(a, b or "")}
<p><a href="/learn/sukuyo">What Sukuyō is, and how the shuku is found →</a></p>"""
    return ("Find your shuku · Sukuyō · The Wyrd Console", body + jp_font(body))
