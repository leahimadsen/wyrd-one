'use strict';
/* ============================================================
   RUNES
   The twenty-four runes drawn as strokes on a stave, so they can be
   bound: a bind rune is several runes sharing one upright.
   - WyrdRunes.mount(host, C): your rune stave. Every rune your planets
     and Ascendant light, ranked; a bind rune of all of them and of the
     strongest three; and how to make your own.
   - WyrdRunes.pairHTML(A, B): the binds two charts make together, for Compare.
   The words here are drafts for The Völva to edit.
   ============================================================ */
(() => {
const { norm, GLYPH } = Wyrd.helpers;
const { esc } = WyrdCommon;

/* the Elder Futhark in house order: two to a house, opening then closing */
const NAMES = ["Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz", "Gebo", "Wunjo",
  "Hagalaz", "Nauthiz", "Isa", "Jera", "Eihwaz", "Perthro", "Algiz", "Sowilo",
  "Tiwaz", "Berkano", "Ehwaz", "Mannaz", "Laguz", "Ingwaz", "Dagaz", "Othala"];
const GLYPHS = ["ᚠ","ᚢ","ᚦ","ᚨ","ᚱ","ᚲ","ᚷ","ᚹ","ᚺ","ᚾ","ᛁ","ᛃ","ᛇ","ᛈ","ᛉ","ᛊ","ᛏ","ᛒ","ᛖ","ᛗ","ᛚ","ᛜ","ᛞ","ᛟ"];
const MEANS = {
  Fehu: "moveable wealth, energy that must circulate", Uruz: "raw strength and health", Thurisaz: "the thorn that defends",
  Ansuz: "the god-voice, inspired speech", Raidho: "the road and right rhythm", Kenaz: "the torch of craft",
  Gebo: "the gift and the bond it makes", Wunjo: "joy and belonging", Hagalaz: "the hail that clears the field",
  Nauthiz: "need, the fire made by friction", Isa: "ice, stillness, focus", Jera: "the year's turning, the harvest",
  Eihwaz: "the yew, the axis through change", Perthro: "the lot-cup, fate and mystery", Algiz: "the elk, the sacred guard",
  Sowilo: "the sun, wholeness and victory", Tiwaz: "the oath kept at cost", Berkano: "the birch, birth and care",
  Ehwaz: "the horse, partnership in motion", Mannaz: "humankind, the self among others", Laguz: "water, flow, the unconscious",
  Ingwaz: "the seed, stored potential", Dagaz: "daybreak, breakthrough", Othala: "inheritance, the ancestral home" };

/* strokes on a box 1 wide and 2 tall; x = .5 is the shared stave */
const S = .5;
const GEOM = {
  Fehu:     [[S,0,S,2],[S,.7,.95,.25],[S,1.1,.95,.65]],
  Uruz:     [[.2,0,.2,2],[.2,0,.8,.55],[.8,.55,.8,2]],
  Thurisaz: [[S,0,S,2],[S,.6,.95,1],[.95,1,S,1.4]],
  Ansuz:    [[S,0,S,2],[S,.15,.95,.6],[S,.6,.95,1.05]],
  Raidho:   [[S,0,S,2],[S,0,.95,.45],[.95,.45,S,.9],[S,.9,.95,2]],
  Kenaz:    [[.85,.45,.25,1],[.25,1,.85,1.55]],
  Gebo:     [[.12,.35,.88,1.65],[.88,.35,.12,1.65]],
  Wunjo:    [[S,0,S,2],[S,0,.95,.45],[.95,.45,S,.9]],
  Hagalaz:  [[.2,0,.2,2],[.8,0,.8,2],[.2,.8,.8,1.2]],
  Nauthiz:  [[S,0,S,2],[.15,.75,.85,1.25]],
  Isa:      [[S,0,S,2]],
  Jera:     [[.45,.35,.12,.75],[.12,.75,.45,1.15],[.55,.85,.88,1.25],[.88,1.25,.55,1.65]],
  Eihwaz:   [[S,0,S,2],[S,0,.9,.35],[S,2,.1,1.65]],
  Perthro:  [[S,0,S,2],[S,.1,.9,.45],[.9,.45,.9,.1],[S,1.9,.9,1.55],[.9,1.55,.9,1.9]],
  Algiz:    [[S,0,S,2],[S,.85,.1,.25],[S,.85,.9,.25]],
  Sowilo:   [[.78,.1,.22,.85],[.22,.85,.78,1.15],[.78,1.15,.22,1.9]],
  Tiwaz:    [[S,0,S,2],[S,0,.1,.5],[S,0,.9,.5]],
  Berkano:  [[S,0,S,2],[S,0,.92,.5],[.92,.5,S,1],[S,1,.92,1.5],[.92,1.5,S,2]],
  Ehwaz:    [[.15,0,.15,2],[.85,0,.85,2],[.15,0,S,.45],[S,.45,.85,0]],
  Mannaz:   [[.15,0,.15,2],[.85,0,.85,2],[.15,0,.85,.8],[.85,0,.15,.8]],
  Laguz:    [[S,0,S,2],[S,0,.92,.5]],
  Ingwaz:   [[S,.6,.85,1],[.85,1,S,1.4],[S,1.4,.15,1],[.15,1,S,.6]],
  Dagaz:    [[.1,.4,.9,1.6],[.9,.4,.1,1.6],[.1,.4,.1,1.6],[.9,.4,.9,1.6]],
  Othala:   [[S,.15,.88,.7],[S,.15,.12,.7],[.88,.7,.15,1.75],[.12,.7,.85,1.75]],
};
const mirror = segs => segs.map(([a, b, c, d]) => [1 - a, b, 1 - c, d]);

/* one rune, or several bound on one stave. Alternate runes are mirrored so the
   branches spread to both sides, as bind-rune carvers do. */
function svg(names, { size = 120, title = "", cls = "", sameSide = false } = {}){
  const w = size * .62, h = size, pad = 8, sx = w - 2 * pad, sy = (h - 2 * pad) / 2;
  const lines = [];
  names.forEach((n, i) => {
    const g = i % 2 && !sameSide ? mirror(GEOM[n]) : GEOM[n];
    for (const [a, b, c, d] of g) lines.push(`<line x1="${(pad + a * sx).toFixed(1)}" y1="${(pad + b * sy).toFixed(1)}" x2="${(pad + c * sx).toFixed(1)}" y2="${(pad + d * sy).toFixed(1)}"/>`);
  });
  return `<svg class="rn-svg ${cls}" viewBox="0 0 ${w.toFixed(0)} ${h}" width="${w.toFixed(0)}" height="${h}" role="img" aria-label="${esc(title || names.join(" bound with "))}">
    <g stroke-linecap="round" stroke-linejoin="round">${[...new Set(lines)].join("")}</g></svg>`;
}

/* the rune a sidereal longitude stands in: two to a whole-sign house from the rising sign */
function runeAt(C, l){
  const cusp = Math.floor(norm(C.ascS) / 30) * 30, i = Math.floor(norm(norm(l) - cusp) / 15);
  return { name: NAMES[i], glyph: GLYPHS[i], house: Math.floor(i / 2) + 1, opening: i % 2 === 0 };
}

/* every rune the chart lights, strongest first */
function lit(C){
  const bodies = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
  const ak = C.karaka && C.karaka.Atmakaraka, cur = C.dashaTree && C.dashaTree.cur && C.dashaTree.cur.lord;
  const weight = b => (b === "Ascendant" ? 3 : 0) + (b === ak ? 3 : 0) + (b === "Sun" || b === "Moon" ? 2 : 0) + (b === cur ? 2 : 0) + 1;
  const by = {};
  for (const b of [...(C.unknownTime ? [] : ["Ascendant"]), ...bodies]){
    const l = b === "Ascendant" ? C.ascS : C.sid[b]; if (l == null) continue;
    const r = runeAt(C, l); (by[r.name] = by[r.name] || { ...r, holders: [], score: 0 });
    by[r.name].holders.push(b); by[r.name].score += weight(b);
  }
  return Object.values(by).sort((a, b) => b.score - a.score);
}

const CRAFT = [
  "Choose by intent first. A bind rune works best holding one purpose; pick the two or three runes whose meanings serve it, and leave the rest out.",
  "Share the stave. Stand the runes on a single upright so they become one sign, not a row of letters. Runes without an upright (Kenaz, Gebo, Jera, Sowilo, Ingwaz, Dagaz, Othala) sit across or around it.",
  "Mirror to balance. A rune may be turned to face the other way so its branches spread to both sides. Turning it does not reverse its meaning when it is bound.",
  "Keep it to three or four. Beyond that, the strokes start to form runes you did not choose. Look at the finished sign and name every rune you can see in it; if one appears that you would not invite, redraw.",
  "Read it back aloud. Say each rune's name as you trace its stroke. A bind rune is finished when you can find every rune in it and say why it is there.",
  "Make it by hand. Carve, burn, paint or draw it in one sitting, with the intent held. A printed sign is a map; the made one is the working.",
];

function mount(host, C){
  const L = lit(C), top = L.slice(0, 3).map(r => r.name), all = L.map(r => r.name);
  const row = r => `<li class="rn-row">${svg([r.name], { size: 64 })}<div><b>${r.glyph} ${r.name}</b> <span class="fine">house ${r.house}, ${r.opening ? "opening" : "closing"} rune</span>
    <p>${MEANS[r.name]}. Lit by ${r.holders.map(b => b === "Ascendant" ? "your Ascendant" : `${GLYPH[b] || ""} ${b}`).join(", ")}.</p></div></li>`;
  host.innerHTML = `
    <div class="rn-staves">
      <figure>${svg(top, { size: 220, title: "Your core bind rune" })}<figcaption><b>Your core bind rune</b><br>${top.map(n => `${GLYPHS[NAMES.indexOf(n)]} ${n}`).join(" · ")}<br><span class="fine">the three runes your chart lights most strongly</span></figcaption></figure>
      <figure>${svg(all, { size: 220, title: "Every rune your chart lights, bound" })}<figcaption><b>Your whole stave</b><br>all ${all.length} lit runes on one upright<br><span class="fine">a sigil of the chart, not a working rune</span></figcaption></figure>
    </div>
    <h3>Your lit runes, strongest first</h3>
    <p class="fine">A rune is lit when a planet or your Ascendant stands in it. It is strongest when it holds your Ascendant, your soul-planet, your Sun or Moon, or the lord of the period you are in.</p>
    <ul class="rn-list">${L.map(row).join("")}</ul>
    <h3>Making your own bind runes</h3>
    <ol class="rn-craft">${CRAFT.map(t => `<li>${t}</li>`).join("")}</ol>
    <p class="fine">To learn each rune in depth, see <a href="/learn/runes">Learn the runes</a>. Your full reading shows the years each lit rune wakes.</p>`;
}

/* ---------- two charts: the runes you bind together ---------- */
const PAIRINGS = [["Sun", "Sun", "your purposes"], ["Moon", "Moon", "your moods and needs"], ["Venus", "Mars", "attraction"], ["Mars", "Venus", "attraction, the other way"],
  ["Sun", "Moon", "will meeting feeling"], ["Moon", "Sun", "feeling meeting will"], ["Ascendant", "Ascendant", "how you meet the world together"]];
function pairHTML(A, B){
  const lon = (C, b) => b === "Ascendant" ? (C.unknownTime ? null : C.ascS) : C.sid[b];
  const binds = PAIRINGS.map(([p, q, what]) => {
    const la = lon(A.C, p), lb = lon(B.C, q); if (la == null || lb == null) return null;
    const ra = runeAt(A.C, la), rb = runeAt(B.C, lb);
    return { p, q, what, ra, rb };
  }).filter(Boolean);
  const la = new Set(lit(A.C).map(r => r.name)), lb = new Set(lit(B.C).map(r => r.name));
  const shared = [...la].filter(n => lb.has(n));
  const card = x => `<li class="rn-pair">${svg(x.ra.name === x.rb.name ? [x.ra.name] : [x.ra.name, x.rb.name], { size: 92 })}
    <div><b>${esc(A.name)}'s ${x.p} ${x.ra.glyph} ${x.ra.name} + ${esc(B.name)}'s ${x.q} ${x.rb.glyph} ${x.rb.name}</b>
    <p>${x.what}: ${MEANS[x.ra.name]}${x.ra.name === x.rb.name ? ", doubled: you meet here in the same rune" : `, bound with ${MEANS[x.rb.name]}`}.</p></div></li>`;
  return `<p>Each of you lights runes with your planets. Where your planets meet, their runes bind into one sign: the rune of that part of the bond.</p>
    <ul class="rn-list">${binds.map(card).join("")}</ul>
    ${shared.length ? `<p><b>Runes you both light:</b> ${shared.map(n => `${GLYPHS[NAMES.indexOf(n)]} ${n}`).join(", ")}. These are the bond's common ground.</p>
      <figure class="rn-shared">${svg(shared.slice(0, 4), { size: 160, title: "The bind rune of the runes you share" })}<figcaption>The bind rune of the runes you share${shared.length > 4 ? " (the first four)" : ""}</figcaption></figure>`
      : "<p>You light no rune in common: the bond is made where your different runes bind.</p>"}`;
}

window.WyrdRunes = { mount, pairHTML, svg, lit, runeAt, NAMES, GLYPHS, GEOM };
})();
