'use strict';
/* ============================================================
   THE HARMONIC BODY
   The old anatomy engraving with its seven stations, the planet
   that feeds each one, the two zodiacs around it and the two
   rave definitions laid over it. Tap a station (or its planet)
   to wake it: the feeding planet's current runs down its thread
   into the station, then along the axis from the last station
   woken. Drag to turn the figure; the three layers sit at
   different depths, so they part as it turns.
   Depends on viz.js for STATIONS, NAKSHATRA, ENGINE, NAK_ARC,
   GLYPH, HOUSES, HOUSE_ONE_ANGLE, norm, signOf, degIn, houseOf, Sound.
   ============================================================ */
(() => {
const NS = "http://www.w3.org/2000/svg";
/* the figure: the engraving (J. Caldwall after John Brisbane, The Anatomy of Painting, 1769), in
   pale ink, the same one the reading's body map uses. It is placed on the 900 × 900 plan so that the
   seven stations marked on it (lib/medical.json FIGURE.at, in the engraving's own pixels) fall where
   the stations stand, and the stations are moved onto it exactly. */
const ETCH = { src: "/static/look/anatomy-light.png", w: 760, h: 994, s: .5549, x: 289.4, y: 168.4,
  at: { asgard: [284, 32], alfheim: [284, 72], vanaheim: [291, 160], midgard: [293, 245], muspelheim: [295, 323], nidavellir: [291, 426], hel: [288, 483] },
  feet: 965 };
const FIGURE = `<image class="etch" href="${ETCH.src}" x="${ETCH.x}" y="${ETCH.y}" width="${(ETCH.w * ETCH.s).toFixed(1)}" height="${(ETCH.h * ETCH.s).toFixed(1)}" preserveAspectRatio="none"/>`;
const ST = STATIONS.map(s => {
  const [ex, ey] = ETCH.at[s.id], x = +(ETCH.x + ex * ETCH.s).toFixed(1), y = +(ETCH.y + ey * ETCH.s).toFixed(1);
  return { ...s, x, y, leadY: s.leadY + (y - s.y) };
});

/* ---------- Human Design centres, as the console drew them on the body ---------- */
const HB_CENTRES = {
  head:  { label:"Head",   gates:[64,61,63] },
  ajna:  { label:"Ajna",   gates:[47,24,4,17,43,11] },
  throat:{ label:"Throat", gates:[62,23,56,35,12,45,33,8,31,20,16] },
  g:     { label:"G",      gates:[1,13,25,46,2,15,10,7] },
  heart: { label:"Heart",  gates:[21,40,26,51] },
  spleen:{ label:"Spleen", gates:[48,57,44,50,32,28,18] },
  solar: { label:"Solar",  gates:[36,22,37,6,49,55,30] },
  sacral:{ label:"Sacral", gates:[34,5,14,29,59,9,3,42,27] },
  root:  { label:"Root",   gates:[53,60,52,19,39,41,58,38,54] }
};
const HB_CHANNELS = [[1,8],[2,14],[3,60],[4,63],[5,15],[6,59],[7,31],[9,52],[10,20],[10,34],
  [10,57],[11,56],[12,22],[13,33],[16,48],[17,62],[18,58],[19,49],[20,34],[20,57],[21,45],
  [23,43],[24,61],[25,51],[26,44],[27,50],[28,38],[29,46],[30,41],[32,54],[34,57],[35,36],
  [37,40],[39,55],[42,53],[47,64]];
const HB_GATE_CENTRE = {};
for (const k in HB_CENTRES) for (const g of HB_CENTRES[k].gates) HB_GATE_CENTRE[g] = k;
const HB_GEOM = {
  head:  { x:450, y:172, shape:"tri-up",    s:25 },
  ajna:  { x:450, y:212, shape:"tri-down",  s:23 },
  throat:{ x:450, y:254, shape:"square",    s:27 },
  g:     { x:450, y:308, shape:"diamond",   s:26 },
  heart: { x:497, y:322, shape:"tri-left",  s:17 },
  spleen:{ x:396, y:346, shape:"tri-right", s:20 },
  solar: { x:504, y:356, shape:"tri-left",  s:20 },
  sacral:{ x:450, y:404, shape:"square",    s:27 },
  root:  { x:450, y:456, shape:"square",    s:27 }
};
function shape(g){
  const { x, y, s } = g, h = s / 2;
  switch (g.shape){
    case "tri-up":    return `M${x},${y-h} L${x+h},${y+h} L${x-h},${y+h} Z`;
    case "tri-down":  return `M${x},${y+h} L${x+h},${y-h} L${x-h},${y-h} Z`;
    case "tri-left":  return `M${x-h},${y} L${x+h},${y-h} L${x+h},${y+h} Z`;
    case "tri-right": return `M${x+h},${y} L${x-h},${y-h} L${x-h},${y+h} Z`;
    case "diamond":   return `M${x},${y-h} L${x+h},${y} L${x},${y+h} L${x-h},${y} Z`;
    default:          return `M${x-h},${y-h} L${x+h},${y-h} L${x+h},${y+h} L${x-h},${y+h} Z`;
  }
}
const gatesOf = rave => [rave.personality, rave.design].flatMap(col => Object.values(col).map(v => v.gate));
/* which way the current runs along a live channel, shared by every bodygraph on the site
   (and by wyrd/bodygraph.py): toward the throat along the circuit, from the centre
   farther from it to the nearer; where the circuit doesn't decide, toward the throat's
   place in the body. */
const THROAT_GAP = { throat: 0, ajna: 82, g: 92, heart: 122, head: 154, spleen: 182, solar: 182, sacral: 210, root: 300 };
function throatDist(gates){
  const have = new Set(gates), adj = {};
  for (const k in HB_CENTRES) adj[k] = new Set();
  for (const [a, b] of HB_CHANNELS) if (have.has(a) && have.has(b)){ adj[HB_GATE_CENTRE[a]].add(HB_GATE_CENTRE[b]); adj[HB_GATE_CENTRE[b]].add(HB_GATE_CENTRE[a]); }
  const dist = { throat: 0 }, q = ["throat"];
  while (q.length){ const c = q.shift(); for (const n of adj[c]) if (!(n in dist)){ dist[n] = dist[c] + 1; q.push(n); } }
  return dist;
}
function runsFrom(dist, c1, c2){            // true when the current runs c1 → c2
  const d1 = dist[c1] ?? 99, d2 = dist[c2] ?? 99;
  return d1 > d2 || (d1 === d2 && THROAT_GAP[c1] >= THROAT_GAP[c2]);
}
function defined(gates){
  const have = new Set(gates), out = new Set();
  for (const [a, b] of HB_CHANNELS) if (have.has(a) && have.has(b)){ out.add(HB_GATE_CENTRE[a]); out.add(HB_GATE_CENTRE[b]); }
  return out;
}

/* ---------- geometry ---------- */
const ZC = 450;
const R_TROP_OUT = 398, R_TROP_IN = 372, R_SID_OUT = 366, R_SID_IN = 340, R_NAK_OUT = 338, R_NAK_IN = 316;
const zp = (r, d) => [ZC + r * Math.cos(d * Math.PI / 180), ZC + r * Math.sin(d * Math.PI / 180)];
const f2 = n => n.toFixed(2);
function band(ri, ro, a0, a1){
  const [x1,y1] = zp(ro, a0), [x2,y2] = zp(ro, a1), [x3,y3] = zp(ri, a1), [x4,y4] = zp(ri, a0);
  const L = ((a1 - a0 + 360) % 360) > 180 ? 1 : 0;
  return `M${f2(x1)},${f2(y1)} A${ro},${ro} 0 ${L} 1 ${f2(x2)},${f2(y2)} L${f2(x3)},${f2(y3)} A${ri},${ri} 0 ${L} 0 ${f2(x4)},${f2(y4)} Z`;
}
function arc(r, a0, a1){
  const [x0,y0] = zp(r, a0), [x1,y1] = zp(r, a1);
  return `M${f2(x0)},${f2(y0)} A${r},${r} 0 ${((a1 - a0 + 360) % 360) > 180 ? 1 : 0} 1 ${f2(x1)},${f2(y1)}`;
}
const SIGN_GLYPH = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];

/* ---------- state ---------- */
let C = null, root = null, deck = null, read = null;
let woken = new Set(), last = null, nkFocus = null, showRave = false, showDharma = false, showZod = true, showTorus = true;
let scanIdx = 0, scanTimer = null;
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const pose = { tilt: 0, turn: 0 };
const cusp = () => Math.floor(norm(C.ascS) / 30) * 30;
const aSid = l => HOUSE_ONE_ANGLE + norm(norm(l) - cusp());
const aTrop = l => aSid(norm(l - C.ay));
const seatOf = b => ST.find(s => s.feeder === b) || null;
const markXY = (b, i) => {
  const st = seatOf(b);
  if (st) return [st.x + (i % 2 === 0 ? -40 : 40), st.y - 6];
  return [450, b === "Rahu" ? 128 : 726];
};
const BODIES = () => Object.keys(GLYPH).filter(b => C.sid[b] != null);
/* the classical seven and the nodes stand on the body; the outer three ride the rings only */
const MARKS = () => ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"].filter(b => C.sid[b] != null);

/* ---------- layer 1: the two zodiacs ---------- */
function zodiacSVG(){
  const ay = C.ay;
  let o = `<circle class="arc trop" cx="450" cy="450" r="${R_TROP_OUT}"/><circle class="arc trop" cx="450" cy="450" r="${R_TROP_IN}"/>
    <circle class="arc sid" cx="450" cy="450" r="${R_SID_OUT}"/><circle class="arc sid" cx="450" cy="450" r="${R_SID_IN}"/>`;
  for (let i = 0; i < 12; i++){
    for (const [fr, ri, ro, a0] of [["trop", R_TROP_IN, R_TROP_OUT, aTrop(i * 30)], ["sid", R_SID_IN, R_SID_OUT, aSid(i * 30)]]){
      const [sx,sy] = zp(ri, a0), [ex,ey] = zp(ro, a0), [lx,ly] = zp((ri + ro) / 2, a0 + 15);
      o += `<line class="spoke ${fr}" x1="${f2(sx)}" y1="${f2(sy)}" x2="${f2(ex)}" y2="${f2(ey)}"/>
        <text class="sg ${fr}" x="${f2(lx)}" y="${f2(ly + 3)}">${SIGN_GLYPH[i]}</text>`;
    }
  }
  const [tnx,tny] = zp(R_TROP_OUT + 9, aTrop(0)), [snx,sny] = zp(R_SID_OUT - 6, aSid(0));
  o += `<text class="ring-name" x="${f2(tnx)}" y="${f2(tny)}" fill="#d9d4c4" opacity=".3">TROPICAL</text>
        <text class="ring-name" x="${f2(snx)}" y="${f2(sny)}" fill="#ffcc33" opacity=".45">SIDEREAL</text>`;
  const a0 = aTrop(0);
  o += `<path class="ay-arc" d="${arc(R_SID_OUT + 4, a0, a0 + ay)}"/>`;
  const [ax,ayy] = zp(R_SID_OUT + 14, a0 + ay / 2);
  o += `<text class="ay-lbl" x="${f2(ax)}" y="${f2(ayy)}">AYANAMSA ${ay.toFixed(2)}°</text>`;
  for (let k = 0; k < 27; k++){
    const s0 = aSid(k * NAK_ARC), s1 = s0 + NAK_ARC, mid = s0 + NAK_ARC / 2;
    const [lx,ly] = zp((R_NAK_IN + R_NAK_OUT) / 2, mid), [tx1,ty1] = zp(R_NAK_IN, s0), [tx2,ty2] = zp(R_NAK_OUT, s0);
    let padas = "";
    for (let p = 1; p < 4; p++){
      const [p1x,p1y] = zp(R_NAK_IN, s0 + p * NAK_ARC / 4), [p2x,p2y] = zp(R_NAK_IN + 7, s0 + p * NAK_ARC / 4);
      padas += `<line class="pada" x1="${f2(p1x)}" y1="${f2(p1y)}" x2="${f2(p2x)}" y2="${f2(p2y)}"/>`;
    }
    const m = norm(mid), flip = m > 90 && m < 270;
    o += `<g class="znak" data-hb-nak="${k}" tabindex="0" role="button" aria-label="${NAKSHATRA[k][0]}">
      <path class="band" d="${band(R_NAK_IN, R_NAK_OUT, s0, s1)}"/>
      <line class="nk-tick" x1="${f2(tx1)}" y1="${f2(ty1)}" x2="${f2(tx2)}" y2="${f2(ty2)}"/>${padas}
      <text class="nk-lbl" x="${f2(lx)}" y="${f2(ly + 2)}" transform="rotate(${f2(flip ? m + 90 : m - 90)} ${f2(lx)} ${f2(ly)})">${NAKSHATRA[k][0].toUpperCase()}</text>
      <path class="arc" d="${arc(R_NAK_OUT, s0, s1)}" style="opacity:0"/></g>`;
  }
  BODIES().forEach((b, i) => {
    const a = aTrop(C.trop[b]), r = R_TROP_OUT + 12 + (i % 2) * 15;
    const [x,y] = zp(r, a), [sx,sy] = zp(R_TROP_OUT + 2, a);
    o += `<line class="zp-stem" x1="${f2(x)}" y1="${f2(y)}" x2="${f2(sx)}" y2="${f2(sy)}"/>
      <text class="zp" x="${f2(x)}" y="${f2(y + 3)}">${GLYPH[b]}</text>`;
  });
  return o;
}

/* ---------- layer 2: the figure, centres and thread ---------- */
/* the live channels as moving light between the centres, rising toward the throat */
function liveChannels(gates){ const have = new Set(gates); return HB_CHANNELS.filter(([a, b]) => have.has(a) && have.has(b)); }
function flowSVG(){
  const lr = showRave ? liveChannels(gatesOf(C.natal)).map(c => c.join("-")) : [];
  const ld = showDharma && C.dharma ? liveChannels(gatesOf(C.dharma)).map(c => c.join("-")) : [];
  const keys = [...new Set([...lr, ...ld])], bundle = {};
  const distR = throatDist(gatesOf(C.natal)), distD = C.dharma ? throatDist(gatesOf(C.dharma)) : {};
  let o = "";
  for (const k of keys){
    const [a, b] = k.split("-").map(Number), ca = HB_GATE_CENTRE[a], cb = HB_GATE_CENTRE[b];
    const pair = [ca, cb].sort().join("|"), i = (bundle[pair] = (bundle[pair] || 0) + 1) - 1;
    /* toward the throat (runsFrom), offset when several share a route */
    const [p, q] = runsFrom(lr.includes(k) ? distR : distD, ca, cb) ? [HB_GEOM[ca], HB_GEOM[cb]] : [HB_GEOM[cb], HB_GEOM[ca]];
    const len = Math.hypot(q.x - p.x, q.y - p.y) || 1, off = (i % 2 ? -1 : 1) * Math.ceil(i / 2) * 4;
    const nx = -(q.y - p.y) / len * off, ny = (q.x - p.x) / len * off;
    const cls = lr.includes(k) && ld.includes(k) ? "both" : lr.includes(k) ? "rave" : "dharma";
    const path = `M${(p.x + nx).toFixed(1)},${(p.y + ny).toFixed(1)} L${(q.x + nx).toFixed(1)},${(q.y + ny).toFixed(1)}`;
    o += `<path class="hb-chan ${cls}" d="${path}"><title>Channel ${a}–${b}</title></path>`;
    if (!reduce) for (let j = 0; j < 2; j++)
      o += `<circle class="hb-spark ${cls}" r="2.6"><animateMotion dur="${(len / 30).toFixed(2)}s" begin="${(j * len / 60).toFixed(2)}s" repeatCount="indefinite" path="${path}"/></circle>`;
  }
  return o;
}
function centresSVG(){
  const r = showRave ? defined(gatesOf(C.natal)) : new Set();
  const d = showDharma ? defined(gatesOf(C.dharma)) : new Set();
  let o = flowSVG();
  for (const k in HB_GEOM){
    const g = HB_GEOM[k], inR = r.has(k), inD = d.has(k);
    const cls = inR && inD ? "both" : inR ? "rave" : inD ? "dharma" : "undefined";
    o += `<g class="centre ${cls}"><path class="shape" d="${shape(g)}"/>
      <text class="lbl" x="${g.x}" y="${g.y + g.s / 2 + 9}">${HB_CENTRES[k].label}</text></g>`;
  }
  return o;
}

/* ---------- layer 3: stations, planets, and the current ---------- */
/* the body map's weights, from the server: how much of the chart gathers at each station, 0 to 1 */
let W8 = {}, HEAVY = [];
function stationsSVG(){
  let o = `<g class="thread"><line x1="450" y1="96" x2="450" y2="760"/>
    <circle class="cap" cx="450" cy="100" r="2.6"/><circle class="cap" cx="450" cy="756" r="2.6"/>
    <text x="450" y="88">RAHU</text><text x="450" y="778">KETU</text></g>
    <g class="hb-flow" id="hbFlow"></g>`;
  /* the planets, each tied by its thread to the station it feeds */
  MARKS().forEach((b, i) => {
    const st = seatOf(b), [x, y] = markXY(b, i), h = houseOf(C.sid[b], C.ascS);
    o += `<g class="g-mark" data-hb-graha="${b}" ${st ? `data-hb-station="${st.id}"` : ""} tabindex="0" role="button"
        aria-label="${b} in house ${h}${st ? ", feeds the " + st.station : ""}">
      ${st ? `<line class="thread" x1="${x}" y1="${y + 3}" x2="${st.x}" y2="${st.y}"/>` : ""}
      <circle class="ring" cx="${x}" cy="${y - 3}" r="9"/>
      <text class="gl" x="${x}" y="${y}">${GLYPH[b]}</text>
      <text class="gl sub" x="${x}" y="${y + 10}">H${h}</text>
      <circle cx="${x}" cy="${y - 3}" r="14" fill="transparent"/></g>`;
  });
  o += `<g class="stations" id="hbStations">`;
  for (const s of ST){
    const dir = s.side === "L" ? -1 : 1, bendX = s.x + dir * 116, endX = s.x + dir * 172;
    o += `<g class="station" data-hb-station="${s.id}" tabindex="0" role="button" style="--band:${s.band}"
        aria-label="${s.station}, ${s.world}, fed by ${s.feeder}">
      <path class="lead" d="M${s.x + dir * 14},${s.y} L${bendX},${s.leadY} L${endX},${s.leadY}"/>
      <text class="tag" x="${endX + dir * 6}" y="${s.leadY - 5}" text-anchor="${s.side === "L" ? "end" : "start"}">${s.tag} · ${s.world}</text>
      ${W8[s.id] != null ? `<circle class="weight${HEAVY.includes(s.id) ? " heavy" : ""}" cx="${s.x}" cy="${s.y}" r="${(9 + 15 * W8[s.id]).toFixed(1)}"/>` : ""}
      <circle class="bloom" cx="${s.x}" cy="${s.y}" r="8"/>
      <circle class="halo" cx="${s.x}" cy="${s.y}" r="13"/>
      <circle class="ring" cx="${s.x}" cy="${s.y}" r="8"/>
      <circle class="core" cx="${s.x}" cy="${s.y}" r="2.2"/>
      ${s.axis ? "" : `<line class="bar" x1="${s.x - 13}" y1="${s.y}" x2="${s.x - 9}" y2="${s.y}"/><line class="bar" x1="${s.x + 9}" y1="${s.y}" x2="${s.x + 13}" y2="${s.y}"/>`}
      <circle cx="${s.x}" cy="${s.y}" r="16" fill="transparent"/></g>`;
  }
  return o + `</g>`;
}

/* ---------- the current ---------- */
function stream(x1, y1, x2, y2, color, ms, cls){
  const g = root.querySelector("#hbFlow");
  if (!g) return Promise.resolve();
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (reduce || len < 1) return Promise.resolve();
  const p = document.createElementNS(NS, "line");
  p.setAttribute("x1", x1); p.setAttribute("y1", y1); p.setAttribute("x2", x2); p.setAttribute("y2", y2);
  p.setAttribute("class", "hb-current " + (cls || ""));
  p.style.stroke = color;
  const head = document.createElementNS(NS, "circle");
  head.setAttribute("r", "3.4"); head.setAttribute("class", "hb-head"); head.style.fill = color;
  g.append(p, head);
  return new Promise(done => {
    const t0 = performance.now();
    (function step(t){
      const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      head.setAttribute("cx", x1 + (x2 - x1) * e); head.setAttribute("cy", y1 + (y2 - y1) * e);
      p.style.strokeDashoffset = String(-t / 18);
      p.style.opacity = String(k < .85 ? .9 : .9 * (1 - (k - .85) / .15));
      if (k < 1) requestAnimationFrame(step);
      else { head.remove(); setTimeout(() => p.remove(), 60); done(); }
    })(t0);
  });
}

/* a standing current along the axis between woken stations */
function paintSpine(){
  const g = root.querySelector("#hbSpine");
  if (!g) return;
  const ys = ST.filter(s => woken.has(s.id)).map(s => s.y);
  if (ys.length < 2){ g.innerHTML = ""; return; }
  const lit = ST.filter(s => woken.has(s.id));
  let o = "";
  for (let i = 0; i < lit.length - 1; i++){
    const a = lit[i], b = lit[i + 1];
    o += `<line class="hb-spine" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" style="stroke:${b.band}"/>`;
  }
  g.innerHTML = o;
}

async function wake(id, opts){
  const s = ST.find(x => x.id === id); if (!s) return;
  const quiet = opts && opts.quiet;
  const node = root.querySelector(`.station[data-hb-station="${id}"]`);
  const stG = root.querySelector("#hbStations");
  stG.classList.add("dimmed");
  root.querySelectorAll(".station.live").forEach(n => n.classList.remove("live"));
  node.classList.add("live");
  /* the feeder's current runs down its thread first */
  const i = MARKS().indexOf(s.feeder), [mx, my] = markXY(s.feeder, i);
  const mark = root.querySelector(`.g-mark[data-hb-graha="${s.feeder}"]`);
  if (mark) mark.classList.add("feeding");
  if (!quiet) Sound.chord(s.ratios.map(r => s.hz * r[0]));
  paintStation(s);
  const from = last ? ST.find(x => x.id === last) : null;
  await Promise.all([
    stream(mx, my + 3, s.x, s.y, s.band, 1100, "feed"),
    from && from.id !== s.id ? stream(from.x, from.y, s.x, s.y, s.band, 1400, "axis") : null
  ]);
  if (mark) setTimeout(() => mark.classList.remove("feeding"), 400);
  node.classList.remove("bloomed"); void node.getBBox(); node.classList.add("bloomed");
  woken.add(id); node.classList.add("woken");
  last = id;
  paintSpine();
}

function sleepAll(){
  stopScan();
  woken.clear(); last = null;
  root.querySelectorAll(".station").forEach(n => n.classList.remove("live", "woken", "bloomed"));
  root.querySelector("#hbStations").classList.remove("dimmed");
  paintSpine();
  read.innerHTML = idleRead();
}

/* the descent scan, crown to root, as the console ran it */
function stepScan(){
  if (scanIdx >= ST.length){ stopScan(); return; }
  wake(ST[scanIdx].id);
  scanIdx++;
  scanTimer = setTimeout(stepScan, 4200);
}
function stopScan(){
  clearTimeout(scanTimer); scanTimer = null;
  const b = root && root.querySelector("[data-hb-scan]");
  if (b){ b.classList.remove("on"); b.textContent = "Descent scan"; }
}

/* ---------- readouts ---------- */
function idleRead(){
  return `<p class="hb-idle">Tap a station, or the planet beside it, to wake it. The planet's current runs down its thread into the station it feeds. Wake a second and the current crosses the axis between them. Tap a mansion on the inner ring to isolate it.</p>`;
}
function paintStation(s){
  const supply = houseOf(C.sid[s.feeder], C.ascS), hh = HOUSES[supply - 1], pos = C.sid[s.feeder];
  const max = Math.max(...s.ratios.map(r => r[0]));
  const bars = s.ratios.map(([r, lab]) =>
    `<div class="hb-barrow"><div class="hb-track"><i style="width:${(r / max * 100).toFixed(1)}%;background:${s.band}"></i></div><span>${lab} · ${(s.hz * r).toFixed(1)} Hz</span></div>`).join("");
  read.innerHTML = `
    <div class="hb-card" style="--band:${s.band}">
      <div class="hb-chip">${s.roman} · ${s.place}</div>
      <h3>${s.world}</h3>
      <div class="hb-rom">${s.station} · ${s.bifrost}</div>
      <p class="kenning">${s.kenning}</p>
      <dl>
        <dt>Operator</dt><dd>${s.operator}<small>${s.opGloss}</small></dd>
        <dt>Fed by</dt><dd>${GLYPH[s.feeder]} ${s.feeder} · ${s.hz.toFixed(2)} Hz<small>Planetary ladder</small></dd>
        <dt>Supply line</dt><dd>House ${supply}${hh && hh.color ? " · " + hh.color : ""}<small>${s.feeder} at ${signOf(pos)} ${degIn(pos).toFixed(2)}°. This station eats that house's colour.</small></dd>
        <dt>Design centre</dt><dd>${s.hd}</dd>
      </dl>
      <div class="hb-ask"><b>Descent scan</b><p>${s.ask}</p></div>
      <div class="hb-bars"><h4>Chord · ratio staff</h4>${bars}</div>
      <button class="hb-btn" data-hb-replay="${s.id}">Sound the chord again</button>
    </div>`;
  drawBars();
}
/* the bars grow one after another, in step with the chord blooming */
function drawBars(){
  const rows = read.querySelectorAll(".hb-barrow");
  rows.forEach(r => r.classList.remove("drawn"));
  rows.forEach((r, i) => setTimeout(() => r.classList.add("drawn"), 60 + i * 90));
}
function paintNak(){
  root.querySelectorAll(".znak").forEach(n => {
    const on = nkFocus !== null && +n.dataset.hbNak === nkFocus;
    n.classList.toggle("lit", on); n.classList.toggle("dim", nkFocus !== null && !on);
  });
  if (nkFocus === null){ read.innerHTML = idleRead(); return; }
  const k = nkFocus, e = ENGINE[k], nk = NAKSHATRA[k], a0 = k * NAK_ARC, a1 = a0 + NAK_ARC;
  const padaOf = l => Math.floor((norm(l) % NAK_ARC) / (NAK_ARC / 4)) + 1;
  const inside = BODIES().filter(b => { const s = norm(C.sid[b]); return s >= a0 && s < a1; });
  const asc = norm(C.ascS) >= a0 && norm(C.ascS) < a1;
  const here = (asc ? [`Lagna · pada ${padaOf(C.ascS)}`] : []).concat(inside.map(b => `${GLYPH[b]} ${b} · pada ${padaOf(C.sid[b])}`));
  read.innerHTML = `
    <div class="hb-card" style="--band:var(--jade)">
      <div class="hb-chip">Mansion ${k + 1} of 27</div>
      <h3>${nk[0]}</h3>
      <div class="hb-rom">${signOf(a0)} ${degIn(a0).toFixed(0)}° to ${signOf(a1)} ${degIn(a1).toFixed(0)}° · lord ${nk[1]} · ${nk[4]}</div>
      <dl>
        ${e && e[1] ? `<dt>Shakti</dt><dd>${e[1]}<small>${e[2]}</small></dd>` : ""}
        ${e && e[3] ? `<dt>Above / below</dt><dd>${e[3]} over ${e[4]}</dd>` : ""}
        ${e && e[5] ? `<dt>Result</dt><dd>${e[5]}</dd>` : ""}
        <dt>Standing here</dt><dd>${here.length ? here.join("<br>") : "nothing in this chart"}</dd>
      </dl>
    </div>`;
}

/* ---------- moving it ---------- */
function setPose(tilt, turn, animate){
  pose.tilt = Math.max(-78, Math.min(0, tilt));
  pose.turn = Math.max(-50, Math.min(50, turn));
  deck.style.transition = animate ? "transform 1200ms var(--ease)" : "none";
  deck.style.transform = `rotateX(${pose.tilt}deg) rotateY(${pose.turn}deg)`;
  root.querySelectorAll("[data-hb-view]").forEach(b => {
    const v = b.dataset.hbView;
    b.classList.toggle("on", (v === "up" && pose.tilt === 0 && pose.turn === 0) || (v === "tilt" && pose.tilt === -52 && pose.turn === 0));
  });
}
function bindDrag(stage){
  let start = null;
  stage.addEventListener("pointerdown", e => {
    start = { x: e.clientX, y: e.clientY, tilt: pose.tilt, turn: pose.turn, moved: false, touch: e.pointerType === "touch" };
  });
  addEventListener("pointermove", e => {
    if (!start) return;
    const dx = e.clientX - start.x, dy = e.clientY - start.y;
    if (!start.moved && Math.hypot(dx, dy) < 6) return;
    if (!start.moved){
      /* on a phone, a mostly vertical drag is a page scroll, so only turn */
      if (start.touch && Math.abs(dy) > Math.abs(dx)){ start = null; return; }
      start.moved = true; stage.classList.add("dragging");
    }
    setPose(start.touch ? start.tilt : start.tilt - dy * 0.35, start.turn + dx * 0.25, false);
  }, { passive: true });
  const end = () => {
    if (start && start.moved){ stage.dataset.justDragged = "1"; setTimeout(() => delete stage.dataset.justDragged, 50); }
    stage.classList.remove("dragging"); start = null;
  };
  addEventListener("pointerup", end); addEventListener("pointercancel", end);
}

/* ---------- the torus field ----------
   The body's own field: it bursts from the crown, falls around both sides in
   nested loops, is drawn back in beneath the feet and rises up the central axis
   to the crown again. Bursts mark where it breaks out: crown, root and feet. */
const AXIS = { x: 450, crown: 150, root: ST[ST.length - 1].y, feet: Math.round(ETCH.y + ETCH.feet * ETCH.s) };
function torusSVG(){
  const { x, crown, feet } = AXIS, loops = [95, 150, 205, 262, 320];
  let o = `<defs><radialGradient id="hbBurst"><stop offset="0" stop-color="rgba(222,236,228,.9)"/><stop offset=".35" stop-color="rgba(95,156,134,.45)"/>
    <stop offset="1" stop-color="rgba(95,156,134,0)"/></radialGradient></defs>`;
  loops.forEach((w, i) => {
    for (const side of [1, -1]){
      const X = k => (x + side * w * k).toFixed(1);
      const d = `M${x},${crown} C${X(.55)},${crown - 120 + i * 8} ${X(1.12)},${crown + 40} ${X(1)},${(crown + feet) / 2} C${X(.92)},${feet - 40} ${X(.5)},${feet + 70 - i * 6} ${x},${feet}`;
      o += `<path d="${d}" class="tf-line"/><path d="${d}" pathLength="200" class="tf-flow" style="animation-delay:${(-i * 1.1 - (side > 0 ? 0 : .55)).toFixed(2)}s"/>`;
    }
  });
  o += `<path d="M${x},${feet} L${x},${crown}" class="tf-line axis"/><path d="M${x},${feet} L${x},${crown}" pathLength="200" class="tf-flow axis"/>`;
  for (const [y, r] of [[crown, 46], [AXIS.root, 30], [feet, 40]])
    o += `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#hbBurst)" class="tf-burst"/>`;
  return o;
}

/* ---------- mount ---------- */
function mount(host, chart){
  C = chart; root = host;
  const BM = C.bodyMap || {}, KEY = ["crown", "brow", "throat", "heart", "solar", "sacrum", "root"];
  W8 = {}; HEAVY = [];
  if (BM.weights) ST.forEach((s, i) => { if (BM.weights[KEY[i]] != null) W8[s.id] = BM.weights[KEY[i]]; });
  if (BM.heavy) HEAVY = BM.heavy.map(k => ST[KEY.indexOf(k)]).filter(Boolean).map(s => s.id); woken = new Set(); last = null; nkFocus = null; stopScan();
  host.classList.add("hb");
  host.innerHTML = `
    <div class="hb-ctl">
      <button class="hb-btn on" data-hb-view="up">Upright</button>
      <button class="hb-btn" data-hb-view="tilt">Tilted</button>
      <button class="hb-btn on" data-hb-toggle="zod" aria-pressed="true">Two zodiacs</button>
      <button class="hb-btn on" data-hb-toggle="torus" aria-pressed="true">Torus field</button>
      <button class="hb-btn" data-hb-scan>Descent scan</button>
      <button class="hb-btn" data-hb-clear>Clear</button>
    </div>
    <div class="hb-stage" id="hbStage">
      <div class="hb-deck" id="hbDeck">
        <svg class="hb-layer hb-zod" viewBox="0 0 900 900" aria-label="The two zodiacs around the body">${zodiacSVG()}</svg>
        <svg class="hb-layer hb-torus" viewBox="0 0 900 900" aria-hidden="true">${torusSVG()}</svg>
        <svg class="hb-layer hb-fig" viewBox="0 0 900 900" role="img" aria-label="The harmonic body">
          ${FIGURE}<g class="hb-centres" id="hbCentres">${centresSVG()}</g></svg>
        <svg class="hb-layer hb-top" viewBox="0 0 900 900" aria-label="The seven stations and the planets that feed them">
          <g id="hbSpine"></g>${stationsSVG()}</svg>
      </div>
    </div>
    <p class="hb-hint">Drag to turn the figure${matchMedia("(pointer:fine)").matches ? " and tip it back" : ""}. The rings, the body and the stations sit at different depths.</p>
    ${C.bodyMap && C.bodyMap.line ? `<p class="hb-gather">${C.bodyMap.line} <small>The glow round each station is how much of your chart lands there.</small></p>` : ""}
    <p class="hb-intro">The same body seen another way. The Harmonic Body is an old anatomy engraving with seven stations from crown to root, each fed by one of your planets, standing beside it on its own thread; the label under each planet is the house it stands in, which gives that station its colour. Your design's centres and live channels sit on the figure too, following the Birth / Dharma switch above. The seven stations and the nine design centres are different maps: the Heart station is not the Heart centre. Around the figure is its torus field, and the two zodiacs: tropical outside, sidereal inside, offset by the ayanamsa, with the twenty-seven mansions on the inner ring.</p>
    <p class="hb-credit">Engraving by J. Caldwall after John Brisbane, <i>The Anatomy of Painting</i>, 1769.</p>
    <div class="hb-strip" role="group" aria-label="The seven stations">${ST.map(s =>
      `<button class="hb-chipbtn" data-hb-station="${s.id}" style="--band:${s.band}"><i></i>${s.roman} · ${s.station}<span>${GLYPH[s.feeder]} ${s.feeder}</span></button>`).join("")}</div>
    <div class="hb-read" id="hbRead" aria-live="polite">${idleRead()}</div>`;
  deck = host.querySelector("#hbDeck"); read = host.querySelector("#hbRead");
  host.querySelector(".hb-zod").classList.toggle("off", !showZod);
  host.querySelector(".hb-torus").classList.toggle("off", !showTorus);
  host.querySelector('[data-hb-toggle="torus"]').classList.toggle("on", showTorus);
  host.querySelector('[data-hb-toggle="torus"]').setAttribute("aria-pressed", showTorus);
  host.querySelector(".hb-centres").classList.toggle("on", showRave || showDharma);
  host.querySelector('[data-hb-toggle="zod"]').classList.toggle("on", showZod);
  setPose(0, 0, false);
  bindDrag(host.querySelector("#hbStage"));
}

/* one listener for the whole section */
document.addEventListener("click", e => {
  if (!root || !root.contains(e.target)) return;
  const stage = root.querySelector("#hbStage");
  if (stage && stage.dataset.justDragged) return;
  const t = e.target;
  const v = t.closest("[data-hb-view]");
  if (v){ setPose(v.dataset.hbView === "tilt" ? -52 : 0, 0, true); return; }
  const tg = t.closest("[data-hb-toggle]");
  if (tg){
    const k = tg.dataset.hbToggle;
    if (k === "zod"){ showZod = !showZod; root.querySelector(".hb-zod").classList.toggle("off", !showZod); tg.classList.toggle("on", showZod); tg.setAttribute("aria-pressed", showZod); root.classList.toggle("zod-on", showZod); return; }
    if (k === "torus"){ showTorus = !showTorus; root.querySelector(".hb-torus").classList.toggle("off", !showTorus); tg.classList.toggle("on", showTorus); tg.setAttribute("aria-pressed", showTorus); return; }
    if (k === "rave") showRave = !showRave; else showDharma = !showDharma;
    const on = k === "rave" ? showRave : showDharma;
    tg.classList.toggle("on", on); tg.setAttribute("aria-pressed", on);
    root.querySelector("#hbCentres").innerHTML = centresSVG();
    root.querySelector("#hbCentres").classList.toggle("on", showRave || showDharma);
    return;
  }
  if (t.closest("[data-hb-scan]")){
    if (scanTimer){ stopScan(); return; }
    sleepAll(); scanIdx = 0;
    const b = t.closest("[data-hb-scan]"); b.classList.add("on"); b.textContent = "Stop scan";
    stepScan(); return;
  }
  if (t.closest("[data-hb-clear]")){ nkFocus = null; paintNak(); sleepAll(); return; }
  const rp = t.closest("[data-hb-replay]");
  if (rp){ const s = ST.find(x => x.id === rp.dataset.hbReplay); if (s){ Sound.chord(s.ratios.map(r => s.hz * r[0])); drawBars(); } return; }
  const st = t.closest("[data-hb-station]");
  if (st){ stopScan(); nkFocus = null; root.querySelectorAll(".znak").forEach(n => n.classList.remove("lit", "dim")); wake(st.dataset.hbStation); return; }
  const nk = t.closest("[data-hb-nak]");
  if (nk){ const k = +nk.dataset.hbNak; nkFocus = nkFocus === k ? null : k; paintNak(); return; }
});
document.addEventListener("keydown", e => {
  if (!root || !root.contains(e.target) || (e.key !== "Enter" && e.key !== " ")) return;
  const el = e.target.closest("g[data-hb-station], g[data-hb-nak]");
  if (el){ e.preventDefault(); el.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
});

/* the Your design land's switch: which design's centres and channels sit on the figure */
function setDesign(v){
  showRave = v !== "dharma"; showDharma = v !== "birth" && !!(C && C.dharma);
  const g = root && root.querySelector("#hbCentres"); if (!g) return;
  g.innerHTML = centresSVG(); g.classList.toggle("on", showRave || showDharma);
}
window.WyrdBody = { mount, setDesign, centres: HB_CENTRES, channels: HB_CHANNELS, runsFrom };
})();
