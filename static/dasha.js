'use strict';
/* ============================================================
   THE VIMSHOTTARI CLOCK
   The console's clock, rebuilt for the site. It reads the
   period tree from viz.js (dashaTree, subPeriods, DASHA_SEQ),
   which was verified against the server engine, and adds the
   decoding: what the system is, and how this person's own clock
   was set, worked through with their own numbers.
   Interpretation of the periods stays in the paid reading.
   ============================================================ */
(() => {
const COL = { Ketu:"#ff7a8a", Venus:"#ff8c1a", Sun:"#ffcc33", Moon:"#c8f7ff", Mars:"#ff3b4e",
              Rahu:"#6b6bff", Jupiter:"#ffd400", Saturn:"#22b8ff", Mercury:"#22e07a" };
const YRS = Object.fromEntries(DASHA_SEQ);
let root = null, D = null, selM = 0, selA = 0;

const ageAt = jd => (jd - CHART.jd) / YEAR;
const ages = r => {
  const a = ageAt(r.from), b = ageAt(r.to);
  return a < 0 ? `birth to age ${b.toFixed(0)}` : `age ${a.toFixed(0)} to ${b.toFixed(0)}`;
};
const yrs = n => n >= 2 ? `${n.toFixed(n % 1 ? 1 : 0)} years` : n >= 1 / 6 ? `${(n * 12).toFixed(0)} months` : `${Math.max(1, Math.round(n * 365.2425))} days`;
const mansionsOf = lord => NAKSHATRA.map((r, i) => r[1] === lord ? i : -1).filter(i => i >= 0);
const seat = lord => CHART.sid[lord] == null ? null
  : { i: nakIndex(CHART.sid[lord]), house: houseOf(CHART.sid[lord], CHART.ascS) };
const stamp = (rows, list) => rows.map(r => Object.assign(r, { now: list.now >= r.from && list.now < r.to, past: list.now >= r.to }));

/* ---------- a band of periods: HTML, so the names stay readable on a phone ---------- */
function band(rows, level, sel){
  const t0 = rows[0].from, total = rows[rows.length - 1].to - t0, now = jdNow();
  const segs = rows.map((r, k) => {
    const w = (r.to - r.from) / total * 100;
    return `<button class="vd-seg ${r.now ? "now" : r.past ? "past" : ""} ${k === sel ? "sel" : ""}"
      data-vd-level="${level}" data-vd-k="${k}" style="flex-basis:${w.toFixed(3)}%;--c:${COL[r.lord]}"
      aria-label="${r.lord}, ${fmtYM(r.from)} to ${fmtYM(r.to)}"><span>${w > 7 ? r.lord : w > 3.2 ? r.lord.slice(0, 2) : ""}</span></button>`;
  }).join("");
  const nx = (now - t0) / total * 100;
  const needle = nx >= 0 && nx <= 100 ? `<i class="vd-needle" style="left:${nx.toFixed(3)}%"></i>` : "";
  return `<div class="vd-band">${segs}${needle}</div>`;
}
function detail(r, extra){
  const born = r.from < CHART.jd;
  return `<p class="vd-det"><b style="color:${COL[r.lord]}">${r.lord}</b> · ${born ? "birth" : fmtYM(r.from)} to ${fmtYM(r.to)} · ${yrs(born ? (r.to - CHART.jd) / YEAR : r.years)} · ${ages(r)}${r.now ? ` · <em>running now, ${(((jdNow() - r.from) / (r.to - r.from)) * 100).toFixed(0)}% through</em>` : r.past ? " · past" : ""}${extra || ""}</p>`;
}

function paintBands(){
  const M = D.maha, m = M[selM];
  const A = stamp(subPeriods(m.lord, m.from, m.years), D);
  if (selA >= A.length) selA = 0;
  const a = A[selA];
  const P = stamp(subPeriods(a.lord, a.from, a.years), D);
  const pNow = P.findIndex(p => p.now);
  root.querySelector("#vdBands").innerHTML = `
    <div class="vd-row"><h4>The full cycle · ${M.length} periods from birth</h4>${band(M, "m", selM)}${detail(m, m.partial ? ` (${m.lord}'s full span is ${m.years} years)` : "")}</div>
    <div class="vd-row"><h4>Inside ${m.lord} · nine chapters</h4>${band(A, "a", selA)}${detail(a)}</div>
    <div class="vd-row"><h4>Inside ${m.lord} / ${a.lord} · nine passages</h4>${band(P, "p", pNow)}${pNow >= 0 ? detail(P[pNow]) : ""}</div>
    <p class="vd-tip">Tap a period on the top band to open its chapters below it; tap a chapter to open its passages.</p>`;
}

function render(){
  D = dashaTree(); if (!D) return;
  selM = Math.max(0, D.maha.indexOf(D.cur));
  selA = Math.max(0, D.antars.findIndex(a => a.now));
  const moon = NAKSHATRA[D.moonNak], first = D.maha[0], lord = moon[1];
  const ownMansions = mansionsOf(lord).map(i => NAKSHATRA[i][0]);
  const cur = D.cur, curA = D.curA, sub = cur.years * YRS[curA.lord] / 120;

  const level = (r, label) => {
    const s = seat(r.lord);
    return `<div style="--c:${COL[r.lord]}"><div class="lvl">${label}</div><div class="lord">${r.lord}</div>
      <div class="dt">${fmtFull(r.from)} to ${fmtFull(r.to)}</div>
      <div class="rem">${yrs(Math.max(0, (r.to - jdNow()) / YEAR))} left · ${(((jdNow() - r.from) / (r.to - r.from)) * 100).toFixed(0)}% through</div>
      ${s ? `<div class="dt vd-seat">${r.lord} stands in ${NAKSHATRA[s.i][0]}, house ${s.house}</div>` : ""}</div>`;
  };

  const rows = D.maha.map(m => {
    const s = seat(m.lord);
    return `<tr class="${m.now ? "now" : m.past ? "past" : ""}"><td><span class="swatch" style="background:${COL[m.lord]}"></span>${m.lord}</td>
      <td>${m.years}y${m.partial ? ` (${D.balance.toFixed(2)} left)` : ""}</td><td>${fmtYM(Math.max(m.from, CHART.jd))} to ${fmtYM(m.to)}</td>
      <td>${ages(m)}</td><td>${s ? `${NAKSHATRA[s.i][0]} · H${s.house}` : "—"}</td><td>${s && ENGINE[s.i] ? ENGINE[s.i][1] : "—"}</td></tr>`;
  }).join("");

  const lords = DASHA_SEQ.map(([l, y]) => {
    const ms = mansionsOf(l), s = seat(l);
    return `<div class="vd-lord"><dt><span class="swatch" style="background:${COL[l]}"></span>${l} · ${y}y</dt>
      <dd>${ms.map(i => s && i === s.i ? `<b>${NAKSHATRA[i][0]} ← ${l} stands here</b>` : NAKSHATRA[i][0]).join(" · ")}${
        s && !ms.includes(s.i) ? `<br><small>stands in ${NAKSHATRA[s.i][0]}, which ${NAKSHATRA[s.i][1]} governs</small>` : ""}</dd></div>`;
  }).join("");

  root.innerHTML = `
    <div class="vd-decode">
      <h3>What the Vimshottari is</h3>
      <p>Vimshottari means <em>one hundred and twenty</em>. It is the main timing system of Jyotish: a single clock, set at the moment of birth, that divides a life into periods, each ruled by one of the nine grahas. While a planet's period runs, that planet's concerns lead, and every other placement in the chart is lived through it.</p>
      <h3>How this clock is built</h3>
      <p>The whole sequence hangs off one measurement: <em>where the Moon stood inside its mansion when you were born</em>. Each of the twenty-seven mansions has a ruling planet, and the nine rulers repeat three times across the twenty-seven — so the Moon's mansion names the lord whose period was already running when you arrived, and how far through the mansion you were born tells you how much of that period was left to you.</p>
      <p>The nine periods run 7, 20, 6, 10, 7, 18, 16, 19 and 17 years and sum to <em>120</em> — a full human span. Each divides into nine sub-periods in the same order and in the same proportions, and each of those divides again. Three levels are shown below; the pattern continues as far down as you care to take it.</p>
      <ol class="vd-order">${DASHA_SEQ.map(([l, y]) => `<li style="--c:${COL[l]}"><b>${y}</b>${l}</li>`).join("")}</ol>
    </div>

    <div class="vd-yours">
      <h3>How your clock was set</h3>
      <div class="vd-step"><span>1</span><p>Your Moon stood in <b>${moon[0]}</b>, at ${signOf(CHART.sid.Moon)} ${degIn(CHART.sid.Moon).toFixed(2)}°. ${moon[0]} is ruled by <b>${lord}</b>, which governs ${ownMansions.join(", ")}.</p></div>
      <div class="vd-step"><span>2</span><p>You were born <b>${(D.through * 100).toFixed(1)}%</b> of the way through ${moon[0]}, so the same share of ${lord}'s ${YRS[lord]} years had already run before you arrived.</p></div>
      <div class="vd-step"><span>3</span><p>That left you <b>${D.balance.toFixed(2)} years</b> of ${lord} (${YRS[lord]} × ${(100 - D.through * 100).toFixed(1)}%). Your clock opened in ${lord} and handed over to ${D.maha[1].lord} in ${fmtYM(first.to)}. From there the lords follow in fixed order, each for its full span.</p></div>
      <div class="vd-step"><span>4</span><p>Each period divides by the same rule. A chapter lasts <em>period years × chapter lord's years ÷ 120</em>, so inside your ${cur.years}-year ${cur.lord} period, the ${curA.lord} chapter runs ${cur.years} × ${YRS[curA.lord]} ÷ 120 = <b>${sub.toFixed(2)} years</b>. Each chapter divides again the same way into passages.</p></div>
    </div>

    <h3 class="vd-h">Running now</h3>
    <div class="now-card vd-now">
      ${level(cur, "Mahadasha · the era")}${level(curA, "Antardasha · the chapter")}${level(D.curP, "Pratyantardasha · the passage")}
    </div>

    <div id="vdBands"></div>

    <h3 class="vd-h">The full sequence</h3>
    <div class="tw"><table class="vd-table"><tr><th>Lord</th><th>Span</th><th>Dates</th><th>Your age</th><th>Stands in</th><th>Shakti</th></tr>${rows}</table></div>

    <h3 class="vd-h">Each lord governs three mansions</h3>
    <dl class="vd-lords">${lords}</dl>
    <p class="vd-note">A lord standing in one of its own three mansions runs its era undiluted. A lord standing in someone else's is running its era through another power — and that second mansion's engine is the one to read.</p>`;
  paintBands();
}

document.addEventListener("click", e => {
  const s = root && e.target.closest(".vd-seg");
  if (!s || !root.contains(s)) return;
  const k = +s.dataset.vdK;
  if (s.dataset.vdLevel === "m"){
    selM = k;
    const m = D.maha[k], A = subPeriods(m.lord, m.from, m.years), n = jdNow();
    const i = A.findIndex(a => n >= a.from && n < a.to);
    selA = i >= 0 ? i : 0;
  } else if (s.dataset.vdLevel === "a") selA = k;
  else return;
  paintBands();
});

window.WyrdDasha = { mount(host){ root = host; render(); } };
})();
