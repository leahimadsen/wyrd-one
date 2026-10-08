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
<h2>The 64 gates</h2><ul class="terms">{gates}</ul>{_cta()}"""
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
    rows = "".join(f"<url><loc>{e(base + u)}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>'
