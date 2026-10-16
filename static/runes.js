'use strict';
/* ============================================================
   RUNES
   The twenty-four runes drawn as strokes on a stave, so they can be
   bound: a bind rune is several runes sharing one upright.
   - WyrdRunes.mount(host, C): your activated runes. The rune wheel with them
     lit on it, then every rune your planets and Ascendant light, ranked, and
     how each plays out through the lunar mansion of the planet that lights it.
   - WyrdRunes.pairHTML(A, B): the runes between two charts, for Compare.
   The words here are drafts for The Völva to edit.
   ============================================================ */
(() => {
const { norm, GLYPH, HOUSES } = Wyrd.helpers;
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

/* ---------- the rune wheel ----------
   The twenty-four runes in their ring, two to each house from the rising sign, oriented like every
   wheel in the console (house 1 opens at one o'clock, the houses run clockwise). A rune is lit when
   a planet or the Ascendant stands in it; the planets stand inside the ring at their degrees, and
   the three strongest runes carry their rank. Tap a lit rune to go to its reading below. */
const ONE = typeof HOUSE_ONE_ANGLE === "number" ? HOUSE_ONE_ANGLE : -60;
function wheel(C, L){
  const cx = 300, cy = 300, f = n => n.toFixed(1), rad = a => a * Math.PI / 180;
  const P = (r, a) => [cx + r * Math.cos(rad(a)), cy + r * Math.sin(rad(a))];
  const cell = (r0, r1, a0, a1) => { const [x0, y0] = P(r1, a0), [x1, y1] = P(r1, a1), [x2, y2] = P(r0, a1), [x3, y3] = P(r0, a0);
    return `M${f(x0)},${f(y0)}A${r1},${r1} 0 0 1 ${f(x1)},${f(y1)}L${f(x2)},${f(y2)}A${r0},${r0} 0 0 0 ${f(x3)},${f(y3)}Z`; };
  const cusp = Math.floor(norm(C.ascS) / 30) * 30, ang = l => ONE + norm(norm(l) - cusp);
  const rank = Object.fromEntries(L.slice(0, 3).map((r, i) => [r.name, i + 1])), on = Object.fromEntries(L.map(r => [r.name, r]));
  const HR = [252, 282], RR = [168, 246], PR = 146;
  let o = "";
  /* the houses, in their colours */
  for (let h = 0; h < 12; h++){
    const a0 = ONE + h * 30, [x, y] = P((HR[0] + HR[1]) / 2, a0 + 15);
    o += `<path d="${cell(HR[0], HR[1], a0, a0 + 30)}" class="rw-house" style="fill:${HOUSES[h].hex}"/>`
      + `<text x="${f(x)}" y="${f(y)}" class="rw-hn">${h + 1}</text>`;
  }
  /* the runes: drawn upright in their cells, lit ones in the house's colour */
  for (let i = 0; i < 24; i++){
    const n = NAMES[i], r = on[n], a0 = ONE + i * 15, [x, y] = P((RR[0] + RR[1]) / 2 + 4, a0 + 7.5), hex = HOUSES[Math.floor(i / 2)].hex;
    const g = GEOM[n].map(([p, q, s2, t]) => `<line x1="${f(x - 11 + p * 22)}" y1="${f(y - 20 + q * 20)}" x2="${f(x - 11 + s2 * 22)}" y2="${f(y - 20 + t * 20)}"/>`).join("");
    const tip = `${n} · house ${Math.floor(i / 2) + 1}, ${i % 2 ? "closing" : "opening"} · ${MEANS[n]}${r ? ` · lit by ${r.holders.map(b => b === "Ascendant" ? "your Ascendant" : `your ${b}`).join(", ")}` : ""}`;
    o += `<g class="rw-rune${r ? " lit" : ""}${rank[n] ? " top" : ""}"${r ? ` data-rune="${n}" tabindex="0" role="button" aria-label="${esc(tip)}"` : ""} style="--h:${hex}">
      <title>${esc(tip)}</title><path d="${cell(RR[0], RR[1], a0, a0 + 15)}" class="rw-cell"/><g class="rw-strokes">${g}</g>
      ${rank[n] ? (([rx, ry]) => `<circle cx="${f(rx)}" cy="${f(ry)}" r="8" class="rw-rank"/><text x="${f(rx)}" y="${f(ry)}" class="rw-rank-n">${rank[n]}</text>`)(P(RR[0] + 12, a0 + 7.5)) : ""}</g>`;
  }
  for (let i = 0; i < 24; i++){ const [x0, y0] = P(RR[0], ONE + i * 15), [x1, y1] = P(i % 2 ? RR[1] : HR[1], ONE + i * 15);
    o += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="${i % 2 ? "rw-div" : "rw-div house"}"/>`; }
  /* the planets inside the ring, at their degrees, stepped inward where they crowd */
  const bodies = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"].filter(b => C.sid[b] != null)
    .map(b => ({ b, a: ang(C.sid[b]) })).sort((p, q) => p.a - q.a), placed = [];
  for (const p of bodies){
    let r = PR; while (placed.some(x => x.r === r && Math.abs(((p.a - x.a + 540) % 360) - 180) < 9)) r -= 22;
    placed.push({ ...p, r });
    const [tx0, ty0] = P(RR[0] - 1, p.a), [tx1, ty1] = P(RR[0] - 9, p.a), [gx, gy] = P(r, p.a);
    o += `<line x1="${f(tx0)}" y1="${f(ty0)}" x2="${f(tx1)}" y2="${f(ty1)}" class="rw-tick"/><text x="${f(gx)}" y="${f(gy)}" class="rw-pl">${GLYPH[p.b] || p.b[0]}︎<title>${p.b}</title></text>`;
  }
  if (!C.unknownTime){
    const a = ang(C.ascS), [x0, y0] = P(46, a), [x1, y1] = P(HR[1] + 6, a), [lx, ly] = P(HR[1] + 18, a);
    o += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="rw-asc"/><text x="${f(lx)}" y="${f(ly)}" class="rw-asc-l">ASC</text>`;
  }
  o += `<circle cx="${cx}" cy="${cy}" r="44" class="rw-core"/><text x="${cx}" y="${cy - 8}" class="rw-count">${L.length}</text><text x="${cx}" y="${cy + 14}" class="rw-count-l">of 24 lit</text>`;
  return `<figure class="rw"><svg viewBox="-12 -12 624 624" role="group" aria-label="Your rune wheel: the twenty-four runes two to each house, ${L.length} of them lit by your planets${C.unknownTime ? "" : " and Ascendant"}">${o}</svg>
    <figcaption>The twenty-four runes, two to each house, counted from your ${C.unknownTime ? "Sun's sign (your birth time is unknown)" : "rising sign"}. A rune is lit where a planet${C.unknownTime ? "" : " or your Ascendant"} stands in it; the numbers mark your three strongest. Tap a lit rune to read it below.</figcaption></figure>`;
}

/* how a rune plays out through the mansion of the planet that lights it */
function through(C, r, b){
  const { NAKSHATRA, nakIndex } = Wyrd.helpers, L = C.lex || {};
  const l = b === "Ascendant" ? C.ascS : C.sid[b], ni = nakIndex(l), nk = NAKSHATRA[ni], q = (L.nak || [])[ni] || "";
  const R = (L.rune || {})[r.name] || {};
  const who = b === "Ascendant" ? "your Ascendant" : `your ${GLYPH[b] || ""} ${b}`;
  return `<li><b>Through ${who} in ${nk[0]}</b> <span class="fine">· ruled by ${nk[1]}, the ${nk[5].toLowerCase()}</span>
    <p>${q} Here ${r.name} works in that manner.${R.light ? ` At its best: ${R.light.charAt(0).toLowerCase() + R.light.slice(1)}` : ""}
    ${R.shadow ? ` When it goes wrong: ${R.shadow.charAt(0).toLowerCase() + R.shadow.slice(1)}` : ""}</p></li>`;
}

function mount(host, C, opts = {}){
  const L = lit(C), R = (C.lex || {}).rune || {}, all = !!opts.all;       /* members: every rune in full */
  const card = (r, i) => `<div class="rn-card${i < 3 ? " lead" : ""}" id="rn-${r.name}">
    <h3><span class="rn-g" aria-hidden="true">${r.glyph}</span> ${r.name} <span class="fine">· house ${r.house}, ${r.opening ? "opening" : "closing"} rune${i < 3 ? " · one of your three strongest" : ""}</span></h3>
    <p class="rn-means">${MEANS[r.name].charAt(0).toUpperCase() + MEANS[r.name].slice(1)}.</p>
    ${i === 0 || all ? `<ul class="rn-thru">${r.holders.map(b => through(C, r, b)).join("")}</ul>
    ${R[r.name] && R[r.name].call ? `<p class="rn-call">Its call: <em>${R[r.name].call}</em></p>` : ""}`
      : `<p class="fine">Lit by ${r.holders.map(b => b === "Ascendant" ? "your Ascendant" : `your ${GLYPH[b] || ""} ${b}`).join(", ")}. How it works through ${r.holders.length > 1 ? "their mansions" : "its mansion"} is in your reading.</p>`}</div>`;
  host.innerHTML = `
    <p>Twenty-four runes ring your chart, two to each house, counted from your rising sign. A rune is activated when a planet or your Ascendant stands in it.
    Each activated rune works through the lunar mansion of the planet that lights it, so the same rune reads differently in different charts. Strongest first:
    a rune is strongest when it holds your Ascendant, your soul-planet, your Sun or Moon, or the lord of the period you are in.</p>
    ${wheel(C, L)}
    ${L.map(card).join("")}
    <p class="fine">${all ? "In the Order, every rune is read in full here." : "Your strongest rune is read in full above, as a taste; the Order sees every one in full."} The Wyrd Reading reads every one of them through its mansion, ranks them, and names the years each one wakes. To learn the runes themselves, see <a href="/learn/runes">Learn the runes</a>.</p>`;
}

/* the wheel's lit runes go to their reading */
document.addEventListener("click", e => {
  const g = e.target.closest && e.target.closest(".rw-rune.lit"); if (!g) return;
  const c = document.getElementById("rn-" + g.dataset.rune); if (!c) return;
  c.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  c.classList.remove("rn-flash"); void c.offsetWidth; c.classList.add("rn-flash");
});
document.addEventListener("keydown", e => {
  if ((e.key === "Enter" || e.key === " ") && e.target.closest && e.target.closest(".rw-rune.lit")){ e.preventDefault(); e.target.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
});

/* ---------- two charts: the runes between you ---------- */
function pairHTML(A, B){
  const la = lit(A.C), lb = lit(B.C), nb = new Set(lb.map(r => r.name));
  const shared = la.filter(r => nb.has(r.name));
  const top = (P, L) => `<li><b>${esc(P.name)}</b>: ${L.slice(0, 3).map(r => `${r.glyph} ${r.name} (${MEANS[r.name]})`).join("; ")}</li>`;
  return `<ul class="kar-plain">${top(A, la)}${top(B, lb)}</ul>
    ${shared.length ? `<p><b>Runes you both activate:</b> ${shared.map(r => `${r.glyph} ${r.name}`).join(", ")}. This is the bond's common ground: where you recognise each other without explaining.</p>`
      : `<p>You activate no rune in common: each of you brings the other a force they do not carry.</p>`}`;
}

window.WyrdRunes = { mount, pairHTML, svg, wheel, lit, runeAt, NAMES, GLYPHS, GEOM };
})();
