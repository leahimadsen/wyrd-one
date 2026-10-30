"""Public pages search engines can read: the astrology readings on offer, and a
learning page for every gate, nakshatra (lunar mansion) and sidereal sign.

Each learning page carries the facts and a short taste of The Völva's register
from lib/corpus.json, then points to the free birth chart and the paid reading.
The full passages stay in the paid reading."""
import html, json, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
ESSAYS = json.load(open(os.path.join(HERE, "lib", "essays.json"), encoding="utf-8"))["NAKSHATRA"]   # the long essays, by page
SUBSTACK = os.environ.get("SUBSTACK_URL", "https://thewebofwyrd.substack.com").strip().rstrip("/")
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


# who wrote the pages, told to search engines the same way everywhere, so the site and The Web of Wyrd read as one author
def _author():
    return {"@type": "Person", "name": "The Völva", "url": SUBSTACK, "sameAs": [SUBSTACK]}


def _publisher(base):
    return {"@type": "Organization", "name": "The Wyrd Console", "url": base + "/", "logo": base + "/static/icons/icon-512.png?v=2"}


def _article(base, path, headline, desc):
    return _ld({"@context": "https://schema.org", "@type": "Article", "headline": headline[:110], "description": desc[:300],
                "author": _author(), "publisher": _publisher(base), "mainEntityOfPage": base + path, "inLanguage": "en",
                "image": base + "/static/look/share.jpg"})


def _essay(s, name):
    """The Völva's long essay on a mansion, where there is one (lib/essays.json)."""
    x = ESSAYS.get(s)
    if not x: return ""
    part = f'the {ORD27[x["part"] - 1]} part of <i>{e(x["series"])}</i>' if x.get("part") else f'from <i>{e(x["series"])}</i>'
    return (f'<h2>The full essay</h2><p>The Völva\'s long essay on {e(name)} is <a href="{e(x["url"])}">{e(x["title"])}</a>, '
            f'{part}, on The Web of Wyrd.</p>')


PRICE = "$44"      # the one-off reading's price; app.py sets it from config.PRICE_CENTS

def _cta():
    return ('<div class="cta"><p>See where this sits in your own chart. The birth chart is free: sidereal and tropical '
            'positions, the 27 nakshatras, the 64 gates and the runes. The full written reading is ' + PRICE + '.</p>'
            '<p><a class="btn-cast" href="/">Cast your free birth chart</a></p>'
            '<p><a href="/reports">See the astrology readings →</a></p></div>')


# ---------------- the readings ----------------
def _testimonials(where):
    from . import testimonials
    return testimonials.render(where)


def reports(base, price_cents, member_cents, month_cents=1100, year_cents=9900, pro_cents=3300, pro_n=30,
            together_cents=2200, together_extra=1100, member_off=20, consult_cents=10000, path_cents=25000, path_calls=3):
    p = price_cents / 100
    m = lambda c: f"${c // 100}" if c % 100 == 0 else f"${c / 100:.2f}"
    body = f"""
<h1>Astrology readings by The Völva</h1>
<p class="lede">Start with the free birth chart: the whole path, in both zodiacs, with your design, runes and timing. When you want it read, there are four ways in.</p>
<div class="plans">
  <section class="plan lead" data-arcanum="reading" data-line="Your whole chart, read in full."><h2>The Wyrd Reading</h2><div class="price">{m(price_cents)}<small> once</small></div>
    <p class="muted">A natal astrology reading in fifteen sections, written for your placements and nobody else's. It opens with the story of how you got here; the sections decode it.</p>
    <ul><li>The Seat you rise from, the engine of your Moon, and the Matrix your Saturn builds</li>
    <li>Every planet in both zodiacs, and how they feed each other; your Soul-Planet and its cabinet</li>
    <li>Your whole life by Vimshottari era, and your runes and the years each one wakes</li>
    <li>Your Birth Design and Dharma Design, drawn and read, and every old map of the body on one figure</li>
    <li>The Path of Dharma step by step, your numbers, and every question your chart asks</li></ul>
    <a class="btn-buy" href="/">Cast your chart, then get the reading</a>
    <a class="alt" href="/sample">Read a sample reading first</a></section>
  <section class="plan" data-arcanum="together" data-line="Two or more charts, one story."><h2>The Reading Together</h2><div class="price">{m(together_cents)}<small> for two</small></div>
    <p class="muted">and {m(together_extra)} for each person you add, up to nine</p>
    <ul><li>A story about how you ended up together, and what your bond is for, how it lifts you and where it can struggle</li>
    <li>What each of you wakes in the other, the old eight-fold match, how your bodies meet, and your numbers side by side</li>
    <li>The next thirty years, chapter by chapter and year by year, with the years to watch</li></ul>
    <a class="btn-cast" href="/chart#compare">Add people in Compare, then get it</a></section>
  <section class="plan" data-arcanum="order" data-line="Your weather, every week."><h2>The Order</h2><div class="price">{m(month_cents)}<small> a month</small></div>
    <p class="muted">or {m(year_cents)} a year</p>
    <ul><li>Body Weather by email every Monday: how the week's sky moves through your Birth Design and your Dharma Design</li>
    <li>Your chart opened up: every rune read in full, your Dharma Design read, and the planets on your body map</li>
    <li>The Wyrd Reading for {m(member_cents)} instead of {m(price_cents)}, and {member_off}% off the reading together</li></ul>
    <a class="btn-cast" href="/membership">See the Order</a></section>
  <section class="plan" data-arcanum="circle" data-line="For those who read for others."><h2>The Inner Circle</h2><div class="price">{m(pro_cents)}<small> a month</small></div>
    <ul><li>For astrologers and practitioners: The Wyrd Reading for your clients, {pro_n} a month</li>
    <li>This week's Body Weather for any client</li><li>Everything in the Order</li></ul>
    <a class="btn-cast" href="/membership#pro">See the Inner Circle</a></section>
</div>
<section class="one-to-one"><p class="hall-kicker">One to one</p><h2>A lantern for your path</h2>
<p>A first 1:1 consult is {m(consult_cents)}: about an hour together on your chart and what you need, and your full written reading opens as soon as you book.
For ongoing support there is <b>the Lightning Path</b>: {["", "one", "two", "three", "four", "five", "six"][path_calls] if path_calls < 7 else path_calls} one-hour calls a month, and messaging between them, for {m(path_cents)} a month.</p>
<p><a class="btn-buy" href="/letmelightyourpath">Book a 1:1 consult</a> <a class="alt" href="/letmelightyourpath">See the Lightning Path</a></p></section>
{_testimonials("reports")}
<h2>Questions</h2>
<h3>What do I need for an astrology reading?</h3><p>Your date, time and place of birth. If you don't know the time, the free chart still works with solar houses, and the reading tells you which parts depend on the time.</p>
<h3>Is this sidereal or tropical astrology?</h3><p>Both. Signs, nakshatras and houses are sidereal (Lahiri). The 64 gates use the tropical zodiac, as Human Design does. Your Dharma Design is the ninth harmonic (D9) of the sidereal positions.</p>
<h3>How do I get my reading?</h3><p>Straight after payment it opens in your browser. Save it as a PDF from your browser's print menu.</p>
<h3>Can astrologers use these tools with their clients?</h3><p>Yes. Astrologers and practitioners can use these tools with their own clients through <a href="/membership#pro">the Inner Circle</a>.</p>
<h3>How do I reach The Völva?</h3><p><a href="/contact">Write to her here</a>. For a session together, see <a href="/letmelightyourpath">a lantern for your path</a>.</p>
"""
    faq = [("What do I need for an astrology reading?", "Your date, time and place of birth. If you don't know the time, the free chart still works with solar houses."),
           ("Is this sidereal or tropical astrology?", "Both. Signs, nakshatras and houses are sidereal (Lahiri). The 64 gates use the tropical zodiac. The Dharma Design is the ninth harmonic (D9) of the sidereal positions."),
           ("How do I get my reading?", "Straight after payment it opens in your browser, and can be saved as a PDF.")]
    ld = _ld({"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": "The Wyrd Reading: a natal astrology reading", "brand": {"@type": "Brand", "name": "The Wyrd Console"},
         "description": "A personal astrology report written from your birth chart by The Völva: sidereal signs, nakshatras, the 64 gates, the Birth and Dharma Designs, the runes, and the Vimshottari eras of a life.",
         "url": base + "/reports", "image": base + "/static/icons/icon-512.png?v=2",
         "offers": {"@type": "Offer", "price": f"{p:.2f}", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": base + "/reports"}},
        {"@type": "Product", "name": "The Reading Together: a relationship astrology reading", "brand": {"@type": "Brand", "name": "The Wyrd Console"},
         "description": "A synastry reading for two to nine people by The Völva: the bond by Sukuyō and the planets, the eight-fold match, how your designs meet, your numbers, and the next thirty years together.",
         "url": base + "/reports", "image": base + "/static/icons/icon-512.png?v=2",
         "offers": {"@type": "Offer", "price": f"{together_cents / 100:.2f}", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": base + "/reports"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]})
    return ("Astrology Readings & Birth Chart Reports · The Wyrd Console",
            f"Personal astrology readings by The Völva, written from your exact birth chart: sidereal and tropical signs, nakshatras, your design and Dharma Design, runes and timing. ${p:.0f}, ready the moment you pay.",
            body, ld)


# ---------------- learning pages ----------------
def learn_index(base):
    gates = "".join(f'<li><a href="/learn/gates/{g}">Gate {g} · {e(C["GATE_NAME"][str(g)])}</a></li>' for g in GATES)
    naks = "".join(f'<li><a href="/learn/nakshatras/{s}">{e(C["NAKSHATRA"][i][0])}</a> <span class="muted">· {e(C["NAKSHATRA"][i][6])}</span></li>' for s, i in NAKS)
    from .zodiac import Z
    signs = "".join(f'<li><a href="/learn/signs/{s}">{Z["SIGNS"][i]["glyph"]}︎ {e(C["SIGN_FRAME"][i][0])}</a> '
                    f'<span class="muted">· {e(Z["SIGNS"][i]["skt"])}</span></li>' for s, i in SIGNS)
    long = [x for s, _ in NAKS if (x := ESSAYS.get(s))]
    essays = (f'<p>The Völva\'s long essays on the mansions, <i>{e(long[0]["series"])}</i>, appear on The Web of Wyrd: '
              + ", ".join(f'<a href="{e(x["url"])}">{e(x["title"])}</a>' for x in long) + ".</p>") if long else ""
    body = f"""<h1>Learn astrology with the Wyrd Console</h1>
<p class="lede">The building blocks of your birth chart: the twelve signs, the twenty-seven nakshatras, the sixty-four gates and the twenty-four runes, each in The Völva's words.</p>
<div class="cta"><p><b>New to charts?</b> The quickest way in is your own: cast it, then walk it in short steps, one ring at a time.</p>
<p><a class="btn-cast" href="/">Cast your chart and start the walk</a></p></div>
<h2 id="signs">The 12 signs of the zodiac</h2>
<p>Start with <a href="/learn/signs">the zodiac</a>: the two ways of measuring it, this year's dates, the elements, the rulers and the dignities. Then each sign in full: what it brings, the body it gives, every planet in it, its mansions and stars, how the old traditions drew it, and people born under it.</p>
<ul class="terms">{signs}</ul>
<h2 id="nakshatras">The 27 nakshatras (lunar mansions)</h2>
<p>The oldest map of the sky in Jyotish: twenty-seven mansions of 13°20′ that the Moon passes through, one a day. Each has a ruling planet, a deity, a power of its own, and a part of the body. Each page reads one in full: what it's about, what it's good for, where it goes wrong, and its question.</p>
<ul class="terms">{naks}</ul>
{essays}
<h2 id="gates">The 64 gates</h2><ul class="terms">{gates}</ul>
<h2 id="mandala">The Wyrd Mandala</h2>
<p>Two zodiacs turning against each other, with the mansions, the padas, a Buddhist and a Nordic deck, and the Asura voids laid on them. <a href="/learn/mandala">Learn to read the Wyrd Mandala</a>, then <a href="/mandala">open it</a>. Its cards are <a href="/deck">the Wyrd deck</a>, 108 of them, and your Moon draws yours. Or take the free masterclass, <a href="/masterclass">How I Read the Wyrd Mandala</a>.</p>
<h2 id="sukuyo">Sukuyō</h2>
<p>The Japanese art of the lunar mansions: twenty-seven shuku read from the old lunar calendar, and the six relations that say how two people stand to each other. <a href="/learn/sukuyo">Learn Sukuyō and find your shuku</a>.</p>
<h2>Go further</h2><ul class="terms"><li><a href="/learn/runes">Learn the runes: the 24 runes of the Elder Futhark</a></li>
<li><a href="/learn/numbers">Learn the numbers: life path, name numbers, Stavefall and Vedic</a></li>
<li><a href="/learn/dharma">Learn the Dharma Design: the 64 gates of dharma</a></li></ul>{_cta()}"""
    return ("Learn Astrology: Signs, Nakshatras, the 64 Gates, Runes & Dharma · The Wyrd Console",
            "A free guide to the twelve sidereal signs, the twenty-seven nakshatras and the sixty-four gates, written by The Völva.",
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
    desc = f"Gate {g}, {name}: {first(r.get('e'))}"[:300]
    return (f"Gate {g} {name} Meaning · Human Design & Astrology · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), (f"Gate {g}", f"/learn/gates/{g}")])
            + _article(base, f"/learn/gates/{g}", f"Gate {g}: {name}", desc))


ORD27 = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth",
         "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth", "twenty-first", "twenty-second",
         "twenty-third", "twenty-fourth", "twenty-fifth", "twenty-sixth", "twenty-seventh"]


def nakshatra(base, s):
    """A free reading of one lunar mansion: what it's about, what it's good for and where it goes wrong, what it
    rules, the body and face it gives, its four padas, the gates that fall in it, and its question. Every line comes
    from The Völva's corpus (NAKSHATRA, ENGINE, NAK_DEEP) and register_ext (GANA, AIMS)."""
    from . import engine as E
    from .reading_more import X as RX
    i = NAK_BY.get(s)
    if i is None: return None
    n, d, g = C["NAKSHATRA"][i], C["NAK_DEEP"][i], C["ENGINE"][i]
    names = [x[0] for x in C["NAKSHATRA"]]
    start = i * 360 / 27; arc = 40 / 3
    sign_of = lambda x: C["SIGN_FRAME"][int(x // 30) % 12][0]
    deg = lambda x: f"{int(x % 30)}°{int(round((x % 1) * 60)) % 60:02d}′"
    years = dict(E.DASHA)[n[1]]
    gana = d[2].split(" ·")[0]
    sounds = d[9].split()
    padas = "".join(f"<tr><td>{p + 1}</td><td>{deg(start + p * arc / 4)} {e(sign_of(start + p * arc / 4))}</td>"
                    f"<td>{e(E.SIGNS[(i * 4 + p) % 12])}</td><td>{e(RX['AIMS'][(i * 4 + p) % 4]['aim'])}</td>"
                    f"<td>{e(sounds[p]) if p < len(sounds) else '—'}</td></tr>" for p in range(4))
    gates = sorted({gt for gt in GATES for ln in range(1, 7) if (m := E.gate_mansion(gt, ln)) and i in (m["primary"], m["secondary"])})
    gate_links = ", ".join(f'<a href="/learn/gates/{gt}">{gt} {e(C["REGISTER"][str(gt)]["t"])}</a>' for gt in gates)
    aims = "".join(f"<li><b>{e(a['aim'])}</b>: {e(a['says'])}</li>" for a in RX["AIMS"])
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn#nakshatras">Nakshatras</a></p>
<h1>{e(n[0])}</h1>
<p class="lede">{e(n[6])}</p>
<p>{e(n[0])} is the {ORD27[i]} of the twenty-seven lunar mansions, running from {deg(start)} {e(sign_of(start))} to {deg(start + arc)} {e(sign_of(start + arc - 1e-6))} in the sidereal zodiac. Its stars are {e(d[1][0].lower() + d[1][1:])}. The Moon passes through it in about a day each month, so it colours a day, and it colours a whole life when it holds your Moon or your rising degree.</p>

<h2>What it's about</h2>
<p>{e(g[6])}</p>
<p>Its power (shakti) is <b>{e(g[1])}</b>, {e(g[2])}. What comes down through it is {e(g[3])}; what rises from it is {e(g[4])}; and the fruit it bears is {e(g[5])}.</p>

<h2>What it's good for</h2>
<p>{e(d[12])}</p>
<p><b>At its best:</b> {e(g[7])}</p>

<h2>Where it goes wrong</h2>
<p>{e(d[13])}</p>
<p><b>The dark gift</b> (a choice, made knowing): {e(g[8])}</p>
<p><b>The distortion</b> (unconscious): {e(g[9])}</p>

<h2>What it rules, and what rules it</h2>
<dl class="facts">
  <dt>Ruling planet</dt><dd>{e(n[1])}. When the Moon is here at birth, life opens in {e(n[1])}'s period of the Vimshottari clock, which runs {years} years in full.</dd>
  <dt>Deity</dt><dd>{e(n[2])}</dd><dt>Symbol</dt><dd>{e(n[3])}</dd>
  <dt>In the body</dt><dd>{e(n[5])}</dd>
  <dt>Nature</dt><dd>{e(d[2])}. {e(RX["GANA"].get(gana, ""))}</dd>
  <dt>Animal</dt><dd>{e(d[3])}</dd>
  <dt>Guna</dt><dd>{e(d[4])}</dd><dt>Dosha</dt><dd>{e(d[5])}</dd>
  <dt>Caste</dt><dd>{e(d[6])}</dd><dt>Aim</dt><dd>{e(d[7])}</dd>
  <dt>Motion</dt><dd>{e(d[8])}</dd><dt>Sounds</dt><dd>{e(d[9])}, one for each pada, used for names given under this mansion</dd>
</dl>

<h2>The body and the face it gives</h2>
<p>When {e(n[0])} rises, or holds the Moon, this is the build the old descriptions give:</p>
<p>{e(d[10])}</p><p>{e(d[11])}</p>

<h2>Its four padas</h2>
<p>Each mansion splits into four padas of 3°20′. Each pada falls in one sign of the navamsa, the ninefold chart, and works through one of the four aims of life.</p>
<div class="tw"><table><tr><th>Pada</th><th>Begins</th><th>Navamsa</th><th>Aim</th><th>Sound</th></tr>{padas}</table></div>
<ul class="kar-plain">{aims}</ul>
{f'<h2>Gates in {e(n[0])}</h2><p>These gates of the wheel fall in this mansion, so it feeds them wherever they sit in a chart: {gate_links}.</p>' if gates else ""}

<h2>Its question</h2>
<p class="rd-ask"><i>{e(g[10])}</i></p>
{_essay(s, n[0])}
<p><a href="/learn/nakshatras/{slug(names[i - 1])}">← {e(names[i - 1])}</a> · <a href="/learn/nakshatras/{slug(names[(i + 1) % 27])}">{e(names[(i + 1) % 27])} →</a></p>{_cta()}"""
    desc = f"{n[0]} nakshatra in Vedic astrology: ruled by {n[1]}, deity {n[2]}. {n[6]} What it's good for, where it goes wrong, its padas and its question."[:300]
    return (f"{n[0]} Nakshatra: Meaning, Ruler, Deity, Padas · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), (n[0], f"/learn/nakshatras/{s}")])
            + _article(base, f"/learn/nakshatras/{s}", f"{n[0]} Nakshatra: Meaning, Ruler, Deity and Padas", desc))


def sign(base, s):
    """A full page for one sign: see wyrd/zodiac.py."""
    from . import zodiac
    return zodiac.sign_page(base, s)


def signs_index(base):
    """The zodiac overview at /learn/signs: see wyrd/zodiac.py."""
    from . import zodiac
    return zodiac.index_page(base)


def sitemap(base):
    urls = ["/", "/reports", "/letmelightyourpath", "/contact", "/membership", "/today", "/mandala", "/sample", "/learn", "/learn/signs", "/learn/sukuyo", "/learn/mandala", "/masterclass", "/deck", "/privacy"]
    urls += [f"/learn/gates/{g}" for g in GATES] + [f"/learn/nakshatras/{s}" for s, _ in NAKS] + [f"/learn/signs/{s}" for s, _ in SIGNS]
    urls += ["/learn/runes"] + [f"/learn/runes/{r[0]}" for r in RUNES] + ["/learn/numbers", "/learn/dharma"] + [f"/learn/dharma/gates/{g}" for g in GATES]
    rows = "".join(f"<url><loc>{e(base + u)}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>'


# ---------------- the Wyrd deck ----------------
DECK_SCRIPT = """<link rel="stylesheet" href="/static/deck.css?v=1">
<script src="/static/deck.js?v=3"></script>
<script>
(() => {
  const host = document.getElementById("deckHost");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const FAM = [["t", "The trumps of the sign"], ["b", "The Buddhist deck · where it comes from"], ["n", "The Nordic deck · where it lands"], ["v", "The Asura voids"]];
  WyrdDeck.ready().then(D => {
    const all = D.all(), bySign = D.SIGNS.map((_, s) => ["tb", "tn"].map(k => k + String(s).padStart(2, "0")).concat(all.filter(id => D.signOf(id) === s)));
    const cardBtn = id => { const c = D.card(id), sub = c.kind === "v" ? `station ${c.numeral}` : c.kind === "t" ? `the ${c.deck === "buddhist" ? "Buddhist" : "Nordic"} trump · ${c.numeral}` : c.trump;
      return `<button type="button" data-card="${id}" aria-label="Open the card ${esc(c.title)}"><div class="wd-card">${D.svg(id, { face: true })}</div><span>${esc(c.title)}<small>${esc(sub)}</small></span></button>`; };
    /* the twelve signs are laid out at once, and each sign's nine plates are fetched and drawn in turn */
    host.innerHTML = D.SIGNS.map((name, s) => `<section class="dk-sign" data-sign="${s}"><h2>${name}</h2><p class="dk-loading">Laying out ${name}…</p></section>`).join("");
    bySign.reduce((p, ids, s) => p.then(() => D.need(ids)).then(() => {
      const sec = host.querySelector(`[data-sign="${s}"]`);
      sec.innerHTML = `<h2>${D.SIGNS[s]}</h2>` + FAM.map(([k, name]) => `<p class="dk-fam">${name}</p>
        <div class="dk-grid${k === "t" ? " dk-trumps" : ""}">${ids.filter(id => id[0] === k).map(cardBtn).join("")}</div>`).join("");
    }), Promise.resolve());
    const AYD = window.WYRD && WYRD.FRAME ? WYRD.FRAME.ayanamsa.degrees : 24.225;
    const station = id => { const c = D.card(id); if (c.kind === "v") return c.station + 1; if (c.kind === "b") return c.decan * 3 + 1;
      if (c.kind === "t" && c.deck === "buddhist") return c.sign * 9 + 1;
      const t = (c.kind === "t" ? c.sign * 30 : c.decan * 10) - AYD; return Math.floor((((t % 360) + 360) % 360) / (10 / 3)) % 108 + 1; };
    host.addEventListener("click", e => { const b = e.target.closest("[data-card]"); if (!b) return;
      D.open(b.dataset.card, { links: [{ href: `/mandala#s${String(station(b.dataset.card)).padStart(3, "0")}`, text: "Find it in the Mandala" }, { href: "/", text: "Draw your own card" }] }); });
  }).catch(() => { host.innerHTML = `<p class="err">The deck couldn't load just now. Please try again in a moment.</p>`; });
})();
</script>"""


def deck(base):
    body = """<h1>The Wyrd Deck</h1>
<p class="lede">The Völva's deck of 108 cards, one for every station of the Wyrd Mandala.</p>
<p>The deck is read off the Mandala's two rings. <b>The Buddhist deck</b> has 36 cards, one for each decan of the sidereal ring: where a thing comes from.
<b>The Nordic deck</b> has 36, one for each decan of the tropical ring: where it lands. And <b>the Asura voids</b> have 36, the tunnels beneath the mansions,
one at the fourth, seventh and ninth pada of every sign. Each card carries its decan or its station, its trump and the runes of its sign.</p>
<p>Above the 108 stand <b>the trumps of the zodiac</b>, two for every sign: its Buddhist trump on the sidereal ring and its Nordic trump on the tropical ring,
each carrying its sign, its ruler, its three minors and its runes.</p>
<p>Everyone has a card. Your Moon draws it: the card of the decan your Moon was born in, read on both rings, and the void it sits over if it sits over one.
Your card adds your Moon's mansion, its deity and its rune, and the first gates of your Path of Dharma, ready to share, and your Moon's sign gives you its two trumps.</p>
<p class="dk-cta"><a class="btn-cast" href="/">Cast your free chart and draw your card</a> <a class="alt" href="/mandala">Open the Wyrd Mandala</a></p>
<div id="deckHost"><p class="dk-loading">Laying out the deck…</p></div>"""
    ld = _ld({"@context": "https://schema.org", "@type": "CreativeWork", "name": "The Wyrd Deck", "creator": _author(),
              "description": "A deck of 108 cards read off the Wyrd Mandala: the Buddhist deck on the sidereal ring, the Nordic deck on the tropical ring, and the 36 Asura voids.",
              "url": base + "/deck"})
    return ("The Wyrd Deck: 108 Cards of the Wyrd Mandala · The Wyrd Console",
            "The Völva's deck of 108 cards: the Buddhist deck on the sidereal ring, the Nordic deck on the tropical ring, and the 36 Asura voids. Draw your own card from your chart.",
            body, ld)


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
    desc = f"The {name} rune {glyph}: {R['means']} Lit well: {R['light']} Its call: {R['call']}"
    return (f"{name} Rune Meaning ({glyph}) · Elder Futhark · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), ("Runes", "/learn/runes"), (name, f"/learn/runes/{s}")])
            + _article(base, f"/learn/runes/{s}", f"The {name} Rune: Meaning in the Elder Futhark", desc))


# ---------------- the first page's way into Learn ----------------
def home_explore():
    """Plain links from the first page to every mansion and rune, so search engines (and people who scroll)
    find the learning pages from the page everyone lands on."""
    naks = "".join(f'<a href="/learn/nakshatras/{s}">{e(C["NAKSHATRA"][i][0])}</a>' for s, i in NAKS)
    runes = "".join(f'<a href="/learn/runes/{r[0]}"><span aria-hidden="true">{r[1]}</span> {e(r[2])}</a>' for r in RUNES)
    return f"""<section class="explore" aria-labelledby="exH">
  <h2 id="exH">Learn the building blocks</h2>
  <h3>The twenty-seven lunar mansions</h3><p class="ex-links">{naks}</p>
  <h3>The twenty-four runes of the Elder Futhark</h3><p class="ex-links">{runes}</p>
  <p class="ex-more"><a href="/learn/signs">The twelve signs</a> <a href="/learn#gates">The sixty-four gates</a> <a href="/learn/dharma">The Dharma Design</a> <a href="/learn/numbers">The numbers</a> <a href="/deck">The Wyrd deck</a> <a href="/learn">Everything to learn</a></p>
</section>"""


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
            "What the Dharma Design is, the Pentagram Cross, the dharma profile, the eleven spheres of the Path of Dharma, and the 64 gates of dharma, by The Völva.",
            body, _crumbs(base, [("Learn", "/learn"), ("Dharma Design", "/learn/dharma")]))


def _dharma_arcs(g):
    span = _E.gate_span(g); a = span["start"]; out = []
    for k in range(9):
        lo = _E.norm((a + 360 * k) / 9); hi = _E.norm(lo + 5.625 / 9)
        out.append((lo, hi))
    out.sort()
    fmt = lambda l: f"{_E.sign_of(l)} {int(l % 30)}°{int(round((l % 1) * 60)) % 60:02d}′"
    return [f"{fmt(lo)} – {fmt(hi)}" for lo, hi in out]


def _dharma_wake(g):
    """How to wake the gate, and the channels it is half of, from lib/dharma.json."""
    from . import dharma as DH, rave as RV
    w = DH.T["GATES"].get(str(g), {})
    if not w.get("ok"): return ""
    chans = "".join(f'<li>Channel {a}–{b}, {e(DH.T["CHANNELS"][DH.key(a, b)]["name"])}, with <a href="/learn/dharma/gates/{b if a == g else a}">gate {b if a == g else a}</a>: '
                    f'{e(DH.T["CHANNELS"][DH.key(a, b)]["what"])}</li>' for a, b in RV.CHANNELS if g in (a, b))
    return (f'<h2>How to wake it</h2><p>{e(w["do"])}</p><p>{e(DH.T["SIGN"].format(sign=w["sign"]))}</p>'
            f'<p class="muted">The Sun lights this gate each year {e(DH.sun_week(g))}.</p>'
            f'<h2>Its other halves</h2><p>Every gate is half of a channel. Where your Birth Design holds the other half, you have a bridge.</p><ul>{chans}</ul>')


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
{_dharma_wake(g)}
<h2>Where it comes from</h2><p>{e(L["DHARMA_POSITIONS"])}</p>
<ul>{"".join(f"<li>{e(x)}</li>" for x in _dharma_arcs(g))}</ul>
<p class="muted">At birth this gate sits at {e(r["h"])}. See <a href="/learn/gates/{g}">Gate {g} in the birth design</a>.</p>
<p><a href="/learn/dharma/gates/{prev_g}">← Gate {prev_g} of dharma</a> · <a href="/learn/dharma/gates/{next_g}">Gate {next_g} of dharma →</a></p>{_cta()}"""
    desc = f"Gate {g}, {name}, in the Dharma Design: {first(r.get('e'))}"[:300]
    return (f"Gate {g} of Dharma: {name} · Dharma Design · The Wyrd Console", desc, body,
            _crumbs(base, [("Learn", "/learn"), ("Dharma Design", "/learn/dharma"), (f"Gate {g}", f"/learn/dharma/gates/{g}")])
            + _article(base, f"/learn/dharma/gates/{g}", f"Gate {g} of Dharma: {name}", desc))


# ---------------- the numbers ----------------
NUMS = json.load(open(os.path.join(HERE, "lib", "numbers.json"), encoding="utf-8"))
_GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"}


def numbers_learn(base):
    """How the numbers are counted and the two seatings, Stavefall and Vedic. Each number's light is a taste;
    its shadow, and where its planets stand in a chart, are the reading's."""
    from .numbers import STAVEFALL, VEDIC
    T, N = NUMS["LEARN"], NUMS["NUMBER"]
    ps = lambda xs: "".join(f"<p>{e(x)}</p>" for x in xs)
    rows = "".join(
        f'<tr><td><b>{n}</b></td><td>{e(N[str(n)]["name"])}</td><td>{_GLYPH[STAVEFALL[n][0]]} {STAVEFALL[n][0]} <span class="muted">· {STAVEFALL[n][1].lower()}</span></td>'
        f'<td>{_GLYPH[VEDIC[n]]} {VEDIC[n]}</td></tr>' for n in range(1, 10))
    masters = "".join(f'<tr><td><b>{n}</b></td><td>{e(N[str(n)]["name"])}</td><td colspan="2" class="muted">sits where {r} sits</td></tr>'
                      for n, r in ((11, 2), (22, 4), (33, 6)))
    lit = "".join(f'<li><b>{n} · {e(N[str(n)]["name"])}.</b> {e(N[str(n)]["light"])}</li>' for n in (*range(1, 10), 11, 22, 33))
    body = f"""<p class="crumbs"><a href="/learn">Learn</a></p>
<h1>{e(T["TITLE"])}</h1><p class="lede">{e(T["LEDE"])}</p>
<h2>{e(T["TABLE_H"])}</h2>
<div class="tw"><table class="mini"><tr><th>Number</th><th></th><th>Stavefall</th><th>Vedic</th></tr>{rows}{masters}</table></div>
<h3>Each number, lit well</h3><ul class="ln-list">{lit}</ul>
<h2>{e(T["COUNT_H"])}</h2>{ps(T["COUNT"])}
<h2>{e(T["NAME_H"])}</h2>{ps(T["NAME"])}
<h2>{e(T["MASTER_H"])}</h2><p>{e(T["MASTER"])}</p>
<h2>{e(T["SEATS_H"])}</h2>
<h3>{e(T["STAVEFALL_H"])}</h3>{ps(T["STAVEFALL"])}
<h3>{e(T["VEDIC_H"])}</h3>{ps(T["VEDIC"])}
<h2>{e(T["READ_H"])}</h2><p>{e(T["READ"])}</p>
<p class="muted">Your free chart shows your numbers and both their planets. What each one means for you, its shadow, and where its planets stand in your own chart, is in the reading.</p>{_cta()}"""
    return ("Numerology: Life Path, Name Numbers, Stavefall and Vedic · The Wyrd Console", T["DESC"], body,
            _crumbs(base, [("Learn", "/learn"), ("Numbers", "/learn/numbers")]))
