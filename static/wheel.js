'use strict';
/* ============================================================
   THE WHEEL
   The natal chart as one drawing, outside in:
     tropical signs · sidereal signs · the 24 runes (two to a house)
     · the 64 gates (personality and design lit) · the 27 mansions
     · the twelve houses in their colours · the bodies
   and at the centre the aspects between the bodies. (The Dharma
   Weave is not drawn here: it belongs to the paid reading.)
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
function rave(chart){ return raveOf(chart.natal); }
/* any rave: the birth one (chart.natal) or the dharma one (chart.dharma) */
function raveOf(R){
  const { centres, channels } = window.WyrdBody;
  const centreOf = {}; for (const k in centres) for (const g of centres[k].gates) centreOf[g] = k;
  const gates = new Set([R.personality, R.design].flatMap(c => Object.values(c).map(v => v.gate)));
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
  const P_ = R.personality, D_ = R.design;
  return { type, strategy, authority, definition, profile: R.profile, defined: def,
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

/* ---------- drawing ----------
   Rings are stacked from the outside in, so the simple view can leave rings
   out without leaving gaps. Every ring is its own <g class="ring ring-…"> so a
   lesson can spotlight one, and every cell carries data-k so a tap can say
   what it is. */
const WIDTH = { tro: 40, sid: 32, run: 38, gat: 34, nak: 28, hou: 32 };
const LEVELS = { full: ["tro","sid","run","gat","nak","hou"], simple: ["tro","sid","run","hou"], compact: ["tro","run","hou"] };
function svg(chart, opt = {}){
  C = chart;
  const level = opt.compact ? "compact" : opt.level === "simple" ? "simple" : "full";
  const full = level === "full", big = level !== "compact", unknown = !!opt.unknownTime;
  const R = {}; let r = 492;
  for (const k of LEVELS[level]){ const w = level === "compact" ? { tro: 52, run: 56, hou: 46 }[k] : WIDTH[k]; R[k] = [r - w, r]; r -= w; }
  R.pl = R.hou[0] - (big ? 26 : 48); R.deg = R.pl - 26; R.des = full ? R.hou[0] - 92 : 0; R.core = full ? 128 : big ? 150 : 190;
  const g = (cls, inner) => `<g class="ring ${cls}">${inner}</g>`;
  let o = `<defs><radialGradient id="wGlow"><stop offset="0" stop-color="rgba(120,100,220,.16)"/><stop offset="1" stop-color="rgba(0,0,0,0)"/></radialGradient></defs>
    <circle cx="500" cy="500" r="492" class="wh-back"/>`;

  /* tropical signs: glyph medallions */
  let t = "";
  for (let i = 0; i < 12; i++){
    const a0 = aTrop(i * 30), m = (R.tro[0] + R.tro[1]) / 2, [x, y] = P(m, a0 + 15), s = big ? 26 : 40;
    t += `<path d="${cell(R.tro[0], R.tro[1], a0, a0 + 30)}" class="wh-cell wh-tro${i % 2 ? " alt" : ""}" data-k="trop:${i}"/>
      <rect x="${f(x - s / 2)}" y="${f(y - s / 2)}" width="${s}" height="${s}" rx="5" class="wh-badge"/>${label(m, a0 + 15, SG[i], "wh-badge-g")}`;
  }
  o += g("ring-tro", t);
  if (R.sid){
    t = "";
    for (let i = 0; i < 12; i++){
      const a0 = aSid(i * 30);
      t += `<path d="${cell(R.sid[0], R.sid[1], a0, a0 + 30)}" class="wh-cell wh-sid${i % 2 ? " alt" : ""}" data-k="sign:${i}"/>${label((R.sid[0] + R.sid[1]) / 2, a0 + 15, ABBR[i], "wh-abbr", true)}`;
    }
    o += g("ring-sid", t);
  }
  /* runes: two per house; a rune is lit when a body stands in it */
  const litRunes = new Set(WHEEL_BODIES.map(b => runeAt(C.sid[b]).glyph));
  t = "";
  for (let h = 0; h < 12; h++) for (const half of [0, 1]){
    const a0 = HOUSE_ONE_ANGLE + h * 30 + half * 15, rn = HOUSES[h][half ? "egress" : "ingress"], lit = litRunes.has(rn[0]);
    t += `<path d="${cell(R.run[0], R.run[1], a0, a0 + 15)}" class="wh-cell wh-run${lit ? " lit" : ""}" data-k="rune:${h * 2 + half}"/>
      ${label((R.run[0] + R.run[1]) / 2, a0 + 7.5, rn[0], "wh-rune" + (lit ? " lit" : ""))}`;
  }
  o += g("ring-run", t);
  /* gates: personality lit ivory, design lit jade */
  if (R.gat){
    const pg = new Set(Object.values(C.natal.personality).map(v => v.gate)), dg = new Set(Object.values(C.natal.design).map(v => v.gate));
    t = "";
    GATE_ORDER.forEach((gt, i) => {
      const a0 = aTrop(302 + i * 5.625), cls = pg.has(gt) && dg.has(gt) ? " both" : pg.has(gt) ? " pers" : dg.has(gt) ? " des" : "";
      t += `<path d="${cell(R.gat[0], R.gat[1], a0, a0 + 5.625)}" class="wh-cell wh-gate${cls}" data-k="gate:${gt}"/>
        ${label((R.gat[0] + R.gat[1]) / 2, a0 + 2.8125, gt, "wh-gn" + cls)}`;
    });
    o += g("ring-gat", t);
  }
  /* the twenty-seven mansions */
  if (R.nak){
    const moon = nakIndex(C.sid.Moon);
    t = "";
    NAK_SHORT.forEach((n, i) => {
      const a0 = aSid(i * 360 / 27);
      t += `<path d="${cell(R.nak[0], R.nak[1], a0, a0 + 360 / 27)}" class="wh-cell wh-nak${i % 2 ? " alt" : ""}${i === moon ? " moon" : ""}" data-k="nak:${i}"/>
        ${label((R.nak[0] + R.nak[1]) / 2, a0 + 180 / 27, n, "wh-nk" + (i === moon ? " moon" : ""), true)}`;
    });
    o += g("ring-nak", t);
  }
  /* houses in their colours */
  t = "";
  for (let h = 0; h < 12; h++){
    const a0 = HOUSE_ONE_ANGLE + h * 30, sign = (Math.floor(norm(C.ascS) / 30) + h) % 12;
    t += `<path d="${cell(R.hou[0], R.hou[1], a0, a0 + 30)}" fill="${HOUSES[h].hex}" class="wh-cell wh-house" data-k="house:${h}"/>
      ${label((R.hou[0] + R.hou[1]) / 2, a0 + 15, h + 1, "wh-hn")}`;
    if (big) t += label(R.hou[0] - 9, a0 + 15, ABBR[sign], "wh-tiny");
  }
  o += g("ring-hou", t) + `<circle cx="500" cy="500" r="${R.hou[0]}" fill="url(#wGlow)"/>`;

  /* the angles (left out when the birth time is unknown) */
  if (!unknown){
    t = "";
    for (const [n, l] of [["ASC", C.ascS], ["DSC", C.ascS + 180], ["MC", C.mcS], ["IC", C.mcS + 180]]){
      const a = aSid(l), [x0, y0] = P(R.core, a), [x1, y1] = P(big ? 510 : 500, a), [lx, ly] = P(big ? 540 : 520, a);
      t += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="wh-ang${n === "ASC" || n === "MC" ? " main" : ""}"/>`;
      if (big) t += `<g class="wh-angl" data-k="angle:${n}"><text x="${f(lx)}" y="${f(ly - 7)}" class="wh-angn">${n}</text><text x="${f(lx)}" y="${f(ly + 9)}" class="wh-tiny">${dm(l)} ${ABBR[Math.floor(norm(l) / 30)]}</text></g>`;
    }
    o += g("ring-ang", t);
  }

  /* the aspects: a chord between every pair of bodies in aspect, in the aspect's colour */
  if (full){
    const AB = WHEEL_BODIES, ra = R.des - 22;
    t = `<circle cx="500" cy="500" r="${ra}" class="wh-aspring"/>`;
    for (const b of AB){ const [x, y] = P(ra, aSid(C.sid[b])); t += `<circle cx="${f(x)}" cy="${f(y)}" r="3" class="wh-aspdot"/>`; }
    for (let i = 0; i < AB.length; i++) for (let k = i + 1; k < AB.length; k++){
      if (AB[i] === "Rahu" && AB[k] === "Ketu") continue;
      const x = aspectBetween(C.sid[AB[i]], C.sid[AB[k]]); if (!x || x.n === 1) continue;
      const [x0, y0] = P(ra, aSid(C.sid[AB[i]])), [x1, y1] = P(ra, aSid(C.sid[AB[k]]));
      t += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" stroke="${x.col}" class="wh-asp" data-a="${AB[i]} ${AB[k]}"/>`;
    }
    o += g("ring-asp", t);
  }

  /* the bodies: personality (birth) outside, design (88° of Sun earlier) inside */
  const tick = (a, r0, r1, cls) => { const [x0, y0] = P(r0, a), [x1, y1] = P(r1, a); return `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="${cls}"/>`; };
  t = "";
  for (const p of spread(WHEEL_BODIES.map(b => ({ b, a: aSid(C.sid[b]) })), big ? 7.5 : 11)){
    const l = C.sid[p.b], [x, y] = P(R.pl, p.at);
    t += `<g class="wh-pl" data-body="${p.b}" tabindex="${big ? 0 : -1}" role="button" aria-label="${p.b}, ${signOf(l)} ${dm(l)}">
      ${tick(p.a, R.hou[0], R.hou[0] - 10, "wh-tick")}${tick(p.a, R.hou[0] - 10, R.pl + 14, "wh-lead")}
      <circle cx="${f(x)}" cy="${f(y)}" r="${big ? 17 : 26}" class="wh-hit"/><text x="${f(x)}" y="${f(y)}" class="wh-glyph">${GLYPH[p.b]}</text>
      ${big ? label(R.deg, p.at, dm(l).replace(/′$/, ""), "wh-deg") : ""}</g>`;
  }
  o += g("ring-pl", t);
  if (full && C.tropDes){
    t = "";
    for (const p of spread(WHEEL_BODIES.map(b => ({ b, a: aTrop(C.tropDes[b]) })), 7.5)){
      const [x, y] = P(R.des, p.at);
      t += `<g class="wh-pl des" data-body="${p.b}" data-des="1"><circle cx="${f(x)}" cy="${f(y)}" r="14" class="wh-hit"/><text x="${f(x)}" y="${f(y)}" class="wh-glyph des">${GLYPH[p.b]}</text></g>`;
    }
    o += g("ring-des", t);
  }
  /* bodies of a second chart (compare): an outer ring of markers just inside the houses */
  if (opt.other){
    t = "";
    const O = opt.other;
    for (const p of spread(WHEEL_BODIES.map(b => ({ b, a: aSid(O.sid[b]) })), 7.5)){
      const [x, y] = P(R.hou[0] - 50, p.at);
      t += `<g class="wh-pl other" data-body="${p.b}" data-other="1">${tick(p.a, R.hou[0], R.hou[0] - 30, "wh-tick other")}<circle cx="${f(x)}" cy="${f(y)}" r="14" class="wh-hit"/><text x="${f(x)}" y="${f(y)}" class="wh-glyph other">${GLYPH[p.b]}</text></g>`;
    }
    o += g("ring-other", t);
  }

  /* the centre */
  o += `<circle cx="500" cy="500" r="${R.core}" class="wh-core"/>`;
  if (full){
    const rv = rave(C), lines = [
      ["wh-c1", opt.name || "Your chart"], ["wh-c2", opt.place || ""], ["wh-c2", opt.when || ""],
      ["wh-c3", rv.type], ["wh-c4", `profile ${rv.profile}`]];
    const ys = [446, 480, 501, 534, 562];
    lines.forEach(([c, tx], i) => { o += `<text x="500" y="${ys[i]}" class="${c}">${esc(tx)}</text>`; });
  } else {
    const ys = big ? [466, 502, 538] : [452, 502, 552];
    o += `<text x="500" y="${ys[0]}" class="wh-cc">☉ ${signOf(C.sid.Sun)}</text><text x="500" y="${ys[1]}" class="wh-cc">☽ ${signOf(C.sid.Moon)}</text>
      <text x="500" y="${ys[2]}" class="wh-cc">${unknown ? "↑ time unknown" : "↑ " + signOf(C.ascS)}</text>`;
  }
  const aria = `Natal chart: Sun in ${signOf(C.sid.Sun)}, Moon in ${signOf(C.sid.Moon)}${unknown ? "" : `, ${signOf(C.ascS)} rising`}`;
  return `<svg class="wwheel lv-${level}" viewBox="${big ? "-90 -40 1180 1080" : "0 0 1000 1000"}" role="${big ? "group" : "img"}" aria-label="${aria}">${o}</svg>`;
}

/* ---------- what a tap on the wheel points at ---------- */
function bodyFacts(chart, b, design){
  C = chart;
  if (design){
    const tl = C.tropDes[b], gt = C.natal.design[b];
    return { body: b, design: true, trop: tl, gate: gt, keys: [`gate:${gt.gate}`, `trop:${Math.floor(norm(tl) / 30)}`] };
  }
  const l = C.sid[b], tl = C.trop[b], ru = runeAt(l), h = houseOf(l, C.ascS), into = norm(norm(l) - cusp());
  return { body: b, sid: l, trop: tl, rune: ru, house: h, nak: nakIndex(l), gate: C.natal.personality[b], desGate: C.natal.design[b],
    keys: [`sign:${Math.floor(norm(l) / 30)}`, `trop:${Math.floor(norm(tl) / 30)}`, `rune:${Math.floor(into / 15)}`,
           `gate:${C.natal.personality[b].gate}`, `nak:${nakIndex(l)}`, `house:${h - 1}`] };
}
/* which bodies stand in a given cell */
function bodiesIn(chart, key){
  C = chart;
  const [kind, v] = key.split(":"), n = +v;
  return WHEEL_BODIES.filter(b => {
    const l = C.sid[b], into = norm(norm(l) - cusp());
    switch (kind){
      case "sign":  return Math.floor(norm(l) / 30) === n;
      case "trop":  return Math.floor(norm(C.trop[b]) / 30) === n;
      case "rune":  return Math.floor(into / 15) === n;
      case "house": return Math.floor(into / 30) === n;
      case "nak":   return nakIndex(l) === n;
      case "gate":  return C.natal.personality[b].gate === n || C.natal.design[b].gate === n;
    }
    return false;
  });
}
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c])); }


/* ---------- the explorable wheel ----------
   mount(host, chart, {level, name, place, when, unknownTime, focus})
   Draws the wheel with a Simple / Full switch and a card that says what a
   tapped planet or ring cell is. Returns { setLevel, focus, select }. */
const RING_NAME = { trop: ["tropical", "Tropical sign"], sign: ["sidereal", "Sidereal sign"], rune: ["rune", "Rune"], gate: ["gate", "Gate"],
  nak: ["nakshatra", "Mansion"], house: ["house", "House"] };
function mount(host, chart, opts = {}){
  let level = opts.level || "simple", sel = null, focus = opts.focus || null;
  const gl = (k, l) => window.Wyrd && Wyrd.gloss ? Wyrd.gloss(k, l) : (l || k);
  const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;
  host.classList.add("wx");
  host.innerHTML = `
    ${opts.noSwitch ? "" : `<div class="wx-bar" role="group" aria-label="How much of the wheel to show">
      <button type="button" class="wx-lv" data-lv="simple">Simple</button><button type="button" class="wx-lv" data-lv="full">Full</button>
      <span class="wx-hint">Tap any planet or ring to see what it is.</span></div>`}
    <div class="wx-stage"></div>
    <div class="wx-card" aria-live="polite"></div>`;
  const stage = host.querySelector(".wx-stage"), card = host.querySelector(".wx-card");

  function draw(){
    stage.innerHTML = svg(chart, { ...opts, level });
    host.querySelectorAll(".wx-lv").forEach(b => b.setAttribute("aria-pressed", b.dataset.lv === level));
    applyFocus(); if (sel) select(sel.kind, sel.v, true); else idle();
  }
  function applyFocus(){
    const s = stage.querySelector("svg"); if (!s) return;
    s.classList.toggle("focusing", !!focus);
    s.querySelectorAll(".ring").forEach(r => r.classList.toggle("in-focus", !!focus && focus.some(k => r.classList.contains("ring-" + k))));
  }
  function idle(){
    card.innerHTML = opts.idle || `<p class="wx-idle">Tap a planet to follow it through every ring: its sign in both zodiacs, its house, mansion, rune and gate.</p>`;
  }
  function light(keys){
    stage.querySelectorAll(".hi").forEach(e => e.classList.remove("hi"));
    stage.querySelector("svg").classList.toggle("selecting", keys.length > 0);
    for (const k of keys) stage.querySelectorAll(`[data-k="${k}"]`).forEach(e => e.classList.add("hi"));
  }
  function select(kind, v, quiet){
    sel = { kind, v };
    if (kind === "body" || kind === "des"){
      const F = bodyFacts(chart, v, kind === "des");
      light(F.keys);
      stage.querySelectorAll(`.wh-pl[data-body="${v}"]${kind === "des" ? "[data-des]" : ":not([data-des]):not([data-other])"}`).forEach(e => e.classList.add("hi"));
      if (kind === "des"){
        card.innerHTML = `<h4><span class="wx-g des">${GLYPH[v]}</span> Design ${v}</h4><dl>
          <dt>${gl("design", "Design")} position</dt><dd>${SIGNS[Math.floor(norm(F.trop) / 30)]} ${dm(F.trop)} tropical</dd>
          <dt>${gl("gate")}</dt><dd>${F.gate.gate}.${F.gate.line}${GATE_NAME[F.gate.gate] ? " · " + GATE_NAME[F.gate.gate] : ""}</dd></dl>`;
      } else {
        const l = F.sid;
        card.innerHTML = `<h4><span class="wx-g">${GLYPH[v]}</span> ${v}</h4><dl>
          <dt>${gl("sidereal", "Sidereal sign")}</dt><dd>${signOf(l)} ${dm(l)}</dd>
          <dt>${gl("tropical", "Tropical sign")}</dt><dd>${SIGNS[Math.floor(norm(F.trop) / 30)]} ${dm(F.trop)}</dd>
          <dt>${gl("house")}</dt><dd>${opts.unknownTime ? `${F.house} <small>(solar houses; birth time unknown)</small>` : F.house}</dd>
          <dt>${gl("nakshatra", "Mansion")}</dt><dd>${NAKSHATRA[F.nak][0]}, ${gl("pada", "pada")} ${pada(l)} <small>· ruled by ${NAKSHATRA[F.nak][1]}</small></dd>
          <dt>${gl("rune")}</dt><dd>${F.rune.glyph} ${F.rune.name} <small>· house ${F.rune.house}</small></dd>
          <dt>${gl("gate")}</dt><dd>${F.gate.gate}.${F.gate.line}${GATE_NAME[F.gate.gate] ? " · " + GATE_NAME[F.gate.gate] : ""}</dd>
          <dt>${gl("design", "Design gate")}</dt><dd>${F.desGate.gate}.${F.desGate.line}</dd></dl>`;
      }
    } else {
      const key = `${kind}:${v}`, here = bodiesIn(chart, key);
      light([key]);
      here.forEach(b => stage.querySelectorAll(`.wh-pl[data-body="${b}"]:not([data-des]):not([data-other])`).forEach(e => e.classList.add("hi")));
      const [gk, gname] = RING_NAME[kind] || [kind, kind];
      let title = "", extra = "";
      if (kind === "sign" || kind === "trop") title = `${SIGNS[v]} <small>(${kind === "sign" ? "sidereal" : "tropical"})</small>`;
      if (kind === "house"){ const sg = (Math.floor(norm(chart.ascS) / 30) + +v) % 12; title = `House ${+v + 1}`; extra = `<p>${SIGNS[sg]} (sidereal) fills this house. Its colour is ${HOUSES[v].color.toLowerCase()}.</p>`; }
      if (kind === "rune"){ const h = Math.floor(v / 2), rn = HOUSES[h][v % 2 ? "egress" : "ingress"]; title = `${rn[0]} ${rn[1]}`;
        extra = `<p>The ${v % 2 ? gl("egress", "closing rune") : gl("ingress", "opening rune")} of house ${h + 1}.</p>`; }
      if (kind === "gate") title = `Gate ${v}${GATE_NAME[v] ? " · " + GATE_NAME[v] : ""}`;
      if (kind === "nak") title = `${NAKSHATRA[v][0]} <small>· ruled by ${NAKSHATRA[v][1]}</small>`;
      const who = here.length ? here.map(b => `${GLYPH[b]} ${b}`).join(", ") : "No planet stands here.";
      card.innerHTML = `<h4>${title}</h4><p class="wx-kind">${gl(gk, gname)}</p>${extra}<p>${here.length ? "Here: " : ""}${who}</p>`;
    }
    if (!quiet && opts.onSelect) opts.onSelect(sel);
    if (!quiet && window.Wyrd && Wyrd.pulse) Wyrd.pulse("tap", kind);
  }
  stage.addEventListener("click", e => {
    const pl = e.target.closest(".wh-pl");
    if (pl && !pl.dataset.other){ select(pl.dataset.des ? "des" : "body", pl.dataset.body); return; }
    const c = e.target.closest("[data-k]");
    if (c){ const [k, v] = c.dataset.k.split(":"); if (RING_NAME[k]) { select(k, isNaN(+v) ? v : +v); return; } }
    sel = null; light([]); idle();
  });
  stage.addEventListener("keydown", e => {
    const pl = e.target.closest(".wh-pl");
    if (pl && (e.key === "Enter" || e.key === " ")){ e.preventDefault(); select("body", pl.dataset.body); }
  });
  host.addEventListener("click", e => { const b = e.target.closest(".wx-lv[data-lv]"); if (b){ level = b.dataset.lv; draw(); window.Wyrd && Wyrd.pulse && Wyrd.pulse("act", "level"); } });
  draw();
  return {
    setLevel(l){ level = l; draw(); },
    focus(keys){ focus = keys; applyFocus(); },
    select(kind, v){ select(kind, v); },
    clear(){ sel = null; light([]); idle(); },
    get level(){ return level; },
  };
}

window.WyrdWheel = { mount, svg, rave, raveOf, bodyFacts, bodiesIn, runeAt: (chart, l) => { C = chart; return runeAt(l); }, RAVE_BODIES, WHEEL_BODIES, NAK_SHORT, ABBR, dm };
})();
