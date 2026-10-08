'use strict';
/* ============================================================
   THE WHEEL
   The natal chart as one drawing, outside in:
     tropical signs · sidereal signs · the 24 runes (two to a house)
     · the 64 gates (personality and design lit) · the 27 mansions
     · the twelve houses in their colours · the bodies
   and at the centre the Pentagram Cross of the two Dharma Suns.
   Oriented like every wheel in the console: house 1 opens at one
   o'clock and the houses run clockwise (HOUSE_ONE_ANGLE, viz.js).
   Also works out the rave summary (type, authority, definition)
   from the gates, using the centres and channels in body.js.
   Data only: what the placements mean stays in the paid reading.
   ============================================================ */
(() => {
const NAK_SHORT = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha",
  "Magha","P.Phalguni","U.Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
  "P.Ashadha","U.Ashadha","Shravana","Dhanishta","Shatabhisha","P.Bhadra","U.Bhadra","Revati"];
const ABBR = SIGNS.map(s => s.slice(0, 3).toUpperCase());
const SG = SIGN_GLYPH.map(g => g + "︎");            /* text glyphs, not emoji */
const RAVE_BODIES = ["Sun","Earth","Moon","Rahu","Ketu","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"];
const WHEEL_BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
const f = n => n.toFixed(1);
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };

/* ---------- geometry ---------- */
let C = null;
const cusp = () => Math.floor(norm(C.ascS) / 30) * 30;
const aSid = l => HOUSE_ONE_ANGLE + norm(norm(l) - cusp());
const aTrop = l => aSid(norm(l - C.ay));
const P = (r, a) => [500 + r * Math.cos(a * Math.PI / 180), 500 + r * Math.sin(a * Math.PI / 180)];
function cell(r0, r1, a0, a1){
  const [x0, y0] = P(r1, a0), [x1, y1] = P(r1, a1), [x2, y2] = P(r0, a1), [x3, y3] = P(r0, a0), big = a1 - a0 > 180 ? 1 : 0;
  return `M${f(x0)},${f(y0)} A${r1},${r1} 0 ${big} 1 ${f(x1)},${f(y1)} L${f(x2)},${f(y2)} A${r0},${r0} 0 ${big} 0 ${f(x3)},${f(y3)} Z`;
}
function label(r, a, text, cls, rotate){
  const [x, y] = P(r, a);
  let rot = "";
  if (rotate){ let t = a + 90; if (norm(t) > 90 && norm(t) < 270) t += 180; rot = ` transform="rotate(${f(t)} ${f(x)} ${f(y)})"`; }
  return `<text x="${f(x)}" y="${f(y)}" class="${cls}"${rot}>${text}</text>`;
}
/* push labels apart so none sit on top of each other */
function spread(items, gap){
  const s = items.slice().sort((a, b) => a.a - b.a);
  s.forEach(i => i.at = i.a);
  for (let pass = 0; pass < 6; pass++)
    for (let i = 0; i < s.length; i++){
      const p = s[(i + s.length - 1) % s.length], q = s[i];
      let d = q.at - p.at; if (i === 0) d += 360;
      if (d < gap){ p.at -= (gap - d) / 2; q.at += (gap - d) / 2; }
    }
  return s;
}

/* ---------- the rave summary, worked out from the gates ---------- */
function rave(chart){
  const { centres, channels } = window.WyrdBody;
  const centreOf = {}; for (const k in centres) for (const g of centres[k].gates) centreOf[g] = k;
  const gates = new Set([chart.natal.personality, chart.natal.design].flatMap(c => Object.values(c).map(v => v.gate)));
  const live = channels.filter(([a, b]) => gates.has(a) && gates.has(b));
  const def = new Set(live.flatMap(([a, b]) => [centreOf[a], centreOf[b]]));
  const adj = {}; for (const [a, b] of live){ const x = centreOf[a], y = centreOf[b]; (adj[x] ||= new Set()).add(y); (adj[y] ||= new Set()).add(x); }
  const reach = (from, to) => { const seen = new Set([from]), q = [from];
    while (q.length){ const c = q.shift(); if (c === to) return true; for (const n of adj[c] || []) if (!seen.has(n)){ seen.add(n); q.push(n); } }
    return false; };
  const motorToThroat = ["heart","solar","sacral","root"].some(m => def.has(m) && reach(m, "throat"));
  let type;
  if (!def.size) type = "Reflector";
  else if (def.has("sacral")) type = motorToThroat ? "Manifesting Generator" : "Generator";
  else type = motorToThroat ? "Manifestor" : "Projector";
  const authority = !def.size ? "Lunar" : def.has("solar") ? "Emotional" : def.has("sacral") ? "Sacral"
    : def.has("spleen") ? "Splenic" : def.has("heart") ? (reach("heart", "throat") ? "Ego manifested" : "Ego projected")
    : def.has("g") && reach("g", "throat") ? "Self-projected" : "Mental (none)";
  /* definition: how many separate islands the defined centres make */
  const seen = new Set(); let islands = 0;
  for (const c of def) if (!seen.has(c)){ islands++; const q = [c]; seen.add(c);
    while (q.length){ for (const n of adj[q.shift()] || []) if (!seen.has(n)){ seen.add(n); q.push(n); } } }
  const definition = ["No definition","Single","Split","Triple split","Quadruple split"][islands] || `${islands}-way split`;
  const strategy = { "Generator":"To respond", "Manifesting Generator":"To respond, then inform", "Manifestor":"To inform",
    "Projector":"To wait for the invitation", "Reflector":"To wait a lunar cycle" }[type];
  const P_ = chart.natal.personality, D_ = chart.natal.design;
  return { type, strategy, authority, definition, profile: chart.natal.profile,
    cross: `${P_.Sun.gate}/${P_.Earth.gate} | ${D_.Sun.gate}/${D_.Earth.gate}`,
    centres: Object.keys(centres).filter(k => def.has(k)).map(k => centres[k].label),
    open: Object.keys(centres).filter(k => !def.has(k)).map(k => centres[k].label),
    channels: live.map(([a, b]) => `${a}–${b}`) };
}

/* the rune a sidereal longitude stands in: two per whole-sign house */
function runeAt(l){
  const into = norm(norm(l) - cusp()), h = Math.floor(into / 30);
  const r = HOUSES[h][into % 30 < 15 ? "ingress" : "egress"];
  return { glyph: r[0], name: r[1], house: h + 1 };
}

/* ---------- drawing ---------- */
function svg(chart, opt = {}){
  C = chart;
  const full = !opt.compact;
  const R = full
    ? { tro: [452, 492], sid: [420, 452], run: [382, 420], gat: [348, 382], nak: [320, 348], hou: [288, 320], pl: 262, deg: 236, des: 196, core: 128 }
    : { tro: [440, 492], sid: null, run: [384, 440], gat: null, nak: null, hou: [338, 384], pl: 290, deg: 0, des: 0, core: 190 };
  let o = `<defs><radialGradient id="wGlow"><stop offset="0" stop-color="rgba(120,100,220,.16)"/><stop offset="1" stop-color="rgba(0,0,0,0)"/></radialGradient></defs>
    <circle cx="500" cy="500" r="${R.tro[1]}" class="wh-back"/>`;

  /* tropical signs: glyph medallions */
  for (let i = 0; i < 12; i++){
    const a0 = aTrop(i * 30);
    o += `<path d="${cell(R.tro[0], R.tro[1], a0, a0 + 30)}" class="wh-cell wh-tro${i % 2 ? " alt" : ""}"/>`;
    const [x, y] = P((R.tro[0] + R.tro[1]) / 2, a0 + 15), s = full ? 26 : 40;
    o += `<rect x="${f(x - s / 2)}" y="${f(y - s / 2)}" width="${s}" height="${s}" rx="5" class="wh-badge"/>${label((R.tro[0] + R.tro[1]) / 2, a0 + 15, SG[i], "wh-badge-g")}`;
  }
  /* sidereal signs */
  if (R.sid) for (let i = 0; i < 12; i++){
    const a0 = aSid(i * 30);
    o += `<path d="${cell(R.sid[0], R.sid[1], a0, a0 + 30)}" class="wh-cell wh-sid${i % 2 ? " alt" : ""}"/>${label((R.sid[0] + R.sid[1]) / 2, a0 + 15, ABBR[i], "wh-abbr", true)}`;
  }
  /* runes: two per house; a rune is lit when a body stands in it */
  const litRunes = new Set(WHEEL_BODIES.map(b => { const r = runeAt(C.sid[b]); return r.glyph; }));
  for (let h = 0; h < 12; h++) for (const half of [0, 1]){
    const a0 = HOUSE_ONE_ANGLE + h * 30 + half * 15, r = HOUSES[h][half ? "egress" : "ingress"], lit = litRunes.has(r[0]);
    o += `<path d="${cell(R.run[0], R.run[1], a0, a0 + 15)}" class="wh-cell wh-run${lit ? " lit" : ""}"><title>${r[1]} · house ${h + 1}</title></path>
      ${label((R.run[0] + R.run[1]) / 2, a0 + 7.5, r[0], "wh-rune" + (lit ? " lit" : ""))}`;
  }
  /* gates: personality lit ivory, design lit jade */
  if (R.gat){
    const pg = new Set(Object.values(C.natal.personality).map(v => v.gate)), dg = new Set(Object.values(C.natal.design).map(v => v.gate));
    GATE_ORDER.forEach((g, i) => {
      const a0 = aTrop(302 + i * 5.625), cls = pg.has(g) && dg.has(g) ? " both" : pg.has(g) ? " pers" : dg.has(g) ? " des" : "";
      o += `<path d="${cell(R.gat[0], R.gat[1], a0, a0 + 5.625)}" class="wh-cell wh-gate${cls}"><title>Gate ${g}${GATE_NAME[g] ? " · " + GATE_NAME[g] : ""}</title></path>
        ${label((R.gat[0] + R.gat[1]) / 2, a0 + 2.8125, g, "wh-gn" + cls)}`;
    });
  }
  /* the twenty-seven mansions */
  if (R.nak){
    const moon = nakIndex(C.sid.Moon);
    NAK_SHORT.forEach((n, i) => {
      const a0 = aSid(i * 360 / 27);
      o += `<path d="${cell(R.nak[0], R.nak[1], a0, a0 + 360 / 27)}" class="wh-cell wh-nak${i % 2 ? " alt" : ""}${i === moon ? " moon" : ""}"><title>${NAKSHATRA[i][0]} · ruled by ${NAKSHATRA[i][1]}</title></path>
        ${label((R.nak[0] + R.nak[1]) / 2, a0 + 180 / 27, n, "wh-nk" + (i === moon ? " moon" : ""), true)}`;
    });
  }
  /* houses in their colours */
  for (let h = 0; h < 12; h++){
    const a0 = HOUSE_ONE_ANGLE + h * 30, sign = (Math.floor(norm(C.ascS) / 30) + h) % 12;
    o += `<path d="${cell(R.hou[0], R.hou[1], a0, a0 + 30)}" fill="${HOUSES[h].hex}" class="wh-house"/>
      ${label((R.hou[0] + R.hou[1]) / 2, a0 + 15, h + 1, "wh-hn")}`;
    if (full) o += label(R.hou[0] - 9, a0 + 15, ABBR[sign], "wh-tiny");
  }
  o += `<circle cx="500" cy="500" r="${R.hou[0]}" fill="url(#wGlow)"/>`;

  /* the angles */
  const ang = [["ASC", C.ascS], ["DSC", C.ascS + 180], ["MC", C.mcS], ["IC", C.mcS + 180]];
  for (const [n, l] of ang){
    const a = aSid(l), [x0, y0] = P(R.core, a), [x1, y1] = P(full ? 510 : 500, a), [lx, ly] = P(full ? 540 : 520, a);
    o += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="wh-ang${n === "ASC" || n === "MC" ? " main" : ""}"/>`;
    if (full) o += `<text x="${f(lx)}" y="${f(ly - 7)}" class="wh-angn">${n}</text><text x="${f(lx)}" y="${f(ly + 9)}" class="wh-tiny">${dm(l)} ${ABBR[Math.floor(norm(l) / 30)]}</text>`;
  }

  /* the Pentagram Cross: five spikes from the two Dharma Suns */
  if (full){
    const D = C.dharma, a0 = aTrop(D.suns.p);
    for (let k = 0; k < 5; k++){
      const a = a0 + k * 72, [tx, ty] = P(R.core + 60, a), [b1x, b1y] = P(R.core + 2, a - 13), [b2x, b2y] = P(R.core + 2, a + 13);
      o += `<path d="M${f(tx)},${f(ty)} L${f(b1x)},${f(b1y)} L${f(b2x)},${f(b2y)} Z" class="wh-star"/>`;
    }
    for (const [k, l, g] of [["P", D.suns.p, D.personality.Sun], ["D", D.suns.d, D.design.Sun]]){
      const [x, y] = P(R.core + 60, aTrop(l)), [lx, ly] = P(R.core + 80, aTrop(l));
      o += `<circle cx="${f(x)}" cy="${f(y)}" r="5" class="wh-sun ${k}"/><text x="${f(lx)}" y="${f(ly)}" class="wh-tiny wh-sunl">☉ ${k} ${g.gate}.${g.line}</text>`;
    }
  }

  /* the bodies: personality (birth) outside, design (88° of Sun earlier) inside */
  const tick = (a, r0, r1, cls) => { const [x0, y0] = P(r0, a), [x1, y1] = P(r1, a); return `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="${cls}"/>`; };
  const pers = spread(WHEEL_BODIES.map(b => ({ b, a: aSid(C.sid[b]) })), full ? 7.5 : 11);
  for (const p of pers){
    const l = C.sid[p.b], g = C.natal.personality[p.b], [x, y] = P(R.pl, p.at);
    o += tick(p.a, R.hou[0], R.hou[0] - 10, "wh-tick") + tick(p.a, R.hou[0] - 10, R.pl + 14, "wh-lead");
    o += `<g class="wh-pl"><title>${p.b} · ${signOf(l)} ${dm(l)} sidereal · ${NAKSHATRA[nakIndex(l)][0]} · house ${houseOf(l, C.ascS)} · gate ${g.gate}.${g.line} · rune ${runeAt(l).name}</title>
      <text x="${f(x)}" y="${f(y)}" class="wh-glyph">${GLYPH[p.b]}</text></g>`;
    if (full) o += label(R.deg, p.at, dm(l).replace(/′$/, ""), "wh-deg");
  }
  if (full && C.tropDes){
    const des = spread(WHEEL_BODIES.map(b => ({ b, a: aTrop(C.tropDes[b]) })), 7.5);
    for (const p of des){
      const [x, y] = P(R.des, p.at), g = C.natal.design[p.b];
      o += `<g class="wh-pl"><title>Design ${p.b} · gate ${g.gate}.${g.line}</title><text x="${f(x)}" y="${f(y)}" class="wh-glyph des">${GLYPH[p.b]}</text></g>`;
    }
  }

  /* the centre */
  o += `<circle cx="500" cy="500" r="${R.core}" class="wh-core"/>`;
  if (full){
    const rv = rave(C), lines = [
      ["wh-c0", "full weave"], ["wh-c1", opt.name || "Your chart"], ["wh-c2", opt.place || ""], ["wh-c2", opt.when || ""],
      ["wh-c3", rv.type], ["wh-c4", `${rv.profile} · dh ${C.dharma.profile}`]];
    const ys = [432, 464, 497, 518, 548, 574];
    lines.forEach(([c, t], i) => { o += `<text x="500" y="${ys[i]}" class="${c}">${esc(t)}</text>`; });
  } else {
    o += `<text x="500" y="452" class="wh-cc">☉ ${signOf(C.sid.Sun)}</text><text x="500" y="502" class="wh-cc">☽ ${signOf(C.sid.Moon)}</text><text x="500" y="552" class="wh-cc">↑ ${signOf(C.ascS)}</text>`;
  }
  const label_ = `Natal chart: Sun in ${signOf(C.sid.Sun)}, Moon in ${signOf(C.sid.Moon)}, ${signOf(C.ascS)} rising`;
  return `<svg class="wwheel${full ? "" : " compact"}" viewBox="${full ? "-90 -40 1180 1080" : "0 0 1000 1000"}" role="img" aria-label="${label_}">${o}</svg>`;
}
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c])); }

window.WyrdWheel = { svg, rave, runeAt: (chart, l) => { C = chart; return runeAt(l); }, RAVE_BODIES };
})();
