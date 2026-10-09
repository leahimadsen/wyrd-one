'use strict';
/* ============================================================
   THE SKY AROUND THE EARTH
   Today's sky as a torus of light with the Earth at its centre.
   Over the top of the ring, from the outer edge in: the sidereal
   signs, the twenty-seven mansions, the sixty-four gates and the
   tropical signs. The planets ride the outer edge at their degrees;
   with a birth chart, its planets ride the inner edge, so a moving
   planet and the natal one it crosses line up across the ring.
   One control folds it flat into a wheel seen from above (Aries at
   nine o'clock, as on the other wheels) and back out into three
   dimensions. Drag to turn it; tap to see what is there. With the
   mandala loaded (tarot.js), a fifth band carries its cards.
   Plain canvas, no library. Shares its look with torus.js.
   - WyrdSkyTorus.mount(host, { rows, natal, ay, caption, mode, tarot })
       rows:  [{ body, sid, gate, line, retro }] (the sky now)
       natal: { sid: {Sun: lon, ...} } (optional)
   ============================================================ */
(() => {
const { norm, nakIndex, GLYPH, NAKSHATRA } = Wyrd.helpers;
const TAU = Math.PI * 2, D2R = Math.PI / 180;
const SIGNS_ = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SG = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"].map(g => g + "︎");
const BASE = [                       /* outer edge → over the top → inner edge */
  { id: "signs", name: "Sidereal signs" }, { id: "mansions", name: "Mansions" },
  { id: "gates", name: "Gates" }, { id: "tropical", name: "Tropical signs" },
];
const TAROT_RGB = [[150, 120, 230], [110, 150, 230], [200, 120, 150], [120, 190, 170], [220, 170, 110], [150, 200, 120]];
const NU = 216, PER = 6, NB = 12, R = 1, r = 0.42;
const GATE_AT = trop => GATE_ORDER[Math.floor(norm(trop - 302) / 5.625)];

function mount(host, opts){
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tarot = opts.tarot || null;                                   // the 108 padas of the mandala, when loaded
  const LAYERS = tarot ? [...BASE, { id: "tarot", name: "The mandala's cards" }] : BASE, NV = LAYERS.length * PER;
  const rows = opts.rows || [], natal = opts.natal && opts.natal.sid ? opts.natal.sid : null;
  const ay = opts.ay != null ? opts.ay : (rows[0] ? norm(rows[0].trop - rows[0].sid) : 24.2);
  const cap = opts.caption || { set textContent(v){} };
  host.classList.add("st-host");
  host.innerHTML = `<canvas class="st-cv" tabindex="0" role="img" aria-label="Today's planets on the zodiac around the Earth. Drag or use the arrow keys to turn it; tap to see what is there."></canvas>`;
  const cv = host.querySelector("canvas"), ctx = cv.getContext("2d");

  /* ---------- what each cell is ---------- */
  const at = (lon, b) => Math.abs(((lon - b + 540) % 360) - 180);
  const bodiesIn = (lo, hi) => rows.filter(x => norm(x.sid - lo) < norm(hi - lo)).map(x => x.body);
  const skyGates = new Set(rows.map(x => x.gate)), moon = rows.find(x => x.body === "Moon");
  const moonNak = moon ? nakIndex(moon.sid) : -1;
  function cell(layer, lon){
    const trop = norm(lon + ay);
    switch (layer){
      case "signs": { const s = Math.floor(norm(lon) / 30), here = bodiesIn(s * 30, s * 30 + 30);
        return { lit: here.length > 0, rgb: here.length ? [255, 222, 150] : s % 2 ? [205, 165, 90] : [228, 192, 118], label: `${SIGNS_[s]} (sidereal)${here.length ? " · " + here.join(", ") : ""}` }; }
      case "mansions": { const n = nakIndex(lon);
        return { lit: n === moonNak, rgb: n === moonNak ? [150, 255, 220] : n % 2 ? [70, 110, 170] : [92, 132, 192], label: `${NAKSHATRA[n][0]}${n === moonNak ? " · the Moon's mansion today" : ""}` }; }
      case "gates": { const g = GATE_AT(trop), lit = skyGates.has(g), who = rows.filter(x => x.gate === g).map(x => x.body);
        return { lit, rgb: lit ? [240, 236, 225] : [70, 130, 150], label: `Gate ${g}${GATE_NAME[g] ? " · " + GATE_NAME[g] : ""}${who.length ? " · lit by " + who.join(", ") : ""}` }; }
      case "tropical": { const s = Math.floor(trop / 30); return { rgb: s % 2 ? [150, 110, 240] : [175, 140, 255], label: `${SIGNS_[s]} (tropical)` }; }
      case "tarot": { const c = WyrdTarot.at(tarot, lon), who = rows.filter(x => Math.floor(norm(x.sid) / (10 / 3)) === c.idx).map(x => x.body), t = Math.floor(c.idx / 9);
        return { lit: who.length > 0, rgb: who.length ? [255, 236, 200] : TAROT_RGB[t % TAROT_RGB.length].map(v => v - (c.idx % 2) * 18),
          label: `${WyrdTarot.trump(c)} · ${WyrdTarot.minor(c)} (${c.ruler})${c.void ? " · void: " + c.void : ""}${who.length ? " · " + who.join(", ") : ""}` }; }
    }
  }
  const COL = [];
  for (let i = 0; i < NU; i++){ const lon = (i + .5) * 360 / NU; COL.push(LAYERS.map(L => cell(L.id, lon))); }

  /* ---------- geometry: m = 0 is the flat wheel seen from above, m = 1 the torus tipped toward you ---------- */
  let m = opts.mode === "3d" ? 1 : 0, target = m, yaw = 0, spin = 0, pitchOff = 0, W = 0, H = 0, dpr = 1, raf = null, quads = [], pick = null;
  const uOf = i => i / NU * TAU;                                     // ecliptic longitude, radians
  const vOf = j => j / NV * Math.PI;                                  // over the top: 0 outer edge … π inner edge
  const pitch = () => m * 1.05 + pitchOff;
  function base(u, v, lift = 0){                                      // Aries at nine o'clock, signs running anticlockwise
    const rr = r + lift, rho = R + rr * Math.cos(v), th = Math.PI + u;
    return [rho * Math.cos(th), -rho * Math.sin(th), rr * Math.sin(v) * Math.max(m, .0001)];
  }
  function rot([x, y, z]){
    const cu = Math.cos(yaw), su = Math.sin(yaw), x1 = x * cu - y * su, y1 = x * su + y * cu;
    const cp = Math.cos(pitch()), sp = Math.sin(pitch());
    return [x1, y1 * cp - z * sp, y1 * sp + z * cp];
  }
  function proj([x, y, z]){ const d = 4.2, k = Math.min(W, H) * 1.06 / (d - z); return [W / 2 + x * k, H / 2 + y * k, z]; }
  const P3 = (u, v, lift) => proj(rot(base(u, v, lift)));
  const normal = (u, v) => { const th = Math.PI + u; return rot([Math.cos(v) * Math.cos(th), -Math.cos(v) * Math.sin(th), Math.sin(v) * Math.max(m, .2)]); };
  const glow = (rgb, k) => rgb.map(c => Math.min(255, Math.round(c + (255 - c) * k)));

  function earth(){
    const c = proj(rot([0, 0, 0])), s = Math.min(W, H) * 1.06 / 4.2 * (R - r) * (natal ? .5 : .62);   // inside the hole, clear of the inner edge
    ctx.globalCompositeOperation = "lighter";
    const halo = ctx.createRadialGradient(c[0], c[1], s * .6, c[0], c[1], s * 2.2);
    halo.addColorStop(0, "rgba(90,160,255,.28)"); halo.addColorStop(1, "rgba(60,120,255,0)");
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(c[0], c[1], s * 2.2, 0, TAU); ctx.fill();
    ctx.globalCompositeOperation = "source-over";
    const g = ctx.createRadialGradient(c[0] - s * .35, c[1] - s * .4, s * .1, c[0], c[1], s);
    g.addColorStop(0, "#9fd7ff"); g.addColorStop(.45, "#2f6fb8"); g.addColorStop(.8, "#173d6e"); g.addColorStop(1, "#0b1d36");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c[0], c[1], s, 0, TAU); ctx.fill();
    /* a hint of land, turning with the ring */
    ctx.save(); ctx.beginPath(); ctx.arc(c[0], c[1], s, 0, TAU); ctx.clip();
    ctx.fillStyle = "rgba(110,170,120,.55)";
    for (const [a, d, w] of [[.4, .35, .38], [2.3, .5, .3], [4.1, .2, .42], [5.4, .62, .22]]){
      const t = a + yaw; ctx.beginPath(); ctx.ellipse(c[0] + Math.cos(t) * s * d, c[1] + Math.sin(t) * s * d * .7, s * w, s * w * .62, t, 0, TAU); ctx.fill();
    }
    ctx.restore();
    ctx.fillStyle = "rgba(220,235,255,.85)"; ctx.font = `${Math.round(Math.max(10, s * .26))}px Texturina, serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle"; if (m < .5) ctx.fillText("Earth", c[0], c[1]);
  }

  function draw(){
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    const P = [];
    for (let i = 0; i <= NU; i++){ P.push([]); for (let j = 0; j <= NV; j++) P[i].push(P3(uOf(i), vOf(j))); }
    quads = [];
    ctx.globalCompositeOperation = "lighter";
    /* the underside of the tube: a faint shell, only once the ring has depth */
    if (m > .05) for (let i = 0; i < NU; i += 2) for (let j = 0; j < NB; j++){
      const v0 = Math.PI + j / NB * Math.PI, v1 = Math.PI + (j + 1) / NB * Math.PI, u0 = uOf(i), u1 = uOf(i + 2);
      const a = P3(u0, v0), b = P3(u1, v0), c = P3(u1, v1), d = P3(u0, v1), n = normal(uOf(i + 1), (v0 + v1) / 2);
      ctx.fillStyle = `rgba(120,140,230,${(m * (n[2] > 0 ? .05 : .025)).toFixed(3)})`;
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath(); ctx.fill();
    }
    /* the layers, as light. With depth, the half of the ring nearer than the Earth is painted after it,
       over a veil, so the Earth sits inside the ring rather than on top of its near edge */
    const zE = proj(rot([0, 0, 0]))[2], nearer = [];
    const paint = (q, veil) => {
      const [a, b, c, d] = q.pts;
      const path = () => { ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath(); };
      if (veil){ ctx.globalCompositeOperation = "source-over"; ctx.fillStyle = `rgba(8,12,28,${(.55 * m).toFixed(3)})`; path(); ctx.fill(); ctx.globalCompositeOperation = "lighter"; }
      ctx.fillStyle = q.fill; path(); ctx.fill();
    };
    for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++){
      const k = Math.floor(j / PER), a = P[i][j], b = P[i + 1][j], c = P[i + 1][j + 1], d = P[i][j + 1];
      const n = normal(uOf(i + .5), vOf(j + .5)), col = COL[i][k], front = n[2] > 0, fres = 1 - Math.abs(n[2]);
      const alpha = (front ? 1 : .5) * ((col.lit ? .36 : .1) + .2 * fres * fres * m);
      const [r_, g_, b_] = glow(col.rgb, col.lit ? .35 : .22);
      const q = { pts: [a, b, c, d], z: (a[2] + b[2] + c[2] + d[2]) / 4, col, i, k, fill: `rgba(${r_},${g_},${b_},${alpha.toFixed(3)})` };
      if (m > .3 && q.z > zE) nearer.push(q); else paint(q, false);
      if (front) quads.push(q);
    }
    ctx.globalCompositeOperation = "source-over";
    earth();
    ctx.globalCompositeOperation = "lighter";
    for (const q of nearer) paint(q, true);
    /* threads: the layer edges and every sign */
    ctx.lineWidth = 1;
    for (let k = 0; k <= LAYERS.length; k++){
      ctx.strokeStyle = "rgba(190,220,255,.18)"; ctx.beginPath();
      for (let i = 0; i <= NU; i++){ const q = P[i][Math.min(NV, k * PER)]; i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); } ctx.stroke();
    }
    for (let s = 0; s < 12; s++){
      const i = s * NU / 12; ctx.strokeStyle = "rgba(210,190,255,.16)"; ctx.beginPath();
      for (let j = 0; j <= NV; j++){ const q = P[i][j]; j ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); } ctx.stroke();
    }
    ctx.globalCompositeOperation = "source-over";
    /* the sign glyphs, written on the sidereal band and the tropical band */
    const R0 = Math.min(W, H), fs = Math.max(11, R0 * .036);
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const write = (k, lon, text, a0) => {
      const u = lon * D2R, v = vOf(k * PER + PER / 2), nz = m < .35 ? 1 : normal(u, v)[2]; if (nz < .05) return;
      const p = P3(u, v, .004), a = a0 * Math.min(1, (nz - .05) * 3);
      ctx.font = `${Math.round(fs * (k ? .62 : .72))}px Texturina, serif`; ctx.shadowColor = "rgba(180,220,255,.7)"; ctx.shadowBlur = 6;
      ctx.fillStyle = `rgba(236,240,255,${a})`; ctx.fillText(text, p[0], p[1]);
    };
    /* each sign named on both bands: sidereal on the outer, tropical on the inner */
    for (let s = 0; s < 12; s++){ write(0, s * 30 + 15, `${SG[s]} ${SIGNS_[s].slice(0, 3)}`, .95); write(3, norm(s * 30 + 15 - ay), `${SG[s]} ${SIGNS_[s].slice(0, 3)}`, .7); }
    ctx.shadowBlur = 0;
    /* the planets: today's on the outer edge, the birth chart's on the inner */
    const place = (lon, v, lift) => { const u = lon * D2R; return { p: P3(u, v, lift), z: normal(u, v)[2] }; };
    const marks = [
      ...rows.map(x => ({ b: x.body, retro: x.retro, sky: true, ...place(x.sid, 0, .1) })),
      ...(natal ? Object.keys(natal).filter(b => GLYPH[b] && b !== "Earth").map(b => ({ b, sky: false, ...place(natal[b], Math.PI, .1) })) : []),
    ].sort((a, b) => a.z - b.z);
    for (const k of marks){
      const [x, y] = k.p, rad = Math.max(9, R0 * (k.sky ? .026 : .02)), a = k.z > -.2 ? 1 : .35;
      ctx.globalCompositeOperation = "lighter";
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad * 2.4);
      g.addColorStop(0, k.sky ? `rgba(255,248,230,${.9 * a})` : `rgba(150,240,215,${.85 * a})`); g.addColorStop(1, "rgba(200,180,255,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, rad * 2.4, 0, TAU); ctx.fill();
      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = "rgba(5,8,14,.85)"; ctx.beginPath(); ctx.arc(x, y, rad * .95, 0, TAU); ctx.fill();
      ctx.fillStyle = k.sky ? (k.retro ? "#9fe0cc" : `rgba(255,246,225,${a})`) : `rgba(140,235,205,${a})`;
      ctx.font = `${Math.round(rad * 1.25)}px Texturina, serif`; ctx.fillText(GLYPH[k.b], x, y + 1);
    }
    if (pick){ const q = quads.find(q => q.i === pick.i && q.k === pick.k); if (q){ ctx.strokeStyle = "rgba(255,226,160,.95)"; ctx.lineWidth = 2;
      ctx.beginPath(); q.pts.forEach(([x, y], n) => n ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.stroke(); } }
  }

  function frame(){
    const was = m;
    if (m !== target) m = reduce ? target : m + Math.sign(target - m) * Math.min(Math.abs(target - m), .035);
    if (target === 0){ yaw *= reduce ? 0 : .9; pitchOff *= .8; if (Math.abs(yaw) < 1e-3) yaw = 0; }
    else if (spin && !drag) yaw += spin;
    draw();
    raf = (target === m && !spin && !drag && was === m && (target === 0 ? yaw === 0 : true) && (reduce || !spin)) ? null : requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
  function size(){
    const rect = host.getBoundingClientRect(); dpr = Math.min(2, devicePixelRatio || 1);
    W = rect.width; H = Math.round(rect.width);
    cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + "px"; draw();
  }

  /* ---------- turning and tapping ---------- */
  let drag = null;
  cv.addEventListener("pointerdown", e => { drag = { x: e.clientX, y: e.clientY, yaw, pitchOff, moved: false }; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", e => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 5) drag.moved = true;
    if (drag.moved && target === 1){ spin = 0; yaw = drag.yaw - dx * .008; pitchOff = Math.max(-1.0, Math.min(.5, drag.pitchOff + dy * .005)); kick(); }
  });
  cv.addEventListener("pointerup", e => { const d = drag; drag = null; if (d && !d.moved) tap(e); else if (target === 1 && !reduce) setTimeout(() => { if (!drag){ spin = .0018; kick(); } }, 2500); });
  cv.addEventListener("keydown", e => {
    const k = { ArrowLeft: [.12, 0], ArrowRight: [-.12, 0], ArrowUp: [0, -.08], ArrowDown: [0, .08] }[e.key];
    if (k && target === 1){ e.preventDefault(); spin = 0; yaw += k[0]; pitchOff = Math.max(-1, Math.min(.5, pitchOff + k[1])); kick(); }
  });
  function tap(e){
    const rect = cv.getBoundingClientRect(), x = e.clientX - rect.left, y = e.clientY - rect.top;
    const near = [...rows.map(p => ({ p, v: 0, sky: true })), ...(natal ? Object.keys(natal).filter(b => GLYPH[b]).map(b => ({ p: { body: b, sid: natal[b] }, v: Math.PI, sky: false })) : [])]
      .map(o => ({ ...o, q: P3(o.p.sid * D2R, o.v, .1) })).filter(o => Math.hypot(o.q[0] - x, o.q[1] - y) < Math.max(14, Math.min(W, H) * .03))[0];
    if (near){
      const p = near.p; pick = null;
      const card = tarot ? ` · ${WyrdTarot.minor(WyrdTarot.at(tarot, p.sid))}` : "";
      cap.textContent = near.sky ? `${p.body} today · ${SIGNS_[Math.floor(norm(p.sid) / 30)]} ${Math.floor(norm(p.sid) % 30)}° sidereal · ${SIGNS_[Math.floor(norm(p.sid + ay) / 30)]} ${Math.floor(norm(p.sid + ay) % 30)}° tropical · ${NAKSHATRA[nakIndex(p.sid)][0]} · gate ${p.gate}.${p.line}${card}${p.retro ? " · retrograde" : ""}`
        : `Your ${p.body} at birth · ${SIGNS_[Math.floor(norm(p.sid) / 30)]} ${Math.floor(norm(p.sid) % 30)}° sidereal · ${SIGNS_[Math.floor(norm(p.sid + ay) / 30)]} ${Math.floor(norm(p.sid + ay) % 30)}° tropical${card}${rows.filter(t => at(t.sid, p.sid) < 3).map(t => ` · ${t.body} is crossing it now`).join("")}`;
      kick(); return;
    }
    const inside = pts => { let c = false; for (let a = 0, b = pts.length - 1; a < pts.length; b = a++){
      const [xa, ya] = pts[a], [xb, yb] = pts[b]; if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) c = !c; } return c; };
    const q = [...quads].sort((a, b) => b.z - a.z).find(q => inside(q.pts));
    if (!q){ pick = null; cap.textContent = ""; setMode(target === 1 ? "flat" : "3d"); return; }    // empty space: fold or unfold
    pick = { i: q.i, k: q.k };
    cap.textContent = `${LAYERS[q.k].name}: ${q.col.label}`;
    kick();
  }
  function setMode(v){
    target = v === "3d" ? 1 : 0; spin = target && !reduce ? .0018 : 0; pick = null;
    if (opts.onMode) opts.onMode(target ? "3d" : "flat");
    kick();
  }
  addEventListener("resize", size);
  size();
  return { setMode, get mode(){ return target ? "3d" : "flat"; }, resize: size, stop(){ if (raf){ cancelAnimationFrame(raf); raf = null; } } };
}

window.WyrdSkyTorus = { mount };
})();
