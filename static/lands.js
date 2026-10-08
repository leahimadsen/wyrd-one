'use strict';
/* A land built on the chart page (Compare lives in compare.js):
   WHAT'S COMING  a twelve-month calendar of the sky and the transits that touch this chart,
                  with the clock's turning points added from the period tree.
   Data only, like the rest of the free side. */
(() => {
const { signOf, houseOf, GLYPH } = Wyrd.helpers;
const { esc } = WyrdCommon;
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
    const b = e.target.closest("[data-f]"); if (b){ filter = b.dataset.f; paint(); if (Wyrd.pulse) Wyrd.pulse("calendar", filter); }
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

window.WyrdLands = { calendar };
})();
