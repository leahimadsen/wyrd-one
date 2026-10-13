'use strict';
/* THE BENCH, as a place to learn.
   Every chapter of a life is two planets sounding together: the era's lord as the root,
   the chapter's lord as the interval above it. How well the two get on in this chart
   (the fivefold friendship) sets the interval, from a unison to a tritone.
   - Your life as music: every era, coloured chapter by chapter; open one and play it.
   - The pair: what the two lords are by nature, what they are in this chart, and the
     compound they make, on the little table everyone's chart is read from.
   - Any two: put any two grahas together and hear them.
   - The ladder: the six states in order, on one root.
   - Train your ear: hear a pair and name its state.
   Uses viz.js's tables and engine (RESONANCE, pairResonance, dashaTree, Sound…).
   Its own clicks are data-bn-*, so viz.js's old bench handlers never catch them. */
(() => {
const { GLYPH } = Wyrd.helpers;
const STATES = ["self", "great friend", "friend", "neutral", "enemy", "great enemy"];
const EASY = ["great friend", "neutral", "great enemy"];
const yr = jd => jdToDay(jd).getUTCFullYear();
const cents = R => (1200 * Math.log2(R.ratio[0] / R.ratio[1])).toFixed(0);

let host, D = null, era = 0, pair = null, chap = null, seq = null, quiz = null, easy = true, score = { right: 0, asked: 0 };

const hz = g => TONE[g] || (g === "Rahu" ? 63.11 : 47.33);
function sound(root, ratio){
  const f = typeof root === "number" ? root : hz(root);
  Sound.chord([f / 2, f, f * ratio[0] / ratio[1], f * 2]);
}
const soundPairOf = (a, b) => sound(a, pairResonance(a, b).ratio);
function stopSeq(){ if (seq){ seq.forEach(clearTimeout); seq = null; } host.querySelectorAll(".bn-ch.play").forEach(x => x.classList.remove("play")); const b = host.querySelector("[data-bn-play]"); if (b) b.textContent = "▶ Play this era"; }

/* ---------------- your life as music ---------------- */
function chapters(m){ return subPeriods(m.lord, m.from, m.years).map(a => ({ ...a, r: pairResonance(m.lord, a.lord) })); }
function life(){
  const born = CHART.jd, end = D.maha[D.maha.length - 1].to, span = end - born, now = jdNow();
  const eras = D.maha.map((m, i) => {
    const a = Math.max(m.from, born), w = (m.to - a) / span * 100;
    const strip = chapters(m).filter(c => c.to > born).map(c => `<i style="flex-grow:${(c.to - Math.max(c.from, born)).toFixed(1)};background:${RESON_COL[c.r.rel]}"></i>`).join("");
    return `<button type="button" class="bn-era${i === era ? " on" : ""}" style="width:${w.toFixed(3)}%" data-bn-era="${i}" aria-pressed="${i === era}" aria-label="${m.lord} era, ${yr(a)} to ${yr(m.to)}">
      <span class="bn-strip">${strip}</span><span class="bn-gl">${GLYPH[m.lord]}</span></button>`;
  }).join("");
  const here = (now - born) / span * 100;
  return `<div class="bn-life"><div class="bn-eras">${eras}</div><div class="bn-here" style="left:${here.toFixed(2)}%"><b>now</b></div></div>
    <div class="bn-ages"><span>born ${yr(born)}</span><span>${yr(end)}</span></div>`;
}
function eraPanel(){
  const m = D.maha[era], cs = chapters(m), now = jdNow(), born = CHART.jd;
  const a = Math.max(m.from, born);
  const age = jd => Math.max(0, (jd - born) / YEAR).toFixed(0);
  const chips = cs.map((c, i) => {
    const R = c.r, cur = now >= c.from && now < c.to, before = c.to < born;
    return `<button type="button" class="bn-ch${i === chap ? " on" : ""}${cur ? " now" : ""}${before ? " pre" : ""}" style="flex-grow:${c.years.toFixed(3)};--c:${RESON_COL[R.rel]}" data-bn-ch="${i}"
      aria-label="${c.lord} chapter, ${yr(c.from)} to ${yr(c.to)}: ${R.state}${cur ? ", now" : ""}">
      <span class="g">${GLYPH[c.lord]}</span><span class="s">${R.state}</span><span class="y">${yr(c.from)}</span></button>`;
  }).join("");
  return `<div class="bn-erahead"><h4>${GLYPH[m.lord]} The ${m.lord} era <small>${yr(a)} to ${yr(m.to)} · age ${age(a)} to ${age(m.to)}</small></h4>
      <button type="button" class="tz-chip" data-bn-play>▶ Play this era</button></div>
    <div class="bn-chs" role="group" aria-label="The chapters of this era">${chips}</div>
    <p class="nw-fine">${m.lord} is the root all era long. Each chapter sounds another planet above it. Tap one to hear it and see why it sounds that way${D.maha.indexOf(D.cur) === era ? "; the outlined one is now" : ""}.</p>`;
}
function legend(){
  return `<div class="bn-legend">${STATES.map(k => `<button type="button" data-bn-state="${k}" style="--c:${RESON_COL[k]}"><i></i>${RESONANCE[k].state}</button>`).join("")}</div>`;
}

/* ---------------- the pair, and why ---------------- */
const NAT = { friend: "a friend", neutral: "neutral", enemy: "an enemy", self: "itself" };
function why(){
  const [a, b] = pair, r = pairResonance(a, b), col = RESON_COL[r.rel];
  if (r.outer) return `<div class="bn-card"><p>${r.reads}</p></div>`;
  const cell = (n, t) => { const k = MAITRI[n + "|" + t]; const on = r.natural === n && r.temporal === t;
    return `<td><button type="button" class="${on ? "on" : ""}" style="--c:${RESON_COL[k]}" data-bn-state="${k}">${RESONANCE[k].state}<small>${k}</small></button></td>`; };
  const steps = a === b ? `<p>A planet paired with itself: one tone, no second term. <b>Genesis</b>, the unison.</p>`
    : `<ol class="bn-why">
      <li><span>By nature</span><div>${a} counts ${b} ${NAT[r.natural]}. <small>The same in every chart.</small></div></li>
      <li><span>In your chart</span><div>${b} stands in the ${ORDN(r.houses)} sign from ${a}: ${r.temporal === "enemy" ? "an" : "a"} ${r.temporal} for now. <small>Counted from the root, the 2nd, 3rd, 4th, 10th, 11th and 12th signs make a friend; the rest an enemy.</small></div></li>
      <li><span>Together</span><div><b style="color:${col}">${r.rel}</b>, which sounds as <b style="color:${col}">${r.state}</b>: a ${r.interval.toLowerCase()}, ${r.ratio[0]}:${r.ratio[1]}. <small>Find it on the table below.</small></div></li></ol>`;
  return `<div class="bn-card" style="border-left-color:${col}">
    <div class="bn-top"><div><div class="bn-state" style="color:${col}">${r.state}</div>
      <div class="bn-sub">${GLYPH[a]} ${a} root · ${GLYPH[b]} ${b} above · ${r.interval} · ${r.ratio[0]}:${r.ratio[1]}${when()}</div></div>
      <button type="button" class="tz-chip" data-bn-sound>♪ Sound it</button></div>
    <p class="bn-reads">${r.reads}</p>
    ${steps}
    ${a === b ? "" : `<table class="bn-table"><caption>The fivefold friendship: nature across, this chart down</caption>
      <thead><tr><th></th><th>temporal friend</th><th>temporal enemy</th></tr></thead>
      <tbody>${["friend", "neutral", "enemy"].map(n => `<tr><th>natural ${n}</th>${cell(n, "friend")}${cell(n, "enemy")}</tr>`).join("")}</tbody></table>`}
    ${beatSVG(r.rootHz, r.ivHz)}
    <details class="bn-num"><summary>The numbers</summary>
      <p>Root ${r.rootHz.toFixed(2)} Hz · interval ${r.ivHz.toFixed(2)} Hz · ${r.cents.toFixed(0)} cents · beat ${r.beat.toFixed(2)} Hz. The trace draws both tones and their sum: the simpler the ratio, the sooner the sum repeats and the steadier it sits. As the numbers grow it heaves, and that heaving is what roughness is.</p></details>
  </div>`;
}
function when(){
  if (chap === null || !D.maha[era] || D.maha[era].lord !== pair[0]) return "";
  const m = D.maha[era], c = subPeriods(m.lord, m.from, m.years)[chap];
  return c && c.lord === pair[1] ? ` · your chapter ${yr(c.from)} to ${yr(c.to)}` : "";
}
const ORDN = n => n + (["th","st","nd","rd"][(n % 100 - 20) % 10] || ["th","st","nd","rd"][n % 100] || "th");
function picker(){
  const row = (side, cur) => `<div class="bn-pick" role="group" aria-label="${side === 0 ? "Root" : "Above it"}">${CLASSICAL.map(g =>
    `<button type="button" data-bn-g="${side}:${g}" aria-pressed="${g === cur}">${GLYPH[g]} ${g}</button>`).join("")}</div>`;
  return `<div class="bn-pickers"><div><h5>Root <small>the era's lord</small></h5>${row(0, pair[0])}</div>
    <div><h5>Above it <small>the chapter's lord</small></h5>${row(1, pair[1])}</div></div>`;
}

/* ---------------- the ladder ---------------- */
function ladder(){
  return `<div class="ladder">${STATES.map(k => {
    const R = RESONANCE[k];
    return `<button type="button" data-bn-state="${k}" style="border-left-color:${RESON_COL[k]}">
      <span class="nm">${R.state}</span><span class="rt">${R.ratio[0]}:${R.ratio[1]}</span>
      <span class="rd">${R.interval} · ${k}</span></button>`; }).join("")}</div>
    <button type="button" class="tz-chip" data-bn-ladder>▶ Play the whole ladder</button>
    <p class="nw-fine">All six on the same root, so the only thing changing is the interval. The step to listen for is from Transition to Tension: that is where consonance ends.</p>`;
}

/* ---------------- train your ear ---------------- */
function newQuiz(){
  const pool = easy ? EASY : STATES, k = pool[Math.floor(Math.random() * pool.length)];
  const roots = Object.values(TONE);
  quiz = { k, root: roots[Math.floor(Math.random() * roots.length)], got: null };
}
function ear(){
  const pool = easy ? EASY : STATES;
  let out = `<div class="cr-btns" role="group" aria-label="How many states">
      <button type="button" class="tz-chip" data-bn-easy="1" aria-pressed="${easy}">Three states</button>
      <button type="button" class="tz-chip" data-bn-easy="0" aria-pressed="${!easy}">All six</button></div>`;
  if (!quiz) return out + `<p><button type="button" class="tz-chip nw-play" data-bn-q>▶ Play a mystery pair</button></p>`;
  out += `<p><button type="button" class="tz-chip" data-bn-again>↻ Hear it again</button></p>
    <div class="cr-opts">${pool.map(k => `<button type="button" class="cr-opt${quiz.got ? (k === quiz.k ? " right" : k === quiz.got ? " wrong" : "") : ""}" data-bn-ans="${k}"${quiz.got ? " disabled" : ""}>${RESONANCE[k].state}</button>`).join("")}</div>`;
  if (quiz.got){
    const R = RESONANCE[quiz.k];
    out += `<p class="cr-say">${quiz.got === quiz.k ? "Yes." : "Not quite."} That was <b style="color:${RESON_COL[quiz.k]}">${R.state}</b>, a ${R.interval.toLowerCase()} (${R.ratio[0]}:${R.ratio[1]}).
      ${quiz.got !== quiz.k ? `<button type="button" class="nw-link" data-bn-compare>Hear the two side by side</button>` : ""}</p>
      <p class="cr-score">${score.right} of ${score.asked} right <button type="button" class="tz-chip" data-bn-q>Another ▶</button></p>`;
  }
  return out;
}

/* ---------------- painting ---------------- */
function paint(part){
  const q = s => host.querySelector(s);
  if (!part || part === "life"){ q(".bn-lifehost").innerHTML = life(); q(".bn-erahost").innerHTML = eraPanel(); }
  if (!part || part === "pair"){ q(".bn-whyhost").innerHTML = why(); q(".bn-pickhost").innerHTML = picker(); }
  if (!part || part === "ear") q(".bn-earhost").innerHTML = ear();
}
function choose(i){
  chap = i; const m = D.maha[era], c = subPeriods(m.lord, m.from, m.years)[i];
  pair = [m.lord, c.lord];
  host.querySelectorAll(".bn-ch").forEach((b, k) => b.classList.toggle("on", k === i));
  paint("pair");
}

function mount(el){
  host = el;
  if (!CHART){ host.innerHTML = `<div class="empty">Cast a chart to open the bench</div>`; return; }
  D = dashaTree();
  era = Math.max(0, D.maha.indexOf(D.cur));
  chap = subPeriods(D.cur.lord, D.cur.from, D.cur.years).findIndex(a => a.lord === D.curA.lord);
  pair = [D.cur.lord, D.curA.lord];
  host.innerHTML = `
    <div class="howto"><h5>How to use the bench</h5>
      <p>Your life runs in eras and chapters, each ruled by a planet. In every chapter two planets sound together: the era's lord as the <em>root</em>, the chapter's lord above it. How well those two get on in your chart sets the interval between them, from a unison to a tritone. Put sound on, then tap.</p></div>
    <h3 class="sec-h">Your life as music</h3>
    <div class="bn-lifehost"></div>${legend()}
    <div class="bn-erahost"></div>
    <h3 class="sec-h">Why it sounds that way</h3>
    <div class="bn-whyhost"></div>
    <h3 class="sec-h">Try any two</h3>
    <div class="bn-pickhost"></div>
    <h3 class="sec-h">The ladder</h3>
    ${ladder()}
    <h3 class="sec-h">Train your ear</h3>
    <div class="bn-earhost"></div>`;
  paint();

  host.addEventListener("click", e => {
    const t = e.target;
    const er = t.closest("[data-bn-era]");
    if (er){ stopSeq(); era = +er.dataset.bnEra; const m = D.maha[era];
      const cs = subPeriods(m.lord, m.from, m.years), now = jdNow();
      const i = cs.findIndex(c => now >= c.from && now < c.to);
      paint("life"); choose(i >= 0 ? i : cs.findIndex(c => c.to > CHART.jd)); soundPairOf(pair[0], pair[1]); return; }
    const ch = t.closest("[data-bn-ch]");
    if (ch){ stopSeq(); choose(+ch.dataset.bnCh); soundPairOf(pair[0], pair[1]); return; }
    if (t.closest("[data-bn-play]")){
      if (seq){ stopSeq(); return; }
      const m = D.maha[era], cs = subPeriods(m.lord, m.from, m.years), btns = host.querySelectorAll(".bn-ch");
      host.querySelector("[data-bn-play]").textContent = "❚❚ Stop";
      seq = cs.map((c, i) => setTimeout(() => {
        btns.forEach((b, k) => b.classList.toggle("play", k === i));
        soundPairOf(m.lord, c.lord);
        if (i === cs.length - 1) seq.push(setTimeout(stopSeq, 1900));
      }, i * 1700));
      return;
    }
    if (t.closest("[data-bn-sound]")){ soundPairOf(pair[0], pair[1]); return; }
    const st = t.closest("[data-bn-state]");
    if (st){ const R = RESONANCE[st.dataset.bnState]; sound(hz(pair[0]), R.ratio); return; }
    if (t.closest("[data-bn-ladder]")){
      stopSeq(); const rows = host.querySelectorAll(".ladder button");
      seq = STATES.map((k, i) => setTimeout(() => { rows.forEach((b, j) => b.classList.toggle("play", j === i)); sound(126.22, RESONANCE[k].ratio);
        if (i === STATES.length - 1) seq.push(setTimeout(() => rows.forEach(b => b.classList.remove("play")), 1900)); }, i * 1700));
      return;
    }
    const gp = t.closest("[data-bn-g]");
    if (gp){ const [side, g] = gp.dataset.bnG.split(":"); pair[+side] = g; chap = null;
      host.querySelectorAll(".bn-ch").forEach(b => b.classList.remove("on"));
      paint("pair"); soundPairOf(pair[0], pair[1]); return; }
    const ez = t.closest("[data-bn-easy]"); if (ez){ easy = ez.dataset.bnEasy === "1"; quiz = null; paint("ear"); return; }
    if (t.closest("[data-bn-q]")){ newQuiz(); sound(quiz.root, RESONANCE[quiz.k].ratio); paint("ear"); return; }
    if (t.closest("[data-bn-again]") && quiz){ sound(quiz.root, RESONANCE[quiz.k].ratio); return; }
    const an = t.closest("[data-bn-ans]");
    if (an && quiz && !quiz.got){ quiz.got = an.dataset.bnAns; score.asked++; if (quiz.got === quiz.k) score.right++; paint("ear"); return; }
    if (t.closest("[data-bn-compare]") && quiz){ sound(quiz.root, RESONANCE[quiz.k].ratio); setTimeout(() => sound(quiz.root, RESONANCE[quiz.got].ratio), 1900); }
  });
}

window.WyrdBench = { mount };
})();
