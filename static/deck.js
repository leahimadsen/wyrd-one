'use strict';
/* ============================================================
   THE WYRD DECK
   108 cards, read off the Wyrd Mandala:
   - the Buddhist deck's 36 minors, one per decan of the sidereal ring
     ("where it comes from");
   - the Nordic deck's 36 minors, one per decan of the tropical ring
     ("where it lands");
   - the 36 Asura voids, the fourth, seventh and ninth pada of each sign.
   Each card is a 1080 x 1920 story card in The Völva's engraved style: her
   paper, her knotwork, a plate, the card's name and its three facts. A
   person's card adds their Moon (its mansion, deity and rune) and the
   Path of Dharma, and can be shared as an image.

   The engraved plates are in static/deck/plates.js (made from the design
   canvas by scripts/deck_plates.py). A card whose engraving isn't done yet
   is set as a pip card of its suit, so every card can be drawn today.

   - WyrdDeck.ready(): Promise, once the mandala, plates and fonts are in
   - WyrdDeck.card(id): the card's words and look ("b00", "n35", "v004")
   - WyrdDeck.forMoon(C): the cards a chart's Moon draws, primary first
   - WyrdDeck.person(C): the Moon and Path of Dharma a person's card prints
   - WyrdDeck.svg(id, { person, face }): the card as SVG markup
   - WyrdDeck.png(id, { person, face }): Promise of a PNG Blob
   - WyrdDeck.share(blob, name, text): the share sheet, else a download
   - WyrdDeck.engraved(id): true once the card's own engraving exists
   ============================================================ */
(() => {
const W = 1080, STORY_H = 1920, PAD_X = 96, TOP = 84, BOTTOM = 88;
const norm = d => ((d % 360) + 360) % 360;
const pad2 = n => String(n).padStart(2, "0"), pad3 = n => String(n).padStart(3, "0");
const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const ROMAN = n => { let o = ""; for (const [v, s] of [[100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]]) while (n >= v){ o += s; n -= v; } return o; };
const roman = n => ROMAN(n).toLowerCase();
const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
const ELEMENT = ["fire", "earth", "air", "water"];
const ORD = ["first", "second", "third", "fourth"];
const RUNES = ["Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz", "Gebo", "Wunjo", "Hagalaz", "Nauthiz", "Isa", "Jera",
  "Eihwaz", "Perthro", "Algiz", "Sowilo", "Tiwaz", "Berkano", "Ehwaz", "Mannaz", "Laguz", "Ingwaz", "Dagaz", "Othala"];
/* the runes as she draws them on the cards, each in a 40 x 80 box */
const RUNE_PATH = {
  Fehu: "M20 2L20 78M20 28.6L34.4 11.5M20 43.8L34.4 26.7", Uruz: "M10.4 2L10.4 78M10.4 2L29.6 22.9M29.6 22.9L29.6 78",
  Thurisaz: "M20 2L20 78M20 24.8L34.4 40M34.4 40L20 55.2", Ansuz: "M20 2L20 78M20 7.7L34.4 24.8M20 24.8L34.4 41.9",
  Raidho: "M20 2L20 78M20 2L34.4 19.1M34.4 19.1L20 36.2M20 36.2L34.4 78", Kenaz: "M31.2 19.1L12 40M12 40L31.2 60.9",
  Gebo: "M7.8 15.3L32.2 64.7M32.2 15.3L7.8 64.7", Wunjo: "M20 2L20 78M20 2L34.4 19.1M34.4 19.1L20 36.2",
  Hagalaz: "M10.4 2L10.4 78M29.6 2L29.6 78M10.4 32.4L29.6 47.6", Nauthiz: "M20 2L20 78M8.8 30.5L31.2 49.5", Isa: "M20 2L20 78",
  Jera: "M18.4 15.3L7.8 30.5M7.8 30.5L18.4 45.7M21.6 34.3L32.2 49.5M32.2 49.5L21.6 64.7", Eihwaz: "M20 2L20 78M20 2L32.8 15.3M20 78L7.2 64.7",
  Perthro: "M20 2L20 78M20 5.8L32.8 19.1M32.8 19.1L32.8 5.8M20 74.2L32.8 60.9M32.8 60.9L32.8 74.2", Algiz: "M20 2L20 78M20 34.3L7.2 11.5M20 34.3L32.8 11.5",
  Sowilo: "M29 5.8L11 34.3M11 34.3L29 45.7M29 45.7L11 74.2", Tiwaz: "M20 2L20 78M20 2L7.2 21M20 2L32.8 21",
  Berkano: "M20 2L20 78M20 2L33.4 21M33.4 21L20 40M20 40L33.4 59M33.4 59L20 78", Ehwaz: "M8.8 2L8.8 78M31.2 2L31.2 78M8.8 2L20 19.1M20 19.1L31.2 2",
  Mannaz: "M8.8 2L8.8 78M31.2 2L31.2 78M8.8 2L31.2 32.4M31.2 2L8.8 32.4", Laguz: "M20 2L20 78M20 2L33.4 21",
  Ingwaz: "M20 24.8L31.2 40M31.2 40L20 55.2M20 55.2L8.8 40M8.8 40L20 24.8", Dagaz: "M7.2 17.2L32.8 62.8M32.8 17.2L7.2 62.8M7.2 17.2L7.2 62.8M32.8 17.2L32.8 62.8",
  Othala: "M20 7.7L32.2 28.6M20 7.7L7.8 28.6M32.2 28.6L8.8 68.5M7.8 28.6L31.2 68.5" };
const runeBox = n => { const xs = RUNE_PATH[n].match(/[\d.]+/g).map(Number).filter((_, i) => i % 2 === 0); return [Math.min(...xs), Math.max(...xs)]; };

/* where the planets are exalted: on the sidereal ring (the Buddhist deck) and, for the Nordic deck,
   the seven planetary trumps at their tropical degrees */
const EX_SID = [["Sun", 10], ["Moon", 33], ["Mercury", 165], ["Jupiter", 95], ["Venus", 357], ["Saturn", 200], ["Mars", 298]];
const EX_TROP = [["The Sun", 19], ["The High Priestess", 33], ["The Magician", 165], ["The Empress", 357], ["The Tower", 298], ["Wheel of Fortune", 105], ["The World", 201]];
/* the Mandala's frame: the ayanamsa of 2026, which sets where the tropical cards land */
const AY = () => (window.WYRD && WYRD.FRAME && WYRD.FRAME.ayanamsa && WYRD.FRAME.ayanamsa.degrees) || (24 + 13.5 / 60);

/* ---------- the look of each suit, by element, and of the voids ---------- */
const PAL = {
  fire:  { bg: "#ecd3cc", vig: "rgba(80,30,20,.26)", tint: "#c4523c", wash: "#f5e1da", mid: "#8a2a1a", inner: "#f6e6e0", text2: "#5a4a3c", light: "#faf5ec" },
  earth: { bg: "#d3e5d9", vig: "rgba(20,50,40,.26)", tint: "#3e9c84", wash: "#e3efe7", mid: "#1d5e4f", inner: "#e8f2ec", text2: "#4c4a3e", light: "#faf7ef" },
  /* air and water wait for their first engraved sets; these follow fire and earth's weights */
  air:   { bg: "#ece0c2", vig: "rgba(70,50,10,.26)", tint: "#c2902a", wash: "#f5ecd8", mid: "#7a5312", inner: "#f7efdf", text2: "#5a4d36", light: "#fbf7ec" },
  water: { bg: "#d3dfec", vig: "rgba(20,35,60,.26)", tint: "#3f72a8", wash: "#e2eaf4", mid: "#1d3d68", inner: "#e8eff7", text2: "#45495a", light: "#f8f9fb" },
};
for (const p of Object.values(PAL)) Object.assign(p, { ink: "#1d1712", line: "#1d1712", value: "#1d1712", title: "#1d1712", accent: p.mid,
  caption: "#3a2e24", plate: "#f6f1e8", plateOpacity: .62, plateBg: p.inner, knot: "#1d1712", knotOpacity: .6, vigStop: .52, medal: p.inner });
PAL.void = { bg: "#322838", vig: "rgba(0,0,0,.45)", vigStop: .5, ink: "#ece2cf", line: "#e8dcc6", tint: "#b583b1", wash: "#261d2a", mid: "#5e3459",
  inner: "#19141c", ring: "#9e6a9a", text2: "#c9bccb", value: "#efe6d6", title: "#f1e8d8", accent: "#dcb6d8", caption: "#c9bccb", light: "#33283a",
  plate: "#0e0b10", plateOpacity: 1, plateBg: "#0e0b10", plateRing: "#261e2b", knot: "#e8dcc6", knotOpacity: .26, medal: "#19141c" };
for (const p of Object.values(PAL)) { p.ring = p.ring || p.tint; p.plateRing = p.plateRing || p.bg; }

/* ---------- type: her three faces, served from this site so a shared image carries them ---------- */
const FACES = [
  ["Wyrd Fell", "/static/fonts/fell.woff", "normal"], ["Wyrd Fell", "/static/fonts/fell-italic.woff", "italic"],
  ["Wyrd Fell SC", "/static/fonts/fell-sc.woff", "normal"], ["Wyrd Fraktur", "/static/fonts/fraktur.woff", "normal"]];
const FAM = { fell: "'Wyrd Fell','IM Fell English',Georgia,serif", sc: "'Wyrd Fell SC','IM Fell English SC','Wyrd Fell',Georgia,serif",
  frak: "'Wyrd Fraktur','UnifrakturMaguntia','Old English Text MT',serif" };
/* each face's normal line height and ascent, as fractions of the size (from the fonts' own tables) */
const MET = { fell: { lh: 1.2686, asc: .9053 }, sc: { lh: 1.2686, asc: .9053 }, frak: { lh: 1.0352, asc: .7847 } };
let fontsP = null;
function loadFonts(){
  if (fontsP) return fontsP;
  if (!window.FontFace || !document.fonts) return (fontsP = Promise.resolve());
  fontsP = Promise.all(FACES.map(([fam, url, style]) => { const f = new FontFace(fam, `url(${url}) format("woff")`, { style }); document.fonts.add(f); return f.load().catch(() => null); })).then(() => {});
  return fontsP;
}
const mctx = (() => { try { return document.createElement("canvas").getContext("2d"); } catch (_) { return null; } })();
/* a line of type: its width, so long words can shrink or wrap the way they would on the canvas */
function width(t, f, size, italic = false, ls = 0){
  const n = String(t).length;
  if (!mctx) return n * size * (f === "frak" ? .5 : .46) + n * ls;
  mctx.font = `${italic ? "italic " : ""}${size}px ${FAM[f]}`;
  return mctx.measureText(t).width + n * ls;
}
const box = l => l.lh ? l.lh * l.size : MET[l.f].lh * l.size;
const baseOf = (l, top) => top + (box(l) - MET[l.f].lh * l.size) / 2 + MET[l.f].asc * l.size;
function textEl(l, x, top, anchor = "middle"){
  const ls = l.ls || 0, shift = anchor === "middle" ? ls / 2 : 0;
  return `<text x="${(x + shift).toFixed(1)}" y="${baseOf(l, top).toFixed(1)}" font-family="${FAM[l.f]}" font-size="${l.size}"${l.italic ? ' font-style="italic"' : ""}${ls ? ` letter-spacing="${ls}"` : ""} fill="${l.color}" text-anchor="${anchor}">${esc(l.t)}</text>`;
}
/* words that run past a column: first a little smaller, then onto a second line */
function fit(l, maxW){
  if (width(l.t, l.f, l.size, l.italic, l.ls) <= maxW) return [l];
  const small = { ...l, size: +(l.size * .88).toFixed(1) };
  if (width(small.t, small.f, small.size, small.italic, small.ls) <= maxW) return [small];
  const words = String(l.t).split(" "), out = []; let cur = "";
  for (const w of words){ const tryT = cur ? cur + " " + w : w; if (cur && width(tryT, l.f, l.size, l.italic, l.ls) > maxW){ out.push(cur); cur = w; } else cur = tryT; }
  if (cur) out.push(cur);
  return out.map(t => ({ ...l, t }));
}

/* ---------- the mandala's data ---------- */
let M = null, readyP = null;
function loadScript(src){ return new Promise(res => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = res; document.head.appendChild(s); }); }
function ready(){
  if (readyP) return readyP;
  const mandala = (window.WyrdTarot ? WyrdTarot.load() : fetch("/static/mandala.json").then(r => r.json())).then(j => { M = j; });
  const plates = window.WYRD_PLATES ? Promise.resolve() : loadScript("/static/deck/plates.js?v=1");
  readyP = Promise.all([mandala, plates, loadFonts()]).then(() => { if (!M || !M.decans) throw new Error("The deck couldn't load."); return api; });
  readyP.catch(() => { readyP = null; });
  return readyP;
}
const station = i => ({ i, n: i + 1, nak: M.padas[i].nak, pada: M.padas[i].pada, void: M.padas[i].void, sign: Math.floor(i / 9), q: i % 9 });
const stationsBetween = (a, b) => { const out = []; let i = Math.floor(norm(a) / (10 / 3)) % 108; const end = Math.floor((norm(b) - 1e-9) / (10 / 3)) % 108; for (;;){ out.push(i); if (i === end) break; i = (i + 1) % 108; } return out; };
const decanAt = lon => Math.floor(norm(lon) / 10) % 36;
const minorParts = m => { const x = /^(\d+) of (.+)$/.exec(m); return x ? { n: +x[1], suit: x[2] } : { n: 0, suit: m }; };
const voidsLine = (ids, L) => {
  const vs = ids.filter(i => M.padas[i].void);
  if (vs.length === 1) return L.accent(`${M.padas[vs[0]].void}'s void at ${ROMAN(vs[0] + 1)}`);
  if (vs.length > 1) return L.accent(`voids at ${vs.slice(0, -1).map(i => ROMAN(i + 1)).join(", ")} and ${ROMAN(vs[vs.length - 1] + 1)}`);
  return null;
};
/* "Ashwini iv · Bharani i, ii", or "Rohini i – iii" */
function padaList(ids){
  const by = [];
  for (const i of ids){ const s = station(i); const last = by[by.length - 1]; if (last && last.nak === s.nak) last.p.push(s.pada); else by.push({ nak: s.nak, p: [s.pada] }); }
  return by.map(g => `${g.nak} ${g.p.length >= 3 ? `${roman(g.p[0])} – ${roman(g.p[g.p.length - 1])}` : g.p.map(roman).join(", ")}`).join(" · ");
}

/* ---------- a card's words ---------- */
const cache = {};
const valid = id => { const m = /^([bnv])(\d+)$/.exec(id || ""); if (!m) return false; const k = +m[2];
  return m[1] === "v" ? k >= 1 && k <= 108 && [3, 6, 8].includes((k - 1) % 9) : k >= 0 && k < 36; };
function card(id){
  if (cache[id]) return cache[id];
  if (!valid(id)) return null;
  const kind = id[0], k = parseInt(id.slice(1), 10);
  const c = kind === "v" ? voidCard(k - 1) : minorCard(kind, k);
  const plate = window.WYRD_PLATES && WYRD_PLATES[id];
  if (plate){ c.engraved = true; c.plate = plate; c.label = plate.label; applyWords(c, plate.words); }
  return (cache[id] = c);
}
const COL_W = (W - 2 * PAD_X - 2 * (2 + 36)) / 3;
function lineKit(pal){
  return {
    label: t => ({ t, f: "sc", size: 22, ls: 4.4, color: pal.accent }),
    value: (t, size = 31) => ({ t, f: "fell", size, color: pal.value }),
    trump: t => ({ t, f: "frak", size: 38, lh: 1.1, color: pal.value, trump: true }),
    sub: t => ({ t, f: "fell", size: 21, italic: true, color: pal.text2 }),
    accent: t => ({ t, f: "fell", size: 21, italic: true, color: pal.accent }),
  };
}
function minorCard(kind, k){
  const d = M.decans[k], s = Math.floor(k / 3), j = k % 3, lo = 10 * j, hi = lo + 10;
  const fam = ELEMENT[s % 4], pal = PAL[fam], L = lineKit(pal);
  const deck = kind === "b" ? d.buddhist : d.nordic, mp = minorParts(deck.minor), runes = [RUNES[2 * s], RUNES[2 * s + 1]];
  const col1 = { label: "its decan", lines: [L.value(`${d.ruler} in ${SIGNS[s]}`), L.sub(`${lo}° to ${hi}° ${kind === "b" ? "sidereal" : "tropical"}`)] };
  const a = 30 * s + lo, b = a + 10;
  if (kind === "b"){
    for (const [p, x] of EX_SID) if (x >= a && x < b) col1.lines.push(L.accent(`${p === "Sun" || p === "Moon" ? "the " : ""}${p} exalted at ${x % 30}°`));
  } else {
    for (const [t, x] of EX_TROP) if (x >= a && x < b){ const long = `${t} stands at ${x % 30}°`; col1.lines.push(L.accent(width(long, "fell", 21, true) <= COL_W ? long : `${t} at ${x % 30}°`)); }
  }
  const col2 = { label: "its trump", lines: [L.trump(deck.trump), L.sub(runes.join(" · "))], runes };
  let col3;
  if (kind === "b"){
    const ids = [3 * k, 3 * k + 1, 3 * k + 2];
    if (k === 0) col3 = { label: "its stations", lines: [L.value(`I – III · ${station(0).nak}`), L.accent("the Fool stands at its gate")] };
    else col3 = { label: "its stations", lines: [L.value(`${ROMAN(ids[0] + 1)} – ${ROMAN(ids[2] + 1)}`), L.sub(padaList(ids)), voidsLine(ids, L)].filter(Boolean) };
  } else {
    const ids = stationsBetween(a - AY(), b - AY()), naks = [...new Set(ids.map(i => M.padas[i].nak))].join(" · ");
    const where = width(`${naks}, in 2026`, "fell", 21, true) <= COL_W ? `${naks}, in 2026` : naks;
    const crosses = ids.indexOf(107) >= 0 && ids.indexOf(0) > ids.indexOf(107);
    col3 = { label: "it lands on", lines: [L.value(`${ROMAN(ids[0] + 1)} – ${ROMAN(ids[ids.length - 1] + 1)}`), L.sub(where),
      crosses ? L.accent("it crosses the Fool's gate") : voidsLine(ids, L)].filter(Boolean) };
  }
  return { id: (kind === "b" ? "b" : "n") + pad2(k), kind, fam, pal, sign: s, decan: k, n: mp.n, suit: mp.suit, ruler: d.ruler,
    numeral: ROMAN(mp.n), title: deck.minor, trump: deck.trump, deck: kind === "b" ? "buddhist" : "nordic",
    cols: [col1, col2, col3], label: `${deck.minor}, ${kind === "b" ? "the Buddhist deck" : "the Nordic deck"}` };
}
function voidCard(i){
  const s = station(i), pal = PAL.void, L = lineKit(pal), mid = (i + .5) * 10 / 3;
  const b = M.decans[decanAt(mid)].buddhist.minor, n = M.decans[decanAt(mid + AY())].nordic.minor;
  const opp = station((i + 54) % 108), t1 = station((i + 36) % 108), t2 = station((i + 72) % 108);
  const col1 = { label: "its cards", lines: [L.value(b, 28), L.sub(`${n}, in 2026`)] };
  if (s.q === 8) col1.lines.push(L.accent(`it closes ${SIGNS[s.sign]}`));
  return { id: "v" + pad3(i + 1), kind: "v", fam: "void", pal, sign: s.sign, station: i, n: i + 1, numeral: ROMAN(i + 1), title: s.void,
    kicker: `asura void · the tunnel beneath ${s.nak.toLowerCase()}`, sub: `station ${roman(i + 1)} · the ${ORD[s.pada - 1]} pada · navamsa in ${SIGNS[i % 12]}`,
    cols: [col1, { label: "across the wheel", lines: [L.value(opp.void, 28), L.sub(`station ${ROMAN(opp.n)}`)] },
      { label: "in trine", lines: [L.value(t1.void, 25), L.value(t2.void, 25), L.sub(`stations ${ROMAN(t1.n)} · ${ROMAN(t2.n)}`)] }],
    label: `${s.void}, the Asura void of station ${ROMAN(i + 1)}` };
}
/* an engraved card prints the words approved with it on the canvas */
function applyWords(c, words){
  const face = words.filter(w => !/^(the moon in|the path of dharma|draw your own card|The Völva ·)/.test(w.t) && !/^(Signature|Crucible) · Gate/.test(w.t));
  const L = lineKit(c.pal), cols = [];
  let i = 0;
  if (c.kind === "v"){ i = 4; }                    // numeral, kicker, name, sub: generated the same way
  else {
    const t = face[1]; if (t && t.black) c.titleSize = t.size;
    i = 3;
  }
  for (; i < face.length; i++){
    const w = face[i];
    if (w.sc && w.size === 22){ cols.push({ label: w.t, lines: [] }); continue; }
    const col = cols[cols.length - 1]; if (!col) continue;
    if (w.black) col.lines.push(L.trump(w.t));
    else if (w.italic) col.lines.push(w.color && w.color.toLowerCase() === c.pal.accent.toLowerCase() ? L.accent(w.t) : L.sub(w.t));
    else col.lines.push(L.value(w.t, w.size || 31));
  }
  if (cols.length === 3){ cols.forEach((col, k) => { if (c.cols[k] && c.cols[k].runes) col.runes = c.cols[k].runes; }); c.cols = cols; }
}

/* ---------- a person's card: their Moon, and the Path of Dharma ---------- */
function forMoon(C){
  const sid = C.sid.Moon, trop = C.trop ? C.trop.Moon : sid + AY(), i = Math.floor(norm(sid) / (10 / 3)) % 108;
  const out = [{ id: "b" + pad2(decanAt(sid)), why: "where your Moon comes from: its decan on the sidereal ring" },
               { id: "n" + pad2(decanAt(trop)), why: "where your Moon lands: its decan on the tropical ring" }];
  if (M.padas[i].void) out.push({ id: "v" + pad3(i + 1), why: `the Asura void your Moon sits over, at station ${ROMAN(i + 1)}` });
  return out;
}
/* the cards at one of the Mandala's 108 stations (0-based): its Buddhist card, the Nordic card(s) where it lands, and its void */
function stationCards(i){
  const a = i * 10 / 3, b = a + 10 / 3, out = [{ id: "b" + pad2(decanAt(a + 1e-9)), why: "where it comes from" }];
  const n0 = decanAt(a + AY()), n1 = decanAt(b + AY() - 1e-9);
  out.push({ id: "n" + pad2(n0), why: "where it lands" });
  if (n1 !== n0) out.push({ id: "n" + pad2(n1), why: "where it lands" });
  if (M.padas[i].void) out.push({ id: "v" + pad3(i + 1), why: "its Asura void" });
  return out;
}
function person(C){
  const H = (window.Wyrd && Wyrd.helpers) || {}, NAK = H.NAKSHATRA, GN = H.GATE_NAME || {};
  const sid = C.sid.Moon, ni = Math.floor(norm(sid) / (360 / 27)), nk = NAK ? NAK[ni] : [M.padas[Math.floor(norm(sid) / (10 / 3))].nak, "", ""];
  /* the rune of the Moon: two runes to a whole-sign house, counted from the rising sign (as the Runes page does) */
  const cusp = Math.floor(norm(C.ascS != null ? C.ascS : C.sid.Sun) / 30) * 30, ri = Math.floor(norm(norm(sid) - cusp) / 15);
  const N = C.natal || {}, g = (side, b) => N[side] && N[side][b] ? N[side][b].gate : null;
  const gates = [["Signature", g("personality", "Sun")], ["Crucible", g("personality", "Earth")], ["Aura", g("design", "Sun")], ["Objective", g("design", "Earth")]];
  return { nak: nk[0], deity: nk[2] || "", rune: RUNES[ri], house: Math.floor(ri / 2) + 1, gates,
    caption: gates[0][1] ? `Signature · Gate ${gates[0][1]}${GN[gates[0][1]] ? " · " + GN[gates[0][1]] : ""}` : "" };
}

/* ---------- the plates for cards not yet engraved: pips of the suit ---------- */
const PIPS = {
  2: [[190, 100], [190, 260]], 3: [[190, 70], [190, 180], [190, 290]], 4: [[115, 95], [265, 95], [115, 265], [265, 265]],
  5: [[110, 85], [270, 85], [190, 180], [110, 275], [270, 275]], 6: [[115, 70], [265, 70], [115, 180], [265, 180], [115, 290], [265, 290]],
  7: [[115, 70], [265, 70], [190, 125], [115, 180], [265, 180], [115, 290], [265, 290]],
  8: [[115, 70], [265, 70], [190, 125], [115, 180], [265, 180], [190, 235], [115, 290], [265, 290]],
  9: [[115, 58], [265, 58], [115, 138], [265, 138], [190, 180], [115, 222], [265, 222], [115, 302], [265, 302]],
  10: [[115, 58], [265, 58], [190, 98], [115, 138], [265, 138], [115, 222], [265, 222], [190, 262], [115, 302], [265, 302]] };
const PIP_SCALE = { 2: 1.45, 3: 1.15, 4: 1.2, 5: 1, 6: 1, 7: .86, 8: .86, 9: .72, 10: .72 };
function emblem(suit, p){
  const ink = (w, extra = "") => `stroke="${p.ink}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round" ${extra}`;
  const tint = `fill="${p.tint}"`, wash = `fill="${p.wash}"`, light = `fill="${p.light}"`, none = `fill="none"`;
  switch (suit){
    case "Double Vajras": {
      const arm = `<path d="M-5 -11C-10 -19 -8 -27 0 -35C8 -27 10 -19 5 -11Z" ${tint} ${ink(1.5)}/><path d="M0 -13V-31" ${none} ${ink(.8)}/><path d="M-6.5 -12H6.5" ${none} ${ink(1.5)}/>`;
      return `<circle r="41" ${wash} ${ink(1.5)}/><circle r="37" ${none} ${ink(.8)}/>${[0, 90, 180, 270].map(a => `<g transform="rotate(${a})">${arm}</g>`).join("")}
        ${[45, 135, 225, 315].map(a => `<circle cx="${(22 * Math.cos(a * Math.PI / 180)).toFixed(1)}" cy="${(22 * Math.sin(a * Math.PI / 180)).toFixed(1)}" r="2.2" fill="${p.ink}"/>`).join("")}
        <circle r="8.5" ${tint} ${ink(2.2)}/><circle r="3" fill="${p.ink}"/>`;
    }
    case "Jewels":
      return `${[0, 45, 90, 135, 180, 225, 270, 315].map(a => `<path d="M0 -34V-42" transform="rotate(${a})" ${none} ${ink(1.5)}/>`).join("")}
        <path d="M-27 -7L-15 -24H15L27 -7L0 31Z" ${tint} ${ink(2.2)}/>
        <path d="M-27 -7H27M-15 -24L-7 -7L0 31M15 -24L7 -7L0 31M-7 -7L0 -24L7 -7" ${none} ${ink(.8)}/>
        <path d="M-15 -24L-27 -7L-7 -7Z" fill="${p.light}" fill-opacity=".55"/>`;
    case "Vajras": {
      const half = s => `<g transform="scale(1 ${s})"><path d="M0 -11L3.4 -25L0 -40L-3.4 -25Z" ${tint} ${ink(1.5)}/>
        <path d="M-1 -12C-19 -16 -18 -32 -2 -39M1 -12C19 -16 18 -32 2 -39" ${none} ${ink(2.2)}/>
        <ellipse cy="-15.5" rx="7" ry="2.6" ${wash} ${ink(.8)}/><ellipse cy="-11" rx="10" ry="4" ${tint} ${ink(1.5)}/></g>`;
      return `<circle r="44" ${wash} ${ink(1.5)}/><circle r="40" ${none} ${ink(.8)}/>${half(1)}${half(-1)}<circle r="7.5" ${tint} ${ink(2.2)}/><circle r="2.6" fill="${p.ink}"/>`;
    }
    case "Lotuses": {
      const petal = (a, sc) => `<path d="M0 6C-10 -2 -10 -18 0 -30C10 -18 10 -2 0 6Z" transform="rotate(${a} 0 6) scale(${sc})" ${tint} ${ink(1.5)}/>`;
      return `<circle r="42" ${wash} ${ink(1.5)}/>${petal(-72, .78)}${petal(72, .78)}${petal(-38, .92)}${petal(38, .92)}${petal(0, 1)}
        <path d="M-34 14C-22 10 -10 18 0 14S22 10 34 14" ${none} ${ink(1.5)}/><path d="M-28 21C-18 18 -8 24 0 21S18 18 28 21" ${none} ${ink(.8)}/>`;
    }
    case "Wands":
      return `<path d="M0 -40C-8 -48 -3 -54 0 -60C3 -54 8 -48 0 -40Z" ${tint} ${ink(1.5)}/>
        <rect x="-5.5" y="-40" width="11" height="80" rx="3" ${light} ${ink(2.2)}/>
        ${[-26, -8, 10, 28].map(y => `<path d="M-5.5 ${y}H5.5" ${none} ${ink(.8)}/>`).join("")}
        <rect x="-7" y="-18" width="14" height="5" ${tint} ${ink(1.5)}/><rect x="-7" y="17" width="14" height="5" ${tint} ${ink(1.5)}/>`;
    case "Shields":
      return `<circle r="36" ${wash} ${ink(3.2)}/><path d="M-18 -31V31M0 -36V36M18 -31V31" ${none} ${ink(.8)}/>
        ${[0, 45, 90, 135, 180, 225, 270, 315].map(a => `<circle cx="${(30 * Math.cos(a * Math.PI / 180)).toFixed(1)}" cy="${(30 * Math.sin(a * Math.PI / 180)).toFixed(1)}" r="1.8" fill="${p.ink}"/>`).join("")}
        <circle r="10" ${tint} ${ink(2.2)}/><circle r="3.2" fill="${p.ink}"/>`;
    case "Swords":
      return `<path d="M-5 14L-5 -32L0 -43L5 -32L5 14Z" ${light} ${ink(1.5)}/><path d="M0 10V-32" ${none} ${ink(.8)}/>
        <rect x="-19" y="12" width="38" height="5.5" rx="1.5" ${tint} ${ink(1.5)}/><rect x="-3.2" y="17.5" width="6.4" height="15" ${tint} ${ink(1.5)}/>
        <path d="M-9 37C-9 31 9 31 9 37C9 41 -9 41 -9 37Z" ${tint} ${ink(1.5)}/>`;
    case "Cups":
      return `<path d="M-22 -22H22C22 0 10 8 0 8C-10 8 -22 0 -22 -22Z" ${tint} ${ink(2.2)}/><ellipse cy="-22" rx="22" ry="5" ${wash} ${ink(1.5)}/>
        <path d="M-14 -12C-8 -9 8 -9 14 -12" ${none} ${ink(.8)}/><path d="M-2.5 8V25M2.5 8V25" ${none} ${ink(1.5)}/>
        <ellipse cy="16" rx="5.5" ry="3" ${tint} ${ink(1.5)}/><path d="M-16 32C-12 25 12 25 16 32Z" ${wash} ${ink(1.5)}/>`;
  }
  return `<circle r="30" ${tint} ${ink(2.2)}/>`;
}
function plateBase(p, extra = ""){
  return `<defs><pattern id="@@sky" width="8" height="3.6" patternUnits="userSpaceOnUse"><line x1="0" y1="1.8" x2="8" y2="1.8" stroke="${p.ink}" stroke-width=".8"/></pattern>
    <radialGradient id="@@glowg" cx="190" cy="180" r="230" gradientUnits="userSpaceOnUse"><stop offset=".3" stop-color="#000"/><stop offset=".82" stop-color="#fff"/></radialGradient>
    <mask id="@@glow"><rect width="380" height="360" fill="url(#@@glowg)"/></mask>
    <filter id="@@etch" x="-4%" y="-4%" width="108%" height="108%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="11"/><feDisplacementMap in="SourceGraphic" scale="1.3"/></filter>${extra}</defs>
    <rect width="380" height="360" fill="${p.plate}" fill-opacity="${p.plateOpacity}"/><rect width="380" height="360" fill="url(#@@sky)" mask="url(#@@glow)"/>`;
}
function pipPlate(c){
  const p = c.pal, spots = PIPS[c.n] || [[190, 180]], sc = PIP_SCALE[c.n] || 1;
  return `${plateBase(p)}<g filter="url(#@@etch)">${spots.map(([x, y]) => `<g transform="translate(${x} ${y}) scale(${sc})">${emblem(c.suit, p)}</g>`).join("")}</g>`;
}
function voidPlate(c){
  const p = c.pal;
  const rings = Array.from({ length: 9 }, (_, k) => { const t = k / 8, rx = 150 - 136 * t, ry = 112 - 102 * t, cy = 196 - 30 * t;
    return `<ellipse cx="190" cy="${cy.toFixed(1)}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" fill="${k === 8 ? p.plate : "none"}" stroke="${p.ink}" stroke-width="${k < 2 ? 2.2 : k < 5 ? 1.5 : .8}"/>`; }).join("");
  const stars = [[48, 40], [92, 26], [300, 34], [336, 70], [262, 18], [40, 96]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.6" fill="${p.ink}"/>`).join("");
  return `${plateBase(p, `<pattern id="@@hd" width="3.6" height="3.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><line x1="0" y1="0" x2="0" y2="3.6" stroke="${p.ink}" stroke-width=".8"/></pattern>`)}
    <g filter="url(#@@etch)">${stars}<ellipse cx="190" cy="196" rx="150" ry="112" fill="url(#@@hd)" opacity=".55"/>${rings}
    <path d="M0 322C40 316 80 326 120 320S200 314 240 321S320 326 380 320" fill="none" stroke="${p.ink}" stroke-width="1.5"/>
    <path d="M10 334C44 330 80 338 118 333S196 329 228 334S306 339 346 333M0 348C36 344 72 352 112 347S190 342 222 348S300 353 340 347" fill="none" stroke="${p.tint}" stroke-width="1.5" stroke-dasharray="14 6 3 6"/></g>`;
}

/* ---------- laying a card out ---------- */
let uidN = 0;
function blocks(c, person, face){
  const p = c.pal, L = lineKit(p), out = [];
  /* the head: numeral, then the plate in its frame */
  const numeral = { t: c.numeral, f: "sc", size: 46, ls: 14.72, color: p.accent };
  out.push({ h: box(numeral) + 14 + 628, draw: top => {
    const fy = top + box(numeral) + 14, plate = c.engraved ? c.plate.svg : c.kind === "v" ? voidPlate(c) : pipPlate(c);
    return textEl(numeral, W / 2, top)
      + `<rect x="${200}" y="${(fy - 9).toFixed(1)}" width="680" height="646" fill="${p.line}"/>`
      + `<rect x="${202}" y="${(fy - 7).toFixed(1)}" width="676" height="642" fill="${p.plateRing}"/>`
      + `<rect x="209" y="${fy.toFixed(1)}" width="662" height="628" fill="${p.line}"/>`
      + `<rect x="212" y="${(fy + 3).toFixed(1)}" width="656" height="622" fill="${p.plateBg}"/>`
      + `<svg x="220" y="${(fy + 11).toFixed(1)}" width="640" height="606" viewBox="0 0 380 360" overflow="hidden">${plate}</svg>`;
  } });
  /* the name */
  if (c.kind === "v"){
    const kick = { t: c.kicker, f: "sc", size: 25, ls: 6.5, color: p.accent };
    const name = { t: c.title, f: "frak", size: 112, lh: 1.02, color: p.title };
    while (width(name.t, "frak", name.size) > 860 && name.size > 60) name.size -= 4;
    const sub = { t: c.sub, f: "fell", size: 30, italic: true, color: p.text2 };
    out.push({ h: box(kick) + 4 + box(name) + 4 + box(sub), draw: top => textEl(kick, W / 2, top) + textEl(name, W / 2, top + box(kick) + 4) + textEl(sub, W / 2, top + box(kick) + 4 + box(name) + 4) });
  } else {
    let size = c.titleSize || 96; while (width(c.title, "frak", size) > 820 && size > 56) size -= 2;
    const t = { t: c.title, f: "frak", size, lh: size <= 88 ? 1.06 : 1.04, color: p.title };
    const deckH = MET.fell.lh * 27;
    out.push({ h: box(t) + 6 + deckH, draw: top => {
      const by = top + box(t) + 6 + MET.fell.asc * 27, a = `the ${c.deck} deck · `, b = c.deck === "buddhist" ? "where it comes from" : "where it lands";
      const wa = width(a, "sc", 25, false, 5), wb = width(b, "fell", 27, true), x0 = W / 2 - (wa + wb) / 2;
      return textEl(t, W / 2, top) + `<text x="${x0.toFixed(1)}" y="${by.toFixed(1)}" text-anchor="start"><tspan font-family="${FAM.sc}" font-size="25" letter-spacing="5" fill="${p.accent}">${esc(a)}</tspan><tspan font-family="${FAM.fell}" font-size="27" font-style="italic" fill="${p.text2}">${esc(b)}</tspan></text>`;
    } });
  }
  /* the three facts */
  const cols = c.cols.map(col => { const lab = L.label(col.label), lines = [].concat(...col.lines.map(l => l.trump ? [l] : fit(l, COL_W)));
    return { col, lab, lines, h: box(lab) + lines.reduce((s, l) => s + 4 + box(l), 0) }; });
  const rowH = Math.max(...cols.map(c => c.h));
  out.push({ h: rowH, draw: top => cols.map((cc, k) => {
    const cx = PAD_X + COL_W / 2 + k * (COL_W + 38); let y = top, o = textEl(cc.lab, cx, y); y += box(cc.lab);
    for (const l of cc.lines){
      y += 4;
      if (l.trump && cc.col.runes){
        const w = width(l.t, "frak", l.size), gy = y + (box(l) - 32) / 2;
        o += cc.col.runes.map((r, i) => `<svg x="${(i ? cx + w / 2 + 12 : cx - w / 2 - 28).toFixed(1)}" y="${gy.toFixed(1)}" width="16" height="32" viewBox="0 0 40 80"><path d="${RUNE_PATH[r]}" fill="none" stroke="${p.ink === "#ece2cf" ? p.value : "#1d1712"}" stroke-width="5" stroke-linecap="square"/></svg>`).join("");
      }
      o += textEl(l, cx, y); y += box(l);
    }
    return o;
  }).join("") + [0, 1].map(k => `<rect x="${(PAD_X + COL_W + 18 + k * (COL_W + 38)).toFixed(1)}" y="${(top + 4).toFixed(1)}" width="2" height="${(rowH - 8).toFixed(1)}" fill="${p.line}" opacity="${c.kind === "v" ? .5 : .6}"/>`).join("") });
  if (face) return out;
  /* the person: their Moon, then the Path of Dharma */
  const P = person || {};
  const moonL = { t: `the moon in ${(P.nak || "").toLowerCase()}`, f: "sc", size: 27, ls: 6.48, color: p.accent };
  out.push({ h: box(moonL) + 14 + 210, draw: top => textEl(moonL, W / 2, top) + medallions(c, P, top + box(moonL) + 14) });
  const pathL = { t: "the path of dharma", f: "sc", size: 30, ls: 7.2, color: p.accent }, cap = { t: P.caption || "", f: "fell", size: 33, italic: true, color: p.caption };
  out.push({ h: box(pathL) + 6 + 150 + 6 + box(cap), draw: top => textEl(pathL, W / 2, top) + pathStrip(c, P, top + box(pathL) + 6) + (cap.t ? textEl(cap, W / 2, top + box(pathL) + 162) : "") });
  const f1 = { t: "The Völva · Web of Wyrd", f: "frak", size: 46, lh: 1.1, color: p.title }, f2 = { t: "draw your own card at wyrdconsole.com", f: "sc", size: 24, ls: 4.8, color: p.accent };
  out.push({ h: box(f1) + 4 + box(f2), draw: top => textEl(f1, W / 2, top) + textEl(f2, W / 2, top + box(f1) + 4) });
  return out;
}
function medallions(c, P, top){
  const p = c.pal, ring = (x, inner) => `<svg x="${x}" y="${top.toFixed(1)}" width="210" height="210" viewBox="0 0 240 240">
    <defs><path id="@@t${x}" d="M32 120A88 88 0 0 1 208 120"/><path id="@@b${x}" d="M21 120A99 99 0 0 0 219 120"/></defs>
    <circle cx="120" cy="120" r="114" fill="none" stroke="${p.ink}" stroke-width="3.2"/>
    <circle cx="120" cy="120" r="108" fill="none" stroke="${p.ink}" stroke-width="3.5" stroke-dasharray=".1 6.6" stroke-linecap="round"/>
    <circle cx="120" cy="120" r="76" fill="none" stroke="${p.ink}" stroke-width="1.5"/><circle cx="120" cy="120" r="70" fill="none" stroke="${p.ink}" stroke-width=".8"/>${inner(x)}</svg>`;
  const arc = (x, which, t, size, ls) => `<text font-family="${FAM.sc}" font-size="${size}" letter-spacing="${ls}" fill="${p.accent}" text-anchor="middle"><textPath href="#@@${which}${x}" startOffset="50%">${esc(t)}</textPath></text>`;
  const deity = String(P.deity || "").replace(/^the /i, ""), words = deity.split(" "), two = words.length > 1;
  const star = two ? "M120 70L122.6 80.4L133 83L122.6 85.6L120 96L117.4 85.6L107 83L117.4 80.4Z" : "M120 76L123.5 90L137 93.5L123.5 97L120 111L116.5 97L103 93.5L116.5 90Z";
  let dsize = two ? 30 : 40; while ((two ? Math.max(...[words.slice(0, -1).join(" "), words[words.length - 1]].map(w => width(w, "fell", dsize, true))) : width(deity, "fell", dsize, true)) > 128 && dsize > 18) dsize -= 1;
  const dText = two ? `<text font-family="${FAM.fell}" font-size="${dsize}" font-style="italic" fill="${p.value}" text-anchor="middle"><tspan x="120" y="130">${esc(words.slice(0, -1).join(" "))}</tspan><tspan x="120" y="162">${esc(words[words.length - 1])}</tspan></text>`
    : `<text x="120" y="152" font-family="${FAM.fell}" font-size="${dsize}" font-style="italic" fill="${p.value}" text-anchor="middle">${esc(deity)}</text>`;
  const r = P.rune || "Fehu", [x0, x1] = runeBox(r), tx = 120 - 1.4 * (x0 + x1) / 2;
  const runeG = `<g transform="translate(${tx.toFixed(1)} 64) scale(1.4)"><path d="${RUNE_PATH[r]}" transform="translate(2 1.4)" fill="none" stroke="${p.tint}" stroke-width="4" stroke-linecap="square"/><path d="${RUNE_PATH[r]}" fill="none" stroke="${p.ink}" stroke-width="3.6" stroke-linecap="square"/></g>`;
  return ring(282, x => arc(x, "t", "the deity", 19, 5) + arc(x, "b", "of the mansion", 16, 3) + `<path d="${star}" fill="${p.tint}" stroke="${p.ink}" stroke-width="1.5" stroke-linejoin="round"/>` + dText)
    + ring(588, x => arc(x, "t", "rune of the moon", 19, 4) + arc(x, "b", `${r.toLowerCase()} · house ${roman(P.house || 1)}`, 16, 3) + runeG);
}
function pathStrip(c, P, top){
  const p = c.pal, g = (P.gates || []).map(x => x[1] == null ? "" : x[1]);
  const ink = w => `stroke="${p.ink}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
  return `<svg x="110" y="${top.toFixed(1)}" width="860" height="150" viewBox="0 0 860 150">
    <path d="M24 66C120 56 200 76 300 66S480 56 560 66S740 76 836 66" fill="none" ${ink(1.5)}/><path d="M24 70C120 60 200 80 300 70S480 60 560 70S740 80 836 70" fill="none" ${ink(.8)}/>
    <text font-family="${FAM.fell}" font-size="17" font-style="italic" fill="${p.caption}" text-anchor="middle"><tspan x="70" y="22">Signature</tspan><tspan x="152" y="22">Crucible</tspan><tspan x="234" y="22">Aura</tspan><tspan x="316" y="22">Objective</tspan></text>
    <circle cx="70" cy="66" r="35" fill="none" stroke="${p.tint}" stroke-width="3"/>
    ${[[70, 29], [152, 26], [234, 26], [316, 26]].map(([x, r]) => `<circle cx="${x}" cy="66" r="${r}" fill="${p.mid}" ${ink(3.2)}/>`).join("")}
    <text font-family="${FAM.fell}" font-size="27" fill="#fbf6ea" text-anchor="middle">${[70, 152, 234, 316].map((x, i) => `<tspan x="${x}" y="75">${esc(g[i])}</tspan>`).join("")}</text>
    ${[430, 492, 554, 616, 708, 766].map(x => `<circle cx="${x}" cy="66" r="14" fill="${p.wash}" ${ink(1.5)}/><circle cx="${x}" cy="66" r="4" fill="${p.ink}"/>`).join("")}
    <path d="M826 46L844 66L826 86L808 66Z" fill="${p.wash}" ${ink(1.5)}/><path d="M826 59L832 66L826 73L820 66Z" fill="${p.ink}"/>
    <text font-family="${FAM.sc}" font-size="22" letter-spacing="3" fill="${p.accent}" text-anchor="middle"><tspan x="193" y="132">mission</tspan><tspan x="523" y="132">illuminations</tspan><tspan x="766" y="132">the diamond</tspan></text></svg>`;
}

/* ---------- the whole card ---------- */
function geometry(c, person, face){
  const bl = blocks(c, person, face), sum = bl.reduce((s, b) => s + b.h, 0);
  if (face){ const g = c.kind === "v" ? 28 : 45, H = Math.round(TOP + sum + g * (bl.length - 1) + BOTTOM + 30); return { bl, H, g }; }
  return { bl, H: STORY_H, g: (STORY_H - TOP - BOTTOM - sum) / (bl.length - 1) };
}
function frame(p, H){
  return `<rect x="36.5" y="36.5" width="1007" height="${H - 73}" rx="19.5" fill="none" stroke="${p.line}" stroke-width="5"/>
    <rect x="46.5" y="46.5" width="987" height="${H - 93}" rx="9.5" fill="none" stroke="${p.inner}" stroke-width="15"/>
    <rect x="55.5" y="55.5" width="969" height="${H - 111}" rx="1" fill="none" stroke="${p.line}" stroke-width="3"/>
    <rect x="61" y="61" width="958" height="${H - 122}" fill="none" stroke="${p.ring}" stroke-width="8"/>`;
}
const KNOT = { tr: ["/static/look/knot-tr.png", 388, 374], bl: ["/static/look/knot-bl.png", 387, 381] };
const knotBox = (which, H) => { const [, w, h] = KNOT[which], s = Math.min(380 / w, 370 / h); return which === "tr" ? [W - 30 - 380, 30, w * s, h * s] : [30, H - 30 - 370, w * s, h * s]; };
function background(u, p, H, images){
  const py = ((H - 640) / 2) % 640;
  return `<defs><pattern id="${u}paper" patternUnits="userSpaceOnUse" x="220" y="${py}" width="640" height="640"><image href="${images.paper}" width="640" height="640"/></pattern>
    <radialGradient id="${u}vig" cx=".5" cy=".42" r="1" gradientTransform="translate(.5 .42) scale(1.15 .85) translate(-.5 -.42)"><stop offset="${p.vigStop}" stop-color="${p.vig}" stop-opacity="0"/><stop offset="1" stop-color="${p.vig}"/></radialGradient>
    <filter id="${u}knot"><feFlood flood-color="${p.knot}"/><feComposite in2="SourceAlpha" operator="in"/></filter></defs>
    <rect width="${W}" height="${H}" fill="${p.bg}"/><rect width="${W}" height="${H}" fill="url(#${u}paper)" style="mix-blend-mode:multiply"/><rect width="${W}" height="${H}" fill="url(#${u}vig)"/>
    ${["tr", "bl"].map(k => { const [x, y, w, h] = knotBox(k, H); return `<image href="${images[k]}" x="${x}" y="${y}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" filter="url(#${u}knot)" opacity="${p.knotOpacity}"/>`; }).join("")}`;
}
const IMAGES = { paper: "/static/look/paper.jpg", tr: KNOT.tr[0], bl: KNOT.bl[0] };
function svg(id, { person = null, face = false, bg = true, fonts = "", title = "" } = {}){
  const c = card(id), p = c.pal, { bl, H, g } = geometry(c, person, face), u = `wd${++uidN}-`;
  let y = TOP, body = "";
  for (const b of bl){ body += b.draw(y); y += b.h + g; }
  const label = title || (person ? `${c.label}. The Moon in ${person.nak}, its deity ${person.deity}, its rune ${person.rune} in house ${ROMAN(person.house)}. ${person.caption}.` : c.label);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(label)}">${fonts ? `<style>${fonts}</style>` : ""}`
    + (bg ? background(u, p, H, typeof bg === "object" ? bg : IMAGES) : "") + frame(p, H) + body.replace(/@@/g, u) + `</svg>`;
}

/* ---------- the card as an image ---------- */
let fontCSS = null;
const toData = (buf, type) => { let s = ""; const b = new Uint8Array(buf); for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000)); return `data:${type};base64,${btoa(s)}`; };
function embedFonts(){
  if (fontCSS) return fontCSS;
  fontCSS = Promise.all(FACES.map(([fam, url, style]) => fetch(url).then(r => r.arrayBuffer()).then(b => `@font-face{font-family:'${fam}';font-style:${style};src:url(${toData(b, "font/woff")}) format('woff')}`).catch(() => "")))
    .then(a => a.join(""));
  return fontCSS;
}
const loadImg = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
async function png(id, opts = {}){
  await ready();
  const c = card(id), p = c.pal, fonts = await embedFonts();
  const markup = svg(id, { ...opts, bg: false, fonts }), H = +/viewBox="0 0 \d+ (\d+)"/.exec(markup)[1];
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H; const ctx = cv.getContext("2d");
  /* her paper, the vignette and the knotwork, laid down first */
  ctx.fillStyle = p.bg; ctx.fillRect(0, 0, W, H);
  try {
    const paper = await loadImg(IMAGES.paper), pat = ctx.createPattern(paper, "repeat");
    if (pat.setTransform) pat.setTransform(new DOMMatrix().translate(220, ((H - 640) / 2) % 640));
    ctx.globalCompositeOperation = "multiply"; ctx.fillStyle = pat; ctx.fillRect(0, 0, W, H); ctx.globalCompositeOperation = "source-over";
  } catch (_) {}
  ctx.save(); ctx.translate(W * .5, H * .42); ctx.scale(W * 1.15, H * .85);
  const gr = ctx.createRadialGradient(0, 0, 0, 0, 0, 1); gr.addColorStop(p.vigStop, "rgba(0,0,0,0)"); gr.addColorStop(1, p.vig);
  ctx.fillStyle = gr; ctx.fillRect(-1, -1, 2, 2); ctx.restore();
  for (const k of ["tr", "bl"]){
    try {
      const im = await loadImg(IMAGES[k]), [x, y, w, h] = knotBox(k, H), off = document.createElement("canvas"); off.width = Math.ceil(w); off.height = Math.ceil(h);
      const o = off.getContext("2d"); o.drawImage(im, 0, 0, w, h); o.globalCompositeOperation = "source-in"; o.fillStyle = p.knot; o.fillRect(0, 0, w, h);
      ctx.globalAlpha = p.knotOpacity; ctx.drawImage(off, x, y); ctx.globalAlpha = 1;
    } catch (_) {}
  }
  /* then the card itself */
  const url = URL.createObjectURL(new Blob([markup], { type: "image/svg+xml" }));
  try { const im = await loadImg(url); ctx.drawImage(im, 0, 0, W, H); } finally { URL.revokeObjectURL(url); }
  return new Promise((res, rej) => cv.toBlob(b => b ? res(b) : rej(new Error("The image couldn't be made.")), "image/png"));
}
function download(blob, name){
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 8000);
}
/* the phone's share sheet (Instagram stories, messages ...) where there is one; otherwise the image is saved */
async function share(blob, name, text){
  const file = window.File ? new File([blob], name, { type: "image/png" }) : null;
  if (file && navigator.canShare && navigator.canShare({ files: [file] })){
    try { await navigator.share({ files: [file], text }); return "shared"; }
    catch (e){ if (e && e.name === "AbortError") return "cancelled"; }
  }
  download(blob, name); return "saved";
}
const fileName = id => `wyrd-card-${card(id).title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`;
/* can this browser hand an image to the share sheet? */
const canShareFiles = () => { try { return !!(window.File && navigator.canShare && navigator.canShare({ files: [new File([new Blob(["x"])], "x.png", { type: "image/png" })] })); } catch (_) { return false; } };

/* ---------- the large view: any card, opened over the page ---------- */
let lb = null, lbBack = null;
function closeLB(){ if (!lb || lb.hidden) return; lb.hidden = true; lb.innerHTML = ""; document.documentElement.style.overflow = ""; if (lbBack && lbBack.focus) lbBack.focus(); }
function open(id, { person = null, links = [] } = {}){
  return ready().then(() => {
    const c = card(id); if (!c) return;
    if (!lb){
      lb = document.createElement("div"); lb.className = "wd-lb"; lb.hidden = true; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true");
      document.body.appendChild(lb);
      lb.addEventListener("click", e => { if (e.target === lb || e.target.closest("[data-lb=close]") || e.target.closest("a[href^='#']")) closeLB(); });
      document.addEventListener("keydown", e => { if (lb && !lb.hidden && e.key === "Escape") closeLB(); });
    }
    const face = !person, markup = svg(id, { person, face }), H = +/viewBox="0 0 \d+ (\d+)"/.exec(markup)[1];
    lbBack = document.activeElement;
    lb.style.setProperty("--arw", (1080 / H).toFixed(4));
    lb.setAttribute("aria-label", c.label);
    lb.innerHTML = `<button type="button" class="wd-lb-close wd-btn" data-lb="close" aria-label="Close">×</button><div class="wd-card">${markup}</div>
      <div class="wd-lb-bar"><button type="button" data-lb="save">Save the image</button>${links.map(l => `<a href="${esc(l.href)}">${esc(l.text)}</a>`).join("")}</div>
      <p class="wd-lb-note" aria-live="polite"></p>`;
    lb.hidden = false; document.documentElement.style.overflow = "hidden";
    lb.querySelector("[data-lb=close]").focus();
    let made = null;
    lb.querySelector("[data-lb=save]").addEventListener("click", async () => {
      const note = lb.querySelector(".wd-lb-note"); note.textContent = "Making the image…";
      try { const b = await (made = made || png(id, { person, face })); download(b, fileName(id)); note.textContent = "Saved."; }
      catch (_) { note.textContent = "The image couldn't be made in this browser."; }
    });
  });
}

/* the card as the rules alone would set it, before any approved words: used to check the rules against the engraved cards */
const rules = id => valid(id) ? (id[0] === "v" ? voidCard(parseInt(id.slice(1), 10) - 1) : minorCard(id[0], parseInt(id.slice(1), 10))) : null;
const api = { ready, card, rules, valid, forMoon, stationCards, person, svg, png, share, download, fileName, canShareFiles, open, close: closeLB, engraved: id => !!(window.WYRD_PLATES && WYRD_PLATES[id]),
  all: () => [...Array(36).keys()].flatMap(k => ["b" + pad2(k), "n" + pad2(k)]).concat([...Array(108).keys()].filter(i => i % 9 === 3 || i % 9 === 6 || i % 9 === 8).map(i => "v" + pad3(i + 1))),
  signOf: id => card(id).sign, SIGNS };
window.WyrdDeck = api;
})();
