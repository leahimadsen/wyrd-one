'use strict';
/* The chart page. The landing page casts the chart and keeps it in this tab's
   sessionStorage (a shared link carries the birth details instead); this page
   draws the map, with the chart as its hub, and opens one land at a time.
   Lands are built the first time they are visited, so the page stays light. */
(async () => {
const $ = id => document.getElementById(id);
const { signOf, degIn, nakIndex, houseOf, norm, GLYPH, NAKSHATRA } = Wyrd.helpers;
const { esc, cast, keep, current, shareLink, fromLink, isSaved, toggleSaved, refreshSaved } = WyrdCommon;
const g = (k, l) => Wyrd.gloss(k, l);

/* ---------- which chart: a shared link, or the one cast in this tab ---------- */
let saved = current();
const linkParam = new URLSearchParams(location.search).get("b");
if (linkParam){
  const b = fromLink(linkParam);
  if (b){
    try { const j = await cast(b); keep(b, j); saved = { birth: b, result: j }; }
    catch (x) { document.body.innerHTML = `<p class="err" style="padding:40px">${esc(x.message)} <a href="/">Cast a chart</a></p>`; return; }
  }
  history.replaceState(null, "", "/chart" + location.hash);     // the details don't stay in the address bar
}
if (!saved || !saved.result || !saved.result.chart){ location.replace("/"); return; }
const { birth, result: J } = saved, C = J.chart, T = C.dashaTree, unknown = !!C.unknownTime;
const X = C.extras || {};
Wyrd.setChart(C);

/* ---------- small facts used across the page ---------- */
const BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
const EXALT = { Sun: 0, Moon: 1, Mars: 9, Mercury: 5, Jupiter: 3, Venus: 11, Saturn: 6 };
const OWN = { Sun: [4], Moon: [3], Mars: [0, 7], Mercury: [2, 5], Jupiter: [8, 11], Venus: [1, 6], Saturn: [9, 10] };
const MOOLA = { Sun: [4, 0, 20], Moon: [1, 3, 30], Mars: [0, 0, 12], Mercury: [5, 15, 20], Jupiter: [8, 0, 10], Venus: [6, 0, 15], Saturn: [10, 0, 20] };
function dignity(b){
  if (!(b in EXALT)) return null;
  const l = C.sid[b], s = Math.floor(norm(l) / 30), d = degIn(l), m = MOOLA[b];
  if (s === EXALT[b] && !(b === "Mercury" && d >= 15) && !(b === "Moon" && d >= 3)) return { k: "ex", label: "exalted", key: "exalted" };
  if (s === (EXALT[b] + 6) % 12) return { k: "deb", label: "debilitated", key: "debilitated" };
  if (s === m[0] && d >= m[1] && d < m[2]) return { k: "mt", label: "moolatrikona", key: "moolatrikona" };
  if (OWN[b].includes(s)) return { k: "own", label: "own sign", key: "ownsign" };
  return null;
}
const retro = b => !!(X.retro && X.retro[b]);
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };
const fmt = l => `${signOf(l)} ${dm(l)}`;
const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;

/* ---------- the lands ---------- */
const LANDS = [
  { id: "chart",     name: "Your chart",            mark: "☉", teaser: unknown ? `Sun in ${signOf(C.sid.Sun)} · Moon in ${signOf(C.sid.Moon)}` : `${signOf(C.ascS)} rising · Moon in ${NAKSHATRA[nakIndex(C.sid.Moon)][0]}`,
    terms: ["sidereal", "tropical", "house", "nakshatra", "pada", "rune", "gate", "design", "retro", "dignity", "navamsa"],
    prompt: "Your reading reads these placements together: the Seat you rise from, the engine of your Moon, your soul-planet and its cabinet." },
  { id: "body",      name: "The harmonic body",     mark: "✶", teaser: "Seven stations, each fed by one of your planets",
    terms: ["station7", "centre", "channel", "type"], prompt: "Your reading reads the gates of your work and what your defined centres carry." },
  { id: "dharma",    name: "The Dharma Weave",      mark: "⛤", teaser: C.dharma ? `Dharma profile ${C.dharma.profile} · the Pentagram Cross` : "What the chart ripens into",
    terms: [], prompt: "Your reading reads your dharma Suns and Earths from the register, and walks the Path of Dharma step by step, with when each step opens in your life." },
  { id: "clock",     name: "The Vimshottari clock", mark: "◷", teaser: `${T.cur.lord} era · ${T.curA.lord} chapter, running now`,
    terms: ["vimshottari", "mahadasha", "antardasha", "pratyantar", "moonmansion"], prompt: "Your reading reads the periods running now: what this era and this chapter ask of you." },
  { id: "calendar",  name: "What's coming",         mark: "☷", teaser: "The next twelve months, dated",
    terms: [], prompt: "Your reading reads the periods running now, and the questions your chart keeps asking whatever the sky does." },
  { id: "armillary", name: "The armillary",         mark: "◎", teaser: "Your sky as a sphere you can open",
    terms: ["armillary", "ayanamsa", "gate", "rune"], prompt: "Your reading draws every frame of the sphere into one account of you." },
  { id: "reading",   name: "Your full reading",     mark: "✦", teaser: "Eight movements, written for you · $44", gold: true, terms: [] },
  { id: "compare",   name: "Compare",               mark: "⚭", teaser: "You and another, or a unit of three or four",
    terms: [], prompt: "Your reading is about your chart alone, read in full: the ground every bond stands on." },
  { id: "sky",       name: "The sky now",           mark: "☾", teaser: "Today's planets crossing yours",
    terms: ["transit", "sadesati", "retro", "orb"], prompt: "Your reading names what your chart asks of you, whatever today's sky is doing." },
  { id: "colour",    name: "The colour room",       mark: "◐", teaser: "Your twelve houses as a colour wheel",
    terms: ["house", "sign"], prompt: "Your reading reads the houses your planets light, one by one." },
  { id: "bench",     name: "The bench",             mark: "♪", teaser: "Hear two of your planets together",
    terms: ["graha", "aspect"], prompt: "Your reading reads how your planets work together, as a cabinet around your soul-planet." },
];
const LEARN = { id: "learn", name: "Learn your chart", mark: "✧" };
const ORDER = [LEARN, ...LANDS];

/* ---------- the header: who, the tools, the path ---------- */
$("who").textContent = birth.name ? `${birth.name}'s chart` : "Your chart";
$("chartMeta").textContent = `${birth.date}${unknown ? " · time unknown" : ` at ${birth.time} (${J.utc})`} · ${J.place.label}`;
if (J.offlineSince){
  const when = typeof J.offlineSince === "number" ? ` on ${new Date(J.offlineSince).toLocaleDateString()}` : "";
  $("unknownNote").hidden = false;
  $("unknownNote").textContent = `You're offline, so this is the chart as it was saved${when}. Your placements don't change, but "The sky now" and "What's coming" need a connection.`;
}
if (unknown){
  const span = C.moonSpan && C.moonSpan.length > 1 ? ` Your Moon may have been in ${C.moonSpan.join(" or ")}.` : "";
  $("unknownNote").hidden = false;
  $("unknownNote").textContent = ($("unknownNote").textContent ? $("unknownNote").textContent + " " : "") + `Birth time unknown: the chart is cast for noon, houses are counted from your Sun's sign, and the rising sign and angles are left out.${span}`;
  $("readingUnknown").hidden = false;
}
function drawTools(){
  const sv = isSaved(birth);
  const html = short => `<a class="ctool" href="/?edit=1" data-pulse="act:edit" ${short ? `aria-label="Edit birth details" title="Edit birth details"` : ""}>✎${short ? "" : " Edit details"}</a>
    <button type="button" class="ctool" data-tool="save" aria-pressed="${sv}" ${short ? `aria-label="${sv ? "Saved" : "Save chart"}" title="${sv ? "Saved" : "Save chart"}"` : ""}>${sv ? "★" : "☆"}${short ? "" : sv ? " Saved" : " Save chart"}</button>
    <button type="button" class="ctool" data-tool="share" ${short ? `aria-label="Copy link" title="Copy link"` : ""}>⤴${short ? "" : " Copy link"}</button>
    ${short ? "" : `<button type="button" class="ctool" data-install hidden>⬇ Install the app</button>`}`;
  $("tools").innerHTML = html(false);
  $("tabTools").innerHTML = html(true);
  WyrdCommon.syncInstall();
}
drawTools();
function toast(msg){ const t = $("toast"); t.textContent = msg; t.classList.add("on"); clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove("on"), 2600); }
document.addEventListener("click", async e => {
  const t = e.target.closest("[data-tool]"); if (!t) return;
  if (Wyrd.pulse) Wyrd.pulse("act", t.dataset.tool);
  if (t.dataset.tool === "save"){ const { offlineSince, ...fresh } = J; const on = toggleSaved(birth, fresh); drawTools(); toast(on ? "Saved in this browser. It's listed on the first page." : "Removed from this browser."); }
  if (t.dataset.tool === "share"){
    const url = shareLink(birth);
    try { await navigator.clipboard.writeText(url); toast("Link copied. Anyone with it can open this chart."); }
    catch (_) { prompt("Copy this link. Anyone with it can open this chart:", url); }
  }
});
function drawStart(){
  const p = WyrdLearn.progress();
  $("startHere").innerHTML = p && p.max > 0
    ? `<b>Continue learning your chart</b><span>Step ${p.step + 1} of ${p.total} · ${Math.round((p.max + 1) / p.total * 100)}% walked</span>`
    : `<b>New to charts? Start here</b><span>Walk through your own chart in ${WyrdLearn.count} short steps, one ring at a time</span>`;
  $("startHere").href = p ? `#learn/${p.step + 1}` : "#learn/1";
}
drawStart();

/* ---------- the map ---------- */
function drawMap(){
  const n = LANDS.length;
  const pos = LANDS.map((l, i) => { const a = i * 2 * Math.PI / n; return { ...l, x: 50 + 40 * Math.sin(a), y: 50 - 40 * Math.cos(a) }; });
  const paths = pos.map(p => `<line x1="50" y1="50" x2="${p.x.toFixed(2)}" y2="${p.y.toFixed(2)}"${p.gold ? ` class="gold"` : ""}/>`).join("");
  $("map").innerHTML = `
    <svg class="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <circle cx="50" cy="50" r="40" class="rail"/>${paths}</svg>
    <div class="map-core tz-core"></div>
    ${pos.map(p => `<a class="land${p.gold ? " gold" : ""}" href="#${p.id}" style="--x:${p.x.toFixed(2)}%;--y:${p.y.toFixed(2)}%">
      <span class="land-mark" aria-hidden="true">${p.mark}</span><b>${p.name}</b><small>${p.teaser}</small></a>`).join("")}`;
  $("tabsIn").innerHTML = `<a href="#map" class="tab tab-map">◎ Map</a><a href="#learn" class="tab tab-learn" data-tab="learn">✧ Learn</a>` +
    LANDS.map(l => `<a href="#${l.id}" class="tab${l.gold ? " gold" : ""}" data-tab="${l.id}">${l.name.replace(/^The |^Your /, "")}</a>`).join("");
}

/* the torus at the map's centre, and its layer switches */
let TZ = null;
function mountTorus(){
  const core = document.querySelector(".tz-core");
  try { TZ = WyrdTorus.mount(core, C, { caption: $("tzCap") }); }
  catch (_) { core.outerHTML = `<a class="map-core" href="#chart" aria-label="Open your chart">${WyrdWheel.svg(C, { compact: true, unknownTime: unknown })}</a>`; return; }
  $("tzLayers").innerHTML = TZ.layers.map(l => `<button type="button" class="tz-chip" data-layer="${l.id}" aria-pressed="true">${l.name}</button>`).join("")
    + `<a class="tz-chip open" href="#chart">Open your chart →</a>`;
  $("tzLayers").addEventListener("click", e => {
    const b = e.target.closest("[data-layer]"); if (!b) return;
    const v = b.getAttribute("aria-pressed") !== "true"; b.setAttribute("aria-pressed", v); TZ.toggle(b.dataset.layer, v);
  });
}

/* ---------- Your chart ---------- */
function chartLand(){
  const wx = $("chartWheel");
  const W = WyrdWheel.mount(wx, C, { level: "full", name: birth.name || "Your chart", place: J.place.label.split(",")[0],
    when: unknown ? `${birth.date} · time unknown` : `${birth.date} ${birth.time}`, unknownTime: unknown });
  wx.querySelector(".wx-bar").insertAdjacentHTML("beforeend",
    `<span class="wx-dl"><button type="button" class="wx-lv" data-dl="png">Download image</button><button type="button" class="wx-lv" data-dl="svg">SVG</button></span>`);
  wx.addEventListener("click", e => { const d = e.target.closest("[data-dl]"); if (d && Wyrd.pulse) Wyrd.pulse("act", "download"); if (d) downloadWheel(wx.querySelector(".wx-stage svg"), d.dataset.dl); });

  const NP = C.natal.personality, ND = C.natal.design, PL = X.placidus;
  const gl = v => v ? `${v.gate}.${v.line}` : "—";
  const head = [["Body"], [g("sidereal", "Sidereal")], [g("tropical", "Tropical")], [g("nakshatra", "Mansion") + " · " + g("pada", "pada")],
    [g("house", unknown ? "House (solar)" : "House")], ...(PL ? [[g("placidus", "Placidus")]] : []), [g("rune", "Rune")], [g("navamsa", "Navamsa")],
    [g("dignity", "Dignity")], [g("gate", "Gate")], [g("design", "Design gate")]];
  const rows = BODIES.map(b => {
    const l = C.sid[b], ru = WyrdWheel.runeAt(C, l), d = dignity(b);
    return `<tr><th scope="row">${GLYPH[b]} ${b}${retro(b) ? ` <span class="rx" title="retrograde">℞</span>` : ""}</th><td>${fmt(l)}</td><td>${fmt(C.trop[b])}</td>
      <td>${NAKSHATRA[nakIndex(l)][0]} ${pada(l)}</td><td>${houseOf(l, C.ascS)}</td>${PL ? `<td>${PL.houses[b]}</td>` : ""}<td>${ru.glyph} ${ru.name}</td>
      <td>${C.nav && C.nav[b] != null ? signOf(C.nav[b]) : "—"}</td><td>${d ? `<span class="dg ${d.k}">${d.label}</span>` : ""}</td><td>${gl(NP[b])}</td><td class="des">${gl(ND[b])}</td></tr>`;
  }).join("");
  const dash = n => `<td>—</td>`.repeat(n);
  const angRow = (n, l, lt, mansion) => { const ru = WyrdWheel.runeAt(C, l);
    return `<tr class="ang"><th scope="row">${g(n === "Ascendant" ? "asc" : "mc", n)}</th><td>${fmt(l)}</td><td>${fmt(lt)}</td><td>${mansion}</td>
      <td>${houseOf(l, C.ascS)}</td>${PL ? `<td>${n === "Ascendant" ? 1 : 10}</td>` : ""}<td>${ru.glyph} ${ru.name}</td><td>${n === "Ascendant" && C.navAsc != null ? signOf(C.navAsc) : "—"}</td>${dash(3)}</tr>`; };
  $("posTable").innerHTML = `<caption>Sidereal is Lahiri; the gates run on the tropical wheel. ℞ marks a planet that was retrograde.</caption>
    <tr>${head.map(h => `<th scope="col">${h[0]}</th>`).join("")}</tr>
    ${rows}
    <tr><th scope="row">⊕ Earth</th>${dash(PL ? 8 : 7)}<td>${gl(NP.Earth)}</td><td class="des">${gl(ND.Earth)}</td></tr>
    ${unknown ? "" : angRow("Ascendant", C.ascS, C.ascT, `${NAKSHATRA[nakIndex(C.ascS)][0]} ${pada(C.ascS)}`) + angRow("Midheaven", C.mcS, C.mcT, NAKSHATRA[nakIndex(C.mcS)][0])}`;

  const rv = WyrdWheel.rave(C), P = X.panchanga;
  const kar = Object.entries(C.karaka).map(([k, b]) => `<li><span>${k === "Atmakaraka" ? g("atmakaraka", "Atma") : k.replace("karaka", "")}</span>${GLYPH[b]} ${b}</li>`).join("");
  const asp = [];
  for (let i = 0; i < BODIES.length; i++) for (let k = i + 1; k < BODIES.length; k++){
    const [a, b] = [BODIES[i], BODIES[k]]; if (a === "Rahu" && b === "Ketu") continue;
    const x = aspectBetween(C.sid[a], C.sid[b]);
    if (x) asp.push(`<li><span>${GLYPH[a]} ${a} · ${GLYPH[b]} ${b}</span><span style="color:${x.col}">${x.name}</span><span>${x.orb.toFixed(1)}°</span></li>`);
  }
  $("facts").innerHTML = `
    <div class="fact"><h3>The rave</h3>
      <dl><dt>${g("type")}</dt><dd>${rv.type}</dd><dt>${g("strategy")}</dt><dd>${rv.strategy}</dd><dt>${g("authority")}</dt><dd>${rv.authority}</dd>
      <dt>${g("definition")}</dt><dd>${rv.definition}</dd><dt>${g("profile")}</dt><dd>${rv.profile}</dd><dt>${g("cross", "Cross gates")}</dt><dd>${rv.cross}</dd>
      <dt>${g("centre", "Defined")}</dt><dd>${rv.centres.join(", ") || "—"}</dd><dt>Open</dt><dd>${rv.open.join(", ") || "—"}</dd>
      <dt>${g("channel", "Channels")}</dt><dd>${rv.channels.join(", ") || "—"}</dd></dl></div>
    ${P ? `<div class="fact"><h3>${g("panchanga", "Your birth day")}</h3>
      <dl><dt>${g("vara")}</dt><dd>${P.vara} <small>(${P.varaLord})</small></dd><dt>${g("tithi")}</dt><dd>${P.paksha} ${P.tithiName} <small>(${P.tithi} of 30)</small></dd>
      <dt>Mansion</dt><dd>${unknown && C.moonSpan && C.moonSpan.length > 1 ? C.moonSpan.join(" or ") : P.nakshatra}</dd><dt>${g("yoga")}</dt><dd>${P.yoga}</dd><dt>${g("karana")}</dt><dd>${P.karana}</dd>
      ${P.sunrise && !unknown ? `<dt>Sunrise</dt><dd>${P.sunrise}${P.beforeSunrise ? " <small>(born before it: still the previous Vedic day)</small>" : ""}</dd>` : ""}</dl></div>` : ""}
    <div class="fact"><h3>${g("karaka", "The seven karakas")}</h3><ul class="kar">${kar}</ul>
      <h3 class="fact-h2">${g("aspect", "Aspects")}</h3><ul class="kar asp">${asp.join("") || "<li>None within orb</li>"}</ul></div>
    ${PL ? `<div class="fact"><h3>${g("placidus", "Placidus cusps")}</h3><p class="fine">Tropical. For comparison with the whole-sign houses this console reads.</p>
      <ol class="cusps">${PL.cusps.map((c, i) => `<li><span>${i + 1}</span>${SIGNS[Math.floor(norm(c) / 30)]} ${dm(c)}</li>`).join("")}</ol></div>` : ""}`;
}

/* the wheel as a file: copy the computed look onto each element so it stands alone */
function downloadWheel(svgEl, kind){
  if (!svgEl) return;
  const clone = svgEl.cloneNode(true), src = svgEl.querySelectorAll("*"), dst = clone.querySelectorAll("*");
  const PROPS = ["fill", "stroke", "stroke-width", "stroke-dasharray", "opacity", "font-size", "font-family", "font-weight", "text-anchor", "dominant-baseline", "letter-spacing"];
  src.forEach((el, i) => { const cs = getComputedStyle(el); dst[i].setAttribute("style", PROPS.map(p => `${p}:${cs.getPropertyValue(p)}`).join(";")); });
  clone.classList.remove("selecting", "focusing");
  const vb = clone.getAttribute("viewBox").split(" ").map(Number);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg"); clone.setAttribute("width", vb[2]); clone.setAttribute("height", vb[3]);
  clone.insertAdjacentHTML("afterbegin", `<rect x="${vb[0]}" y="${vb[1]}" width="${vb[2]}" height="${vb[3]}" fill="#05080a"/>`);
  const text = new XMLSerializer().serializeToString(clone), name = `${(birth.name || "chart").replace(/[^\w-]+/g, "-")}-wheel`;
  const save = (blob, ext) => { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `${name}.${ext}`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); };
  const blob = new Blob([text], { type: "image/svg+xml" });
  if (kind === "svg"){ save(blob, "svg"); return; }
  const img = new Image(), url = URL.createObjectURL(blob);
  img.onload = () => {
    const k = 2, cv = document.createElement("canvas"); cv.width = vb[2] * k; cv.height = vb[3] * k;
    cv.getContext("2d").drawImage(img, 0, 0, cv.width, cv.height); URL.revokeObjectURL(url);
    cv.toBlob(b => save(b, "png"), "image/png");
  };
  img.src = url;
}

/* ---------- each land, built on first visit ---------- */
let learn = null;
const BUILD = {
  learn: () => { learn = WyrdLearn.mount($("learnHost"), { C, birth, unknown, name: birth.name, dignity, retro, onStep: drawStart }); },
  chart: chartLand,
  body: () => window.WyrdBody && WyrdBody.mount($("bodyHost"), C),
  clock: () => { window.WyrdDasha && WyrdDasha.mount($("dashaHost"));
    if (unknown) $("dashaHost").insertAdjacentHTML("afterbegin", `<p class="unknown-note">The clock is set by the Moon. Without a birth time your Moon could be anywhere in a day's travel, so these dates may be out by months.</p>`); },
  calendar: () => WyrdLands.calendar($("calHost"), { C, birth, unknown }),
  dharma: () => WyrdDharma.mount($("dharmaHost"), { C, unknown }),
  armillary: () => { $("armHostWrap").innerHTML = Wyrd.armillary(); watchArmillary($("p-armillary")); },
  sky: () => renderTransits(C),
  colour: () => { $("colourHost").innerHTML = Wyrd.colour(); setTimeout(() => Wyrd.afterColour(), 0); },
  bench: () => { $("benchHost").innerHTML = Wyrd.bench(); },
  compare: () => WyrdCompare.mount($("cmpHost"), { C, birth, unknown }),
  reading: () => {},
};
const built = new Set();
function decorate(L){
  const panel = $("p-" + L.id), lede = panel.querySelector(".lede");
  if (L.terms && L.terms.length && lede) lede.insertAdjacentHTML("afterend", Wyrd.glossTerms(L.terms));
  if (L.prompt) panel.insertAdjacentHTML("beforeend", `<p class="rd-prompt">✦ ${L.prompt} <a href="#reading">About the reading →</a></p>`);
}

/* ---------- moving between the map and the lands ---------- */
/* where other visitors usually go next, learned from the anonymous counts */
let NEXT = {}, prevLand = null;
fetch("/api/pulse/next").then(r => r.ok ? r.json() : {}).then(j => { NEXT = j || {}; }).catch(() => {});
function go(){
  const [id, arg] = location.hash.slice(1).split("/");
  const here = ORDER.some(l => l.id === id) ? id : "map";
  if (Wyrd.pulse && here !== prevLand){ Wyrd.pulse("land", here); if (prevLand) Wyrd.pulse("move", `${prevLand}-${here}`); }
  prevLand = here;
  const land = ORDER.find(l => l.id === id);
  $("skyHost").hidden = !!land; $("tabs").hidden = !land; $("landNav").hidden = !land;
  ORDER.forEach(l => { $("p-" + l.id).hidden = l !== land; });
  document.querySelectorAll("[data-tab]").forEach(t =>
    t.dataset.tab === id ? t.setAttribute("aria-current", "page") : t.removeAttribute("aria-current"));
  if (!land){ drawStart(); Wyrd.sky.start(); if (TZ) TZ.start(); document.title = `${birth.name ? birth.name + "'s chart" : "Your chart"} · The Wyrd Console`; return; }
  Wyrd.sky.stop(); if (TZ) TZ.stop();
  if (!built.has(id)){ built.add(id); if (land !== LEARN) decorate(land); BUILD[id](); }
  if (id === "learn" && arg && learn) learn.show(+arg - 1);
  const i = ORDER.indexOf(land), prev = ORDER[(i + ORDER.length - 1) % ORDER.length], next = ORDER[(i + 1) % ORDER.length];
  const often = (NEXT[id] || []).map(n => ORDER.find(l => l.id === n)).filter(l => l && l.id !== id);
  $("landNav").innerHTML = (often.length ? `<p class="often">People here often go on to ${often.map(l => `<a href="#${l.id}">${l.name}</a>`).join(" or ")}.</p>` : "")
    + `<a href="#${prev.id}">← ${prev.name}</a><a href="#map" class="to-map">◎ Back to the map</a><a href="#${next.id}">${next.name} →</a>`;
  document.title = `${land.name} · The Wyrd Console`;
  const tab = document.querySelector(`[data-tab="${id}"]`); if (tab) tab.scrollIntoView({ block: "nearest", inline: "center" });
  scrollTo(0, 0);
  $("lands").focus({ preventScroll: true });
}

drawMap();
mountTorus();
addEventListener("hashchange", go);
go();

/* ---------- the reading ---------- */
$("buyBtn").addEventListener("click", async () => {
  if (Wyrd.pulseNow) Wyrd.pulseNow("act", "buy");
  const err = $("buyErr"), btn = $("buyBtn"); err.textContent = "";
  btn.disabled = true; btn.textContent = "Opening checkout…";
  try {
    const r = await fetch("/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(birth) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "Checkout couldn't open.");
    location.href = j.url;
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = "Get my reading — $44"; }
});
if (new URLSearchParams(location.search).get("cancelled")) $("buyErr").textContent = "Checkout was cancelled — your chart is still here whenever you're ready.";
})();
