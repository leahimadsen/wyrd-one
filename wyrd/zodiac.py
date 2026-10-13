"""The zodiac in the learning pages: an overview of the twelve signs (/learn/signs) and a full page for each one.

Where the words come from, so each kind can be edited in its own place:
  corpus.json, placements.json, register_ext.json, karakas.json, matrix.json, medical.json, story.json, vargas.json
                     The Völva's register: what each sign brings and how it feels, the body, every planet in the sign,
                     and the sign in the deeper charts.
  zodiac.json        Names, classical forms, and how three older traditions drew the stars, each with its source.
  zodiac_sky.json    Worked out: the Sun's dates in each sign, the ayanamsa, and where each sign's stars stand.
  notables.json      People born under each sign, with their skies worked out by tools/notables.py.
"""
import datetime, html, json, math, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = lambda f: json.load(open(os.path.join(HERE, "lib", f), encoding="utf-8"))
C, X, P = L("corpus.json"), L("register_ext.json"), L("placements.json")
KA, MX, MD, ST, VG = L("karakas.json"), L("matrix.json"), L("medical.json"), L("story.json"), L("vargas.json")
Z, ZS, N = L("zodiac.json"), L("zodiac_sky.json"), L("notables.json")
e = html.escape

SIGNS = [s[0] for s in C["SIGN_FRAME"]]
NAKS = [n[0] for n in C["NAKSHATRA"]]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]
SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
         "Rahu": "☊", "Ketu": "☋", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"}
TXT = "︎"          # ask for the text form of a glyph, not an emoji


def slug(s):
    from .pages import slug as _s
    return _s(s)


def cap(s): return s[:1].upper() + s[1:]


def _dignity():
    from .reading_more import EXALT, OWN, ROOT
    return EXALT, OWN, ROOT


def _year():
    y = str(datetime.date.today().year)
    years = sorted(ZS["SID_INGRESS"])
    return y if y in ZS["SID_INGRESS"] else (years[-1] if y > years[-1] else years[0])


def _day(ymd, year=True):
    y, m, d = ymd
    return f"{d} {MONTHS[m - 1]}" + (f" {y}" if year else "")


def sun_dates(i, table="SID_INGRESS"):
    """When the Sun is in sign i this year, as (start, end) day strings."""
    row = ZS[table][_year()]
    return _day(row[i], False), _day(row[(i + 1) % 12], False)


def ayanamsa():
    a = ZS["AYANAMSA"][_year()]
    return a, f"{int(a)}°{round((a % 1) * 60):02d}′"


def _dms(lon):
    d = lon % 30; m = round((d % 1) * 60)
    if m == 60: d, m = d + 1, 0
    return f"{int(d)}°{m:02d}′"


def mansions_in(i):
    """The lunar mansions in sign i, each with the padas that fall inside it."""
    out = []
    for k in range(27):
        lo, hi = k * 40 / 3, (k + 1) * 40 / 3
        pads = [p + 1 for p in range(4) if i * 30 <= lo + p * 10 / 3 < (i + 1) * 30]
        if pads: out.append((k, pads, max(lo, i * 30), min(hi, (i + 1) * 30)))
    return out


def gates_in_tropical(i):
    from . import engine as E
    out = []
    for g in E.GATE_ORDER:
        sp = E.gate_span(g); a = sp["start"]
        mid = (a + 5.625 / 2) % 360
        if int(mid // 30) == i: out.append((mid, g))
    return [g for _, g in sorted(out, key=lambda t: (t[0] - i * 30) % 360)]


def people(sign, key):
    rows = [p for p in N["PEOPLE"] if p.get("sky", {}).get(key) == sign]
    return sorted(rows, key=lambda p: tuple(p["born"]))


def _born(p):
    y, m, d = p["born"]
    era = f"{y}" if y > 0 else f"{-y + 1} BCE"
    return f"{d} {MONTHS[m - 1]} {era}" + (" (Julian calendar)" if p["cal"] == "J" else "")


def _person(p, show):
    sky = p.get("sky", {})
    bits = []
    if show == "sun":
        if sky.get("sun_nak"): bits.append(f'Sun in <a href="/learn/nakshatras/{slug(sky["sun_nak"])}">{e(sky["sun_nak"])}</a>')
        if sky.get("moon"): bits.append(f'Moon in <a href="/learn/signs/{slug(sky["moon"])}">{e(sky["moon"])}</a>')
        if sky.get("trop") and sky.get("trop") != sky.get("sun"): bits.append(f'tropical {e(sky["trop"])}')
        elif sky.get("trop"): bits.append("the same sign in both zodiacs")
    else:
        if sky.get("sun"): bits.append(f'Sun in <a href="/learn/signs/{slug(sky["sun"])}">{e(sky["sun"])}</a>')
    unsure = f' <span class="muted">({e(p["unsure"])})</span>' if p.get("unsure") else ""
    return (f'<li><b>{e(p["name"])}</b>, {e(p["note"])}. <span class="z-born">Born {e(_born(p))}.</span>'
            f'{" " + " · ".join(bits) + "." if bits else ""}{unsure}</li>')


def _stars(i):
    S = ZS["STARS"][SIGNS[i]]
    rows = sorted(S["own_in"] + S["guests"], key=lambda r: r["lon"])
    if not rows: return ""
    def mansion(r):
        if r["nak"]: return f'<a href="/learn/nakshatras/{slug(r["nak"])}">{e(r["nak"])}</a>'
        a, b = r["edge"]
        return f'on the line between <a href="/learn/nakshatras/{slug(a)}">{e(a)}</a> and <a href="/learn/nakshatras/{slug(b)}">{e(b)}</a>'
    body = "".join(f'<tr><td><b>{e(r["name"])}</b>{"<br><small>" + e(r["bayer"]) + "</small>" if r["bayer"] else ""}</td><td>{e(r["of"])}</td>'
                   f'<td>{r["mag"]:.1f}</td><td>{r["deg"]}° {e(r["sign"])}</td><td>{mansion(r)}</td></tr>' for r in rows)
    return (f'<div class="tw"><table class="z-stars"><tr><th>Star</th><th>Constellation</th><th>Brightness</th><th>Sidereal place</th><th>Mansion</th></tr>{body}</table></div>'
            '<p class="muted">Brightness is the star\'s magnitude: the lower the number, the brighter, and below 1 is among the brightest in the sky. '
            'Places are rounded to the degree.</p>')


def _strays(i, con):
    out = ZS["STARS"][SIGNS[i]]["own_out"]
    if not out: return ""
    where = "; ".join(f'{e(r["name"])} at about {r["deg"]}° {e(r["sign"])}' for r in out)
    return (f"<p>The constellation and the sign are not the same thing. The sign is an exact thirty degrees; the constellation is a figure "
            f"of uneven size. Some stars of {e(con)} stand outside sidereal {e(SIGNS[i])}: {where}.</p>")


CON = {"Scorpio": "Scorpius", "Capricorn": "Capricornus"}


def sign_page(base, s):
    from .pages import NAK_BY, _crumbs, _cta, _ld
    i = next((k for k, n in enumerate(SIGNS) if slug(n) == s), None)
    if i is None: return None
    name = SIGNS[i]; z = Z["SIGNS"][i]; x = X["SIGNS"][i]; h = C["HOUSES"][i]; md = MD["SIGN"][name]
    EXALT, OWN, ROOT = _dignity()
    rulers = [b for b in SEVEN if i in OWN[b]]
    exalted = [b for b in SEVEN if EXALT[b] == i]
    fallen = [b for b in SEVEN if (EXALT[b] + 6) % 12 == i]
    roots = [b for b in SEVEN if ROOT[b][0] == i]
    nxt, prv, opp = SIGNS[(i + 1) % 12], SIGNS[i - 1], SIGNS[(i + 6) % 12]
    trine = [SIGNS[(i + 4) % 12], SIGNS[(i + 8) % 12]]
    con = CON.get(name, name)
    s0, s1 = sun_dates(i); t0, t1 = sun_dates(i, "TROP_INGRESS"); n0, n1 = sun_dates((i + 6) % 12)
    link = lambda n: f'<a href="/learn/signs/{slug(n)}">{e(n)}</a>'
    dg = lambda b, extra="": f"{GLYPH[b]}{TXT} {'the ' if b in ('Sun', 'Moon') else ''}{b}{extra}"
    facts = [("Sanskrit name", f"{e(z['skt'])}, {e(z['means'])}"),
             ("Element and mode", f"{cap(x['element'])}, {x['mode']}"),
             ("Ruled by", " and ".join(dg(b) for b in rulers))]
    if exalted: facts.append(("Exalted here", "; ".join(dg(b, f", at its peak at {Z['EXALT_DEG'][b]}°") for b in exalted)))
    if fallen: facts.append(("In its fall here", "; ".join(dg(b, f", at its lowest at {Z['EXALT_DEG'][b]}°") for b in fallen)))
    if roots: facts.append(("Root sign of", "; ".join(dg(b, f", from {ROOT[b][1]}° to {ROOT[b][2]}°") for b in roots)))
    facts += [("Odd or even", "Odd: counted masculine in Jyotish" if i % 2 == 0 else "Even: counted feminine in Jyotish"),
              ("Direction", z["dir"].capitalize()),
              ("Rising", cap(Z["RISES"][z["rises"]])),
              ("Drawn as", cap(e(z["form"]))),
              ("In the body", e(cap(md["parts"]))),
              ("Opposite", link(opp)),
              ("Same element", " and ".join(link(t) for t in trine)),
              ("On the natural wheel", f'House {h["n"]}: {e(h["phase"])}'),
              ("Its colour", f'<span class="z-swatch" style="background:{h["hex"]}"></span>{e(h["color"])}'),
              ("Its runes", f'<a href="/learn/runes/{slug(h["ingress"][1])}">{h["ingress"][0]} {e(h["ingress"][1])}</a> opens it, '
                            f'<a href="/learn/runes/{slug(h["egress"][1])}">{h["egress"][0]} {e(h["egress"][1])}</a> closes it')]
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)

    mans = "".join(f'<tr><td><a href="/learn/nakshatras/{slug(NAKS[k])}">{e(NAKS[k])}</a></td><td>{_dms(lo)} to {_dms(hi) if hi < (i + 1) * 30 else "30°00′"}</td>'
                   f'<td>{"all four" if len(pads) == 4 else ("pada " if len(pads) == 1 else "padas ") + ", ".join(map(str, pads))}</td>'
                   f'<td>{e(C["NAKSHATRA"][k][1])}</td></tr>' for k, pads, lo, hi in mansions_in(i))
    gates = gates_in_tropical(i)
    gate_links = ", ".join(f'<a href="/learn/gates/{g}">{g} {e(C["GATE_NAME"][str(g)])}</a>' for g in gates)

    order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]
    planets = "".join(f'<li><span class="z-pg" aria-hidden="true">{GLYPH[b]}{TXT}</span> {e(P["PIS"][b][i])}</li>' for b in order[:9])
    outer = "".join(f'<li><span class="z-pg" aria-hidden="true">{GLYPH[b]}{TXT}</span> {e(P["PIS"][b][i])}</li>' for b in order[9:])

    trad = "".join(f'<h3>{e(t)}</h3><p>{e(txt)}</p><p class="z-src">Source: {e(src)}</p>' for t, txt, src in z["trad"])
    points = ""
    if name == "Cancer":
        points = f'<p>Between the two donkey stars sits Praesepe, the Beehive cluster, at about {round(ZS["POINTS"]["praesepe"] % 30)}° sidereal Cancer, in Pushya.</p>'

    suns, moons = people(name, "sun"), people(name, "moon")
    sun_list = f'<ul class="z-people">{"".join(_person(p, "sun") for p in suns)}</ul>' if suns else ""
    moon_list = (f'<h3>With the Moon in {e(name)}</h3><p class="muted">{e(Z["TEACH"]["MOON_NOTE"])}</p>'
                 f'<ul class="z-people">{"".join(_person(p, "moon") for p in moons)}</ul>') if moons else ""
    fruit = VG["FRUIT"][i].replace("it ripens into", "ripens into", 1)
    costume = ST["COSTUME"][name]

    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn/signs">The zodiac</a></p>
<h1><span class="z-glyph" aria-hidden="true">{z["glyph"]}{TXT}</span> {e(name)}</h1>
<p class="z-skt">{e(z["skt"])} · {e(z["means"])} · the {ORD[i]} sign</p>
<p class="lede">{e(cap(x["karma"]))}.</p>
<p>{e(name)} runs from {i * 30}° to {i * 30 + 30}° of the sidereal zodiac, which is measured against the stars. This year the Sun passes through it from {s0} to {s1}; its stars stand highest at midnight from {n0} to {n1}, when the Sun is on the other side of the sky. In the tropical zodiac, measured by the seasons, the Sun is in {e(name)} from {t0} to {t1}.</p>

<h2>At a glance</h2>
<dl class="facts z-facts">{dl}</dl>

<h2>What it brings, and how it feels</h2>
<p>Every sign is read twice on this site: against the stars, for what it brings into a life, and against the seasons, for how it feels from inside.</p>
<p><b>Against the stars.</b> {e(P["SIGN_SID"][i])}</p>
<p><b>Against the seasons.</b> {e(P["SIGN_TROP"][i])} In short, {e(x["felt"])}.</p>
<p>Most people born with the Sun in sidereal {e(name)} were told they were {e(nxt)}.</p>
<p class="z-shift">{e(P["SHIFT"][(i + 1) % 12])}</p>

<h2>{e(name)} rising</h2>
<p>{e(name)} rising gives {e(C["SIGN_FRAME"][i][1])}</p>
<p>In the body, {e(name)} holds {e(md["parts"])}. {e(md["line"])}</p>
<p>If {e(name)} is rising, the story your reading opens with dresses you in {e(costume)}.</p>

<h2>Every planet in {e(name)}</h2>
<ul class="z-planets">{planets}</ul>
<h3>The outer planets</h3>
<p class="muted">Too slow and too far to be seen with the eye, so the old texts don't read them; each stays in a sign for years and marks a generation more than a person.</p>
<ul class="z-planets">{outer}</ul>

<h2>{e(name)} in the deeper charts</h2>
<dl class="facts z-deep">
  <dt>Your soul's wish</dt><dd>{e(KA["KARAKAMSA"][i])} <span class="muted">When your soul-planet's navamsa falls here.</span></dd>
  <dt>Partner</dt><dd>{e(KA["PARTNER"][i])} <span class="muted">When the partner planet's navamsa falls here.</span></dd>
  <dt>Work</dt><dd>{e(KA["WORK"][i])} <span class="muted">When the planet of work's navamsa falls here.</span></dd>
  <dt>Saturn here</dt><dd>{e(MX["SATURN_SIGN"][i])}</dd>
  <dt>In the navamsa</dt><dd>A planet whose navamsa falls in {e(name)} {e(fruit)}</dd>
</dl>

<h2>Its mansions</h2>
<p>The Moon's twenty-seven mansions run under the twelve signs, nine quarters (padas) to every sign, so a mansion can start in one sign and end in the next.</p>
<div class="tw"><table class="z-mans"><tr><th>Mansion</th><th>Its part of {e(name)}</th><th>Padas here</th><th>Ruler</th></tr>{mans}</table></div>
{f'<h3>Gates in tropical {e(name)}</h3><p>The gate wheel is laid on the tropical zodiac, so these are the gates that fall in tropical {e(name)}: {gate_links}.</p>' if gates else ""}

<h2>Its stars</h2>
<p>The stars that stand in sidereal {e(name)}: the brightest of {e(con)} and any of the sky's brightest stars that share its stretch of the ecliptic.</p>
{_stars(i)}
{_strays(i, con)}{points}

<h2>How the old traditions drew it</h2>
<p>Three of the oldest written accounts of these stars, each on its own terms.</p>
{trad}

<h2 id="born">Born under {e(name)}</h2>
<h3>With the Sun in {e(name)}</h3>
<p class="muted">{e(Z["TEACH"]["SUN_NOTE"])}</p>
{sun_list}
{moon_list}

<p><a href="/learn/signs/{slug(prv)}">← {Z["SIGNS"][i - 1]["glyph"]}{TXT} {e(prv)}</a> · <a href="/learn/signs">All twelve</a> · <a href="/learn/signs/{slug(nxt)}">{e(nxt)} {Z["SIGNS"][(i + 1) % 12]["glyph"]}{TXT} →</a></p>{_cta()}"""
    desc = (f"{name} ({z['skt']}) in sidereal and tropical astrology: ruled by {' and '.join(rulers)}, {x['element']} and {x['mode']}. "
            f"What it brings, {name} rising, every planet in {name}, its nakshatras and stars, its myths, and famous people born under it.")[:300]
    ld = _crumbs(base, [("Learn", "/learn"), ("The zodiac", "/learn/signs"), (name, f"/learn/signs/{s}")])
    return (f"{name} ({z['skt']}): Meaning, Ruler, Stars, Myth & Famous People · The Wyrd Console", desc, body, ld)


# ---------------- the overview ----------------
def wheel_svg():
    """The two zodiacs on one wheel: sidereal signs and mansions outside, the tropical signs inside, turned by the ayanamsa."""
    ay, ays = ayanamsa()
    cx = cy = 340
    def pt(r, lon):
        a = math.radians(180 + lon)
        return cx + r * math.cos(a), cy - r * math.sin(a)
    def wedge(r0, r1, a0, a1, fill, cls=""):
        large = 1 if (a1 - a0) % 360 > 180 else 0
        x0, y0 = pt(r1, a0); x1, y1 = pt(r1, a1); x2, y2 = pt(r0, a1); x3, y3 = pt(r0, a0)
        return (f'<path class="{cls}" d="M{x0:.1f},{y0:.1f} A{r1},{r1} 0 {large} 0 {x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} '
                f'A{r0},{r0} 0 {large} 1 {x3:.1f},{y3:.1f} Z" fill="{fill}"/>')
    def label(r, lon, text, cls, rotate=None):
        """rotate: 'tan' runs the text along the ring, 'rad' runs it across; either way it is never upside down."""
        x, y = pt(r, lon)
        rot = ""
        if rotate:
            ang = (-(180 + lon) - (90 if rotate == "tan" else 0)) % 360
            if 90 < ang < 270: ang -= 180
            rot = f' transform="rotate({ang:.1f} {x:.1f} {y:.1f})"'
        return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{rot}>{e(text)}</text>'
    short = lambda n: n.replace("Purva ", "P. ").replace("Uttara ", "U. ")
    out = []
    for i in range(12):
        h = C["HOUSES"][i]["hex"]
        out.append(wedge(262, 330, i * 30, i * 30 + 30, h, "zw-sid"))
        out.append(label(306, i * 30 + 15, Z["SIGNS"][i]["glyph"] + TXT, "zw-glyph"))
        out.append(label(278, i * 30 + 15, SIGNS[i], "zw-name", "tan"))
    for k in range(27):
        out.append(wedge(204, 262, k * 40 / 3, (k + 1) * 40 / 3, "#fbf7ee" if k % 2 else "#efe7d6", "zw-nak"))
        out.append(label(233, k * 40 / 3 + 20 / 3, short(NAKS[k]), "zw-nk", "rad"))
    for i in range(12):
        a0 = i * 30 - ay
        out.append(wedge(132, 196, a0, a0 + 30, C["HOUSES"][i]["hex"], "zw-trop"))
        out.append(label(178, a0 + 15, Z["SIGNS"][i]["glyph"] + TXT, "zw-glyph sm"))
        out.append(label(151, a0 + 15, SIGNS[i], "zw-name sm", "tan"))
    x0, y0 = pt(132, -ay); x1, y1 = pt(340, -ay)
    out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="zw-tick"/>')
    x0, y0 = pt(132, 0); x1, y1 = pt(340, 0)
    out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="zw-zero"/>')
    sx, sy = pt(334, 180)
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" class="zw-star"/>')
    out.append(label(318, 186, "Spica", "zw-nk"))
    out.append(f'<text x="{cx}" y="{cy - 14}" class="zw-mid">ayanamsa</text><text x="{cx}" y="{cy + 14}" class="zw-mid big">{ays}</text>'
               f'<text x="{cx}" y="{cy + 36}" class="zw-mid">{_year()}</text>')
    return (f'<figure class="z-wheel"><svg viewBox="0 0 680 680" role="img" aria-labelledby="zwt">'
            f'<title id="zwt">The sidereal zodiac and its twenty-seven mansions, with the tropical zodiac inside it, turned by {ays}</title>'
            f'{"".join(out)}</svg><figcaption>{e(Z["TEACH"]["WHEEL"])} The red line is 0° sidereal Aries; the dark line is 0° tropical Aries, '
            f'the spring equinox. Spica holds 0° Libra.</figcaption></figure>')


def index_page(base):
    from .pages import _crumbs, _cta
    T = Z["TEACH"]; ay, ays = ayanamsa(); y = _year()
    EXALT, OWN, ROOT = _dignity()
    gap_days = round(ay * 365.25 / 360)
    dates = "".join(f'<tr><td><a href="/learn/signs/{slug(n)}">{Z["SIGNS"][i]["glyph"]}{TXT} {e(n)}</a></td>'
                    f'<td>{" – ".join(sun_dates(i))}</td><td>{" – ".join(sun_dates(i, "TROP_INGRESS"))}</td></tr>' for i, n in enumerate(SIGNS))
    els = ["fire", "earth", "air", "water"]; modes = ["moving", "fixed", "dual"]
    grid = "".join(f'<tr><th>{cap(el)}</th>' + "".join(
        f'<td>{" ".join(link_sign(k) for k in range(12) if X["SIGNS"][k]["element"] == el and X["SIGNS"][k]["mode"] == md)}</td>' for md in modes) + "</tr>" for el in els)
    rule = "".join(
        f'<tr><td>{GLYPH[b]}{TXT} {b}</td><td>{" and ".join(link_sign(k) for k in sorted(OWN[b]))}</td>'
        f'<td>{link_sign(EXALT[b])} {Z["EXALT_DEG"][b]}°</td><td>{link_sign((EXALT[b] + 6) % 12)} {Z["EXALT_DEG"][b]}°</td>'
        f'<td>{link_sign(ROOT[b][0])} {ROOT[b][1]}°–{ROOT[b][2]}°</td></tr>' for b in SEVEN)
    twelve = "".join(
        f'<li><a href="/learn/signs/{slug(n)}"><b>{Z["SIGNS"][i]["glyph"]}{TXT} {e(n)}</b></a> <span class="muted">· {e(Z["SIGNS"][i]["skt"])} · '
        f'{X["SIGNS"][i]["element"]}, {X["SIGNS"][i]["mode"]} · ruled by {" and ".join(("the " if b in ("Sun", "Moon") else "") + b for b in SEVEN if i in OWN[b])}</span><br>{e(cap(X["SIGNS"][i]["karma"]))}.</li>'
        for i, n in enumerate(SIGNS))
    counts = " · ".join(f'<a href="/learn/signs/{slug(n)}#born">{e(n)}</a> {len(people(n, "sun"))}' for n in SIGNS)
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>The zodiac</h1>
<p class="lede">{e(T["LEDE"])}</p>

<h2>Two zodiacs</h2>
<p>{e(T["TWO"])}</p>
<p><b>Sidereal.</b> {e(X["FRAMES"]["sidereal"])}</p>
<p><b>Tropical.</b> {e(X["FRAMES"]["tropical"])}</p>
<p>{e(X["FRAMES"]["both"].replace("Every planet below is read twice.", "On this site every planet is read twice."))}</p>
<p>{e(T["DRIFT"])} In {y} the gap is {ays}.</p>
<p>{e(T["SHIFT"].format(gap=gap_days, keep=31 - gap_days))}</p>
{wheel_svg()}

<h2>When the Sun is in each sign</h2>
<p>The dates for {y}. They move by a day at most from year to year, and the sidereal dates creep about a day later every 72 years.</p>
<div class="tw"><table class="z-dates"><tr><th>Sign</th><th>Sidereal</th><th>Tropical</th></tr>{dates}</table></div>

<h2>Elements and modes</h2>
<p>{e(T["ELEMENTS"])}</p>
<div class="tw"><table class="z-grid"><tr><th></th><th>Moving</th><th>Fixed</th><th>Dual</th></tr>{grid}</table></div>

<h2>Rulers and dignities</h2>
<p>{e(T["RULERS"])}</p>
<div class="tw"><table class="z-rule"><tr><th>Planet</th><th>Rules</th><th>Exalted</th><th>Fall</th><th>Root sign</th></tr>{rule}</table></div>
<p class="muted">Rahu and Ketu, the Moon's nodes, rule no sign here and are given no exaltation: the old texts disagree about both.</p>

<h2>The twelve signs</h2>
<ul class="z-twelve">{twelve}</ul>

<h2 id="born">Born under each sign</h2>
<p>{e(T["PEOPLE"])}</p>
<p class="z-counts">{counts}</p>{_cta()}"""
    desc = ("The twelve zodiac signs in sidereal and tropical astrology: why they differ, this year's dates, elements and modes, rulers, "
            "exaltations, and famous people born under each sign.")
    return ("The Zodiac Signs: Sidereal and Tropical, Dates, Elements and Rulers · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), ("The zodiac", "/learn/signs")]))


def link_sign(k):
    return f'<a href="/learn/signs/{slug(SIGNS[k])}" title="{SIGNS[k]}">{Z["SIGNS"][k]["glyph"]}{TXT} {SIGNS[k]}</a>'
