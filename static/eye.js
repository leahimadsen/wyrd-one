'use strict';
/* ============================================================
   ODIN'S EYE
   The chart page's opening picture: the world tree seen from
   above and a little to one side, laid out as the codex's plates
   lay it. Five worlds stand on the axis, Asgard at the topmost
   bough to Hel where the roots meet; four stand on the ring round
   Midgard, Niflheim north, Jötunheim east, Muspelheim south,
   Vanaheim west. The ring is Jötunheim's shell: a flattened torus
   cut into the twelve houses, the runes round its top, the
   planets on its rim at their degrees. It turns freely, as the
   torus does; tapping it opens that torus. The seven Ladder
   worlds carry the Harmonic Body's stations and soul parts.
   Plain canvas, no library.
   Depends on viz.js for STATIONS and HOUSES, and Wyrd.helpers.
   ============================================================ */
(() => {
const TAU = Math.PI * 2, RAD = Math.PI / 180, VS = "︎";
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
/* the house colours and the runes, as the console seats them: two runes to a house, Fehu and Uruz in the 1st */
const HOUSE = HOUSES.map(h => h.hex);
const RUNES = HOUSES.flatMap(h => [h.ingress, h.egress]);
const BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
const OUTER = new Set(["Uranus","Neptune","Pluto"]);
const FEEDS = Object.fromEntries([...STATIONS.map(s => [s.feeder, s.id]), ["Rahu", "above"], ["Ketu", "below"]]);
const norm = x => ((x % 360) + 360) % 360;
/* the chart, set when the eye is mounted */
let ASC = 0, CUSP = 0, PL = [], UNKNOWN = false, NAK = [], GLYPH = {}, LIT = new Set();
const houseOf = lon => Math.floor(norm(lon - CUSP) / 30);           /* 0 = the 1st */
const runeOf = lon => Math.floor(norm(lon - CUSP) / 15);            /* 0 = Fehu */
const nakOf = lon => Math.floor(norm(lon) / (360 / 27));
const ORD = n => n + ((n % 100 > 10 && n % 100 < 14) ? "th" : ["th","st","nd","rd"][n % 10] || "th");
const deg = l => { const s = Math.floor(norm(l) / 30), d = norm(l) - s * 30; let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; }
  return `${a}°${String(m).padStart(2, "0")}′ ${SIGNS[s]}`; };

/* ---------------- the plan ----------------
   The axis stands upright down the middle; the ring lies flat round Midgard and is seen at a
   slant, so its far side is higher on the page. Laid out on a 1000 × 1280 plan, scaled to the canvas. */
const PW = 1000, PH = 1280, CX = 500, MY = 640;
const K = .4, LIFT = Math.sqrt(1 - K * K);          /* the ring's depth shows at 40%; heights at 92% */
const SH = { R: 290, a: 118, b: 30 };               /* Jötunheim's shell: a flattened torus round the hub */
const NAK_R = 452, COMPASS_R = 538;
const EGG = { rx: 300, ry: 405 };
const PLATE = { y: MY, rx: 124, ry: 50 };
const CROWN = { x: 500, y: 455, rx: 282, ry: 222 }, TOP = 560, ROOT = 1000;
/* a point on the ring: azimuth u, distance rho from the axis, height h above the ring's plane */
const P3 = (rho, h, u) => [CX + rho * Math.cos(u), MY + rho * Math.sin(u) * K - h * LIFT, rho * Math.sin(u) * LIFT + h * K];
/* the shell turns freely: the houses are not tied to the compass. It starts with the middle of
   the 1st house facing you; rot is how far it has turned since. */
let rot = 0, spin = reduce ? 0 : .09, still = 0;
const az = lon => (105 - norm(lon - CUSP)) * RAD + rot;

/* the five on the axis and the four on the ring. The seven Ladder worlds carry the Harmonic
   Body's stations and soul parts; Jötunheim keeps Sjálfr and Niflheim takes Lík, from the plates. */
const ST = Object.fromEntries(STATIONS.map(s => [s.id, s]));
const W = [
  { id:"asgard", on:"Ásgarðr", where:"On the axis: the topmost bough", at:[500, 276], col:"#b05cff", ring:44 },
  { id:"alfheim", on:"Álfheimr", where:"On the axis, in the crown", at:[500, 420], col:"#6b6bff", ring:58 },
  { id:"midgard", on:"Miðgarðr", where:"The hub, where the axis crosses the ring", at:[500, MY], col:"#22e07a", ring:0 },
  { id:"nidavellir", on:"Niðavellir", where:"On the axis, low on the trunk", at:[500, 852], col:"#ff8c1a", ring:86 },
  { id:"hel", on:"Helheimr", where:"On the axis, where the roots meet", at:[500, 1005], col:"#ff3b4e", ring:104 },
  { id:"niflheim", name:"Niflheim", on:"Niflheimr", soul:"Lík", gloss:"the body", where:"On the ring, north", az:225, col:"#d9fbff", gate:true,
    ken:"Mist and ice in the north. Snorri puts the well Hvergelmir here, under one of the three roots." },
  { id:"jotunheim", name:"Jötunheim", on:"Jötunheimr", soul:"Sjálfr", gloss:"the self", where:"On the ring, east; and the shell itself", az:315, col:"#b4c0d4", gate:true },
  { id:"muspelheim", on:"Muspellsheimr", where:"On the ring, south", az:45, col:"#ffd400", gate:true },
  { id:"vanaheim", on:"Vanaheimr", where:"On the ring, west", az:135, col:"#22b8ff", gate:true },
];
for (const w of W){
  const s = ST[w.id];
  if (s){ w.name = s.world; w.soul = s.operator; w.gloss = s.opGloss; w.col = s.band; }
  if (w.gate){ w.u = w.az * RAD; w.base = P3(SH.R, SH.b, w.u); w.front = Math.sin(w.u) > 0; w.out = Math.sign(Math.cos(w.u)); }
}
const COMPASS = [["N", 225], ["E", 315], ["S", 45], ["W", 135]];
const POLES = { above:{ at:[500, 112] }, below:{ at:[500, 1254] } };
const WELLS = [
  { id:"hvergelmir", name:"Hvergelmir", at:[165, 1112], on:"the roaring kettle · under the root to Niflheim", body:"the blood: the heart and the vessels",
    ken:"Every river runs out of it, and the serpent Níðhöggr gnaws the root above it from below." },
  { id:"urdr", name:"Urðarbrunnr", at:[500, 1182], on:"Urðr's well · under the root Snorri puts in heaven", body:"the lymph, and the fluid in the joints",
    ken:"The Norns live by it, and every day they water the tree from it so that its limbs do not wither." },
  { id:"mimir", name:"Mímisbrunnr", at:[835, 1112], on:"Mímir's well · under the root toward the frost giants", body:"the fluid round the brain and the spine",
    ken:"Wisdom and understanding are hidden in it. Odin pledged an eye for a drink from it." },
];
const SAL = { at:[500, 178] };
const byId = id => W.find(w => w.id === id) || WELLS.find(w => w.id === id);
const plOf = name => PL.find(p => p[0] === name);

/* ---------------- growing the tree ----------------
   Each half of the crown, and each half of the roots, is grown backwards from its tips: tips spread
   evenly round the edge of the crown (or along the ground), then neighbours are joined pair by pair
   into ever larger limbs that meet at the trunk, so every limb tapers by how much it carries. */
let seed = 23; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
function half(kind, side){
  const N = kind === "crown" ? 64 : 24, tips = [];
  for (let i = 0; i < N; i++){
    const s = (i + .5) / N + (rnd() - .5) * .45 / N;
    let x, y;
    if (kind === "crown"){
      const phi = (-90 - s * 86) * RAD, k = .86 + rnd() * .14;
      x = CROWN.x + CROWN.rx * k * Math.cos(phi); y = CROWN.y + CROWN.ry * k * Math.sin(phi);
    } else {
      x = CX - 34 - s * 316; y = 1050 + 74 * Math.pow(1 - s, 1.4) + (rnd() - .5) * 10;
      if (i === N - 1){ x = WELLS[0].at[0]; y = WELLS[0].at[1] - 6; }
    }
    if (side > 0) x = 2 * CX - x;
    tips.push({ x, y, mx: x, my: y, count: 1, kids: [] });
  }
  const join = list => {
    if (list.length === 1) return list[0];
    const k = Math.max(1, Math.min(list.length - 1, Math.round(list.length * (.34 + rnd() * .32))));
    const a = join(list.slice(0, k)), b = join(list.slice(k)), n = a.count + b.count;
    return { kids: [a, b], count: n, mx: (a.mx * a.count + b.mx * b.count) / n, my: (a.my * a.count + b.my * b.count) / n };
  };
  const root = join(tips), base = kind === "crown" ? [CX + side * 12, TOP] : [CX + side * 16, ROOT - 4], LN = Math.log(N);
  const place = n => {
    if (n.kids.length){
      const t = Math.pow(1 - Math.log(n.count) / LN, kind === "crown" ? .78 : .85);
      n.x = base[0] + (n.mx - base[0]) * t; n.y = base[1] + (n.my - base[1]) * t;
    }
    n.kids.forEach(place);
  };
  place(root); root.x = base[0]; root.y = base[1];
  return { root, kind, side: side < 0 ? "L" : "R", init: kind === "crown" ? [0, -1] : [0, 1] };
}
const HALVES = [half("crown", -1), half("crown", 1), half("root", -1), half("root", 1)];
const STRANDS = Array.from({ length: 22 }, (_, i) => ({ i, f: i / 21 }));
const STARS = Array.from({ length: 220 }, () => [rnd() * PW, rnd() * PH, rnd() * 1.2 + .3, rnd()]);
const BRIGHT = Array.from({ length: 14 }, () => [rnd() * PW, rnd() * PH * .94, 2 + rnd() * 2.5, rnd()]);
/* constellations in the empty corners, drawn as the hub world draws them (decoration only) */
const CONST = [[120, 120], [880, 110], [110, 1215], [890, 1210]].map(([cx, cy], n) => {
  const pts = [], k = 6 + (n % 3);
  for (let i = 0; i < k; i++) pts.push([cx + (rnd() - .5) * 170, cy + (rnd() - .5) * 120]);
  pts.sort((a, b) => a[0] - b[0]);
  const edges = pts.slice(1).map((p, i) => [i, i + 1]); edges.push([1, Math.min(k - 1, 4)]);
  return { pts, edges };
});
function rock(cx, cy, w, h){
  const top = [], bot = [];
  for (let i = 0; i <= 14; i++){ const u = i / 14 * 2 - 1; top.push([cx + u * w / 2, cy - Math.abs(Math.sin(i * 1.7)) * 5 - (1 - u * u) * 4]); }
  for (let i = 14; i >= 0; i--){ const u = i / 14 * 2 - 1; bot.push([cx + u * w / 2 * (.96 - .1 * rnd()), cy + h * (.18 + .82 * Math.pow(1 - Math.abs(u), 1.6)) * (.75 + rnd() * .35)]); }
  return { cx, cy, w, h, top, bot, ph: rnd() * TAU };
}
const ROCKS = [rock(92, 300, 100, 58), rock(912, 290, 90, 54), rock(84, 955, 84, 50), rock(918, 950, 104, 60), rock(300, 1240, 64, 34), rock(706, 1244, 60, 32)];

/* ---------------- the living wood ---------------- */
const WOOD = { wood:"#d8f6ff", root:"#bfeeff", pulse:"#ffe7a8", halo:"120,220,255" };
const rgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const rgba = (h, a) => { const [r, g, b] = rgb(h); return `rgba(${r},${g},${b},${a})`; };
const norm2 = (x, y) => { const l = Math.hypot(x, y) || 1; return [x / l, y / l]; };

let mode = "shell", names = "realms", sel = null;

function curve(p, c, dir){                 /* a limb: leaves its parent the way the parent was going, then bends to its tip */
  const d = Math.hypot(c[0] - p[0], c[1] - p[1]), to = norm2(c[0] - p[0], c[1] - p[1]);
  const k = norm2(dir[0] * .62 + to[0] * .38, dir[1] * .62 + to[1] * .38);
  const q = [p[0] + k[0] * d * .5, p[1] + k[1] * d * .5], pts = [];
  for (let i = 0; i <= 10; i++){ const t = i / 10, u = 1 - t;
    pts.push([u * u * p[0] + 2 * u * t * q[0] + t * t * c[0], u * u * p[1] + 2 * u * t * q[1] + t * t * c[1]]); }
  return pts;
}
function bez(a, b, c, d, n){
  const pts = [];
  for (let i = 0; i <= n; i++){ const t = i / n, u = 1 - t;
    pts.push([u*u*u*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t*t*t*d[0], u*u*u*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t*t*t*d[1]]); }
  return pts;
}

/* every line goes into a few big paths, grouped by colour, width and depth:
   0 behind Midgard's plate and the near side of the shell, 1 above the plate, 2 in front of everything */
let LAYERS, PULSE_PATHS;
function layer(col, w, z){ const key = col + "|" + w + "|" + z; return LAYERS[key] || (LAYERS[key] = { col, w, z, path: new Path2D() }); }
function addLine(pts, col, w, z){ const L = layer(col, Math.round(w * 4) / 4, z).path; pts.forEach((p, i) => i ? L.lineTo(p[0], p[1]) : L.moveTo(p[0], p[1])); }
function build(){
  LAYERS = {}; PULSE_PATHS = [];
  for (const H of HALVES){
    const crown = H.kind === "crown", z = crown ? 1 : 0, col = crown ? WOOD.wood : WOOD.root;
    const width = n => (crown ? .45 : .55) + .3 * Math.sqrt(n.count);
    const walk = (n, dir, chain) => {
      n.kids.forEach(c => {
        const pts = curve([n.x, n.y], [c.x, c.y], dir);
        addLine(pts, col, width(c), z);
        const nd = norm2(pts[pts.length - 1][0] - pts[pts.length - 2][0], pts[pts.length - 1][1] - pts[pts.length - 2][1]);
        const next = chain.concat(pts.slice(chain.length ? 1 : 0));
        if (!c.kids.length){
          /* twigs at every tip */
          for (const a of [-.55, 0, .5]){ const l = 9 + rnd() * 14, d = [nd[0] * Math.cos(a) - nd[1] * Math.sin(a), nd[0] * Math.sin(a) + nd[1] * Math.cos(a)];
            addLine([[c.x, c.y], [c.x + d[0] * l, c.y + d[1] * l]], col, .55, z); }
          PULSE_PATHS.push({ pts: next, rev: !crown, z });
        }
        walk(c, nd, next);
      });
    };
    walk(H.root, H.init, []);
  }
  /* the central root to Urðarbrunnr */
  { const pts = curve([CX, ROOT], [CX, WELLS[1].at[1] - 8], [0, 1]);
    addLine(pts, WOOD.root, 2.2, 0); PULSE_PATHS.push({ pts, rev: true, z: 0 }); }
  /* the trunk: a bundle of strands */
  for (const st of STRANDS){
    const x0 = CX - 82 + st.f * 164, x1 = CX - 30 + st.f * 60, pts = [];
    for (let k = 0; k <= 40; k++){ const t = k / 40;
      pts.push([x0 + (x1 - x0) * Math.pow(t, .55) + Math.sin(t * 7 + st.i * .8) * 4.5 * (1 - t * .5), ROOT + 6 + (TOP - ROOT - 6) * t]); }
    /* split at the plate so the plate can hide the trunk behind it */
    const lo = [], hi = [];
    for (let k = 0; k < pts.length; k++){
      const p = pts[k]; (p[1] >= PLATE.y ? lo : hi).push(p);
      const q = pts[k + 1]; if (q && (p[1] - PLATE.y) * (q[1] - PLATE.y) < 0){ const t = (PLATE.y - p[1]) / (q[1] - p[1]), m = [p[0] + (q[0] - p[0]) * t, PLATE.y]; lo.push(m); hi.unshift(m); }
    }
    addLine(lo, WOOD.wood, 1.15, 0); addLine(hi.sort((a, b) => b[1] - a[1]), WOOD.wood, 1.15, 1);
    PULSE_PATHS.push({ pts, rev: false, z: 0, trunk: true });
  }
  /* the four great limbs: "the plexi reach out as the branches of Yggdrasil, descending and rising again".
     Each leaves the trunk at the hub, dips, and rises to its world's gate on the shell. */
  for (const w of W.filter(w => w.gate)){
    const z = w.front ? 2 : 0, [ex, ey] = w.base, sx = CX + w.out * 10, sy = MY - 4, dx = ex - sx;
    for (let s = -2; s <= 2; s++){
      const st = [sx, sy + s * 3.4], en = [ex + s * 5, ey + Math.abs(s) * 1.5];
      const pts = bez(st, [st[0] + dx * .32, st[1] + 66], [en[0] - dx * .22, en[1] + 54], en, 28);
      addLine(pts, WOOD.wood, 1.35 - Math.abs(s) * .22, z);
      if (!s) PULSE_PATHS.push({ pts, rev: false, z, limb: true });
    }
  }
}

/* ---------------- Jötunheim's shell ----------------
   A flattened torus lying round the hub. Its surface is cut into your twelve houses in their colours;
   the 24 runes run round its top, two to a house; the planets stand on its outer rim at their degrees.
   Built once into paths: the far half is drawn behind the tree, the near half in front of it. */
const NU = 144, NV = 20, SEGU = TAU / NU;
const tubePt = (u, v) => P3(SH.R + SH.a * Math.cos(v), SH.b * Math.sin(v), u);
const facing = (u, v) => { const nr = SH.b * Math.cos(v), nh = SH.a * Math.sin(v), l = Math.hypot(nr, nh); return (nr * Math.sin(u) * LIFT + nh * K) / l; };
let SHELL;
function buildShell(){
  /* the surface never moves (a torus turned about its axis is the same torus); only which house
     each strip of it belongs to changes as it turns, so the strips are built once and regrouped */
  const mk = () => ({ dark: new Path2D(), top: new Path2D(), inner: new Path2D(), segs: [] }), G = { back: mk(), front: mk() };
  const quad = (P, a, b, c, d) => { P.moveTo(a[0], a[1]); P.lineTo(b[0], b[1]); P.lineTo(c[0], c[1]); P.lineTo(d[0], d[1]); P.closePath(); };
  const line = (P, a, b) => { P.moveTo(a[0], a[1]); P.lineTo(b[0], b[1]); };
  for (let i = 0; i < NU; i++){
    const u0 = i * SEGU, u1 = (i + 1) * SEGU, um = (u0 + u1) / 2, g = Math.sin(um) > 0 ? G.front : G.back;
    const seg = { um, lv: [0, 1, 2, 3].map(() => new Path2D()), rim: null };
    for (let j = 0; j < NV; j++){
      const v0 = j / NV * TAU, v1 = (j + 1) / NV * TAU, f = facing(um, (v0 + v1) / 2);
      if (f < -.02) continue;
      const a = tubePt(u0, v0), b = tubePt(u1, v0), c = tubePt(u1, v1), d = tubePt(u0, v1);
      quad(g.dark, a, b, c, d); quad(seg.lv[Math.max(0, Math.min(3, Math.floor((1 - f) * 4)))], a, b, c, d);
    }
    if (facing(um, 0) > 0){ seg.rim = new Path2D(); line(seg.rim, tubePt(u0, 0), tubePt(u1, 0)); }
    line(g.top, tubePt(u0, Math.PI / 2), tubePt(u1, Math.PI / 2));
    if (facing(um, Math.PI) > 0) line(g.inner, tubePt(u0, Math.PI), tubePt(u1, Math.PI));
    g.segs.push(seg);
  }
  SHELL = { G, step: null };
}
function paintShell(){
  /* group the strips by house for the turn the shell is at, to the nearest strip */
  const step = Math.round(rot / SEGU);
  if (SHELL.step === step) return;
  SHELL.step = step;
  for (const part of ["back", "front"]){
    const g = SHELL.G[part], glow = {}, rim = {};
    for (const sg of g.segs){
      const h = houseOf(CUSP + 105 - (sg.um - step * SEGU) / RAD);
      sg.lv.forEach((P, l) => { const k = h + "|" + l; (glow[k] || (glow[k] = { h, l, path: new Path2D() })).path.addPath(P); });
      if (sg.rim) (rim[h] || (rim[h] = new Path2D())).addPath(sg.rim);
    }
    g.glow = glow; g.rim = rim;
  }
}
const GLOW_A = [.05, .085, .14, .22];
function shell(part, time, z){
  paintShell();
  const g = SHELL.G[part], back = part === "back", sz = Math.sqrt(z), f = back ? .7 : 1;
  const mine = u => (Math.sin(u) > 0) !== back;
  const stroke = (P, col, w, al) => { ctx.strokeStyle = rgba(col, al * .16); ctx.lineWidth = w * 4 / sz; ctx.stroke(P); ctx.strokeStyle = rgba(col, al); ctx.lineWidth = w / sz; ctx.stroke(P); };
  ctx.fillStyle = "rgba(9,3,28,.84)"; ctx.fill(g.dark);
  ctx.globalCompositeOperation = "lighter";
  for (const q of Object.values(g.glow)){ ctx.fillStyle = rgba(HOUSE[q.h], GLOW_A[q.l] * (back ? .75 : 1)); ctx.fill(q.path); }
  /* the rim in the house colours; a gold line round the top; the inner edge in cyan */
  for (const [h, P] of Object.entries(g.rim)) stroke(P, HOUSE[h], 2.2, .95 * f);
  stroke(g.top, "#ffcf7a", 1, .5 * f); stroke(g.inner, "#9ff3ff", 1, .45 * f);
  /* a meridian round the tube at every house's first degree, and a gold one at your rising degree */
  const meridian = (u, col, w, al) => { const P = new Path2D();
    for (let j = 0; j < NV; j++){ const v0 = j / NV * TAU, v1 = (j + 1) / NV * TAU;
      if (facing(u, (v0 + v1) / 2) > 0){ const a = tubePt(u, v0), b = tubePt(u, v1); P.moveTo(a[0], a[1]); P.lineTo(b[0], b[1]); } }
    stroke(P, col, w, al); };
  for (let h = 0; h < 12; h++){ const u = az(CUSP + h * 30); if (mine(u)) meridian(u, "#ffd6f4", 1, .55 * f); }
  if (!UNKNOWN){ const u = az(ASC); if (mine(u)) meridian(u, "#ffb43a", 2.4, f); }
  /* the runes, in gold; brighter where a planet stands */
  const glow = .78 + .22 * Math.sin(time * 1.3);
  ctx.font = "25px 'Noto Sans Runic','Segoe UI Historic','Segoe UI Symbol',sans-serif"; ctx.textAlign = "center";
  for (let k = 0; k < 24; k++){
    const u = az(CUSP + k * 15 + 7.5); if (!mine(u)) continue;
    const [x, y] = P3(SH.R - 6, SH.b, u), lit = LIT.has(k), a = (back ? .62 : 1) * glow;
    ctx.save(); ctx.translate(x, y); ctx.scale(1, .5);
    ctx.fillStyle = lit ? `rgba(255,236,190,${.35 * a})` : `rgba(255,190,80,${.22 * a})`; ctx.fillText(RUNES[k][0], 1.2, 10);
    ctx.fillStyle = lit ? `rgba(255,246,222,${a})` : `rgba(255,206,120,${.86 * a})`; ctx.fillText(RUNES[k][0], 0, 9);
    ctx.restore();
  }
  ctx.font = "700 17px 'Space Mono', monospace";
  for (let h = 0; h < 12; h++){
    const u = az(CUSP + h * 30 + 15); if (!mine(u)) continue;
    const [x, y] = P3(SH.R + SH.a * .8, SH.b * .6, u);
    ctx.save(); ctx.translate(x, y); ctx.scale(1, .62); ctx.fillStyle = rgba(HOUSE[h], back ? .7 : .95); ctx.fillText(h + 1, 0, 5); ctx.restore();
  }
  /* light moving round the shell */
  if (!reduce) for (let k = 0; k < 3; k++){
    const u = time * .22 + k * TAU / 3; if (!mine(u)) continue;
    for (let t = 0; t < 7; t++){ const [x, y] = P3(SH.R + SH.a, 0, u - t * .018);
      ctx.fillStyle = `rgba(255,240,200,${(.8 - t * .11) * (back ? .55 : 1)})`; ctx.beginPath(); ctx.arc(x, y, (3 - t * .35) / sz, 0, TAU); ctx.fill(); }
  }
  ctx.globalCompositeOperation = "source-over";
}
/* is a point behind the near side of the shell? (for the light running up the trunk) */
const behindShell = pt => { const dx = pt[0] - CX, dy = pt[1] - MY; if (dy <= 0) return false; const r = Math.hypot(dx, dy / K); return r > 168 && r < 412; };
const underPlate = pt => pt[1] > PLATE.y && Math.pow((pt[0] - CX) / PLATE.rx, 2) + Math.pow((pt[1] - PLATE.y) / PLATE.ry, 2) < 1;

/* ---------------- drawing ---------------- */
let cv = null, ctx = null, drag = null, dragged = false;
let Wpx = 720, Hpx = 922, dpr = 1, scale = .72;
let cam = { x: PW / 2, y: PH / 2, z: 1 }, camFrom = null, camTo = null, camT = 1;
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

function strokeLayers(zl, z){
  ctx.globalCompositeOperation = "lighter";
  const thin = Math.pow(1 / z, .55);
  for (const L of Object.values(LAYERS)) if (L.z === zl){
    ctx.strokeStyle = rgba(L.col, .09); ctx.lineWidth = L.w * 4.2 * thin; ctx.stroke(L.path);
    ctx.strokeStyle = rgba(L.col, .92); ctx.lineWidth = L.w * thin; ctx.stroke(L.path);
  }
  ctx.globalCompositeOperation = "source-over";
}
function plate(z, time){
  /* Midgard: a small plate round the trunk at the hub, with the gold of its own circle */
  ctx.fillStyle = "rgba(9,3,28,.88)"; ctx.beginPath(); ctx.ellipse(CX, PLATE.y, PLATE.rx, PLATE.ry, 0, 0, TAU); ctx.fill();
  ctx.globalCompositeOperation = "lighter";
  const glow = .75 + .25 * Math.sin(time * 1.3);
  const g = ctx.createRadialGradient(CX, MY, 0, CX, MY, PLATE.rx); g.addColorStop(0, "rgba(34,224,122,.16)"); g.addColorStop(1, "rgba(34,224,122,0)");
  ctx.save(); ctx.translate(CX, MY); ctx.scale(1, PLATE.ry / PLATE.rx); ctx.translate(-CX, -MY); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(CX, MY, PLATE.rx, 0, TAU); ctx.fill(); ctx.restore();
  for (const k of [1, .66]){ ctx.beginPath(); ctx.ellipse(CX, PLATE.y, PLATE.rx * k, PLATE.ry * k, 0, 0, TAU);
    ctx.strokeStyle = `rgba(255,190,80,${.18 * glow})`; ctx.lineWidth = 7 / Math.sqrt(z); ctx.stroke();
    ctx.strokeStyle = `rgba(255,205,110,${.85 * glow})`; ctx.lineWidth = 1.5 / Math.sqrt(z); ctx.stroke(); }
  ctx.globalCompositeOperation = "source-over";
}
function rings(time, z, front){
  /* each world on the axis wears a ring round the trunk, its back half behind it */
  ctx.globalCompositeOperation = "lighter";
  for (const w of W){ if (!w.ring) continue;
    const on = sel === w.id, ry = w.ring * K * .5, a = on ? .95 : .5;
    ctx.beginPath(); ctx.ellipse(w.at[0], w.at[1], w.ring, ry, 0, front ? 0 : Math.PI, front ? Math.PI : TAU);
    ctx.strokeStyle = rgba(w.col, a * .25); ctx.lineWidth = (on ? 9 : 6) / Math.sqrt(z); ctx.stroke();
    ctx.strokeStyle = rgba(w.col, a); ctx.lineWidth = (on ? 2.2 : 1.4) / Math.sqrt(z); ctx.stroke();
  }
  ctx.globalCompositeOperation = "source-over";
}
function drawRock(R, time, z){
  const dy = Math.sin(time * .5 + R.ph) * 4;
  ctx.save(); ctx.translate(0, dy);
  const g = ctx.createLinearGradient(0, R.cy - 8, 0, R.cy + R.h); g.addColorStop(0, "#2b2346"); g.addColorStop(.35, "#141029"); g.addColorStop(1, "#05020f");
  ctx.fillStyle = g; ctx.beginPath(); [...R.top, ...R.bot].forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = "rgba(130,235,255,.45)"; ctx.lineWidth = 1.2 / Math.sqrt(z); ctx.beginPath(); R.top.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke();
  ctx.restore();
}
let SKY = null;
function buildSky(){
  const off = document.createElement("canvas"); off.width = Math.round(Wpx * dpr); off.height = Math.round(Hpx * dpr);
  const c = off.getContext("2d"); c.setTransform(dpr * scale, 0, 0, dpr * scale, 0, 0);
  c.fillStyle = "#050217"; c.fillRect(0, 0, PW, PH);
  let sd = 5; const r2 = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const COLS = [[20, 170, 150], [60, 200, 90], [190, 170, 60], [110, 60, 210], [30, 100, 210], [20, 140, 120]];
  c.globalCompositeOperation = "lighter";
  for (let i = 0; i < 70; i++){
    const edge = r2() < .7, x = edge ? (r2() < .5 ? r2() * 260 : PW - r2() * 260) : r2() * PW, y = r2() * PH;
    const rr = 70 + r2() * 220, [R, G, B] = COLS[Math.floor(r2() * COLS.length)], a = .035 + r2() * .07;
    const g = c.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, `rgba(${R},${G},${B},${a})`); g.addColorStop(1, `rgba(${R},${G},${B},0)`);
    c.fillStyle = g; c.fillRect(x - rr, y - rr, rr * 2, rr * 2);
  }
  c.globalCompositeOperation = "source-over";
  for (let i = 0; i < 26; i++){
    const x = r2() * PW, y = r2() * PH, rr = 40 + r2() * 120;
    const g = c.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, "rgba(4,1,14,.35)"); g.addColorStop(1, "rgba(4,1,14,0)");
    c.fillStyle = g; c.fillRect(x - rr, y - rr, rr * 2, rr * 2);
  }
  /* Sál: the aura round the whole figure, beyond the shell */
  c.save(); c.translate(CX, MY); c.scale(1, 1.22);
  const ag = c.createRadialGradient(0, 0, 0, 0, 0, 500); ag.addColorStop(0, "rgba(154,107,255,0)"); ag.addColorStop(.62, "rgba(154,107,255,.035)");
  ag.addColorStop(.86, "rgba(190,150,255,.09)"); ag.addColorStop(1, "rgba(154,107,255,0)");
  c.fillStyle = ag; c.beginPath(); c.arc(0, 0, 500, 0, TAU); c.fill(); c.restore();
  /* faint knotwork spirals, as in the hub world's sky */
  c.strokeStyle = "rgba(100,190,255,.08)"; c.lineWidth = 1.2;
  for (const [x, y, s0] of [[120, 420, 1], [880, 380, -1], [860, 1090, 1], [140, 860, -1]]){
    c.beginPath(); for (let t = 0; t < 26; t += .1){ const r = 4 + t * 3.2, a = s0 * t; c.lineTo(x + r * Math.cos(a), y + r * Math.sin(a)); } c.stroke();
  }
  SKY = off;
}
/* the frame of the figure: the egg, the axis running out past it, the mansions' ring, the compass */
function frameLines(time, z){
  const sz = Math.sqrt(z);
  ctx.globalCompositeOperation = "lighter";
  ctx.strokeStyle = "rgba(160,225,255,.3)"; ctx.lineWidth = 1.2 / sz;
  ctx.beginPath(); ctx.ellipse(CX, MY, EGG.rx, EGG.ry, 0, 0, TAU); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(CX, POLES.above.at[1] - 18); ctx.lineTo(CX, POLES.below.at[1] + 18); ctx.stroke();
  /* the 27 mansions, outermost; your Moon's is lit */
  ctx.strokeStyle = "rgba(150,200,255,.22)"; ctx.setLineDash([2 / sz, 5 / sz]);
  ctx.beginPath(); ctx.ellipse(CX, MY, NAK_R, NAK_R * K, 0, 0, TAU); ctx.stroke(); ctx.setLineDash([]);
  ctx.beginPath();
  for (let n = 0; n < 27; n++){ const u = az(n * 360 / 27), a = P3(NAK_R - 7, 0, u), b = P3(NAK_R + 7, 0, u); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); }
  ctx.strokeStyle = "rgba(150,200,255,.4)"; ctx.stroke();
  const mn = nakOf(plOf("Moon")[2]);
  ctx.beginPath();
  for (let s = 0; s <= 20; s++){ const p = P3(NAK_R, 0, az(mn * 360 / 27 + s / 20 * 360 / 27)); s ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
  ctx.strokeStyle = "rgba(150,255,220,.22)"; ctx.lineWidth = 8 / sz; ctx.stroke();
  ctx.strokeStyle = "rgba(170,255,230,.95)"; ctx.lineWidth = 2 / sz; ctx.stroke();
  /* the compass, and the spokes running out to it from each gate */
  ctx.setLineDash([3 / sz, 6 / sz]); ctx.strokeStyle = "rgba(255,205,120,.32)"; ctx.lineWidth = 1 / sz;
  for (const [, d] of COMPASS){ const u = d * RAD, a = P3(SH.R + SH.a + 4, 0, u), b = P3(COMPASS_R - 26, 0, u);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  ctx.setLineDash([]);
  ctx.globalCompositeOperation = "source-over";
  ctx.font = "50px 'UnifrakturMaguntia','Old English Text MT',Georgia,serif"; ctx.textAlign = "center";
  for (const [l, d] of COMPASS){ const [x, y] = P3(COMPASS_R, 0, d * RAD);
    ctx.fillStyle = "rgba(255,180,58,.18)"; ctx.fillText(l, x + 1.5, y + 18);
    ctx.fillStyle = "rgba(255,214,140,.92)"; ctx.fillText(l, x, y + 16); }
  /* the two ends of the axis: the spindle's poles */
  ctx.globalCompositeOperation = "lighter";
  for (const p of Object.values(POLES)){ const [x, y] = p.at, g = ctx.createRadialGradient(x, y, 0, x, y, 16);
    g.addColorStop(0, "rgba(232,221,255,.8)"); g.addColorStop(1, "rgba(232,221,255,0)"); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 16, 0, TAU); ctx.fill(); }
  ctx.globalCompositeOperation = "source-over";
}
/* a world as a portal: a swirling vortex in its colour; the four on the ring stand in stone arches */
function portal(w, x, y, r, time, on){
  const ar = w.gate ? 1.35 : 1;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 3.4);
  g.addColorStop(0, rgba(w.col, .55)); g.addColorStop(.4, rgba(w.col, .18)); g.addColorStop(1, rgba(w.col, 0));
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 3.4, 0, TAU); ctx.fill();
  if (w.gate){
    const aw = r * 1.75, ah = r * 2.5;
    ctx.fillStyle = "#1b1530"; ctx.strokeStyle = rgba(w.col, .7); ctx.lineWidth = r * .08;
    ctx.beginPath(); ctx.moveTo(x - aw, y + ah * .62); ctx.lineTo(x - aw, y - ah * .2); ctx.arc(x, y - ah * .2, aw, Math.PI, 0); ctx.lineTo(x + aw, y + ah * .62); ctx.closePath(); ctx.fill(); ctx.stroke();
  }
  ctx.save(); ctx.beginPath(); ctx.ellipse(x, y, r, r * ar, 0, 0, TAU); ctx.clip();
  ctx.fillStyle = "#07021a"; ctx.fillRect(x - r, y - r * ar, r * 2, r * 2 * ar);
  ctx.globalCompositeOperation = "lighter";
  for (let k = 0; k < 4; k++){
    ctx.beginPath();
    for (let s = 0; s <= 40; s++){ const f = s / 40, a = time * (on ? 2.4 : 1.4) + k * TAU / 4 + f * 5.2, rr = f * r * 1.05;
      const px = x + rr * Math.cos(a), py = y + rr * Math.sin(a) * ar; s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.strokeStyle = rgba(w.col, .9); ctx.lineWidth = r * .16; ctx.stroke();
  }
  const core = ctx.createRadialGradient(x, y, 0, x, y, r * .55); core.addColorStop(0, "rgba(255,255,255,.95)"); core.addColorStop(1, rgba(w.col, 0));
  ctx.fillStyle = core; ctx.beginPath(); ctx.arc(x, y, r * .55, 0, TAU); ctx.fill();
  ctx.restore(); ctx.globalCompositeOperation = "source-over";
  ctx.strokeStyle = w.col; ctx.lineWidth = r * .14; ctx.beginPath(); ctx.ellipse(x, y, r, r * ar, 0, 0, TAU); ctx.stroke();
}
const PULSES = [];
function spawn(){
  const p = PULSE_PATHS[Math.floor(Math.random() * PULSE_PATHS.length)]; if (!p) return;
  if (!p.len){ p.len = 0; for (let i = 1; i < p.pts.length; i++) p.len += Math.hypot(p.pts[i][0] - p.pts[i - 1][0], p.pts[i][1] - p.pts[i - 1][1]); }
  PULSES.push({ p, d: 0, v: 150 + Math.random() * 110 });
}
function along(p, d){
  for (let i = 1; i < p.pts.length; i++){
    const a = p.pts[i - 1], b = p.pts[i], l = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (d <= l){ const t = l ? d / l : 0; return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; }
    d -= l;
  }
  return p.pts[p.pts.length - 1];
}

const NODES = [], SHOWN = {}, MOVE = {};
let last = performance.now();
function frame(now){
  const dt = Math.min(.05, (now - last) / 1000), time = now / 1000; last = now;
  if (camT < 1){ camT = Math.min(1, camT + dt / .95); const e = ease(camT);
    cam = { x: camFrom.x + (camTo.x - camFrom.x) * e, y: camFrom.y + (camTo.y - camFrom.y) * e, z: camFrom.z + (camTo.z - camFrom.z) * e }; }
  if (spin && !drag && now > still && cam.z < 1.001 && camT >= 1) rot += spin * dt;
  const z = cam.z, S = WOOD;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.translate(Wpx / 2, Hpx / 2); ctx.scale(scale * z, scale * z); ctx.translate(-cam.x, -cam.y);
  ctx.lineCap = "round"; ctx.lineJoin = "round";

  if (SKY) ctx.drawImage(SKY, 0, 0, PW, PH);
  ctx.globalCompositeOperation = "lighter";
  for (const C of CONST){
    ctx.strokeStyle = "rgba(110,200,255,.3)"; ctx.lineWidth = 1.1 / Math.sqrt(z); ctx.beginPath();
    for (const [a, b] of C.edges){ ctx.moveTo(...C.pts[a]); ctx.lineTo(...C.pts[b]); } ctx.stroke();
    for (const p of C.pts){ ctx.fillStyle = "rgba(150,220,255,.26)"; ctx.beginPath(); ctx.arc(p[0], p[1], 6 / Math.sqrt(z), 0, TAU); ctx.fill();
      ctx.fillStyle = "rgba(225,245,255,.95)"; ctx.beginPath(); ctx.arc(p[0], p[1], 2.1 / Math.sqrt(z), 0, TAU); ctx.fill(); }
  }
  for (const [x, y, r, ph] of BRIGHT){
    const a = .5 + .5 * Math.sin(time * 1.1 + ph * 9), l = r * 4 * (.7 + .3 * a);
    ctx.strokeStyle = `rgba(220,240,255,${.35 * a})`; ctx.lineWidth = .8 / Math.sqrt(z);
    ctx.beginPath(); ctx.moveTo(x - l, y); ctx.lineTo(x + l, y); ctx.moveTo(x, y - l); ctx.lineTo(x, y + l); ctx.stroke();
    ctx.fillStyle = `rgba(235,248,255,${.6 + .4 * a})`; ctx.beginPath(); ctx.arc(x, y, r * .55, 0, TAU); ctx.fill();
  }
  ctx.globalCompositeOperation = "source-over";
  for (const R of ROCKS) drawRock(R, time, z);
  for (const [x, y, r, ph] of STARS){ ctx.fillStyle = `rgba(220,235,255,${.18 + .22 * Math.sin(time * .7 + ph * 9) ** 2})`; ctx.beginPath(); ctx.arc(x, y, r / Math.sqrt(z), 0, TAU); ctx.fill(); }
  let g = ctx.createRadialGradient(CROWN.x, CROWN.y - 60, 0, CROWN.x, CROWN.y - 60, CROWN.rx * 1.1);
  g.addColorStop(0, `rgba(${S.halo},.10)`); g.addColorStop(1, `rgba(${S.halo},0)`); ctx.fillStyle = g; ctx.fillRect(0, 0, PW, PH);
  g = ctx.createRadialGradient(CX, 1100, 0, CX, 1100, 420); g.addColorStop(0, `rgba(${S.halo},.07)`); g.addColorStop(1, `rgba(${S.halo},0)`);
  ctx.fillStyle = g; ctx.fillRect(0, 760, PW, 520);
  frameLines(time, z);
  for (const w of WELLS){
    const gg = ctx.createRadialGradient(w.at[0], w.at[1], 0, w.at[0], w.at[1], 50); gg.addColorStop(0, "rgba(120,230,255,.4)"); gg.addColorStop(1, "rgba(120,230,255,0)");
    ctx.fillStyle = gg; ctx.beginPath(); ctx.ellipse(w.at[0], w.at[1], 50, 15, 0, 0, TAU); ctx.fill();
    ctx.strokeStyle = sel === w.id ? "#ffb43a" : "rgba(170,240,255,.8)"; ctx.lineWidth = (sel === w.id ? 2.2 : 1.2) / Math.sqrt(z);
    ctx.beginPath(); ctx.ellipse(w.at[0], w.at[1], 36, 10, 0, 0, TAU); ctx.stroke();
  }
  /* back to front: the far side of the shell, what lies behind the plate, the plate, the tree above it,
     the near side of the shell, the two near limbs */
  shell("back", time, z);
  rings(time, z, false);
  strokeLayers(0, z);
  plate(z, time);
  strokeLayers(1, z);
  rings(time, z, true);
  shell("front", time, z);
  strokeLayers(2, z);

  /* light rising: water drawn up the roots, current up the trunk and out along every limb */
  if (!reduce){
    while (PULSES.length < 46) spawn();
    ctx.globalCompositeOperation = "lighter";
    for (let i = PULSES.length - 1; i >= 0; i--){
      const q = PULSES[i]; q.d += q.v * dt;
      if (q.d > q.p.len + 40){ PULSES.splice(i, 1); continue; }
      for (let k = 0; k < 6; k++){
        const dd = q.p.rev ? q.p.len - (q.d - k * 6) : q.d - k * 6; if (dd < 0 || dd > q.p.len) continue;
        const pt = along(q.p, dd); if (q.p.z === 0 && (underPlate(pt) || behindShell(pt))) continue;
        ctx.fillStyle = rgba(S.pulse, .9 - k * .14); ctx.beginPath(); ctx.arc(pt[0], pt[1], (3 - k * .38) / Math.sqrt(z), 0, TAU); ctx.fill();
      }
    }
    ctx.globalCompositeOperation = "source-over";
  }
  worlds(time, z, dt);
}

/* where each world's portal stands right now (the gates stand on the shell, so they grow up from its top) */
function spot(w, r){ return w.gate ? [w.base[0], w.base[1] - r * 1.55] : w.at; }
function worlds(time, z, dt){
  NODES.length = 0;
  const px = 1 / (scale * z), small = Wpx < 500, grow = Math.pow(z, .72), soul = names === "soul";
  const lab = (text, x, y, align, on, fs) => {
    ctx.font = `${on ? "700 " : ""}${fs}px 'Space Mono', monospace`; ctx.textAlign = align;
    ctx.lineWidth = 4 * px; ctx.strokeStyle = "rgba(7,2,26,.92)"; ctx.strokeText(text, x, y);
    ctx.fillStyle = on ? "#ffb43a" : "rgba(234,243,255,.96)"; ctx.fillText(text, x, y);
  };
  const fs = (small ? 9 : 11.5) * px, big = small ? .74 : 1.1;     /* on a phone the portals shrink so the labels keep clear */
  const RW = {};
  for (const w of W){
    const on = sel === w.id, r = (w.gate ? 12 : 9.5) * px * big * grow, [x, y] = spot(w, r);
    RW[w.id] = { x, y, r };
    portal(w, x, y, r, time, on);
    if (on){ ctx.strokeStyle = "#ffb43a"; ctx.lineWidth = 2 * px; ctx.beginPath(); ctx.ellipse(x, y, r + 7 * px, (r + 7 * px) * (w.gate ? 1.35 : 1), 0, 0, TAU); ctx.stroke(); }
    const text = soul ? w.soul.toUpperCase() : w.name.toUpperCase();
    if (w.gate) lab(text, x, w.base[1] + (small ? 17 : 22) * px, "center", on, fs);
    /* on a phone the ring's gates crowd the hub, so Midgard's name goes under its portal */
    else if (small && w.id === "midgard") lab(text, x, y + r + 14 * px, "center", on, fs);
    else lab(text, x - Math.max(r + 12 * px, w.ring + 8), y + 4 * px, "right", on, fs);
    NODES.push({ id: w.id, x, y, r: Math.max(r * 1.8, 16 * px) });
  }
  /* Sál, where your soul plate writes it: at the top of the axis, beyond the egg */
  if (soul){
    const on = sel === "sal", [x, y] = SAL.at;
    ctx.fillStyle = on ? "#ffb43a" : "#d8c8ff"; ctx.beginPath(); ctx.moveTo(x, y - 7 * px); ctx.lineTo(x + 6 * px, y); ctx.lineTo(x, y + 7 * px); ctx.lineTo(x - 6 * px, y); ctx.closePath(); ctx.fill();
    lab("SÁL", x - 12 * px, y + 4 * px, "right", on, fs);
    NODES.push({ id: "sal", x, y, r: 18 * px });
  }
  ctx.font = `italic ${fs}px 'Space Grotesk', sans-serif`; ctx.textAlign = "center";
  for (const w of WELLS){
    const y = Math.min(w.at[1] + 26 * px, PH - 6), on = sel === w.id;
    ctx.lineWidth = 4 * px; ctx.strokeStyle = "rgba(7,2,26,.9)"; ctx.strokeText(w.name, w.at[0], y);
    ctx.fillStyle = on ? "#ffb43a" : "rgba(170,235,255,.92)"; ctx.fillText(w.name, w.at[0], y);
    NODES.push({ id: w.id, x: w.at[0], y: w.at[1], r: 30 });
  }
  /* the planets: in the shell, each on the rim at its degree (pushed outward when they crowd);
     on the Ladder, each beside the world it feeds, the nodes at the poles, the outer three left in the shell */
  const CR = (small ? 8.5 : 9.5) * px, ladderN = {};
  /* in the shell, each planet's disc sits just outside the rim at its degree; where they crowd, they
     fan out along the rim (like labels round a pie) and a gold thread runs back to the true degree */
  const onShell = PL.filter(p => mode === "shell" || !FEEDS[p[0]]);
  const rim = u => { const [x, y] = P3(SH.R + SH.a, 0, u), n = norm2(Math.cos(u), Math.sin(u) / K), o = CR + 5 * px; return [x + n[0] * o, y + n[1] * o]; };
  const fan = {};
  if (onShell.length){
    const us = onShell.map(p => ({ name: p[0], u0: az(p[2]) })).map(q => ({ ...q, u0: ((q.u0 % TAU) + TAU) % TAU }));
    us.sort((a, b) => a.u0 - b.u0);
    let gap = -1, at = 0;                            /* start the chain after the widest empty stretch */
    us.forEach((q, i) => { const nx = i + 1 < us.length ? us[i + 1].u0 : us[0].u0 + TAU, d = nx - q.u0; if (d > gap){ gap = d; at = (i + 1) % us.length; } });
    const chain = us.slice(at).concat(us.slice(0, at)).map((q, i, arr) => ({ ...q, u0: q.u0 + (i && q.u0 < arr[0].u0 ? TAU : 0) }));
    chain.forEach(q => q.u = q.u0);
    const minD = CR * 2 + 3 * px;
    for (let it = 0; it < 120; it++){
      for (let i = 0; i + 1 < chain.length; i++){
        const a = chain[i], b = chain[i + 1], pa = rim(a.u), pb = rim(b.u), d = Math.hypot(pa[0] - pb[0], pa[1] - pb[1]);
        if (d < minD){ const m = (a.u + b.u) / 2, sp = Math.hypot(...[0, 1].map(k => rim(m + .005)[k] - rim(m - .005)[k])) / .01;
          const du = Math.min(.08, (minD - d) / sp) / 2 + .0005; a.u -= du; b.u += du; }
      }
      for (const q of chain) q.u += (q.u0 - q.u) * .02;
    }
    for (const q of chain) fan[q.name] = q.u;
  }
  const targets = PL.map(p => {
    const [name, , lon] = p, u = az(lon), tick = P3(SH.R + SH.a, 0, u);
    if (fan[name] === undefined){
      const f = FEEDS[name];
      if (f === "above" || f === "below") return { p, tick, at: POLES[f].at };
      const w = byId(f), R = RW[f];
      if (w.gate) return { p, tick, at: [R.x + w.out * (R.r * 1.95 + CR + 6 * px), R.y] };
      return { p, tick, at: [R.x + R.r + CR + 8 * px, R.y] };
    }
    return { p, tick, at: rim(fan[name]), shell: true };
  });
  for (const T of targets){
    const [name, glyph] = T.p, m = MOVE[name] || (MOVE[name] = { t: 1, from: T.at });
    if (m.t < 1) m.t = Math.min(1, m.t + dt / .9);
    const e = ease(m.t), x = m.from[0] + (T.at[0] - m.from[0]) * e, y = m.from[1] + (T.at[1] - m.from[1]) * e;
    SHOWN[name] = [x, y];
    const dim = OUTER.has(name) && mode === "ladder", on = sel === "p:" + name, far = T.shell && Math.sin(az(T.p[2])) < 0;
    if (T.shell && m.t >= 1){
      ctx.strokeStyle = `rgba(255,180,58,${dim ? .3 : .75})`; ctx.lineWidth = 1.1 * px;
      ctx.beginPath(); ctx.moveTo(T.tick[0], T.tick[1]); ctx.lineTo(x, y); ctx.stroke();
      ctx.fillStyle = "#ffb43a"; ctx.beginPath(); ctx.arc(T.tick[0], T.tick[1], 2.2 * px, 0, TAU); ctx.fill();
    }
    ctx.globalAlpha = dim ? .42 : far && !on ? .78 : 1;
    ctx.fillStyle = "#160742"; ctx.strokeStyle = on ? "#fff" : OUTER.has(name) ? "#b9a3ff" : "#ffb43a"; ctx.lineWidth = (on ? 2.2 : 1.3) * px;
    ctx.beginPath(); ctx.arc(x, y, CR, 0, TAU); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = `${CR * 1.3}px 'Segoe UI Symbol','Noto Sans Symbols 2','DejaVu Sans',sans-serif`;
    ctx.fillText(glyph + VS, x, y + CR * .45);
    ctx.globalAlpha = 1;
    NODES.push({ id: "p:" + name, x, y, r: CR * 1.15, planet: true });
  }
}

/* ---------------- travelling to a world ---------------- */
let back = null;
function posOf(id){
  if (id === "sal") return SAL.at;
  if (id.startsWith("p:")) return SHOWN[id.slice(2)] || [CX, MY];
  const w = byId(id); return w.gate ? [w.base[0], w.base[1] - 20] : w.at;
}
function travel(id){
  const zz = Wpx < 500 ? 2.1 : 2.4;
  let to = { x: PW / 2, y: PH / 2, z: 1 };
  if (id){ const [x, y] = posOf(id), hw = PW / (2 * zz), hh = PH / (2 * zz);
    to = { x: Math.max(hw, Math.min(PW - hw, x)), y: Math.max(hh, Math.min(PH - hh, y)), z: zz }; }
  camFrom = { ...cam }; camTo = to; camT = reduce ? .999 : 0;
  back.hidden = !id;
  if (reduce) paintOnce();
}

/* ---------------- sizing ---------------- */
function size(){
  const w = Math.min(cv.parentElement.clientWidth, 760);
  if (!w || w === Wpx && SKY) return !!w;
  Wpx = w; Hpx = Math.round(w * PH / PW); dpr = Math.min(2, devicePixelRatio || 1); scale = w / PW;
  cv.width = Math.round(Wpx * dpr); cv.height = Math.round(Hpx * dpr); cv.style.height = Hpx + "px";
  buildSky();
  return true;
}

/* ---------------- the record beside it ---------------- */
let host = null, panelEl = null, capEl = null, ctlEl = null, opts = {};
const the = n => ["Sun", "Moon"].includes(n) ? "the " : "";
const pname = p => `<span class="ey-pl">${p[1]}${VS} ${p[0]}</span>`;
const placed = p => `${deg(p[2])}, in your ${ORD(houseOf(p[2]) + 1)} house`;
const stationOf = lon => Math.floor(norm(lon) / (10 / 3)) % 108 + 1;
const toLand = (href, text) => `<a class="ey-go" href="${href}">${text} →</a>`;
function panel(){
  if (!sel){ panelEl.innerHTML = ""; return; }
  if (sel === "sal"){
    const mn = nakOf(plOf("Moon")[2]);
    panelEl.innerHTML = `<h3>Sál</h3><p class="ey-on">the soul · beyond the shell</p>
      <dl>
        <dt>Odin's Eye</dt><dd>At the top of the axis, beyond the egg, where the soul plate writes it. Here it is the faint glow round the whole figure.</dd>
        <dt>The word</dt><dd>Old Norse <i>sál</i> came in with Christianity, from Old English <i>sāwol</i>. The other eight parts are native words.</dd>
        <dt>Further out</dt><dd>The outermost ring carries the 27 mansions. Your Moon's, ${NAK[mn]}, is lit.</dd>
      </dl>${toLand("#mandala", "The mansions in the Wyrd Mandala")}`;
    return;
  }
  if (sel.startsWith("p:")){
    const p = plOf(sel.slice(2)), [name, glyph, lon] = p, k = runeOf(lon), f = FEEDS[name], st = ST[f];
    const ladder = OUTER.has(name) ? "Feeds nothing. The outer three are real bodies but not grahas, so they stay in the shell."
      : f === "above" ? "Stands at the pole above the crown, the top of the spindle." : f === "below" ? "Stands at the pole below the feet, the foot of the spindle."
      : `Feeds ${st.world}, at the ${st.station}.`;
    const sn = stationOf(lon);
    panelEl.innerHTML = `<h3>${glyph}${VS} ${name}</h3><p class="ey-on">${deg(lon)} · your ${ORD(houseOf(lon) + 1)} house${UNKNOWN ? " (counted from your Sun)" : ""}</p>
      <dl>
        <dt>In the shell</dt><dd>On ${RUNES[k][1]} <span class="ey-rn">${RUNES[k][0]}</span>, the ${k % 2 ? "closing" : "opening"} rune of the ${ORD(Math.floor(k / 2) + 1)} house</dd>
        <dt>On the Ladder</dt><dd>${ladder}</dd>
        <dt>Mansion</dt><dd><a href="#mandala/s${String(sn).padStart(3, "0")}">${NAK[nakOf(lon)]}, station ${sn}</a></dd>
      </dl>${toLand("#chart", "Every placement in Your chart")}${st ? toLand("#design/harmonic", `The ${st.station} on the Harmonic Body`) : ""}`;
    return;
  }
  const well = WELLS.find(w => w.id === sel);
  if (well){
    panelEl.innerHTML = `<h3>${well.name}</h3><p class="ey-on">${well.on}</p>
      <dl><dt>In the codex</dt><dd>${well.body[0].toUpperCase() + well.body.slice(1)}</dd></dl><p class="ey-ken">${well.ken}</p>`;
    return;
  }
  const w = byId(sel), st = ST[w.id], fp = st && plOf(st.feeder);
  let shellRows = "", go = "";
  if (w.id === "jotunheim"){
    const rows = [];
    for (let h = 0; h < 12; h++){ const ps = PL.filter(p => houseOf(p[2]) === h).sort((a, b) => a[2] - b[2]);
      if (ps.length) rows.push(`<li><b style="color:${HOUSE[h]}">${ORD(h + 1)}</b><small>${SIGNS[(CUSP / 30 + h) % 12]}</small><span>${ps.map(pname).join("")}</span></li>`); }
    shellRows = `<dt>The shell</dt><dd>Your twelve houses run round it in their colours, with the runes that seat them, and every planet stands in it at its degree. It turns freely, so no house is tied to a quarter.${UNKNOWN
      ? " Your birth time is unknown, so the houses are counted from your Sun's sign." : ` The gold line across it is your rising degree, ${deg(ASC)}.`}<ul class="ey-hs">${rows.join("")}</ul></dd>`;
    go = `<button type="button" class="ey-go" data-eye-open>Open the shell: your chart as a torus →</button>`;
  } else if (st) go = toLand("#design/harmonic", `Hear the ${st.station} on the Harmonic Body`);
  panelEl.innerHTML = `<h3>${names === "soul" ? `${w.soul} <small>${w.name}</small>` : `${w.name} <small>${w.soul}</small>`}</h3>
    <p class="ey-on">${w.on} · ${w.where.toLowerCase()}</p>
    <dl>
      <dt>Soul</dt><dd>${w.soul} <small>${w.gloss}</small></dd>
      <dt>Station</dt><dd>${st ? `${st.station}, fed by ${the(st.feeder)}${st.feeder}` : `<small>not one of the Ladder's seven</small>`}</dd>
      ${fp ? `<dt>Your ${fp[0]}</dt><dd>${pname(fp)} at ${placed(fp)}</dd>` : ""}
      ${shellRows}
    </dl>
    ${st ? `<p class="ey-ken">${st.kenning}</p>` : w.ken ? `<p class="ey-ken">${w.ken}</p>` : ""}${go}`;
}
const how = () => { if (capEl) capEl.textContent = mode === "shell"
  ? "Your planets stand where they stood when you were born, on the rim of Jötunheim's shell among your houses. Drag the shell to turn it; tap any world, well or planet."
  : "On the Ladder, each of the seven goes to the world it feeds, the same for everyone. Rahu and Ketu go to the poles above and below; the outer three stay in the shell."; };
function choose(id, go){
  sel = id; panel();
  host.querySelectorAll("[data-eye-w]").forEach(b => b.setAttribute("aria-pressed", b.dataset.eyeW === sel));
  if (go) travel(id);
  if (reduce) paintOnce();
  if (window.Wyrd && Wyrd.pulse && id) Wyrd.pulse("tap", "eye-" + (id.startsWith("p:") ? "planet" : id));
}
function buttons(){
  host.querySelector(".ey-worlds").innerHTML = W.map(w => `<button class="ey-w" type="button" data-eye-w="${w.id}" aria-pressed="${sel === w.id}" style="--c:${w.col}"><i></i>${names === "soul" ? w.soul : w.name}</button>`).join("");
}
const press = (attr, v) => ctlEl.querySelectorAll(`[${attr}]`).forEach(b => b.setAttribute("aria-pressed", b.getAttribute(attr) === v));
function setMode(m){
  if (m === mode) return;
  for (const [n, s] of Object.entries(SHOWN)) MOVE[n] = { t: reduce ? 1 : 0, from: s };
  mode = m; press("data-eye-mode", m); how(); panel(); if (reduce) paintOnce();
}
function setNames(n){ names = n; press("data-eye-names", n); buttons(); panel(); if (n !== "soul" && sel === "sal") choose("jotunheim", false); if (reduce) paintOnce(); }

/* ---------------- running ----------------
   It draws only while the hub is showing and on screen. */
let running = false, onScreen = true, raf = null;
function loop(now){ raf = null; if (!(running && onScreen && !document.hidden)) return; frame(now); raf = requestAnimationFrame(loop); }
function kick(){ if (!raf && running && onScreen && !document.hidden){ last = performance.now(); raf = requestAnimationFrame(loop); } }
function paintOnce(){ if (size()) frame(performance.now()); }

function mount(el, C, o = {}){
  host = el; opts = o; capEl = o.caption || null; ctlEl = o.controls || el;
  UNKNOWN = !!C.unknownTime; ASC = C.ascS; CUSP = Math.floor(norm(ASC) / 30) * 30;
  const H = Wyrd.helpers; GLYPH = H.GLYPH; NAK = H.NAKSHATRA.map(n => n[0]);
  PL = BODIES.filter(b => C.sid[b] != null).map(b => [b, GLYPH[b], C.sid[b]]);
  LIT = new Set(PL.map(p => runeOf(p[2])));
  host.innerHTML = `<div class="ey">
      <div class="ey-stage">
        <canvas class="ey-cv" tabindex="0" style="touch-action:pan-y" aria-label="Odin's Eye: the nine worlds on the axis and the ring, with Jötunheim's shell carrying your houses, runes and planets. Drag sideways, or use the left and right arrow keys, to turn the shell."></canvas>
        <button class="ey-back" type="button" hidden>◀ The whole eye</button>
        <div class="ey-worlds" role="group" aria-label="The nine worlds"></div>
      </div>
      <aside class="ey-panel" aria-live="polite"></aside>
    </div>`;
  cv = host.querySelector(".ey-cv"); ctx = cv.getContext("2d"); back = host.querySelector(".ey-back"); panelEl = host.querySelector(".ey-panel");
  ctlEl.insertAdjacentHTML("afterbegin", `<div class="ey-ctl" role="group" aria-label="Which names to show">
      <button type="button" class="tz-chip" data-eye-names="realms" aria-pressed="true">The realms</button>
      <button type="button" class="tz-chip" data-eye-names="soul" aria-pressed="false">The soul</button></div>
    <div class="ey-ctl" role="group" aria-label="Where the planets stand">
      <button type="button" class="tz-chip" data-eye-mode="shell" aria-pressed="true">In the shell</button>
      <button type="button" class="tz-chip" data-eye-mode="ladder" aria-pressed="false">On the Ladder</button></div>`);
  ctlEl.addEventListener("click", e => {
    const n = e.target.closest("[data-eye-names]"); if (n) setNames(n.dataset.eyeNames);
    const m = e.target.closest("[data-eye-mode]"); if (m) setMode(m.dataset.eyeMode);
  });
  back.addEventListener("click", () => travel(null));
  host.querySelector(".ey-worlds").addEventListener("click", e => { const b = e.target.closest("[data-eye-w]"); if (b) choose(b.dataset.eyeW, true); });
  panelEl.addEventListener("click", e => { if (e.target.closest("[data-eye-open]") && opts.onShell) opts.onShell(); });
  /* turning the shell by hand: drag sideways, or the left and right arrows; it rests a moment, then turns on */
  cv.addEventListener("pointerdown", e => { drag = { x: e.clientX, rot, moved: false }; });
  cv.addEventListener("pointermove", e => {
    if (!drag) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved && Math.abs(dx) > 5){ drag.moved = true; try { cv.setPointerCapture(e.pointerId); } catch (_) {} }
    if (drag.moved){ rot = drag.rot - dx / (Wpx * .32); if (reduce) paintOnce(); }
  });
  cv.addEventListener("pointerup", () => { if (drag && drag.moved){ dragged = true; still = performance.now() + 2500; } drag = null; });
  cv.addEventListener("pointercancel", () => { drag = null; });
  cv.addEventListener("keydown", e => {
    const k = { ArrowLeft: .12, ArrowRight: -.12 }[e.key];
    if (k){ e.preventDefault(); rot += k; still = performance.now() + 2500; if (reduce) paintOnce(); }
  });
  cv.addEventListener("click", e => {
    if (dragged){ dragged = false; return; }
    const r = cv.getBoundingClientRect(), sx = (e.clientX - r.left) / r.width * Wpx, sy = (e.clientY - r.top) / r.height * Hpx;
    const x = (sx - Wpx / 2) / (scale * cam.z) + cam.x, y = (sy - Hpx / 2) / (scale * cam.z) + cam.y;
    /* a planet first, if the tap is on one; then the nearest world; then the shell itself, which is Jötunheim */
    let best = null, bd = Infinity;
    for (const n of NODES){ const d = Math.hypot(n.x - x, n.y - y), dd = d - (n.planet ? 1000 : 0); if (d < n.r + 10 / (scale * cam.z) && dd < bd){ bd = dd; best = n.id; } }
    if (!best){ const dx = x - CX, dy = y - MY, rr = Math.hypot(dx, dy / K); if (rr > 168 && rr < 415) best = "jotunheim"; }
    if (best) choose(best, true);
  });
  addEventListener("resize", () => { if (running) size(); });
  document.addEventListener("visibilitychange", kick);
  if ("IntersectionObserver" in window) new IntersectionObserver(es => { onScreen = es[0].isIntersecting; kick(); }).observe(cv);
  build(); buildShell(); buttons(); how(); choose("jotunheim", false);
  if (document.fonts && document.fonts.load) document.fonts.load("30px 'Noto Sans Runic'", "ᚠᛟ").catch(() => {});
  return {
    start(){ running = true; size(); if (reduce) paintOnce(); else kick(); },
    stop(){ running = false; },
    select(id){ choose(id, true); },
  };
}
window.WyrdEye = { mount };
})();
