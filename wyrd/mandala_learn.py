"""The free introduction to the Wyrd Mandala: /learn/mandala.

What the instrument is, its two rotors, its rings from the centre out (with a key drawn as the wheel draws
them), the two decks, the Asura voids, how to read a station, three things to try, and the outline of the
paid course. Words are in lib/mandala_learn.json, the voids' names in lib/wyrd-mandala-108.csv; the course's own teaching is paid and stays off this page."""
import csv, html, json, math, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "mandala_learn.json"), encoding="utf-8"))
e = html.escape

# the wheel's own rings (static/mandala/wyrd-data.js LAYERS) and colours (the console's twelve house colours)
RINGS = [(0, 150), (156, 208), (212, 268), (272, 322), (327, 383), (392, 432), (436, 482)]
HUE = ["#ff3b4e", "#ff6a1f", "#ff8c1a", "#ffb31a", "#ffd400", "#a3e635", "#22e07a", "#14e0c0", "#22b8ff", "#6b6bff", "#b05cff", "#ff2fa8"]


def ring_key():
    """The rings as the wheel draws them, coloured by sign, each named at the side."""
    S, cx, cy, R = .52, 270, 270, 482
    o = []
    for n, (r0, r1) in enumerate(RINGS):
        if n == 0:
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{r1 * S:.1f}" fill="#120b30" stroke="rgba(214,200,255,.35)"/>')
            continue
        for k in range(12):
            a0, a1 = (k * 30 - 90) * math.pi / 180, ((k + 1) * 30 - 90) * math.pi / 180
            p = lambda r, a: (cx + r * S * math.cos(a), cy + r * S * math.sin(a))
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(r1, a0), p(r1, a1), p(r0, a1), p(r0, a0)
            alpha = .55 if n in (1, 6) else .4 if n in (2, 5) else .3
            o.append(f'<path d="M{x0:.1f} {y0:.1f}A{r1 * S:.1f} {r1 * S:.1f} 0 0 1 {x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}'
                     f'A{r0 * S:.1f} {r0 * S:.1f} 0 0 0 {x3:.1f} {y3:.1f}Z" fill="{HUE[k]}" fill-opacity="{alpha}"/>')
    # the triangle, the cross and the bindu
    tri = " ".join(f"{cx + 144 * S * math.cos((a - 90) * math.pi / 180):.1f},{cy + 144 * S * math.sin((a - 90) * math.pi / 180):.1f}" for a in (0, 120, 240))
    o.append(f'<polygon points="{tri}" fill="none" stroke="#f2c14e" stroke-width="1"/><circle cx="{cx}" cy="{cy}" r="3" fill="#f1ecff"/>')
    # the names, with leaders from each ring at three o'clock
    labels = [name for name, _ in T["RINGS"]]
    for n, ((r0, r1), name) in enumerate(zip(RINGS, labels)):
        rm = (r0 + r1) / 2 * S if n else 60 * S
        y = 60 + n * 64
        o.append(f'<path d="M{cx + rm:.1f} {cy:.1f}L{cx + R * S + 22:.1f} {y}H{cx + R * S + 40:.1f}" fill="none" stroke="currentColor" stroke-opacity=".5"/>'
                 f'<circle cx="{cx + rm:.1f}" cy="{cy}" r="3" fill="currentColor" stroke="#fff" stroke-width="1"/>'
                 f'<text x="{cx + R * S + 46:.1f}" y="{y + 4}" fill="currentColor" font-size="15">{e(name)}</text>')
    return (f'<figure class="ml-fig"><svg viewBox="0 0 760 540" role="img" aria-labelledby="mlk"><title id="mlk">The rings of the Wyrd Mandala, '
            f'from the field at the centre to the tropical signs at the rim</title>{"".join(o)}</svg>'
            f'<figcaption>The rings from the centre out, each coloured by sign. The field and the five rings round it turn with the stars (sidereal); the outer two turn with the seasons (tropical).</figcaption></figure>')


SIGNS = "Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces".split()
# the voids as the sheet names them (lib/wyrd-mandala-108.csv), station by station
VOIDS = [(i + 1, r["nakshatra"], int(r["nak_pada"]), r["asura_void"])
         for i, r in enumerate(csv.DictReader(open(os.path.join(HERE, "lib", "wyrd-mandala-108.csv"), encoding="utf-8"))) if r["asura_void"]]


def void_strip():
    """One sidereal sign's nine padas, the voids dark at the fourth, seventh and ninth, with the 3-2-4 spacing above."""
    X = lambda i: 30 + i * 72 + 34          # centre of pada i (0-based)
    o = []
    for i in range(9):
        void = i + 1 in (4, 7, 9)
        o.append(f'<rect x="{30 + i * 72}" y="44" width="68" height="44" rx="3" fill="{"#050010" if void else HUE[0]}"'
                 f' fill-opacity="{1 if void else .3}" stroke="{"#c48cff" if void else "none"}" stroke-width="1.5"/>')
        if void: o.append(f'<circle cx="{X(i)}" cy="66" r="6" fill="none" stroke="#c48cff" stroke-width="1.5"/>')
        o.append(f'<text x="{X(i)}" y="110" text-anchor="middle" fill="currentColor" font-size="15">{i + 1}</text>')
    for a, b, n in ((3, 6, "3"), (6, 8, "2")):
        o.append(f'<path d="M{X(a)} 40Q{(X(a) + X(b)) / 2} {14 if b - a > 2 else 22} {X(b)} 40" fill="none" stroke="currentColor" stroke-opacity=".6"/>'
                 f'<text x="{(X(a) + X(b)) / 2}" y="{24 if b - a > 2 else 30}" text-anchor="middle" fill="currentColor" font-size="15">{n}</text>')
    o.append(f'<path d="M{X(8)} 40Q{X(8) + 40} 18 716 26" fill="none" stroke="currentColor" stroke-opacity=".6" stroke-dasharray="4 4"/>'
             f'<text x="{X(8) + 44}" y="22" text-anchor="middle" fill="currentColor" font-size="15">4</text>')
    return ('<figure class="ml-fig"><svg viewBox="0 0 720 120" role="img" aria-labelledby="mlv"><title id="mlv">One sidereal sign\'s nine padas, '
            'with the voids at the fourth, seventh and ninth</title>' + "".join(o) + '</svg>'
            '<figcaption>One sidereal sign, nine padas. The voids fall on the fourth, the seventh and the ninth, three, two and four apart, '
            'and the last four carry on into the next sign. Every sign is laid the same way.</figcaption></figure>')


def void_table():
    by = {}
    for st, nak, pada, name in VOIDS: by.setdefault((st - 1) // 9, []).append((st, nak, pada, name))
    cell = lambda v, n: f'<td data-n="{n}"><b>{e(v[3])}</b><small>{v[0]:03d} · {e(v[1])} {v[2]}</small></td>'
    rows = "".join(f"<tr><th scope=\"row\">{SIGNS[k]}</th>{''.join(cell(v, n) for v, n in zip(by[k], ('Fourth', 'Seventh', 'Ninth')))}</tr>" for k in sorted(by))
    return (f'<div class="ml-scroll"><table class="ml-voids"><caption>{e(T["VOIDS_TABLE"])}</caption>'
            f'<thead><tr><th scope="col">Sign</th><th scope="col">Fourth</th><th scope="col">Seventh</th><th scope="col">Ninth, closing</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def index_page(base):
    from .pages import _crumbs
    ps = lambda xs: "".join(f"<p>{e(x)}</p>" for x in xs)
    cut = next(k for k, v in enumerate(T["VOIDS"]) if "fourth, the seventh" in v) + 1     # the diagram follows the paragraph that lays them out
    rings = "".join(f"<dt>{e(n)}</dt><dd>{e(t)}</dd>" for n, t in T["RINGS"])
    tries = "".join(f"<li><b>{e(n)}.</b> {e(t)}</li>" for n, t in T["TRY"])
    course = "".join(f"<li><b>{e(n)}</b><span>{e(t)}</span></li>" for n, t in T["COURSE"])
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>Learn the Wyrd Mandala</h1>
<p class="lede">{e(T["LEDE"])}</p>
<p><a class="btn-cast" href="/mandala">{e(T["OPEN"])}</a></p>

<h2 id="rotors">Two zodiacs, turning</h2>{ps(T["ROTORS"])}

<h2 id="rings">The rings, from the centre out</h2>
{ring_key()}
<dl class="facts ml-rings">{rings}</dl>

<h2 id="decks">The two decks</h2>{ps(T["DECKS"])}

<h2 id="voids">The Asura voids</h2>{ps(T["VOIDS"][:cut])}
{void_strip()}
{ps(T["VOIDS"][cut:])}
{void_table()}

<h2 id="station">Reading a station</h2>{ps(T["STATION"])}

<h2 id="try">Try it</h2><p>{e(T["TRY_INTRO"])}</p><ol class="ml-try">{tries}</ol>
<p><a class="btn-cast" href="/mandala">{e(T["OPEN"])}</a> <a class="ml-alt" href="/">Cast your chart first</a></p>

<h2 id="course">Learning the Mandala: the course</h2>
<p>{e(T["COURSE_INTRO"])}</p>
<ol class="ml-course">{course}</ol>
<p class="note-box">The course is coming. When it opens it will be here, and members of the Order will find it in the Hall. <a href="/membership">See the Order</a>.</p>"""
    desc = ("A free introduction to the Wyrd Mandala by The Völva: the two zodiacs turning against each other, the rings from the centre out, "
            "the Buddhist and Nordic decks, the thirty-six Asura voids and their names, how to read a station, and the course to come.")
    return ("Learn the Wyrd Mandala: the Two Rotors, the Rings, the Decks and the Voids · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), ("The Wyrd Mandala", "/learn/mandala")]))
