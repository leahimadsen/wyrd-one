'use strict';
/* ============================================================
   COMPARE
   You and up to eight more people.
   Two people: the pair's facts (the Sukuyō relation by name, the
   Jyotish eight-fold match, every planet in the other's houses, the
   aspects between you, how the two bodygraphs meet, the runes between
   you, the two charts on one wheel, the data). What it all means, in
   words, is the paid reading together (wyrd/together.py, lib/bond.json).
   Three to nine: the unit (every pair's Sukuyō bond in one grid, what
   the group completes together, the elements between you), and any
   pair can be opened in full.
   The words come from dynamics.js.
   ============================================================ */
(() => {
const { signOf, houseOf, GLYPH } = Wyrd.helpers;
const { esc, placeSearch, cast, savedList } = WyrdCommon;
const T = () => window.WyrdDynamics;
const g = (k, l) => Wyrd.gloss(k, l);
const ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"];
const WEIGHT = { Sun: 3, Moon: 3, Venus: 2.5, Mars: 2, Mercury: 1.5, Saturn: 2, Jupiter: 1.5, Rahu: 1.2, Ketu: 1.2 };
const OVERLAY = ["Sun", "Moon", "Venus", "Mars", "Saturn"];
const ELEMENTS = ["Fire", "Earth", "Air", "Water"];
const ORD = n => n + (["th", "st", "nd", "rd"][(n % 100 - 20) % 10] || ["th", "st", "nd", "rd"][n % 100] || "th");
const MAX = 9;
const NTH = ["", "", "a second", "a third", "a fourth", "a fifth", "a sixth", "a seventh", "an eighth", "a ninth"];

/* ---------- the arithmetic of two charts ---------- */
const flavour = x => x.n === 1 ? "conj" : (x.n === 3 || x.n === 6) ? "soft" : "hard";
function contacts(A, B){
  const out = [];
  for (const p of ORDER) for (const q of ORDER){
    const x = aspectBetween(A.C.sid[p], B.C.sid[q]);
    if (!x || x.orb > (x.n === 1 ? 6 : 5)) continue;
    out.push({ p, q, x, f: flavour(x), w: (WEIGHT[p] + WEIGHT[q]) * (1.4 - x.orb / 10) * (x.n === 1 ? 1.15 : 1) });
  }
  return out.sort((a, b) => b.w - a.w);
}
function relation(A, B){
  const a = A.C.extras && A.C.extras.sukuyo, b = B.C.extras && B.C.extras.sukuyo;
  if (!a || !b) return null;
  const RING = ["命","栄","衰","安","危","成","壊","友","親","業","栄","衰","安","危","成","壊","友","親","胎","栄","衰","安","危","成","壊","友","親"];
  const PAIR = { "命": "命", "業": "業胎", "胎": "業胎", "栄": "栄親", "親": "栄親", "友": "友衰", "衰": "友衰", "安": "安壊", "壊": "安壊", "危": "危成", "成": "危成" };
  const k = (b.index - a.index + 27) % 27, m = Math.min(k, 27 - k);
  const toA = RING[k], toB = RING[(27 - k) % 27], pair = PAIR[toA];
  return { a, b, toA, toB, pair, distance: pair === "命" || pair === "業胎" ? null : m <= 4 ? "near" : m <= 8 ? "far" : "middle" };
}
const gatesOf = C => new Set([C.natal.personality, C.natal.design].flatMap(c => Object.values(c).map(v => v.gate)));
const completes = (set, [p, q]) => set.has(p) && set.has(q);

/* ---------- words ---------- */
function contactText(c, A, B){
  const D = T();       /* the contact's full writing and its question are in the paid reading together */
  return `${esc(A.name)}'s ${c.p} (${D.ROLE[c.p]}) meets ${esc(B.name)}'s ${c.q} (${D.ROLE[c.q]}), ${D.FLAVOUR[c.f]}.`;
}
function sukuyoBlock(R, A, B){
  const D = T();
  if (!R) return `<p class="fine">Sukuyō needs both birth dates within the console's range.</p>`;
  const t = D.SUKUYO[R.pair];
  const role = (x, who, of) => `<b>${esc(who)}</b> is ${esc(of)}'s <span class="sk-k">${x}</span> ${D.NAMES[x]}`;
  return `<div class="sk-card">
    <div class="sk-pair"><span class="sk-big">${R.pair}</span><div><h4>${t.title}</h4><p class="fine">${t.short}${R.distance ? ` · ${g("distance", R.distance)}` : ""}</p></div></div>
    <p class="sk-who">${esc(A.name)}: <span class="sk-k">${R.a.kanji}</span> ${R.a.read} · ${esc(B.name)}: <span class="sk-k">${R.b.kanji}</span> ${R.b.read}</p>
    ${R.pair === "命" ? "" : `<p class="sk-who">${role(R.toA, B.name, A.name)}; ${role(R.toB, A.name, B.name)}.</p>`}
    </div>`;
}
function overview(cs, R, together){
  const n = { conj: 0, soft: 0, hard: 0 }; cs.forEach(c => n[c.f]++);
  const lean = n.soft > n.hard * 1.5 ? "The bond leans easy: more of it flows than grinds."
    : n.hard > n.soft * 1.5 ? "The bond leans charged: more of it tests than soothes, and that can be its strength."
    : "Ease and friction are evenly matched.";
  const sk = R ? ` In Sukuyō you are ${T().SUKUYO[R.pair].short} (${R.pair}).` : "";
  return `<p>Between your charts there are <b>${cs.length}</b> contacts: ${n.soft} flowing, ${n.hard} in friction and ${n.conj} fused. ${lean}${sk}
    ${together.length ? ` Together you complete ${together.length} ${g("channel", together.length > 1 ? "channels" : "channel")} neither of you has alone.` : ""}</p>`;
}

/* ---------- what the free side leaves to the paid reading ---------- */
const LOCKED = `<div class="cp-lock"><h4 class="cp-h">The bond in words</h4>
  <p>The full write-up of this bond is in <b>the reading together</b>. It covers what the bond is for, how it lifts you and how it can drag you down,
  the Sukuyō relation and each of the contacts above explained, your planets in each other's houses, and the questions the bond raises.</p>
  <button type="button" class="link-btn cp-tobuy">See the reading together ↑</button></div>`;

/* ---------- the pair ---------- */
function pairView(A, B){
  const D = T(), cs = contacts(A, B), R = relation(A, B);
  const gA = gatesOf(A.C), gB = gatesOf(B.C), both = new Set([...gA, ...gB]);
  const together = WyrdBody.channels.filter(ch => completes(both, ch) && !completes(gA, ch) && !completes(gB, ch));
  const shared = [...gA].filter(x => gB.has(x)).sort((a, b) => a - b);
  const over = (P, Q) => OVERLAY.map(b => { const h = houseOf(P.C.sid[b], Q.C.ascS);
    const phase = typeof HOUSES !== "undefined" && HOUSES[h - 1] ? HOUSES[h - 1].phase : D.HOUSE[h - 1];
    return `<li><b>${esc(P.name)}'s ${GLYPH[b]} ${b}</b> in ${esc(Q.name)}'s ${ORD(h)} house — ${phase.charAt(0).toLowerCase() + phase.slice(1)}.</li>`; }).join("");
  const top = cs.slice(0, 6).map(c => `<li><h5>${esc(A.name)}'s ${GLYPH[c.p]} ${c.p} · ${esc(B.name)}'s ${GLYPH[c.q]} ${c.q}
      <span style="color:${c.x.col}">${c.x.name.toLowerCase()}</span> <small>orb ${c.x.orb.toFixed(1)}°</small></h5><p>${contactText(c, A, B)}</p></li>`).join("");
  const rows = (P, Q) => WyrdWheel.WHEEL_BODIES.map(b => `<tr><th>${GLYPH[b]} ${b}</th><td>${signOf(P.C.sid[b])}</td><td>${houseOf(P.C.sid[b], Q.C.ascS)}</td></tr>`).join("");
  return `<div class="cp-pair">
    <h3 class="sec-h">${esc(A.name)} and ${esc(B.name)}</h3>
    <h4 class="cp-h">${g("sukuyo", "Sukuyō")} · the bond by the lunar mansions</h4>${sukuyoBlock(R, A, B)}
    <h4 class="cp-h">Jyotish · the eight-fold match</h4>${window.WyrdKuta ? WyrdKuta.html(A, B) : ""}
    <h4 class="cp-h">Your planets in each other's houses</h4>${window.WyrdSynastry ? WyrdSynastry.houses(A, B) : `<ul class="cp-over">${over(B, A)}</ul><ul class="cp-over">${over(A, B)}</ul>`}
    <h4 class="cp-h">Traditional synastry · the aspects between you</h4>${overview(cs, R, together)}
    ${top ? `<ol class="cp-contacts">${top}</ol>` : `<p>No close contacts between the main planets: a bond that works through the houses rather than the aspects.</p>`}
    ${LOCKED}
    ${window.WyrdSynastry ? `<h4 class="cp-h">${g("design", "Human Design")} · how your bodies meet</h4>${WyrdSynastry.design(A, B)}` : ""}
    <h4 class="cp-h">${g("rune", "Runes")} · the runes between you</h4>${window.WyrdRunes ? WyrdRunes.pairHTML(A, B) : ""}
    <h4 class="cp-h">${esc(A.name)} inside, ${esc(B.name)} outside</h4><div class="cmp-wheel" data-pair-wheel></div>
    <details class="cp-data"><summary>All the data</summary><div class="facts">
      <div class="fact"><h3>${esc(B.name)} in ${esc(A.name)}'s houses</h3><table class="mini"><tr><th>Planet</th><th>Sign</th><th>House</th></tr>${rows(B, A)}</table></div>
      <div class="fact"><h3>${esc(A.name)} in ${esc(B.name)}'s houses</h3><table class="mini"><tr><th>Planet</th><th>Sign</th><th>House</th></tr>${rows(A, B)}</table></div>
      <div class="fact"><h3>Every contact</h3><ul class="kar asp">${cs.map(c => `<li><span>${GLYPH[c.p]} ${c.p} · ${GLYPH[c.q]} ${c.q}</span><span style="color:${c.x.col}">${c.x.name}</span><span>${c.x.orb.toFixed(1)}°</span></li>`).join("") || "<li>None within orb</li>"}</ul></div>
      <div class="fact"><h3>${g("channel", "Channels you complete together")}</h3><p>${together.map(([p, q]) => `${p}–${q}`).join(", ") || "None"}</p>
        <h3 class="fact-h2">Gates you share</h3><p>${shared.join(", ") || "None"}</p></div></div></details></div>`;
}

/* ---------- the unit ---------- */
function unitView(P){
  const D = T();
  const pairs = []; for (let i = 0; i < P.length; i++) for (let k = i + 1; k < P.length; k++) pairs.push([i, k, relation(P[i], P[k])]);
  const cell = (i, k) => { if (i === k) return `<td class="sk-self">${P[i].C.extras && P[i].C.extras.sukuyo ? `${P[i].C.extras.sukuyo.kanji}<small>${P[i].C.extras.sukuyo.read}</small>` : "—"}</td>`;
    const R = relation(P[i], P[k]); if (!R) return "<td>—</td>";
    return `<td><button type="button" class="sk-cell sk-${R.pair}" data-pair="${Math.min(i, k)}-${Math.max(i, k)}"><span>${R.toB}</span><small>${D.NAMES[R.toB]}${R.distance && P.length <= 4 ? " · " + R.distance : ""}</small></button></td>`; };
  const grid = `<div class="tw"><table class="sk-grid${P.length > 4 ? " dense" : ""}"><tr><th></th>${P.map(p => `<th scope="col" title="${esc(p.name)}">${esc(p.name)}</th>`).join("")}</tr>
    ${P.map((p, i) => `<tr><th scope="row" title="${esc(p.name)}">${esc(p.name)}</th>${P.map((_, k) => cell(i, k)).join("")}</tr>`).join("")}</table></div>
    <p class="fine">Read across: each cell is what the column's person is to the row's person. The diagonal is each person's own shuku. Tap a cell to open that pair below.</p>`;
  const groups = {}; pairs.forEach(([i, k, R]) => { if (R) (groups[R.pair] ||= []).push(`${esc(P[i].name)} & ${esc(P[k].name)}`); });
  const summary = Object.entries(groups).map(([pair, list]) => `<li><b>${pair} ${D.SUKUYO[pair].title.split(" · ")[1]}</b> — ${list.join("; ")}. <span class="fine">${D.SUKUYO[pair].short}.</span></li>`).join("");
  /* what only the whole unit completes */
  const sets = P.map(p => gatesOf(p.C)), all = new Set(sets.flatMap(s => [...s]));
  const unitOnly = WyrdBody.channels.filter(ch => completes(all, ch) && !sets.some(s => completes(s, ch)));
  const pairOnly = unitOnly.filter(ch => pairs.some(([i, k]) => completes(new Set([...sets[i], ...sets[k]]), ch)));
  const brings = ([p, q]) => [p, q].map(gt => `${gt} (${P.filter((_, i) => sets[i].has(gt)).map(x => esc(x.name)).join(", ")})`).join(" + ");
  const centreOf = {}; for (const k in WyrdBody.centres) for (const gt of WyrdBody.centres[k].gates) centreOf[gt] = WyrdBody.centres[k].label;
  const liveAll = WyrdBody.channels.filter(ch => completes(all, ch)), unitCentres = [...new Set(liveAll.flatMap(([p, q]) => [centreOf[p], centreOf[q]]))];
  /* the elements between you */
  const count = [0, 0, 0, 0], rowsE = P.map(p => {
    const pts = [["☉", p.C.sid.Sun], ["☽", p.C.sid.Moon]].concat(p.C.unknownTime ? [] : [["↑", p.C.ascS]]);
    pts.forEach(([, l]) => count[Math.floor(l / 30) % 4]++);
    return `<tr><th>${esc(p.name)}</th>${pts.map(([gl, l]) => `<td>${gl} ${signOf(l)}</td>`).join("")}${p.C.unknownTime ? "<td>—</td>" : ""}</tr>`; }).join("");
  const most = ELEMENTS[count.indexOf(Math.max(...count))], missing = ELEMENTS.filter((_, i) => !count[i]);
  return `<div class="cp-unit">
    <h3 class="sec-h">Your unit of ${P.length}</h3>
    <h4 class="cp-h">${g("sukuyo", "Sukuyō")} · every bond at once</h4>${grid}
    <ul class="cp-sk-sum">${summary}</ul>
    ${window.WyrdKuta ? `<h4 class="cp-h">Jyotish · every pair's match</h4>${P.length > 4 ? `<p class="fine">Strongest match first.</p>` : ""}<ul class="kar">${pairs.map(([i, k]) => { const x = WyrdKuta.read(P[i].C.sid.Moon, P[k].C.sid.Moon), y = WyrdKuta.read(P[k].C.sid.Moon, P[i].C.sid.Moon);
      return [Math.max(x.total, y.total), `<li><span>${esc(P[i].name)} · ${esc(P[k].name)}</span><span>${x.total === y.total ? x.total : `${x.total} / ${y.total}`} of 36</span></li>`]; })
      .sort((a, b) => P.length > 4 ? b[0] - a[0] : 0).map(r => r[1]).join("")}</ul>` : ""}
    <h4 class="cp-h">What you complete together</h4>
    <p>${unitOnly.length ? `The unit completes <b>${unitOnly.length}</b> ${g("channel", unitOnly.length > 1 ? "channels" : "channel")} no one of you has alone:` : "No channel needs the whole unit: each one the group completes, someone already carries."}</p>
    ${unitOnly.length ? `<ul class="ln-list">${unitOnly.map(ch => `<li>${ch[0]}–${ch[1]}: ${brings(ch)}${pairOnly.includes(ch) ? "" : " <small>(only with three or more of you)</small>"}</li>`).join("")}</ul>` : ""}
    <p>Between you, these ${g("centre", "centres")} are defined: ${unitCentres.join(", ") || "none"}.</p>
    <h4 class="cp-h">The elements between you</h4>
    <div class="tw"><table class="mini"><tr><th></th><th>Sun</th><th>Moon</th><th>Rising</th></tr>${rowsE}</table></div>
    <p>${ELEMENTS.map((e, i) => `${e} ${count[i]}`).join(" · ")}. The unit runs on <b>${most}</b>${missing.length ? `, and has no ${missing.join(" or ")} among its Suns, Moons and risings` : ""}.</p>
    <h4 class="cp-h">Each pair in full</h4>
    <div class="cp-pairs" role="group" aria-label="Choose a pair">${pairs.map(([i, k]) => `<button type="button" class="cal-chip" data-pair="${i}-${k}">${esc(P[i].name)} & ${esc(P[k].name)}</button>`).join("")}</div>
    <div class="cp-pair-host"></div></div>`;
}

/* ---------- the page ---------- */
function mount(host, X){
  const people = [{ name: X.birth.name || "You", C: X.C, birth: X.birth, self: true }];
  let adding = false, pairSel = "0-1";
  host.innerHTML = `${Wyrd.glossTerms(["synastry", "sukuyo", "shuku", "sanku", "aspect", "house", "channel"])}
    <div class="cp-people" aria-live="polite"></div>
    <div class="cp-add" hidden></div>
    <div class="cp-buy" hidden></div>
    <div class="cp-out"></div>`;
  const peopleEl = host.querySelector(".cp-people"), addEl = host.querySelector(".cp-add"), out = host.querySelector(".cp-out");

  /* the paid reading together: $22 for two, each extra person adds to it; members' prices come from /api/me */
  const buyEl = host.querySelector(".cp-buy");
  let price = null;
  const dollars = c => "$" + (c % 100 ? (c / 100).toFixed(2) : c / 100);
  fetch("/api/me").then(r => r.json()).then(d => { price = d.together ? { ...d.together, member: d.member } : null; drawBuy(); }).catch(() => {});
  function drawBuy(){
    buyEl.hidden = !price || people.length < 2;
    if (buyEl.hidden) return;
    const n = people.length, total = price.two + price.extra * (n - 2);
    buyEl.innerHTML = `<div class="cp-buybox"><h3 class="cp-h">The reading together</h3>
      <p>A written reading for ${n === 2 ? "the two of you" : `all ${n} of you`}. It starts with a story about how you ended up together, then covers what you bring out in each other and how the next thirty years look for you, year by year.</p>
      <button type="button" class="btn-cast cp-buybtn">Get our reading together — ${dollars(total)}${price.member ? ", your Order price" : ""}</button>
      <p class="muted">${dollars(price.two)} for two${n < price.max ? `, and ${dollars(price.extra)} for each person you add, up to ${price.max}` : ""}.</p>
      <p class="err" role="alert"></p></div>`;
  }
  buyEl.addEventListener("click", async e => {
    const btn = e.target.closest(".cp-buybtn"); if (!btn) return;
    const err = buyEl.querySelector(".err"), label = btn.textContent; err.textContent = "";
    btn.disabled = true; btn.textContent = "Opening checkout…";
    if (Wyrd.pulseNow) Wyrd.pulseNow("act", "buy-together");
    try {
      const r = await fetch("/api/checkout-together", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ people: people.map(p => ({ ...p.birth, name: p.birth.name || p.name })) }) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || "Checkout couldn't open.");
      location.href = j.url;
    } catch (x) { err.textContent = x instanceof TypeError ? "You're offline. Checkout needs a connection." : x.message; btn.disabled = false; btn.textContent = label; }
  });

  function drawPeople(){
    peopleEl.innerHTML = people.map((p, i) => `<span class="cp-chip${p.self ? " self" : ""}"><b>${esc(p.name)}</b>
      <small>${esc(p.birth.date)}${p.C.extras && p.C.extras.sukuyo ? ` · ${p.C.extras.sukuyo.kanji}` : ""}</small>
      ${p.self ? "" : `<button type="button" class="cp-x" data-remove="${i}" aria-label="Remove ${esc(p.name)}">×</button>`}</span>`).join("")
      + (people.length < MAX && !adding ? `<button type="button" class="cp-addbtn">＋ ${people.length === 1 ? "Add a person" : `Add ${NTH[people.length + 1]} person`}</button>` : "");
  }
  function drawForm(){
    const saved = savedList().filter(s => !(s.date === X.birth.date && s.time === X.birth.time && (s.name || "") === (X.birth.name || "")));
    addEl.hidden = !adding;
    if (!adding){ addEl.innerHTML = ""; return; }
    addEl.innerHTML = `<form class="cmp-form cast" autocomplete="off" novalidate>
      ${saved.length ? `<label class="f-name">From your saved charts <select name="saved"><option value="">Choose…</option>${saved.map((s, i) => `<option value="${i}">${esc(s.name || "Unnamed")} · ${esc(s.date)}</option>`).join("")}</select></label>
        <p class="hint f-name">or enter someone new:</p>` : ""}
      <label class="f-name">Their name <span>optional</span><input name="name" maxlength="80"></label>
      <label class="f-name">Their full name at birth <span>optional, for the numbers in the reading together</span><input name="full_name" maxlength="80" autocomplete="off"></label>
      <label>Date of birth <input name="date" type="date" min="1850-01-01" max="2149-12-31"></label>
      <label>Time of birth <input name="time" type="time"></label>
      <label class="f-unknown"><input type="checkbox" name="unknown"> Their birth time is unknown</label>
      <label class="f-place">Place of birth
        <input name="place" id="cmpPlace" placeholder="Start typing a town or city" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="cmpList">
        <ul id="cmpList" role="listbox" hidden></ul></label>
      <button type="submit" class="btn-cast">Add</button> <button type="button" class="link-btn cp-cancel">Cancel</button>
      <p class="err" role="alert"></p></form>`;
    const f = addEl.querySelector("form"), err = f.querySelector(".err");
    let place = null;
    placeSearch(f.querySelector("#cmpPlace"), f.querySelector("#cmpList"), p => { place = p; });
    f.unknown.addEventListener("change", () => { f.time.disabled = f.unknown.checked; if (f.unknown.checked) f.time.value = "12:00"; });
    f.addEventListener("submit", async e => {
      e.preventDefault(); err.textContent = "";
      const btn = f.querySelector("button[type=submit]");
      let b, chart;
      if (f.saved && f.saved.value !== ""){
        const s = saved[+f.saved.value]; const { savedAt, castAt, result, ...birth } = s; b = birth; chart = result && result.chart;
      } else {
        if (!f.date.value || (!f.unknown.checked && !f.time.value)){ err.textContent = "Enter their date of birth, and time if known."; return; }
        if (!place){ err.textContent = "Choose their birthplace from the list as you type."; return; }
        b = { name: f.name.value.trim(), full_name: f.full_name.value.trim() || undefined, date: f.date.value, time: f.unknown.checked ? "12:00" : f.time.value, unknown_time: f.unknown.checked || undefined,
              place_id: place.id, lat: place.lat, lon: place.lon, tz: place.tz, place_label: place.label };
      }
      btn.disabled = true; btn.textContent = "Casting…";
      try {
        if (!chart || !WyrdCommon.fresh({ chart })) chart = (await cast(b)).chart;
        people.push({ name: b.name || `Person ${people.length + 1}`, C: chart, birth: b });
        adding = false; pairSel = `0-${people.length - 1}`; draw();
        if (Wyrd.pulse) Wyrd.pulse("compare", people.length);
      } catch (x) { err.textContent = x instanceof TypeError ? "You're offline. Comparing needs a connection." : x.message; btn.disabled = false; btn.textContent = "Add"; }
    });
    f.querySelector(".cp-cancel").addEventListener("click", () => { adding = false; draw(); });
    (f.saved || f.name).focus();
  }
  function showPair(host2){
    const [i, k] = pairSel.split("-").map(Number);
    if (!people[i] || !people[k]) return;
    host2.innerHTML = pairView(people[i], people[k]);
    WyrdWheel.mount(host2.querySelector("[data-pair-wheel]"), people[i].C, { level: "simple", other: people[k].C, unknownTime: people[i].C.unknownTime, noSwitch: true,
      idle: `<p class="wx-idle"><span style="color:#d9a35a">Amber glyphs</span> are ${esc(people[k].name)}'s planets in ${esc(people[i].name)}'s houses. Tap ${esc(people[i].name)}'s planets to explore them.</p>` });
    host.querySelectorAll("[data-pair]").forEach(b => b.setAttribute("aria-pressed", b.dataset.pair === pairSel));
  }
  function draw(){
    drawPeople(); drawForm(); drawBuy();
    if (people.length < 2){ out.innerHTML = `<p class="cp-empty">Add someone to see how you meet: by ${g("sukuyo", "Sukuyō")}, by the contacts between your planets, and by where each of you lands in the other's houses. Add more people, up to nine in all, to see your unit.</p>`; return; }
    if (people.length === 2){ out.innerHTML = `<div class="cp-pair-host"></div>`; pairSel = "0-1"; showPair(out.querySelector(".cp-pair-host")); return; }
    out.innerHTML = unitView(people); showPair(out.querySelector(".cp-pair-host"));
  }
  host.addEventListener("click", e => {
    if (e.target.closest(".cp-addbtn")){ adding = true; draw(); return; }
    const rm = e.target.closest("[data-remove]"); if (rm){ people.splice(+rm.dataset.remove, 1); pairSel = "0-1"; draw(); return; }
    if (e.target.closest(".cp-tobuy")){ buyEl.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    const pr = e.target.closest("[data-pair]");
    if (pr){ pairSel = pr.dataset.pair; const h = out.querySelector(".cp-pair-host"); showPair(h); h.scrollIntoView({ behavior: "smooth", block: "start" }); }
  });
  draw();
}

window.WyrdCompare = { mount };
})();
