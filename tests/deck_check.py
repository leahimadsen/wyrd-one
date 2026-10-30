"""The Wyrd deck: the 108 cards draw, the engraved ones print the words approved with them, a person's
card carries their Moon and Path of Dharma and nothing private, and the deck is on the chart page, in the
Mandala's record and on its own page.

    python tests/deck_check.py              (the browser parts need node)
"""
import json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("WYRD_DEV_NODE_EPH", "1")
os.environ.pop("DATABASE_URL", None); os.environ.pop("RENDER", None)
bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()

# ---------- the plates: one file a card ----------
PD = os.path.join(ROOT, "static", "deck", "plates")
EVERY = [f"{k}{d:02d}" for d in range(36) for k in "bn"] + [f"v{n:03d}" for n in range(1, 109) if (n - 1) % 9 in (3, 6, 8)]
TRUMPS = [f"t{k}{s:02d}" for k in "bn" for s in range(12)]
files = sorted(f[:-5] for f in os.listdir(PD) if f.endswith(".json")) if os.path.isdir(PD) else []
check("all 108 cards and the 24 trumps have their own engraved plate", files == sorted(EVERY + TRUMPS))
P = {i: json.load(open(os.path.join(PD, i + ".json"), encoding="utf-8")) for i in files}
check("every plate has its label and its engraving", all(p.get("label") and p.get("svg", "").startswith("<defs>") for p in P.values()))
check("the eighteen cut on the design canvas keep the words approved with them", sorted(i for i, p in P.items() if p.get("words")) == sorted(
    ["b00", "b01", "b02", "b03", "b04", "b05", "n00", "n01", "n02", "n03", "n04", "n05", "v004", "v007", "v009", "v013", "v016", "v018"]))
check("the plates carry their own look, no style sheet needed", not any("class=" in p["svg"] for p in P.values()))
svg_ids = [x for p in P.values() for x in re.findall(r'id="([^"]+)"', p["svg"])]
check("every id in a plate is marked to be made unique on the page", svg_ids and all(i.startswith("@@") for i in svg_ids))
check("no plate fetches anything from another site", not any(re.search(r'href="(https?:)?//', p["svg"]) for p in P.values()))
check("no plate draws a name or a date", not any(re.search(r"<text|\b(19|20)\d\d\b", p["svg"]) for p in P.values()))
check("each plate is small enough to fetch on a phone", max((os.path.getsize(os.path.join(PD, i + ".json")) for i in files), default=0) < 40000)
for f in ["fell.woff", "fell-italic.woff", "fell-sc.woff", "fraktur.woff", "OFL-IMFellEnglish.txt", "OFL-UnifrakturMaguntia.txt"]:
    check(f"the card type is served from the site: {f}", os.path.exists(os.path.join(ROOT, "static", "fonts", f)))

# ---------- the pages ----------
chart_js, chart_html, mand, pulse = read("static", "chart.js"), read("static", "chart.html"), read("static", "mandala", "wyrd-mandala.js"), read("wyrd", "pulse.py")
check("the chart page has Your card", 'id="p-card"' in chart_html and 'id="cardHost"' in chart_html and '{ id: "card",' in chart_js)
check("the chart page loads the deck", '/static/deck.js' in chart_html and '/static/deck.css' in chart_html)
check("Your card is in the header's tools", 'href="#card"' in chart_js)
check("the anonymous counts know the card and the Mandala", '"card"' in pulse and '"mandala"' in pulse)
check("the Mandala's record shows the station's cards, loading the deck when first opened", 'class="rec-deck"' in mand and "/static/deck.js" in mand and "stationCards" in mand)
check("each place fetches the plates it draws before drawing them", "D.need(D.forMoon(C)" in chart_js and "Dk.need(Dk.stationCards(" in mand)
check("no page still says an engraving is to come", not re.search(r"engraving to come|still being (cut|engraved)", chart_js + mand + read("wyrd", "pages.py")))

import app as A
web = A.app.test_client()
r = web.get("/deck"); page = r.get_data(as_text=True)
check("the deck page opens and is indexed", r.status_code == 200 and 'content="index, follow"' in page)
check("the deck page loads the deck and offers to draw your own", "/static/deck.js" in page and 'id="deckHost"' in page and 'href="/"' in page)
check("the deck page lays out all twelve signs and fetches each sign's plates", "D.SIGNS.map((name, s)" in page and "D.need(ids)" in page and "Still being engraved" not in page)
check("and shows each sign's two trumps first", '["t", "The trumps of the sign"]' in page and '["tb", "tn"]' in page)
check("the deck is in the sitemap", "/deck</loc>" in web.get("/sitemap.xml").get_data(as_text=True))
check("Völva, never anyone's surname, in the deck's words", "Völva" in page)

# ---------- the cards, drawn as the browser draws them ----------
if not shutil.which("node"):
    print("  skip the browser checks: node isn't installed")
else:
    js = r"""
const fs = require("fs"), path = require("path"), root = %s;
global.window = global; global.document = { createElement: () => ({ getContext: () => null }), head: { appendChild: () => {} } };
global.fetch = u => Promise.resolve({ json: () => JSON.parse(fs.readFileSync(path.join(root, u.split("?")[0]), "utf8")) });
eval(fs.readFileSync(path.join(root, "static/deck.js"), "utf8"));
const out = {};
(async () => {
  const D = await WyrdDeck.ready().catch(e => { out.err = String(e); });
  if (!D){ console.log(JSON.stringify(out)); return; }
  const all = D.all(); out.n = all.length; out.kinds = [...new Set(all.map(i => i[0]))];
  out.pip = D.svg("b20", { person: { nak: "Ashwini", deity: "Ashwini Kumaras", rune: "Fehu", house: 1, gates: [["Signature", 39], ["Crucible", 38], ["Aura", 21], ["Objective", 48]], caption: "" } });
  out.voidPip = D.svg("v058", { face: true });
  out.before = all.filter(D.engraved).length;
  const T = D.trumps(); out.trumps = T;
  await D.need(all.concat(T));
  out.trumpBroken = T.filter(id => { const s = D.svg(id, { face: true }); return !/viewBox="0 0 1080 \d+"/.test(s) || /undefined|NaN|null/.test(s) || !D.card(id).engraved; });
  out.trumpWords = Object.fromEntries(["tb00", "tn04", "tb11", "tn03"].map(id => [id, [D.card(id).numeral, D.card(id).title, ...D.card(id).cols.map(c => [c.label, ...c.lines.map(l => l.t)].join(" / "))]]));
  out.trumpStory = D.svg("tb04", { person: { nak: "Magha", deity: "the Pitris", rune: "Hagalaz", house: 9, gates: [["Signature", 39], ["Crucible", 38], ["Aura", 21], ["Objective", 48]], caption: "Signature · Gate 39 · Provocation" } });
  out.broken = all.filter(id => { const s = D.svg(id, { face: true }); return !/viewBox="0 0 1080 \d+"/.test(s) || /undefined|NaN|null/.test(s); });
  out.engraved = all.filter(D.engraved);
  out.platesIn = all.filter(id => D.card(id).engraved && D.svg(id, { face: true }).indexOf("feTurbulence") > 0).length;
  const P = { nak: "Ashwini", deity: "Ashwini Kumaras", rune: "Fehu", house: 1, gates: [["Signature", 39], ["Crucible", 38], ["Aura", 21], ["Objective", 48]], caption: "Signature · Gate 39 · Provocation" };
  out.story = D.svg("b00", { person: P });
  out.story2 = D.svg("b00", { person: P });
  out.words = { b00: D.card("b00").cols, n00: D.card("n00").cols, v016: D.card("v016").cols, v004: D.card("v004") };
  out.invalid = [D.valid("v057"), D.valid("v058"), D.valid("b36"), D.valid("n35")];
  const C = m => ({ sid: { Moon: m, Sun: 100 }, trop: { Moon: m + 24.2 }, ascS: 5, natal: { personality: { Sun: { gate: 39 }, Earth: { gate: 38 } }, design: { Sun: { gate: 21 }, Earth: { gate: 48 } } } });
  out.moon5 = D.forMoon(C(5)).map(x => x.id); out.moon12 = D.forMoon(C(12)).map(x => x.id); out.moon359 = D.forMoon(C(359.9)).map(x => x.id);
  out.person = D.person(C(12));
  const flat = c => c.cols.map(col => [col.label, ...col.lines.map(l => l.t)]);
  out.rulesOff = ["b01", "b02", "b03", "b04", "b05", "v004", "v007", "v009", "v013", "v016", "v018", "n01", "n03", "n04", "n05"].filter(id => JSON.stringify(flat(D.rules(id))) !== JSON.stringify(flat(D.card(id))))
    .map(id => [id, flat(D.rules(id)), flat(D.card(id))]);
  out.station3 = D.stationCards(3).map(x => x.id);
  console.log(JSON.stringify(out));
})();
""" % json.dumps(ROOT)
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    try: o = json.loads(r.stdout or "{}")
    except ValueError: o = {}; print(r.stdout[:400], r.stderr[:800])
    check("the deck loads", not o.get("err") and o.get("n"))
    check("all 108 cards: 36 Buddhist, 36 Nordic, 36 voids", o.get("n") == 108 and sorted(o.get("kinds", [])) == ["b", "n", "v"])
    check("every card draws, with no missing words", o.get("n") and not o.get("broken"))
    check("a plate is fetched only when its card is wanted", o.get("before") == 0)
    check("once fetched, all 108 cards are drawn from their own engravings", len(o.get("engraved", [])) == 108 and o.get("platesIn") == 108)
    check("the 24 trumps of the zodiac: each sign's Buddhist and Nordic trump", o.get("trumps") == TRUMPS)
    check("every trump draws from its own engraving, with no missing words", o.get("trumps") and not o.get("trumpBroken"))
    tw = o.get("trumpWords", {})
    check("the King: IV, Aries ruled by Mars, the Sun exalted, its minors and the Fool at its gate", (tw.get("tb00") or [""])[:2] == ["IV", "The King"]
          and "its sign / Aries / ruled by Mars / 0° to 30° sidereal / the Sun exalted at 10°" in tw.get("tb00", []) and "its minors / 2 · 3 · 4 of Double Vajras / Fehu · Uruz" in tw.get("tb00", [])
          and any("the Fool stands at its gate" in x for x in tw.get("tb00", [])))
    check("Strength is VIII and lands where tropical Leo falls on the sidereal ring", (tw.get("tn04") or [""])[:2] == ["VIII", "Strength"] and any(x.startswith("it lands on / XXIX – XXXVIII") for x in tw.get("tn04", [])))
    check("Nirvana is XVIII and carries Venus exalted", (tw.get("tb11") or [""])[:2] == ["XVIII", "Nirvana"] and any("Venus exalted at 27°" in x for x in tw.get("tb11", [])))
    st = o.get("trumpStory", "")
    check("a person's trump is a story card with its gilded frame, and no birth details", 'viewBox="0 0 1080 1920"' in st and "#b38a36" in st and "the trump of Leo" in st and not re.search(r"\b(19|20)\d\d-\d\d-\d\d\b", st))
    s = o.get("story", "")
    check("a story card is 1080 x 1920", 'viewBox="0 0 1080 1920"' in s)
    for t in ["2 of Double Vajras", "I – III · Ashwini", "the Fool stands at its gate", "The King", "Fehu · Uruz", "the moon in ashwini", "Kumaras",
              "rune of the moon", "fehu · house i", "the path of dharma", "Signature · Gate 39 · Provocation", "The Völva · Web of Wyrd", "draw your own card at wyrdconsole.com"]:
        check(f"the person's card prints: {t}", t in s)
    check("each card on a page has ids of its own", (lambda a, b: a and b and not set(a) & set(b))(set(re.findall(r'id="([^"]+)"', s)), set(re.findall(r'id="([^"]+)"', o.get("story2", "")))))
    check("and no id repeats inside one card", (lambda l: len(l) == len(set(l)))(re.findall(r'id="([^"]+)"', s)))
    w = o.get("words", {})
    flat = lambda cols: [l["t"] for c in cols for l in [{"t": c["label"]}] + c["lines"]]
    check("the Nordic 2 of Wands prints where it lands, as approved", flat(w.get("n00", [])) == ["its decan", "Mars in Aries", "0° to 10° tropical", "its trump", "The Emperor", "Fehu · Uruz", "it lands on", "CI – CIV", "Uttara Bhadrapada, in 2026", "Kamalaksha's void at CIII"])
    check("Bala prints its cards, the void across the wheel and the two in trine", flat(w.get("v016", [])) == ["its cards", "7 of Jewels", "9 of Swords, in 2026", "across the wheel", "Jalandhara", "station LXX", "in trine", "Diti-Mula", "Bana-Asura", "stations LII · LXXXVIII"])
    v4 = w.get("v004") or {}
    check("Vritra's head: the tunnel beneath Ashwini, station iv, navamsa in Cancer", v4.get("kicker") == "asura void · the tunnel beneath ashwini" and v4.get("sub") == "station iv · the fourth pada · navamsa in Cancer")
    off = o.get("rulesOff", [])
    for i, g, a in off: print(f"         {i}: rules {g}\n               card  {a}")
    check("the rules set the engraved cards' facts just as they were approved", o.get("n") and not off)
    check("a card whose plate can't be fetched is still drawn, as pips of its suit", "4 of Vajras" in o.get("pip", "") and "Karma" in o.get("pip", ""))
    check("and so is such a void", "Tarakasura" in o.get("voidPip", ""))
    check("only real cards: the voids are the 4th, 7th and 9th pada of a sign", o.get("invalid") == [False, True, False, True])
    check("a Moon at 5° sidereal draws the 2 of Double Vajras first, then where it lands, then its two trumps", o.get("moon5") == ["b00", "n02", "tb00", "tn00"])
    check("a Moon over Vritra's station draws its void too, then the trumps of its sidereal and tropical signs", o.get("moon12") == ["b01", "n03", "v004", "tb00", "tn01"])
    check("a Moon at the end of Pisces draws the 10 of Lotuses", (o.get("moon359") or [""])[0] == "b35")
    pp = o.get("person", {})
    check("the person's card reads the Moon's mansion, deity and rune", pp.get("nak") and pp.get("rune") and pp.get("house"))
    check("and the Path of Dharma's first four gates", [g[1] for g in pp.get("gates", [])] == [39, 38, 21, 48])
    check("a station's cards: Vritra's station has its Buddhist card, where it lands, its void and the trumps", o.get("station3") == ["b01", "n03", "v004", "tb00", "tn01"])
    check("no birth details are ever written on a card", not re.search(r"\b(19|20)\d\d-\d\d-\d\d\b|\b\d{1,2}:\d\d\b", s))

print("\nAll deck checks passed." if not bad else f"\n{bad} deck check(s) failed.")
sys.exit(1 if bad else 0)
