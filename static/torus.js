'use strict';
/* ============================================================
   THE TORUS
   The map's centre: the chart as a torus you can turn.
   Around the ring runs the zodiac (sidereal, house 1 facing you).
   Around the tube the layers wrap, each a band: the houses on the
   outer equator, then the sidereal signs, the runes, the gates,
   the mansions and the tropical signs over the top and through
   the hole. The planets ride the outer equator at their degrees.
   Drag (or use the arrow keys) to turn it; tap to see what is
   there; switch layers on and off and they build up again.
   Plain canvas, no library.
   ============================================================ */
(() => {
const { norm, nakIndex, signOf, GLYPH, NAKSHATRA } = Wyrd.helpers;
const TAU = Math.PI * 2;
/* in order round the tube, starting below the outer equator: the houses sit on the outer
   equator, the signs over the top, the runes and gates toward the hole, the mansions underneath */
const LAYERS = [
  { id: "tropical", name: "Tropical signs" }, { id: "houses", name: "Houses" }, { id: "signs", name: "Sidereal signs" },
  { id: "runes", name: "Runes" }, { id: "gates", name: "Gates" }, { id: "mansions", name: "Mansions" },
];
/* the houses run the rainbow, red for the 1st round to magenta for the 12th; every sign's glyph
   takes the colour of the house it stands in */
const RAINBOW = ["#ff2a2a", "#ff7a00", "#ffd400", "#a3e635", "#22c55e", "#14d8a8", "#22d3ee", "#3b82f6", "#5b4bff", "#8b5cf6", "#d946ef", "#ff2fa8"];
const NU = 96, PER = 6, R = 1, r = 0.44;
const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];

function mount(host, C, opts = {}){
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  host.innerHTML = `<canvas class="tz-cv" tabindex="0" role="img" aria-label="Your chart as a torus: the zodiac around the ring, its layers around the tube. Drag or use the arrow keys to turn it; tap to see what is there."></canvas>`;
  const cv = host.querySelector("canvas"), ctx = cv.getContext("2d");
  const cap = opts.caption || { set textContent(v){} };
  const on = Object.fromEntries(LAYERS.map(l => [l.id, true]));
  const shown = Object.fromEntries(LAYERS.map((l, i) => [l.id, reduce ? 1 : 0]));       // 0..1, for the build-up
  let built = reduce ? Infinity : performance.now();
  let yaw = 0, pitch = 1.02, spin = reduce ? 0 : 0.0016, raf = null, W = 0, H = 0, dpr = 1, quads = [], pick = null;

  /* ---------- what each cell is ----------
     The torus is read in one zodiac at a time (Z): sidereal, as Jyotish reads it, or tropical.
     The ring, the houses, the main sign band and the planets follow Z; the band through the hole
     shows the other zodiac. Gates are always tropical and mansions always sidereal. */
  let Z = opts.zodiac === "tropical" ? "tropical" : "sidereal";
  const pg = new Set(Object.values(C.natal.personality).map(v => v.gate)), dg = new Set(Object.values(C.natal.design).map(v => v.gate));
  const moonNak = nakIndex(C.sid.Moon);
  const gateAt = trop => GATE_ORDER[Math.floor(norm(trop - 302) / 5.625)];
  let pos, cusp, litRunes;
  const cuspSid = Math.floor(norm(C.ascS) / 30) * 30;            // runes are always counted in the sidereal houses
  const fromSid = lon => Z === "tropical" ? norm(lon + C.ay) : lon;
  const other = () => Z === "sidereal" ? "tropical" : "sidereal";
  const toSid = lon => Z === "tropical" ? norm(lon - C.ay) : lon, toTrop = lon => Z === "tropical" ? lon : norm(lon + C.ay);
  const houseOfLon = lon => Math.floor(norm(lon - cusp) / 30);
  function seat(){
    pos = b => Z === "tropical" ? C.trop[b] : C.sid[b];
    cusp = Math.floor(norm(Z === "tropical" ? C.ascS + C.ay : C.ascS) / 30) * 30;
    litRunes = new Set(WyrdWheel.WHEEL_BODIES.map(b => Math.floor(norm(C.sid[b] - cuspSid) / 15)));
    LAYERS.find(l => l.id === "signs").name = Z === "tropical" ? "Tropical signs" : "Sidereal signs";
    LAYERS.find(l => l.id === "tropical").name = Z === "tropical" ? "Sidereal signs" : "Tropical signs";
  }
  seat();
  function cell(layer, lon){                     /* lon: the cell's centre, in the zodiac the torus is read in */
    const into = norm(lon - cusp), trop = toTrop(lon);
    switch (layer){
      case "houses": { const h = Math.floor(into / 30); return { rgb: hex(RAINBOW[h]), a: .95, label: `House ${h + 1} · ${HOUSES[h].phase}` }; }
      case "signs": { const s = Math.floor(norm(lon) / 30), c = hex(RAINBOW[houseOfLon(s * 30 + 15)]);
        return { rgb: c.map(v => Math.round(v * (s % 2 ? .78 : .92))), a: 1, label: `${SIGNS[s]} (${Z})` }; }
      case "runes": { const k = Math.floor(norm(toSid(lon) - cuspSid) / 15), rn = HOUSES[Math.floor(k / 2)][k % 2 ? "egress" : "ingress"], lit = litRunes.has(k);
        return { lit, rgb: lit ? [255, 236, 190] : k % 2 ? [120, 110, 190] : [140, 125, 210], a: 1, label: `${rn[0]} ${rn[1]}${lit ? " · a planet stands here" : ""}` }; }
      case "gates": { const g = gateAt(trop), p = pg.has(g), d = dg.has(g);
        return { lit: p || d, rgb: p && d ? [255, 205, 120] : p ? [240, 236, 225] : d ? [110, 230, 196] : [70, 130, 150], a: 1, label: `Gate ${g}${GATE_NAME[g] ? " · " + GATE_NAME[g] : ""}${p ? " · lit at birth" : ""}${d ? " · lit in design" : ""}` }; }
      case "mansions": { const n = nakIndex(toSid(lon)); return { lit: n === moonNak, rgb: n === moonNak ? [150, 255, 220] : n % 2 ? [70, 110, 170] : [90, 130, 190], a: 1, label: `${NAKSHATRA[n][0]}${n === moonNak ? " · your Moon's mansion" : ""}` }; }
      case "tropical": { const o = other() === "tropical" ? trop : toSid(lon), s = Math.floor(o / 30);
        return { rgb: s % 2 ? [150, 110, 240] : [175, 140, 255], a: 1, label: `${SIGNS[s]} (${other()})` }; }
    }
  }
  /* precompute colours: they never change */
  const NV = LAYERS.length * PER;
  let COL = [];
  const paint = () => { COL = []; for (let i = 0; i < NU; i++){ const lon = norm(cusp + (i + .5) * 360 / NU); COL.push(LAYERS.map(L => cell(L.id, lon))); } };
  paint();

  /* ---------- geometry ---------- */
  const uOf = i => i / NU * TAU;                              // angle round the ring; 0 = the 1st house's cusp
  const vOf = j => j / NV * TAU - TAU / 4;                      // around the tube; 0 = outer equator, the houses' middle
  function point(u, v, lift = 0){
    const rr = r + lift, x = (R + rr * Math.cos(v)) * Math.cos(u), y = (R + rr * Math.cos(v)) * Math.sin(u), z = rr * Math.sin(v);
    return rot(x, y, z);
  }
  function rot(x, y, z){
    const cu = Math.cos(yaw), su = Math.sin(yaw);
    const x1 = x * cu - y * su, y1 = x * su + y * cu;            // spin about the torus axis
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    return [x1, y1 * cp - z * sp, y1 * sp + z * cp];             // tip toward the viewer
  }
  function proj([x, y, z]){
    const d = 4.2, k = (Math.min(W, H) * 1.14) / (d - z);       // the viewer stands at +z
    return [W / 2 + x * k, H / 2 + y * k, z];
  }
  const light = (() => { const l = [-.35, -.55, .76], n = Math.hypot(...l); return l.map(v => v / n); })();

  function frame(t){
    const now = performance.now();
    if (spin) yaw += spin * (opts.speed || 1);
    LAYERS.forEach((L, k) => {                                   // the layers build up one by one
      const target = on[L.id] ? 1 : 0, since = (now - built) / 1000 - k * .35;
      shown[L.id] = reduce ? target : on[L.id] ? Math.min(1, Math.max(shown[L.id], since / .6)) : Math.max(0, shown[L.id] - .06);
    });
    draw(); raf = requestAnimationFrame(frame);
  }
  const glow = (rgb, k) => rgb.map(c => Math.min(255, Math.round(c + (255 - c) * k)));
  function draw(){
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    const P = [];
    for (let i = 0; i <= NU; i++){ P.push([]); for (let j = 0; j <= NV; j++) P[i].push(proj(point(uOf(i), vOf(j)))); }
    quads = [];
    /* the surface, as light: every cell glows a little, more at the edges where the eye looks along it,
       and the colours add like light, so the far side shows through */
    ctx.globalCompositeOperation = "lighter";
    for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++){
      const k = Math.floor(j / PER), L = LAYERS[k], vis = shown[L.id]; if (vis <= 0.01) continue;
      const a = P[i][j], b = P[i + 1][j], c = P[i + 1][j + 1], d = P[i][j + 1];
      const u = uOf(i + .5), v = vOf(j + .5);
      const n = rot(Math.cos(v) * Math.cos(u), Math.cos(v) * Math.sin(u), Math.sin(v));
      const col = COL[i][k], fres = 1 - Math.abs(n[2]), front = n[2] > 0;
      const lit = col.lit ? 1 : 0;
      const alpha = vis * (front ? 1 : .55) * ((lit ? .34 : .07) + .2 * fres * fres);
      const [r_, g_, b_] = glow(col.rgb, lit ? .35 : .25);
      ctx.fillStyle = `rgba(${r_},${g_},${b_},${alpha.toFixed(3)})`;
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath(); ctx.fill();
      if (front) quads.push({ pts: [a, b, c, d], z: (a[2] + b[2] + c[2] + d[2]) / 4, col, i, k });
    }
    /* the armature, in neon: the rings between layers glow cyan, and a magenta meridian marks every sign */
    ctx.globalCompositeOperation = "source-over"; ctx.lineWidth = 1.6; ctx.shadowBlur = 8;
    for (let k = 0; k < LAYERS.length; k++){
      const vis = Math.max(shown[LAYERS[k].id], k ? shown[LAYERS[k - 1].id] : shown[LAYERS[LAYERS.length - 1].id]); if (vis <= .01) continue;
      ctx.shadowColor = "rgba(73,232,255,.9)"; ctx.strokeStyle = `rgba(127,246,255,${(.55 * vis).toFixed(3)})`; ctx.beginPath();
      for (let i = 0; i <= NU; i++){ const q = P[i][k * PER]; i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); } ctx.stroke();
    }
    ctx.lineWidth = 1.2; ctx.shadowColor = "rgba(255,79,216,.9)";
    for (let m = 0; m < 12; m++){
      const i = Math.round(m * NU / 12); ctx.strokeStyle = "rgba(255,120,230,.42)"; ctx.beginPath(); let started = false;
      for (let j = 0; j <= NV; j++){ if (shown[LAYERS[Math.min(LAYERS.length - 1, Math.floor(j / PER))].id] <= .01){ started = false; continue; }
        const q = P[i][j]; started ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); started = true; } ctx.stroke();
    }
    ctx.shadowBlur = 0;
    const R0 = Math.min(W, H);
    /* the markings: house numbers, sign glyphs, the runes, written in light */
    const fs = Math.max(10, R0 * .032);
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const carve = (layerId, lon, text, strong, rgb) => {
      const k = LAYERS.findIndex(l => l.id === layerId), vis = shown[layerId]; if (vis <= .05) return;
      const u = norm(lon - cusp) / 360 * TAU, v = vOf(k * PER + PER / 2);
      const n = rot(Math.cos(v) * Math.cos(u), Math.cos(v) * Math.sin(u), Math.sin(v)); if (n[2] < .1) return;
      const p = proj(point(u, v, .004)), a = vis * Math.min(1, (n[2] - .1) * 3);
      ctx.font = `${Math.round(fs)}px Texturina, serif`;
      if (rgb){                                    // a sign's glyph, in its house's colour, lit like neon
        ctx.font = `bold ${Math.round(fs * 1.25)}px Texturina, serif`;
        ctx.shadowColor = `rgba(${rgb.join(",")},1)`; ctx.shadowBlur = 14; ctx.fillStyle = `rgba(${glow(rgb, .45).join(",")},${a})`;
        ctx.fillText(text, p[0], p[1]); ctx.shadowBlur = 4; ctx.fillStyle = `rgba(255,255,255,${a * .55})`; ctx.fillText(text, p[0], p[1]); return;
      }
      ctx.shadowColor = strong ? "rgba(255,240,200,.9)" : "rgba(180,220,255,.7)"; ctx.shadowBlur = strong ? 12 : 6;
      ctx.fillStyle = strong ? `rgba(255,246,222,${a})` : `rgba(226,236,255,${a * .8})`; ctx.fillText(text, p[0], p[1]);
    };
    ctx.globalCompositeOperation = "source-over";
    for (let h = 0; h < 12; h++) carve("houses", cusp + h * 30 + 15, String(h + 1), false, [255, 255, 255]);
    for (let sI = 0; sI < 12; sI++) carve("signs", sI * 30 + 15, SIGN_GLYPH[sI] + "︎", false, hex(RAINBOW[houseOfLon(sI * 30 + 15)]));
    for (let k = 0; k < 24; k++){ const rn = HOUSES[Math.floor(k / 2)][k % 2 ? "egress" : "ingress"]; carve("runes", fromSid(cuspSid + k * 15 + 7.5), rn[0], litRunes.has(k)); }
    for (let sI = 0; sI < 12; sI++){                       // the other zodiac's signs, seated in this one
      const lon = norm(sI * 30 + 15 + (Z === "sidereal" ? -C.ay : C.ay));
      carve("tropical", lon, SIGN_GLYPH[sI] + "︎", false, hex(RAINBOW[houseOfLon(lon)]));
    }
    ctx.shadowBlur = 0;
    /* the planets: orbs of light on the outer equator */
    const marks = WyrdWheel.WHEEL_BODIES.map(b => {
      const u = norm(pos(b) - cusp) / 360 * TAU, n = rot(Math.cos(u), Math.sin(u), 0);
      return { b, p: proj(point(u, 0, .08)), front: n[2] > -0.15, z: n[2] };
    }).sort((a, b) => a.z - b.z);
    for (const m of marks){
      const [x, y] = m.p, rad = Math.max(10, R0 * .03), a = m.front ? 1 : .35;
      ctx.globalCompositeOperation = "lighter";
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad * 2.6);
      g.addColorStop(0, `rgba(255,250,235,${.9 * a})`); g.addColorStop(.35, `rgba(240,225,190,${.35 * a})`); g.addColorStop(1, "rgba(200,180,255,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, rad * 2.6, 0, TAU); ctx.fill();
      ctx.globalCompositeOperation = "source-over";
      if (m.front){ ctx.fillStyle = "rgba(5,8,10,.85)"; ctx.font = `${Math.round(rad * 1.2)}px Texturina, serif`; ctx.fillText(GLYPH[m.b], x, y + 1); }
    }
    if (pick){ const q = quads.find(q => q.i === pick.i && q.k === pick.k); if (q){ ctx.strokeStyle = "rgba(255,226,160,.95)"; ctx.lineWidth = 2;
      ctx.shadowColor = "rgba(255,210,140,.9)"; ctx.shadowBlur = 10;
      ctx.beginPath(); q.pts.forEach(([x, y], n) => n ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.stroke(); ctx.shadowBlur = 0; } }
  }
  function size(){
    const rect = host.getBoundingClientRect(); dpr = Math.min(2, devicePixelRatio || 1);
    W = rect.width; H = Math.round(rect.width);
    cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + "px";
  }
  /* ---------- turning it ---------- */
  let drag = null;
  cv.addEventListener("pointerdown", e => { drag = { x: e.clientX, y: e.clientY, yaw, pitch, moved: false, spin }; spin = 0; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", e => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
    yaw = drag.yaw - dx * .008; pitch = Math.max(-1.55, Math.min(1.55, drag.pitch + dy * .006));
  });
  cv.addEventListener("pointerup", e => {
    const d = drag; drag = null; if (!d) return;
    if (!d.moved) tap(e); else if (!reduce) setTimeout(() => { if (!drag) spin = .0016; }, 2500);
  });
  cv.addEventListener("keydown", e => {
    const k = { ArrowLeft: [.12, 0], ArrowRight: [-.12, 0], ArrowUp: [0, -.08], ArrowDown: [0, .08] }[e.key];
    if (k){ e.preventDefault(); spin = 0; yaw += k[0]; pitch = Math.max(-1.55, Math.min(1.55, pitch + k[1])); if (reduce) draw(); }
  });
  function tap(e){
    const rect = cv.getBoundingClientRect(), x = e.clientX - rect.left, y = e.clientY - rect.top;
    const inside = (pts) => { let c = false; for (let a = 0, b = pts.length - 1; a < pts.length; b = a++){
      const [xa, ya] = pts[a], [xb, yb] = pts[b]; if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) c = !c; } return c; };
    const q = [...quads].sort((p, q2) => q2.z - p.z).find(q => inside(q.pts));
    if (!q){ pick = null; cap.textContent = ""; return; }
    pick = { i: q.i, k: q.k };
    const lon = norm(cusp + (q.i + .5) * 360 / NU);
    const here = WyrdWheel.WHEEL_BODIES.filter(b => Math.abs(((pos(b) - lon + 540) % 360) - 180) < 360 / NU);
    cap.textContent = `${LAYERS[q.k].name}: ${q.col.label} · ${signOf(lon)} ${Math.floor(norm(lon) % 30)}° ${Z}${here.length ? " · " + here.join(", ") : ""}`;
    if (reduce) draw();
    if (window.Wyrd && Wyrd.pulse) Wyrd.pulse("tap", { houses: "house", signs: "sign", runes: "rune", gates: "gate", mansions: "nak", tropical: "trop" }[LAYERS[q.k].id]);
  }
  addEventListener("resize", () => { size(); if (!raf) draw(); });
  size();
  if (reduce) draw();
  return {
    start(){ if (!raf && !reduce) raf = requestAnimationFrame(frame); else if (reduce){ size(); draw(); } },
    stop(){ if (raf){ cancelAnimationFrame(raf); raf = null; } },
    toggle(id, v){ on[id] = v; if (v){ built = performance.now() - LAYERS.findIndex(l => l.id === id) * 350; } if (reduce){ shown[id] = v ? 1 : 0; draw(); } },
    get layers(){ return LAYERS.map(l => ({ ...l, on: on[l.id] })); },
    get zodiac(){ return Z; },
    setZodiac(z){ Z = z === "tropical" ? "tropical" : "sidereal"; seat(); paint(); pick = null; cap.textContent = "";
      if (!reduce){ built = performance.now(); LAYERS.forEach(l => { shown[l.id] = 0; }); } draw(); },
  };
}

window.WyrdTorus = { mount, LAYERS };
})();
