'use strict';
/* Two lands built on the chart page:
   WHAT'S COMING  a twelve-month calendar of the sky and the transits that touch this chart,
                  with the clock's turning points added from the period tree.
   COMPARE        a second chart laid over this one: their planets in your houses and yours
                  in theirs, the aspects between the two, and the channels you complete together.
   Data only, like the rest of the free side. */
(() => {
const { signOf, houseOf, GLYPH } = Wyrd.helpers;
const { esc, placeSearch, cast } = WyrdCommon;
const g = (k, l) => Wyrd.gloss(k, l);
const jdDate = jd => new Date((jd - 2440587.5) * 864e5);
const fmtDay = jd => jdDate(jd).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
const fmtMonth = jd => jdDate(jd).toLocaleDateString(undefined, { month: "long", year: "numeric" });
const PT = { Ascendant: "↑ Ascendant", Midheaven: "MC Midheaven" };
const pt = n => PT[n] || `${GLYPH[n] || ""} ${n}`;

/* ---------- what's coming ---------- */
const KINDS = [
  ["all", "Everything"], ["you", "Touching my chart"], ["clock", "My clock"], ["ingress", "Sign changes"], ["station", "Retrogrades"],
];
function calendar(host, X){
  host.innerHTML = `${Wyrd.glossTerms(["transit", "aspect", "ingressT", "station", "antardasha", "sadesati"])}
    <div class="cal-filter" role="group" aria-label="Show">${KINDS.map(([k, l], i) => `<button type="button" data-f="${k}" aria-pressed="${i === 0}">${l}</button>`).join("")}</div>
    <div class="cal-body" aria-live="polite"><p class="cal-wait">Working out the next twelve months…</p></div>`;
  let events = [], filter = "all";
  const body = host.querySelector(".cal-body");

  function clockEvents(start, end){
    const T = X.C.dashaTree, out = [];
    for (const m of T.maha) if (m.from > start && m.from < end) out.push({ jd: m.from, kind: "clock", level: "era", lord: m.lord });
    for (const m of T.maha){
      if (m.to < start || m.from > end) continue;
      for (const a of subPeriods(m.lord, m.from, m.years)){
        if (a.from > start && a.from < end) out.push({ jd: a.from, kind: "clock", level: "chapter", lord: a.lord, within: m.lord });
        if (a.to < start || a.from > end) continue;
        for (const p of subPeriods(a.lord, a.from, a.years))
          if (p.from > start && p.from < end) out.push({ jd: p.from, kind: "clock", level: "passage", lord: p.lord, within: `${m.lord} / ${a.lord}` });
      }
    }
    return out;
  }
  function line(e){
    switch (e.kind){
      case "transit": return { cls: "you", txt: `${GLYPH[e.body]} ${e.body} ${e.aspect === "conjunction" ? "reaches" : `makes ${/^[aeiou]/.test(e.aspect) ? "an" : "a"} ${e.aspect} to`} your ${pt(e.to)}${e.retro ? " <small>(retrograde)</small>" : ""}` };
      case "sadesati": return { cls: "you", txt: `♄ Saturn enters ${e.sign}: your ${g("sadesati", "Sade Sati")} ${e.phase}` };
      case "ingress": return { cls: "ingress", txt: `${GLYPH[e.body]} ${e.body} enters ${e.sign}${e.retro && !["Rahu", "Ketu"].includes(e.body) ? " <small>(retrograde)</small>" : ""}` };
      case "station": return { cls: "station", txt: `${GLYPH[e.body]} ${e.body} stations ${e.turns} in ${e.sign}` };
      case "clock": return { cls: "clock", txt: `${GLYPH[e.lord]} Your ${e.level === "era" ? "era" : e.level} of ${e.lord} begins${e.within ? ` <small>within ${e.within}</small>` : ""}` };
    }
    return { cls: "", txt: "" };
  }
  function paint(){
    host.querySelectorAll("[data-f]").forEach(b => b.setAttribute("aria-pressed", b.dataset.f === filter));
    const shown = events.filter(e => filter === "all" || (filter === "you" ? e.kind === "transit" || e.kind === "sadesati" : e.kind === filter));
    if (!shown.length){ body.innerHTML = `<p class="cal-wait">Nothing of this kind in the next twelve months.</p>`; return; }
    let html = "", month = "";
    for (const e of shown){
      const m = fmtMonth(e.jd);
      if (m !== month){ if (month) html += "</ol>"; html += `<h3 class="cal-m">${m}</h3><ol class="cal-list">`; month = m; }
      const L = line(e);
      html += `<li class="cal-${L.cls}"><time>${fmtDay(e.jd)}</time><span>${L.txt}</span></li>`;
    }
    body.innerHTML = html + "</ol>" + (X.unknown ? `<p class="unknown-note">Without a birth time, transits to the rising sign and midheaven are left out, and the clock's dates may be out by months.</p>` : "");
  }
  host.addEventListener("click", e => {
    const b = e.target.closest("[data-f]"); if (b){ filter = b.dataset.f; paint(); }
    if (e.target.closest("[data-retry]")) load();
  });
  function load(){
    body.innerHTML = `<p class="cal-wait">Working out the next twelve months…</p>`;
    fetch("/api/calendar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(X.birth) })
      .then(r => r.json().catch(() => ({})).then(j => { if (!r.ok) throw new Error(j.error || "The calendar couldn't be worked out."); return j; }))
      .then(j => {
        const start = j.start, end = start + 365;
        events = j.events.concat(clockEvents(start, end)).sort((a, b) => a.jd - b.jd);
        paint();
      })
      .catch(x => { body.innerHTML = `<p class="err">${x instanceof TypeError ? "You're offline. The calendar needs a connection to work out the coming months." : esc(x.message)} <button type="button" class="link-btn" data-retry>Try again</button></p>`; });
  }
  load();
}

/* ---------- compare two charts ---------- */
function compare(host, X){
  host.innerHTML = `${Wyrd.glossTerms(["synastry", "house", "aspect", "channel"])}
    <form class="cmp-form cast" autocomplete="off" novalidate>
      <label class="f-name">Their name <span>optional</span><input name="name" maxlength="80"></label>
      <label>Date of birth <input name="date" type="date" required min="1850-01-01" max="2149-12-31"></label>
      <label>Time of birth <input name="time" type="time" required></label>
      <label class="f-unknown"><input type="checkbox" name="unknown"> Their birth time is unknown</label>
      <label class="f-place">Place of birth
        <input name="place" id="cmpPlace" placeholder="Start typing a town or city" required role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="cmpList">
        <ul id="cmpList" role="listbox" hidden></ul></label>
      <button type="submit" class="btn-cast">Compare</button>
      <p class="err" role="alert"></p>
    </form>
    <div class="cmp-out" aria-live="polite"></div>`;
  const f = host.querySelector("form"), err = f.querySelector(".err"), out = host.querySelector(".cmp-out");
  let place = null;
  placeSearch(f.querySelector("#cmpPlace"), f.querySelector("#cmpList"), p => { place = p; });
  f.unknown.addEventListener("change", () => { f.time.disabled = f.unknown.checked; if (f.unknown.checked) f.time.value = "12:00"; });
  f.addEventListener("submit", async e => {
    e.preventDefault(); err.textContent = "";
    if (!f.date.value || (!f.unknown.checked && !f.time.value)){ err.textContent = "Enter their date of birth, and time if known."; return; }
    if (!place){ err.textContent = "Choose their birthplace from the list as you type."; return; }
    const b2 = { name: f.name.value.trim(), date: f.date.value, time: f.unknown.checked ? "12:00" : f.time.value, unknown_time: f.unknown.checked || undefined,
                 place_id: place.id, lat: place.lat, lon: place.lon, tz: place.tz, place_label: place.label };
    const btn = f.querySelector("button[type=submit]"); btn.disabled = true; btn.textContent = "Casting…";
    try { const j = await cast(b2); show(j.chart, b2); }
    catch (x) { err.textContent = x instanceof TypeError ? "You're offline. Comparing needs a connection." : x.message; }
    finally { btn.disabled = false; btn.textContent = "Compare"; }
  });

  function show(O, b2){
    const A = X.C, me = X.birth.name || "You", them = b2.name || "Them";
    const B = WyrdWheel.WHEEL_BODIES;
    const houseRows = (P, Q) => B.map(b => `<tr><th>${GLYPH[b]} ${b}</th><td>${signOf(P.sid[b])}</td><td>${houseOf(P.sid[b], Q.ascS)}</td></tr>`).join("");
    const asp = [];
    for (const a of B) for (const b of B){
      const x = aspectBetween(A.sid[a], O.sid[b]);
      if (x && x.orb <= (x.n === 1 ? 6 : 5)) asp.push({ a, b, x });
    }
    asp.sort((p, q) => p.x.orb - q.x.orb);
    /* channels: complete only when the two charts are put together */
    const gates = C => new Set([C.natal.personality, C.natal.design].flatMap(c => Object.values(c).map(v => v.gate)));
    const gA = gates(A), gB = gates(O), both = new Set([...gA, ...gB]);
    const has = (s, [p, q]) => s.has(p) && s.has(q);
    const together = WyrdBody.channels.filter(ch => has(both, ch) && !has(gA, ch) && !has(gB, ch));
    const shared = [...gA].filter(x => gB.has(x)).sort((a, b) => a - b);
    out.innerHTML = `
      <h3 class="sec-h">${esc(me)} inside, ${esc(them)} outside</h3>
      <div class="cmp-wheel"></div>
      ${O.unknownTime ? `<p class="unknown-note">${esc(them)}'s birth time is unknown, so their houses are counted from their Sun.</p>` : ""}
      <div class="facts">
        <div class="fact"><h3>${esc(them)}'s planets in your houses</h3><table class="mini"><tr><th>Planet</th><th>Sign</th><th>Your house</th></tr>${houseRows(O, A)}</table></div>
        <div class="fact"><h3>Your planets in ${esc(them)}'s houses</h3><table class="mini"><tr><th>Planet</th><th>Sign</th><th>Their house</th></tr>${houseRows(A, O)}</table></div>
        <div class="fact"><h3>Aspects between you</h3><ul class="kar asp">${asp.slice(0, 24).map(({ a, b, x }) =>
          `<li><span>Your ${GLYPH[a]} ${a} · their ${GLYPH[b]} ${b}</span><span style="color:${x.col}">${x.name}</span><span>${x.orb.toFixed(1)}°</span></li>`).join("") || "<li>None within orb</li>"}</ul></div>
        <div class="fact"><h3>Channels you complete together</h3>
          <p>${together.length ? together.map(([p, q]) => `${p}–${q}`).join(", ") : "None: no channel needs one gate from each of you."}</p>
          <h3 class="fact-h2">Gates you share</h3><p>${shared.join(", ") || "None"}</p></div>
      </div>`;
    WyrdWheel.mount(out.querySelector(".cmp-wheel"), A, { level: "simple", other: O, unknownTime: X.unknown,
      idle: `<p class="wx-idle"><span style="color:#d9a35a">Amber glyphs</span> are ${esc(them)}'s planets, placed in your houses. Tap your own planets to explore them.</p>` });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

window.WyrdLands = { calendar, compare };
})();
