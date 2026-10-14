'use strict';
/* THE COLOUR ROOM, as a place to learn.
   - Your chart in colour: each planet as a disc on its house's colour, named by the relation.
   - The wheel: the twelve house hues with your planets standing round it, and a short
     lesson in four steps that drives it (the hues, distance, what planets do, your own).
   - The lab (viz.js) to try any planet in any house; a tile above loads straight into it.
   - Train your eye: name the house from its colour, or the relation between two.
   Uses the colour tables in viz.js (HOUSES, HUE_CLASS, CHROMATIC, ACHROMATIC, HARMONY…).
   Its own clicks are data-cr-*, so viz.js's room handlers never catch them. */
(() => {
const { GLYPH } = Wyrd.helpers;
const GRAHAS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"];
const ORD = n => n + (["th","st","nd","rd"][(n % 100 - 20) % 10] || ["th","st","nd","rd"][n % 100] || "th");
const DARK_TEXT = ["Yellow", "Yellow-orange", "Yellow-green", "Orange", "Blue-green", "Green"];
const ink = h => DARK_TEXT.includes(HOUSES[h - 1].color) ? "#120428" : "#fff";
const lc = s => s.charAt(0).toLowerCase() + s.slice(1);
const an = s => (/^[aeiou]/i.test(s) ? "an " : "a ") + lc(s);
const DIST_COL = ["#eaf3ff", "#c9b6ff", "#9a6bff", "#ffcc33", "#74c3a4", "#ff9be8", "#eaf3ff"];
const tone = h => bowl(126.22 * Math.pow(2, (h - 1) / 12), .5);

let C, host, focus = 1, step = 0, cls = null, dist = 3, pick = null;

/* what a graha does to the house it stands in */
function effect(p, h){
  const field = HOUSES[h - 1].hex;
  if (CHROMATIC[p]){
    const c = CHROMATIC[p], [d, name, aspect, gloss] = harmonyBetween(c.seat, h);
    return { kind: "hue", disc: c.hex, field, title: name, sub: aspect, d, gloss, seat: c.seat };
  }
  if (ACHROMATIC[p]){
    const a = ACHROMATIC[p];
    return { kind: "op", disc: p === "Venus" ? glazeDisc(field) : OP_DISC[p], field, after: opAfter(p, field),
             title: a.op, sub: `adds ${lc(a.adds)}`, gloss: a.note, sheen: p === "Venus" };
  }
  return { kind: "prism", disc: null, field, title: "Prism", sub: "splits the hue", gloss: UNRESOLVED.Ketu };
}
const PRISM = `conic-gradient(${HOUSES.map(x => x.hex).join(",")},${HOUSES[0].hex})`;
const houseOfP = p => houseOf(C.sid[p], C.ascS);

/* ---------------- your chart in colour ---------------- */
function palette(){
  const rows = GRAHAS.map(p => ({ p, h: houseOfP(p), e: effect(p, houseOfP(p)) }));
  const tiles = rows.map(({ p, h, e }) => {
    const bg = e.kind === "op" ? `${e.sheen ? SHEEN + "," : ""}linear-gradient(90deg,${e.field} 0 50%,${e.after} 50% 100%)` : e.field;
    const disc = e.kind === "prism" ? PRISM : e.disc;
    return `<button type="button" class="cr-tile${pick === p ? " on" : ""}" data-cr-p="${p}" aria-label="${p} in your ${ORD(h)} house: ${e.title}">
      <span class="cr-field" style="background:${bg}"><span class="cr-disc" style="background:${disc}"></span></span>
      <span class="cr-cap"><b>${GLYPH[p]} ${p}</b><small>house ${h} · ${lc(HOUSES[h - 1].color)}</small><em>${e.title}${e.kind === "hue" ? ` · ${lc(e.sub)}` : ""}</em></span></button>`;
  }).join("");
  const hue = rows.filter(r => r.e.kind === "hue");
  const loud = hue.slice().sort((a, b) => b.e.d - a.e.d)[0], quiet = hue.slice().sort((a, b) => a.e.d - b.e.d)[0];
  let sum = "";
  if (loud && quiet && loud !== quiet)
    sum = `<p class="cr-sum">Your loudest: <b>${GLYPH[loud.p]} ${loud.p}</b> in your ${ORD(loud.h)}, ${lc(loud.e.title)} (${lc(loud.e.sub)}), ${lc(CHROMATIC[loud.p].hue)} on ${lc(HOUSES[loud.h - 1].color)}.
      Your quietest: <b>${GLYPH[quiet.p]} ${quiet.p}</b> in your ${ORD(quiet.h)}, ${lc(quiet.e.title)}${quiet.e.d === 0 ? ", almost lost in its own colour" : ""}.</p>`;
  return `<div class="cr-tiles">${tiles}</div>${sum}
    <p class="nw-fine">The field is the colour of the house. The disc is the planet standing in it. Tap one to open it in the lab below.</p>`;
}

/* ---------------- the wheel ---------------- */
const CX = 170, RO = 126, RI = 70;
const P = (r, d) => [CX + r * Math.cos(d * Math.PI / 180), CX + r * Math.sin(d * Math.PI / 180)];
const mid = h => angleHouse(h) + 15;
function lit(h){
  if (step === 0) return cls ? HUE_CLASS[h - 1] === cls : true;
  if (step === 1) return h === focus || h === ((focus - 1 + dist) % 12) + 1 || h === ((focus - 1 - dist + 12) % 12) + 1;
  if (step === 2) return pick && CHROMATIC[pick] ? h === CHROMATIC[pick].seat || h === houseOfP(pick) : true;
  return true;
}
function chord(a, b, col, w){
  const [ax, ay] = P(RI - 4, mid(a)), [bx, by] = P(RI - 4, mid(b));
  return `<path d="M${ax},${ay} Q${CX},${CX} ${bx},${by}" stroke="${col}" stroke-width="${w || 1.6}" fill="none" opacity=".9"/>`;
}
function wheel(){
  let o = `<svg class="cr-wheel" viewBox="0 0 340 340" role="img" aria-label="The twelve house colours, with your planets around them">
    <defs><linearGradient id="crPrism" x1="0" x2="1">${HOUSES.map((x, i) => `<stop offset="${i / 11}" stop-color="${x.hex}"/>`).join("")}</linearGradient>
    ${(() => { const gz = glazeHex(HOUSES[houseOfP("Venus") - 1].hex);
      return `<radialGradient id="crVenus" cx=".34" cy=".28" r=".8"><stop offset="0" stop-color="#fff"/><stop offset=".1" stop-color="#fff" stop-opacity=".7"/><stop offset=".45" stop-color="${gz}"/><stop offset="1" stop-color="${mixHex(gz, "#000000", .42)}"/></radialGradient>`; })()}</defs>`;
  for (let h = 1; h <= 12; h++){
    const a0 = angleHouse(h), a1 = a0 + 30;
    const [x1, y1] = P(RO, a0), [x2, y2] = P(RO, a1), [x3, y3] = P(RI, a1), [x4, y4] = P(RI, a0);
    const [nx, ny] = P(RO - 20, mid(h)), [kx, ky] = P(RO - 36, mid(h));
    o += `<g class="cr-sec${lit(h) ? "" : " dim"}${h === focus && step !== 0 ? " on" : ""}" data-cr-h="${h}" role="button" tabindex="0" aria-label="House ${h}, ${HOUSES[h - 1].color}">
      <path d="M${x1},${y1} A${RO},${RO} 0 0 1 ${x2},${y2} L${x3},${y3} A${RI},${RI} 0 0 0 ${x4},${y4} Z" fill="${HOUSES[h - 1].hex}"/>
      <text x="${nx}" y="${ny + 4}" class="cr-n" fill="${ink(h)}">${h}</text>
      <text x="${kx}" y="${ky + 3}" class="cr-k" fill="${ink(h)}">${HUE_CLASS[h - 1].slice(0, 3).toUpperCase()}</text></g>`;
  }
  /* chords */
  if (step === 1 && dist > 0){
    o += chord(focus, ((focus - 1 + dist) % 12) + 1, DIST_COL[dist], 2.2);
    if (dist !== 6) o += chord(focus, ((focus - 1 - dist + 12) % 12) + 1, DIST_COL[dist], 2.2);
  } else if (step === 3){
    for (const d of [3, 4, 6]) o += chord(focus, ((focus - 1 + d) % 12) + 1, DIST_COL[d]) + (d !== 6 ? chord(focus, ((focus - 1 - d + 12) % 12) + 1, DIST_COL[d]) : "");
  } else if (step === 2 && pick && CHROMATIC[pick] && CHROMATIC[pick].seat !== houseOfP(pick)){
    o += chord(CHROMATIC[pick].seat, houseOfP(pick), CHROMATIC[pick].hex, 2.4);
  }
  /* your planets round the outside */
  const by = {};
  GRAHAS.forEach(p => (by[houseOfP(p)] = by[houseOfP(p)] || []).push(p));
  for (const [h, ps] of Object.entries(by)) ps.forEach((p, i) => {
    const row = i < 3 ? 0 : 1, k = row ? i - 3 : i, n = row ? ps.length - 3 : Math.min(3, ps.length);
    const [x, y] = P(RO + 15 + row * 21, mid(+h) + (k - (n - 1) / 2) * 9.5);
    const e = effect(p, +h), fill = e.kind === "prism" ? "url(#crPrism)" : p === "Venus" ? "url(#crVenus)" : e.disc;
    const dim = (step === 2 && pick && pick !== p) || (step === 1);
    o += `<g class="cr-pl${dim ? " dim" : ""}${pick === p ? " on" : ""}" data-cr-p="${p}" role="button" tabindex="0" aria-label="${p}, in house ${h}">
      <circle cx="${x}" cy="${y}" r="9.5" fill="${fill}" stroke="${p === "Saturn" ? "#cfc6ff" : "rgba(0,0,0,.45)"}" stroke-width="1"/>
      <text x="${x}" y="${y + 3.6}" class="cr-g" fill="${["Moon", "Jupiter", "Mercury"].includes(p) ? "#120428" : "#fff"}">${GLYPH[p]}</text></g>`;
  });
  /* the centre */
  let c1 = "", c2 = "";
  if (step === 0){ c1 = cls ? cls.toUpperCase() + "S" : "TWELVE HUES"; c2 = cls ? ({ primary: "fire", secondary: "air", tertiary: "earth · water" })[cls] : "twelve houses"; }
  else if (step === 1){ const r = HARMONY[dist]; c1 = `${dist} APART · ${r[2].toUpperCase()}`; c2 = r[1]; }
  else if (step === 2){ c1 = pick ? pick.toUpperCase() : "PLANETS"; c2 = pick ? effect(pick, houseOfP(pick)).title : "carry or change"; }
  else { c1 = `HOUSE ${focus}`; c2 = HOUSES[focus - 1].color; }
  o += `<circle cx="${CX}" cy="${CX}" r="${RI - 6}" class="cr-hole"/>
    <text x="${CX}" y="${CX - 4}" class="cr-c1">${c1}</text><text x="${CX}" y="${CX + 13}" class="cr-c2">${c2}</text></svg>`;
  return o;
}

/* ---------------- the lesson ---------------- */
const STEPS = ["Twelve hues", "Distance", "Planets", "Your houses"];
function lesson(){
  let body = "";
  if (step === 0){
    body = `<p>The colour wheel and the chart are both circles cut into twelve. Lay one on the other with red on the first house, and the colours sort the houses by element without anyone arranging it.</p>
      <div class="cr-btns" role="group" aria-label="Show">${["primary", "secondary", "tertiary"].map(k => `<button type="button" class="tz-chip" data-cr-cls="${k}" aria-pressed="${cls === k}">${k.charAt(0).toUpperCase() + k.slice(1)}</button>`).join("")}</div>
      <p class="cr-say">${!cls ? "Pick one to light it on the wheel." : cls === "primary"
        ? "The three hues nothing can be mixed from (red, yellow, blue) land on houses 1, 5 and 9: the fire trine, where things begin."
        : cls === "secondary" ? "Orange, green and violet, each the meeting of two primaries, land on 3, 7 and 11: the air trine, where things combine."
        : "The six in-between hues fill earth and water. Earth (2, 6, 10) follows a primary and holds what fire began; water (4, 8, 12) leads into the next one and dissolves toward it."}</p>`;
  } else if (step === 1){
    const r = HARMONY[dist], other = ((focus - 1 + dist) % 12) + 1;
    body = `<p>Colour theory names two hues by how far apart they sit on the wheel. Astrology names two planets the same way. Same circle, same steps, the same answers.</p>
      <label class="cr-slide">Steps apart: <b>${dist}</b><input type="range" min="0" max="6" step="1" value="${dist}" data-cr-dist aria-label="Steps apart on the wheel"></label>
      <div class="cr-pair"><span style="background:${HOUSES[focus - 1].hex}">${focus}</span><span style="background:${HOUSES[other - 1].hex}">${other}</span></div>
      <p class="cr-say"><b>${r[1]}</b> in colour, <b>${lc(r[2])}</b> in astrology. ${r[3]}</p>
      <p class="nw-fine">Tap any house on the wheel to measure from there.</p>`;
  } else if (step === 2){
    const chips = GRAHAS.map(p => {
      const e = effect(p, houseOfP(p)), bg = e.kind === "prism" ? PRISM : e.disc;
      return `<button type="button" class="cr-chip${pick === p ? " on" : ""}" data-cr-p="${p}"><i style="background:${bg}"></i>${GLYPH[p]} ${p}</button>`;
    }).join("");
    let say = "Four grahas carry a hue of their own. Four carry none and change the house's colour instead: the Moon and Saturn its value, how light or dark it is; Venus and Rahu its saturation, how vivid. Ketu splits it. Pick one.";
    if (pick && CHROMATIC[pick]){
      const c = CHROMATIC[pick], h = houseOfP(pick), e = effect(pick, h);
      say = `<b>${pick}</b> carries ${lc(c.hue)}, the hue of house ${c.seat}. In your chart it stands in house ${h}, ${lc(HOUSES[h - 1].color)}: ${e.d} ${e.d === 1 ? "step" : "steps"} from home, <b>${lc(e.title)}</b>, ${an(e.sub)}. ${e.gloss}`;
    } else if (pick && ACHROMATIC[pick]){
      const a = ACHROMATIC[pick];
      say = `<b>${pick}</b> has no hue of its own. Its operation is the <b>${a.op.toLowerCase()}</b>${a.constructed ? "" : `, adding ${lc(a.adds)}`}. ${a.note}${a.constructed
        ? ` <span class="nw-fine">The glaze is the painter's way of raising saturation, which no mixture can do. Giving it to Venus is a construction, on the meaning of <i>śukra</i>: bright, clear, pure.</span>` : ""}`;
    } else if (pick) say = `<b>${pick}</b>: ${UNRESOLVED[pick]}`;
    body = `<div class="cr-chips">${chips}</div><p class="cr-say">${say}</p>`;
  } else {
    const occ = GRAHAS.filter(p => houseOfP(p) === focus), h = HOUSES[focus - 1];
    const rel = d => { const j = ((focus - 1 + d) % 12) + 1, r = HARMONY[d];
      return `<li><span class="sw" style="background:${HOUSES[j - 1].hex}"></span>House ${j}, ${lc(HOUSES[j - 1].color)} <small>${lc(r[1])} · ${lc(r[2])}</small></li>`; };
    body = `<p class="cr-say"><b>House ${focus}, ${lc(h.color)}</b> · ${HUE_CLASS[focus - 1]}, ${HUE_ELEMENT[focus - 1].toLowerCase()}. ${h.phase}.</p>
      <p>${occ.length ? `Standing here in your chart: ${occ.map(p => `${GLYPH[p]} ${p}`).join(", ")}.` : "None of your planets stands here."}</p>
      <ul class="cr-rel">${rel(3)}${rel(4)}${rel(6)}</ul>
      <p class="nw-fine">Tap round the wheel. The lines show the house's squares, trines and the one straight across.</p>`;
  }
  return `<div class="cr-steps" role="tablist" aria-label="The lesson">${STEPS.map((s, i) => `<button type="button" role="tab" aria-selected="${i === step}" data-cr-step="${i}"><span>${i + 1}</span>${s}</button>`).join("")}</div>
    <div class="cr-body" role="tabpanel">${body}</div>
    <div class="cr-nav">${step > 0 ? `<button type="button" class="nw-link" data-cr-step="${step - 1}">◀ Back</button>` : "<span></span>"}${step < 3 ? `<button type="button" class="tz-chip" data-cr-step="${step + 1}">Next: ${STEPS[step + 1]} ▶</button>` : ""}</div>`;
}

/* ---------------- train your eye ---------------- */
let Q = null, score = { right: 0, asked: 0 }, qmode = "house";
const rnd = n => Math.floor(Math.random() * n);
const shuffle = a => { for (let i = a.length - 1; i > 0; i--){ const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; };
function newQ(){
  if (qmode === "house"){
    const h = rnd(12) + 1, opts = new Set([h]);
    while (opts.size < 4) opts.add(rnd(12) + 1);
    Q = { h, opts: shuffle([...opts]), got: null };
  } else {
    const a = rnd(12) + 1, d = rnd(6) + 1, b = ((a - 1 + (Math.random() < .5 ? d : 12 - d)) % 12) + 1;
    const opts = new Set([d]);
    while (opts.size < 4) opts.add(rnd(6) + 1);
    Q = { a, b, d, opts: shuffle([...opts]), got: null };
  }
}
function game(){
  if (!Q) newQ();
  const modes = `<div class="cr-btns" role="group" aria-label="Which game">
    <button type="button" class="tz-chip" data-cr-mode="house" aria-pressed="${qmode === "house"}">Name the house</button>
    <button type="button" class="tz-chip" data-cr-mode="rel" aria-pressed="${qmode === "rel"}">Name the relation</button></div>`;
  let ask, opts, after = "";
  if (qmode === "house"){
    ask = `<div class="cr-qsw" style="background:${HOUSES[Q.h - 1].hex}"></div><p>Which house wears this colour?</p>`;
    opts = Q.opts.map(h => `<button type="button" class="cr-opt${Q.got !== null ? (h === Q.h ? " right" : h === Q.got ? " wrong" : "") : ""}" data-cr-ans="${h}"${Q.got !== null ? " disabled" : ""}>House ${h}</button>`).join("");
    if (Q.got !== null) after = `<p class="cr-say">${Q.got === Q.h ? "Yes." : "Not quite."} House ${Q.h} is ${lc(HOUSES[Q.h - 1].color)}, ${an(HUE_CLASS[Q.h - 1])} in ${HUE_ELEMENT[Q.h - 1].toLowerCase()}: ${lc(HOUSES[Q.h - 1].phase)}.</p>`;
  } else {
    ask = `<div class="cr-qpair"><span style="background:${HOUSES[Q.a - 1].hex}"></span><span style="background:${HOUSES[Q.b - 1].hex}"></span></div><p>How do these two stand to each other?</p>`;
    opts = Q.opts.map(d => `<button type="button" class="cr-opt${Q.got !== null ? (d === Q.d ? " right" : d === Q.got ? " wrong" : "") : ""}" data-cr-ans="${d}"${Q.got !== null ? " disabled" : ""}>${HARMONY[d][1]} <small>${lc(HARMONY[d][2])}</small></button>`).join("");
    if (Q.got !== null) after = `<p class="cr-say">${Q.got === Q.d ? "Yes." : "Not quite."} Houses ${Q.a} and ${Q.b} are ${Q.d} ${Q.d === 1 ? "step" : "steps"} apart: ${lc(HARMONY[Q.d][1])} in colour, ${an(HARMONY[Q.d][2])} in astrology. ${HARMONY[Q.d][3]}</p>`;
  }
  return `${modes}<div class="cr-q">${ask}<div class="cr-opts">${opts}</div>${after}
    <p class="cr-score" aria-live="polite">${score.asked ? `${score.right} of ${score.asked} right` : "&nbsp;"}${Q.got !== null ? ` <button type="button" class="tz-chip" data-cr-next>Another ▶</button>` : ""}</p></div>`;
}

/* ---------------- painting ---------------- */
function paint(part){
  if (!part || part === "pal") host.querySelector(".cr-pal").innerHTML = palette();
  if (!part || part === "wheel"){ host.querySelector(".cr-wh").innerHTML = wheel(); host.querySelector(".cr-lesson").innerHTML = lesson(); }
  if (!part || part === "game") host.querySelector(".cr-game").innerHTML = game();
}
function toLab(p){
  labGraha = p; labHouse = houseOfP(p);
  document.querySelectorAll("#labGrahas [data-graha]").forEach(b => b.classList.toggle("on", b.dataset.graha === p));
  document.querySelectorAll("#labHouses [data-house]").forEach(b => b.classList.toggle("on", +b.dataset.house === labHouse));
  paintLab();
}

function mount(el, chart){
  host = el; C = chart;
  focus = houseOfP("Sun");
  host.innerHTML = `
    <div class="howto"><h5>How to use this room</h5>
      <p>Your twelve houses each have a colour, red at the first and round the wheel from there. Your planets either carry a colour of their own or change the colour of the house they stand in. Start with your own chart, then take the lesson, then try the lab.</p></div>
    <h3 class="sec-h">Your chart in colour</h3>
    <div class="cr-pal"></div>
    <h3 class="sec-h">Learn the wheel</h3>
    <div class="cr-learn"><div class="cr-wh"></div><div class="cr-lesson"></div></div>
    <h3 class="sec-h">The lab</h3>
    ${colourLab()}
    <h3 class="sec-h">Train your eye</h3>
    <div class="cr-game"></div>
    <details class="cr-anchor"><summary>The anchor, the one real choice</summary>
      <p>Red at the first house comes from Aries as the natural first sign and Mars as its lord. Defensible, and still a choice. Move the anchor and every correspondence rotates with it, including the elements, so it holds because of where it starts, and where it starts is stated every time.</p></details>`;
  paint();
  toLab(GRAHAS.map(p => ({ p, e: effect(p, houseOfP(p)) })).filter(x => x.e.kind === "hue").sort((a, b) => b.e.d - a.e.d)[0]?.p || "Mars");

  host.addEventListener("click", e => {
    const t = e.target;
    const p = t.closest("[data-cr-p]");
    if (p){
      const v = p.dataset.crP;
      if (p.closest(".cr-pal")){ pick = v; paint("pal"); toLab(v); const lab = host.querySelector(".lab"); if (lab) lab.scrollIntoView({ behavior: "smooth", block: "center" }); return; }
      pick = pick === v ? null : v; if (step !== 2 && p.closest(".cr-wh")) step = 2;
      paint("wheel"); return;
    }
    const h = t.closest("[data-cr-h]");
    if (h){ focus = +h.dataset.crH; if (step === 0 || step === 2) step = 3; tone(focus); paint("wheel"); return; }
    const s = t.closest("[data-cr-step]"); if (s){ step = +s.dataset.crStep; paint("wheel"); return; }
    const k = t.closest("[data-cr-cls]"); if (k){ cls = cls === k.dataset.crCls ? null : k.dataset.crCls; paint("wheel"); return; }
    const m = t.closest("[data-cr-mode]"); if (m){ qmode = m.dataset.crMode; Q = null; paint("game"); return; }
    const a = t.closest("[data-cr-ans]");
    if (a && Q && Q.got === null){
      Q.got = +a.dataset.crAns; score.asked++;
      const right = qmode === "house" ? Q.got === Q.h : Q.got === Q.d;
      if (right) score.right++;
      if (qmode === "house") tone(Q.h); else { tone(Q.a); setTimeout(() => tone(Q.b), 260); }
      paint("game"); return;
    }
    if (t.closest("[data-cr-next]")){ newQ(); paint("game"); }
  });
  host.addEventListener("input", e => { if (e.target.matches("[data-cr-dist]")){ dist = +e.target.value; host.querySelector(".cr-wh").innerHTML = wheel();
    const body = host.querySelector(".cr-lesson"); body.innerHTML = lesson(); const r = body.querySelector("[data-cr-dist]"); if (r) r.focus(); } });
  host.addEventListener("keydown", e => {
    const g2 = e.target.closest && e.target.closest("g[data-cr-h], g[data-cr-p]");
    if (g2 && (e.key === "Enter" || e.key === " ")){ e.preventDefault(); g2.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
  });
}

window.WyrdColour = { mount };
})();
