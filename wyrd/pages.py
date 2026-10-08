"""Public pages search engines can read: the astrology readings on offer, and a
learning page for every gate, nakshatra (lunar mansion) and sidereal sign.

Each learning page carries the facts and a short taste of Saga Devi's register
from lib/corpus.json, then points to the free birth chart and the paid reading.
The full passages stay in the paid reading."""
import html, json, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
e = html.escape


def slug(s):
    s = s.lower().replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ṣ", "s").replace("ṛ", "r")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def first(t, n=1):
    t = re.sub(r"<[^>]+>", "", t or "").strip()
    out = re.split(r"(?<=[.?!])\s+", t)
    return " ".join(out[:n])


NAKS = [(slug(n[0]), i) for i, n in enumerate(C["NAKSHATRA"])]
NAK_BY = dict(NAKS)
SIGNS = [(slug(s[0]), i) for i, s in enumerate(C["SIGN_FRAME"])]
SIGN_BY = dict(SIGNS)
GATES = sorted(int(g) for g in C["REGISTER"])


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj).replace("<", "\\u003c") + "</script>"


def _crumbs(base, trail):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": base + u} for i, (n, u) in enumerate(trail)]
    return _ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})


def _cta():
    return ('<div class="cta"><p>See where this sits in your own chart. The birth chart is free: sidereal and tropical '
            'positions, the 27 nakshatras, the 64 gates and the runes. The full written astrology reading is $44.</p>'
            '<p><a class="btn-cast" href="/">Cast your free birth chart</a></p>'
            '<p><a href="/reports">See the astrology readings →</a></p></div>')


# ---------------- the readings ----------------
def reports(base, price_cents, member_cents):
    p = price_cents / 100
    body = f"""
<h1>Astrology readings by Saga Devi</h1>
<p class="lede">A personal astrology report written from your exact birth chart: sidereal and tropical, the lunar mansions, the 64 gates, the runes, your Vimshottari periods and your Dharma body.</p>
<div class="plans">
  <section class="plan lead"><h2>Natal astrology reading</h2><div class="price">${p:.0f}<small> once</small></div>
    <ul><li>Your full birth chart reading, written from Saga Devi's register</li><li>Sidereal signs, nakshatras and houses</li>
    <li>Your harmonic body and Dharma body</li><li>Your current Vimshottari period</li><li>Questions to work with, gathered at the end</li></ul>
    <a class="btn-buy" href="/chart#reading">Cast your chart, then buy the reading</a>
    <a class="alt" href="/sample">Read a sample reading first</a></section>
  <section class="plan"><h2>Membership</h2><div class="price">$11<small> a month</small></div>
    <ul><li>Body Weather every Monday: how the week's sky lands in your birth body and your Dharma body</li>
    <li>Your chart kept on your account</li><li>The natal reading for ${member_cents / 100:.2f} instead of ${p:.0f}</li></ul>
    <a class="btn-cast" href="/membership">See the membership</a></section>
  <section class="plan"><h2>1:1 consultation</h2><div class="price">$100<small> an hour</small></div>
    <ul><li>A session with Saga Devi on your chart</li><li>Ask through <a href="https://thewebofwyrd.substack.com">The Web of Wyrd</a></li></ul></section>
</div>
<h2>Questions</h2>
<h3>What do I need for an astrology reading?</h3><p>Your date, time and place of birth. If you don't know the time, the free chart still works with solar houses, and the reading tells you which parts depend on the time.</p>
<h3>Is this sidereal or tropical astrology?</h3><p>Both. Signs, nakshatras and houses are sidereal (Lahiri). The 64 gates use the tropical zodiac, as Human Design does. Your Dharma body is the D9 of the tropical positions.</p>
<h3>How do I get my reading?</h3><p>Straight after payment it opens in your browser. Save it as a PDF from your browser's print menu.</p>
<h3>Can astrologers use these tools with their clients?</h3><p>Yes. Astrologers and practitioners can use these tools with their own clients through <a href="/membership#pro">Wyrd Console Professional</a>.</p>
"""
    faq = [("What do I need for an astrology reading?", "Your date, time and place of birth. If you don't know the time, the free chart still works with solar houses."),
           ("Is this sidereal or tropical astrology?", "Both. Signs, nakshatras and houses are sidereal (Lahiri). The 64 gates use the tropical zodiac. The Dharma body is the D9 of the tropical positions."),
           ("How do I get my reading?", "Straight after payment it opens in your browser, and can be saved as a PDF.")]
    ld = _ld({"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": "Natal astrology reading", "brand": {"@type": "Brand", "name": "The Wyrd Console"},
         "description": "A personal astrology report written from your birth chart by Saga Devi: sidereal signs, nakshatras, the 64 gates, the harmonic and Dharma bodies, and Vimshottari periods.",
         "url": base + "/reports", "image": base + "/static/icons/icon-512.png",
         "offers": {"@type": "Offer", "price": f"{p:.2f}", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": base + "/reports"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]})
    return ("Astrology Readings & Birth Chart Reports · The Wyrd Console",
            f"Personal astrology readings by Saga Devi, written from your exact birth chart: sidereal signs, nakshatras, the 64 gates and your Dharma body. ${p:.0f}, ready the moment you pay.",
            body, ld)


# ---------------- learning pages ----------------
def learn_index(base):
    gates = "".join(f'<li><a href="/learn/gates/{g}">Gate {g} · {e(C["GATE_NAME"][str(g)])}</a></li>' for g in GATES)
    naks = "".join(f'<li><a href="/learn/nakshatras/{s}">{e(C["NAKSHATRA"][i][0])}</a></li>' for s, i in NAKS)
    signs = "".join(f'<li><a href="/learn/signs/{s}">{e(C["SIGN_FRAME"][i][0])}</a></li>' for s, i in SIGNS)
    body = f"""<h1>Learn astrology with the Wyrd Console</h1>
<p class="lede">The building blocks of your birth chart: the twelve sidereal signs, the twenty-seven nakshatras, and the sixty-four gates, each in Saga Devi's words.</p>
<h2>The 12 sidereal signs</h2><ul class="terms">{signs}</ul>
<h2>The 27 nakshatras (lunar mansions)</h2><ul class="terms">{naks}</ul>
<h2>The 64 gates</h2><ul class="terms">{gates}</ul>
<h2>Go further</h2><ul class="terms"><li><a href="/learn/runes">Learn the runes: the 24 runes of the Elder Futhark</a></li>
<li><a href="/learn/dharma">Learn the Dharma Design: the 64 gates of dharma</a></li></ul>{_cta()}"""
    return ("Learn Astrology: Signs, Nakshatras & the 64 Gates · The Wyrd Console",
            "A free guide to the twelve sidereal signs, the twenty-seven nakshatras and the sixty-four gates, written by Saga Devi.",
            body, _crumbs(base, [("Learn", "/learn")]))


def gate(base, g):
    r = C["REGISTER"].get(str(g))
    if not r: return None
    name = C["GATE_NAME"][str(g)]
    prev_g, next_g = (g - 2) % 64 + 1, g % 64 + 1
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn#gates">Gates</a></p>
<h1>Gate {g}: {e(name)}</h1>
<p class="lede">{e(r["t"])}</p>
<dl class="facts"><dt>Where it sits</dt><dd>{e(r["h"])}</dd></dl>
<p>{e(first(r.get("e"), 2))}</p>
<h2>When it works</h2><p>{e(first(r.get("l")))}</p>
<h2>A question to carry</h2><p><i>{e(first(r.get("a")))}</i></p>
<p class="muted">The full passage for this gate, with its shadow and how it breaks, is in the paid reading when the gate is in your chart.</p>
<p><a href="/learn/gates/{prev_g}">← Gate {prev_g}</a> · <a href="/learn/gates/{next_g}">Gate {next_g} →</a></p>{_cta()}"""
    return (f"Gate {g} {name} Meaning · Human Design & Astrology · The Wyrd Console",
            f"Gate {g}, {name}: {first(r.get('e'))}"[:300],
            body, _crumbs(base, [("Learn", "/learn"), (f"Gate {g}", f"/learn/gates/{g}")]))


def nakshatra(base, s):
    i = NAK_BY.get(s)
    if i is None: return None
    n, d = C["NAKSHATRA"][i], C["NAK_DEEP"][i]
    names = [x[0] for x in C["NAKSHATRA"]]
    start = i * 360 / 27
    sign_a, sign_b = C["SIGN_FRAME"][int(start // 30)][0], C["SIGN_FRAME"][int((start + 13.3333) // 30) % 12][0]
    deg = lambda x: f"{int(x % 30)}°{int(round((x % 1) * 60)):02d}′"
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn#nakshatras">Nakshatras</a></p>
<h1>{e(n[0])} nakshatra</h1>
<p class="lede">{e(n[6])}</p>
<dl class="facts">
  <dt>Position</dt><dd>{deg(start)} {e(sign_a)} to {deg(start + 40 / 3)} {e(sign_b)} (sidereal)</dd>
  <dt>Ruled by</dt><dd>{e(n[1])}</dd><dt>Deity</dt><dd>{e(n[2])}</dd><dt>Symbol</dt><dd>{e(n[3])}</dd>
  <dt>Nature</dt><dd>{e(n[4])}</dd><dt>Body</dt><dd>{e(n[5])}</dd>
  <dt>Stars</dt><dd>{e(d[1])}</dd>
</dl>
<p><a href="/learn/nakshatras/{slug(names[i - 1])}">← {e(names[i - 1])}</a> · <a href="/learn/nakshatras/{slug(names[(i + 1) % 27])}">{e(names[(i + 1) % 27])} →</a></p>{_cta()}"""
    return (f"{n[0]} Nakshatra Meaning · Vedic Astrology · The Wyrd Console",
            f"{n[0]} nakshatra in Vedic astrology: ruled by {n[1]}, deity {n[2]}. {n[6]}"[:300],
            body, _crumbs(base, [("Learn", "/learn"), (n[0], f"/learn/nakshatras/{s}")]))


def sign(base, s):
    i = SIGN_BY.get(s)
    if i is None: return None
    name, frame = C["SIGN_FRAME"][i]
    house = C["HOUSES"][i]
    naks = [C["NAKSHATRA"][k][0] for k in range(27) if (k * 40 / 3) < (i + 1) * 30 and (k + 1) * 40 / 3 > i * 30]
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn#signs">Signs</a></p>
<h1>{e(name)} in sidereal astrology</h1>
<p class="lede">{e(name)} spans {i * 30}° to {i * 30 + 30}° of the sidereal zodiac, measured against the stars with the Lahiri ayanamsa.</p>
<h2>{e(name)} rising: the body it shapes</h2><p>{e(first(frame, 3))}</p>
<dl class="facts"><dt>Nakshatras in {e(name)}</dt><dd>{", ".join(f'<a href="/learn/nakshatras/{slug(k)}">{e(k)}</a>' for k in naks)}</dd>
<dt>Natural house</dt><dd>House {house["n"]}: {e(house["phase"])}</dd></dl>{_cta()}"""
    return (f"{name} Sign Meaning · Sidereal Astrology · The Wyrd Console",
            f"{name} in sidereal (Vedic) astrology: its nakshatras, its natural house, and the body {name} rising shapes. From Saga Devi's Wyrd Console.",
            body, _crumbs(base, [("Learn", "/learn"), (name, f"/learn/signs/{s}")]))


def sitemap(base):
    urls = ["/", "/reports", "/membership", "/today", "/sample", "/learn"]
    urls += [f"/learn/gates/{g}" for g in GATES] + [f"/learn/nakshatras/{s}" for s, _ in NAKS] + [f"/learn/signs/{s}" for s, _ in SIGNS]
    urls += ["/learn/runes"] + [f"/learn/runes/{r[0]}" for r in RUNES] + ["/learn/dharma"] + [f"/learn/dharma/gates/{g}" for g in GATES]
    rows = "".join(f"<url><loc>{e(base + u)}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>'


# ---------------- the runes ----------------
from . import engine as _E
X = json.load(open(os.path.join(HERE, "lib", "register_ext.json"), encoding="utf-8"))
L = json.load(open(os.path.join(HERE, "lib", "learn_ext.json"), encoding="utf-8"))
RUNES = []                                   # (slug, glyph, name, gloss, house, half) in Futhark order
for _h in C["HOUSES"]:
    for _half in ("ingress", "egress"):
        _g, _n, _gl = _h[_half]
        RUNES.append((slug(_n), _g, _n, _gl, _h["n"], _half))
RUNE_BY = {r[0]: r for r in RUNES}


def _gates_in_rune(name):
    return [g for g in GATES if name in re.split(r"[\s·→]+", C["REGISTER"][str(g)]["h"])]


def runes_index(base):
    fams = []
    for i, a in enumerate(L["AETTIR"]):
        items = "".join(f'<li><a href="/learn/runes/{r[0]}">{r[1]} {e(r[2])}</a></li>' for r in RUNES[i * 8:(i + 1) * 8])
        fams.append(f'<h2>{e(a["name"])} <span class="muted">· {a["houses"]}</span></h2><p>{e(a["says"])}</p><ul class="terms">{items}</ul>')
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>Learn the runes</h1><p class="lede">{e(L["RUNES_LEDE"])}</p>
{"".join(f"<p>{e(p)}</p>" for p in L["RUNES_TEACH"])}
{"".join(fams)}{_cta()}"""
    return ("Learn the Runes: the Elder Futhark in Your Birth Chart · The Wyrd Console",
            "A free guide to the 24 runes of the Elder Futhark: what each rune means, how runes sit in your birth chart, and when they wake in your life.",
            body, _crumbs(base, [("Learn", "/learn"), ("Runes", "/learn/runes")]))


def rune(base, s):
    r = RUNE_BY.get(s)
    if not r: return None
    _, glyph, name, gloss, house, half = r
    R = X["RUNES"][name]; i = RUNES.index(r)
    prev, nxt = RUNES[i - 1], RUNES[(i + 1) % 24]
    sign = C["SIGN_FRAME"][house - 1][0]
    gates = _gates_in_rune(name)
    gl = ", ".join(f'<a href="/learn/gates/{g}">{g} {e(C["GATE_NAME"][str(g)])}</a>' for g in gates)
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn/runes">Runes</a></p>
<h1><span aria-hidden="true">{glyph}</span> {e(name)}</h1>
<p class="lede">{e(R["means"])}</p>
<dl class="facts">
  <dt>Family</dt><dd>{e(L["AETTIR"][i // 8]["name"])}, rune {i % 8 + 1} of 8</dd>
  <dt>Its house</dt><dd>The {"opening" if half == "ingress" else "closing"} rune of house {house}: {e(gloss)}</dd>
  <dt>House {house}</dt><dd>{e(C["HOUSES"][house - 1]["phase"])}</dd>
  <dt>Natural place</dt><dd>The {"first" if half == "ingress" else "second"} half of {e(sign)} on the natural wheel</dd>
</dl>
<h2>Lit well</h2><p>{e(R["light"])}</p>
<h2>Lit badly</h2><p>{e(R["shadow"])}</p>
<h2>Its call</h2><p><i>{e(R["call"])}</i></p>
{f"<h2>Gates that run through {e(name)}</h2><p>{gl}</p>" if gates else ""}
<p class="muted">Where {e(name)} falls in your chart depends on your rising sign. Cast your chart to see whether it is lit, and buy the reading to see the years it wakes.</p>
<p><a href="/learn/runes/{prev[0]}">← {prev[1]} {e(prev[2])}</a> · <a href="/learn/runes/{nxt[0]}">{nxt[1]} {e(nxt[2])} →</a></p>{_cta()}"""
    return (f"{name} Rune Meaning ({glyph}) · Elder Futhark · The Wyrd Console",
            f"The {name} rune {glyph}: {R['means']} Lit well: {R['light']} Its call: {R['call']}",
            body, _crumbs(base, [("Learn", "/learn"), ("Runes", "/learn/runes"), (name, f"/learn/runes/{s}")]))


# ---------------- the Dharma Design ----------------
def dharma_index(base):
    walk = C["SPHERE_WALK"]; seqs = []
    for seq, names in C["SEQUENCE"].items():
        rows = "".join(f'<li><b>{e(n)}</b> · {e(walk.get(n, {}).get("drawn", ""))}: {e(walk.get(n, {}).get("what", ""))}</li>' for n in names)
        seqs.append(f'<h3>{e(seq[0].upper() + seq[1:])}</h3><ol>{rows}</ol>')
    gates = "".join(f'<li><a href="/learn/dharma/gates/{g}">Gate {g} · {e(C["GATE_NAME"][str(g)])}</a></li>' for g in GATES)
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>Learn the Dharma Design</h1><p class="lede">{e(L["DHARMA_LEDE"])}</p>
{"".join(f"<p>{e(p)}</p>" for p in L["DHARMA_TEACH"])}
<h2>{e(C["PATH_NAME"][0].upper() + C["PATH_NAME"][1:])}</h2>
<p>Eleven spheres, walked in order. Each is drawn from one position in the design; in your reading each opens in a particular period of your life.</p>
{"".join(seqs)}
<h2 id="gates">The 64 gates of dharma</h2><ul class="terms">{gates}</ul>{_cta()}"""
    return ("Learn the Dharma Design: the 64 Gates of Dharma · The Wyrd Console",
            "What the Dharma Design is, the Pentagram Cross, the dharma profile, the eleven spheres of the Path of Dharma, and the 64 gates of dharma, by Saga Devi.",
            body, _crumbs(base, [("Learn", "/learn"), ("Dharma Design", "/learn/dharma")]))


def _dharma_arcs(g):
    span = _E.gate_span(g); a = span["start"]; out = []
    for k in range(9):
        lo = _E.norm((a + 360 * k) / 9); hi = _E.norm(lo + 5.625 / 9)
        out.append((lo, hi))
    out.sort()
    fmt = lambda l: f"{_E.sign_of(l)} {int(l % 30)}°{int(round((l % 1) * 60)) % 60:02d}′"
    return [f"{fmt(lo)} – {fmt(hi)}" for lo, hi in out]


def dharma_gate(base, g):
    r = C["REGISTER"].get(str(g))
    if not r: return None
    name = C["GATE_NAME"][str(g)]
    prev_g, next_g = (g - 2) % 64 + 1, g % 64 + 1
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn/dharma">Dharma Design</a> › <a href="/learn/dharma#gates">Gates of dharma</a></p>
<h1>Gate {g} of dharma: {e(name)}</h1>
<p class="lede">{e(r["t"])}</p>
<p>{e(L["DHARMA_GATE"])}</p>
<h2>The engine</h2><p>{e(first(r.get("e"), 2))}</p>
<h2>What ripens</h2><p>{e(first(r.get("l")))}</p>
<h2>The shadow it matures through</h2><p>{e(first(r.get("d")))}</p>
<p class="muted">The full passage for this gate, with how it breaks and how it is repaired, is in the paid reading when the gate is in your Dharma Design.</p>
<h2>A question to carry</h2><p><i>{e(first(r.get("a")))}</i></p>
<h2>Where it comes from</h2><p>{e(L["DHARMA_POSITIONS"])}</p>
<ul>{"".join(f"<li>{e(x)}</li>" for x in _dharma_arcs(g))}</ul>
<p class="muted">At birth this gate sits at {e(r["h"])}. See <a href="/learn/gates/{g}">Gate {g} in the birth design</a>.</p>
<p><a href="/learn/dharma/gates/{prev_g}">← Gate {prev_g} of dharma</a> · <a href="/learn/dharma/gates/{next_g}">Gate {next_g} of dharma →</a></p>{_cta()}"""
    return (f"Gate {g} of Dharma: {name} · Dharma Design · The Wyrd Console",
            f"Gate {g}, {name}, in the Dharma Design: {first(r.get('e'))}"[:300],
            body, _crumbs(base, [("Learn", "/learn"), ("Dharma Design", "/learn/dharma"), (f"Gate {g}", f"/learn/dharma/gates/{g}")]))
