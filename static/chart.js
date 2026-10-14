'use strict';
/* The chart page. The landing page casts the chart and keeps it in this tab's
   sessionStorage (a shared link carries the birth details instead); this page
   draws the map, with the chart as its hub, and opens one land at a time.
   Lands are built the first time they are visited, so the page stays light. */
(async () => {
const $ = id => document.getElementById(id);
const { signOf, degIn, nakIndex, houseOf, norm, GLYPH, NAKSHATRA } = Wyrd.helpers;
const { esc, cast, keep, current, fresh, shareLink, fromLink, isSaved, toggleSaved, refreshSaved } = WyrdCommon;
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
if (!fresh(saved.result) && navigator.onLine !== false){       // cast by an older engine: bring it up to date
  try { const j = await cast(saved.birth); keep(saved.birth, j); saved = { birth: saved.birth, result: j }; } catch (_) {}
}
const { birth, result: J } = saved, C = J.chart, T = C.dashaTree, unknown = !!C.unknownTime;
let MEMBER = false;                    /* set from /api/me: members see every rune in full and the planets on the body map */
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
  if (s === m[0] && d >= m[1] && d < m[2]) return { k: "mt", label: "root sign", key: "moolatrikona" };
  if (OWN[b].includes(s)) return { k: "own", label: "own sign", key: "ownsign" };
  return null;
}
const retro = b => !!(X.retro && X.retro[b]);
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };
const fmt = l => `${signOf(l)} ${dm(l)}`;
const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;

/* ---------- the lands ----------
   One path, in order, each step building on the last: learn the parts, see the whole chart,
   its timing, today and the year ahead, the runes it lights, the body it moves through, and
   how it meets other people. The reading comes after the path; three rooms to explore sit beside it. */
const designType = (() => { try { return WyrdDesign.analyse(C.natal).type; } catch (_) { return ""; } })();
const LEARN = { id: "learn", name: "Learn your chart", short: "Learn", mark: "✧", path: true,
  teaser: "The parts of a chart, taught on yours, in short steps", why: "Start here if charts are new to you." };
const LANDS = [
  { id: "chart",     name: "Your chart",             short: "Chart", mark: "☉", path: true,
    teaser: unknown ? `Sun in ${signOf(C.sid.Sun)} · Moon in ${signOf(C.sid.Moon)}` : `${signOf(C.ascS)} rising · Moon in ${NAKSHATRA[nakIndex(C.sid.Moon)][0]}`,
    why: "Where everything was when you were born, in both zodiacs, and every divisional chart from D1 to D60.",
    terms: ["sidereal", "tropical", "house", "nakshatra", "pada", "rune", "gate", "design", "retro", "dignity", "navamsa"],
    prompt: "Your reading reads these placements together: the Seat you rise from, the engine of your Moon, your Soul-Planet and its cabinet." },
  { id: "clock",     name: "The Vimshottari Clock",  short: "Clock", mark: "◷", path: true,
    teaser: `${T.cur.lord} era · ${T.curA.lord} chapter, running now`, why: "Your Moon sets a clock of planetary eras. Which one you're in now.",
    terms: ["vimshottari", "mahadasha", "antardasha", "pratyantar", "moonmansion"], prompt: "Your reading reads every era of your life, and what this era and this chapter ask of you." },
  { id: "sky",       name: "Now and next",           short: "Now & next", mark: "☾", path: true,
    teaser: "Today's sky on your chart, and the next twelve months", why: "The planets moving now, crossing the chart you were born with.",
    terms: ["transit", "orb", "retro", "station", "ingressT", "sadesati", "antardasha", "tithi"], prompt: "Your reading names what your chart asks of you, whatever today's sky is doing." },
  { id: "runes",     name: "Your activated runes",   short: "Runes", mark: "ᛉ", path: true,
    teaser: "The runes your planets light, read through their mansions", why: "Your houses carry the 24 runes; your planets wake some of them.",
    terms: ["rune", "nakshatra"], prompt: "Your reading ranks your runes and names the years each one wakes." },
  { id: "design",    name: "Your design",            short: "Design", mark: "⬡", path: true,
    teaser: `${designType ? designType + " · " : ""}your Birth and Dharma Designs`, why: "How energy moves through your body, and how your Rashi ripens into your Dharma.",
    terms: ["centre", "channel", "type", "authority", "station7", "dharma", "svadharma", "dharmaweave"], prompt: "Your reading reads the gates of your work and your body's channels through both designs, and walks the Path of Dharma step by step." },
  { id: "compare",   name: "Compare",                short: "Compare", mark: "⚭", path: true,
    teaser: "You and up to eight others", why: "How your chart meets someone else's.",
    terms: [], prompt: "The reading together writes your bond out in full: your story at one table, the old match, and the next thirty years." },
  { id: "reading",   name: "The Wyrd Reading",           short: "Reading", mark: "✦", gold: true,
    teaser: "Your story, then fifteen sections that decode it, written for you", terms: [] },
  { id: "mandala",   name: "The Wyrd Mandala",       short: "Mandala", mark: "✺", explore: true, teaser: "The 108 stations, a card for each, your planets among them",
    terms: ["nakshatra", "pada", "navamsa"] },
  { id: "armillary", name: "The armillary",          short: "Armillary", mark: "◎", explore: true, teaser: "Your sky as a sphere you can open",
    terms: ["armillary", "ayanamsa", "gate", "rune"], prompt: "Your reading draws every frame of the sphere into one account of you." },
  { id: "colour",    name: "The colour room",        short: "Colour", mark: "◐", explore: true, teaser: "Your planets in colour, and a lesson in the wheel",
    terms: ["house", "sign", "aspect", "graha"], prompt: "Your reading reads the houses your planets light, one by one." },
  { id: "bench",     name: "The bench",              short: "Bench", mark: "♪", explore: true, teaser: "Your life's eras as music, and why each chapter sounds as it does",
    terms: ["graha", "mahadasha", "antardasha"], prompt: "Your reading reads how your planets work together, as a cabinet around your Soul-Planet." },
];
const ORDER = [LEARN, ...LANDS];
const PATH = ORDER.filter(l => l.path);
/* old addresses still land in the right place */
const ALIAS = { body: "design/harmonic", dharma: "design/weave", calendar: "sky/coming", map: "" };

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

/* ---------- the map: the path, the reading, the rooms beside it ---------- */
function drawMap(){
  const step = (l, i) => `<a class="path-step" href="#${l.id}"><span class="path-n">${i + 1}</span>
    <span class="land-mark" aria-hidden="true">${l.mark}</span><b>${l.name}</b><small>${l.teaser}</small><em>${l.why}</em></a>`;
  const R = LANDS.find(l => l.gold), ex = LANDS.filter(l => l.explore);
  $("map").innerHTML = `
    <h2 class="path-h">Your chart, step by step</h2>
    <ol class="path-list">${PATH.map((l, i) => `<li>${step(l, i)}</li>`).join("")}</ol>
    <a class="path-reading" href="#reading"><span class="land-mark" aria-hidden="true">${R.mark}</span><b>${R.name}</b><small>${R.teaser}</small></a>
    <h2 class="path-h">Rooms to explore</h2>
    <div class="path-explore">${ex.map(l => `<a class="land" href="#${l.id}"><span class="land-mark" aria-hidden="true">${l.mark}</span><b>${l.name}</b><small>${l.teaser}</small></a>`).join("")}</div>`;
  $("tabsIn").innerHTML = `<a href="#" class="tab tab-map">◎ Map</a>` +
    ORDER.map(l => `<a href="#${l.id}" class="tab${l.gold ? " gold" : ""}${l.explore ? " ex" : ""}" data-tab="${l.id}">${l.path ? PATH.indexOf(l) + 1 + " · " : ""}${l.short}</a>`).join("");
}

/* the hub's window: the torus first, with its own switches; Odin's Eye beside it, built the first
   time it is opened. In the eye, tapping the shell comes back to the torus. */
let TZ = null, EYE = null, hubView = "shell";
function mountHub(){
  $("hubView").addEventListener("click", e => { const b = e.target.closest("[data-hub-view]"); if (b && b.dataset.hubView !== hubView) setHubView(b.dataset.hubView, true); });
  if (!window.WyrdEye) $("hubView").hidden = true;
  setHubView("shell");
}
function setHubView(v, asked){
  const eye = v === "eye", core = document.querySelector(".hub-torus .map-core");
  hubView = v;
  $("eyeHost").hidden = !eye; if (core) core.hidden = eye;
  for (const id of ["eyeCtl", "eyeCap"]) $(id).hidden = !eye;
  for (const id of ["tzZodiac", "tzLayers", "tzCap"]) $(id).hidden = eye;
  document.querySelector(".hub-torus").classList.toggle("eye-win", eye);
  $("hubTitle").textContent = eye ? "✦ odins_eye.wyrd" : "✦ your_chart.wyrd";
  $("hubView").querySelectorAll("[data-hub-view]").forEach(b => b.setAttribute("aria-pressed", b.dataset.hubView === v));
  if (eye && !EYE){
    try { EYE = WyrdEye.mount($("eyeHost"), C, { controls: $("eyeCtl"), caption: $("eyeCap"), onShell: () => { setHubView("shell", true); $("hubView").scrollIntoView({ block: "nearest" }); } }); }
    catch (x) { console.error(x); $("hubView").hidden = true; setHubView("shell"); return; }
  }
  if (!eye && !TZ) mountTorus();
  startHub();
  if (asked && Wyrd.pulse) Wyrd.pulse("act", "hub-" + v);
}
function startHub(){
  if (hubView === "shell"){ if (EYE) EYE.stop(); if (TZ) TZ.start(); }
  else { if (TZ) TZ.stop(); if (EYE) EYE.start(); }
}
function stopHub(){ if (EYE) EYE.stop(); if (TZ) TZ.stop(); }
function mountTorus(){
  const core = document.querySelector(".tz-core");
  try { TZ = WyrdTorus.mount(core, C, { caption: $("tzCap") }); }
  catch (_) { core.outerHTML = `<a class="map-core" href="#chart" aria-label="Open your chart">${WyrdWheel.svg(C, { compact: true, unknownTime: unknown })}</a>`; return; }
  /* read the torus in either zodiac: sidereal (Jyotish) or tropical */
  const zod = $("tzZodiac");
  zod.innerHTML = ["sidereal", "tropical"].map(z => `<button type="button" class="tz-chip tz-z" data-zodiac="${z}" aria-pressed="${z === TZ.zodiac}">${z === "sidereal" ? "Sidereal" : "Tropical"}</button>`).join("");
  zod.addEventListener("click", e => {
    const b = e.target.closest("[data-zodiac]"); if (!b || TZ.zodiac === b.dataset.zodiac) return;
    TZ.setZodiac(b.dataset.zodiac);
    zod.querySelectorAll("[data-zodiac]").forEach(x => x.setAttribute("aria-pressed", x === b));
    $("tzLayers").querySelectorAll("[data-layer]").forEach(x => { const l = TZ.layers.find(l => l.id === x.dataset.layer); if (l) x.textContent = l.name; });
    if (window.Wyrd && Wyrd.pulse) Wyrd.pulse("act", "zodiac-" + b.dataset.zodiac);
  });
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
  /* the mansion and pada, linked to its station in the Wyrd Mandala */
  const station = l => { const k = Math.floor(norm(l) / (10 / 3)) % 108 + 1;
    return `<a class="to-st" href="#mandala/s${String(k).padStart(3, "0")}" title="Open station ${k} in the Wyrd Mandala">${NAKSHATRA[nakIndex(l)][0]} ${pada(l)}</a>`; };
  const gl = v => v ? `${v.gate}.${v.line}` : "—";
  const head = [["Body"], [g("sidereal", "Sidereal")], [g("tropical", "Tropical")], [g("nakshatra", "Mansion") + " · " + g("pada", "pada")],
    [g("house", unknown ? "House (solar)" : "House")], ...(PL ? [[g("placidus", "Placidus")]] : []), [g("rune", "Rune")], [g("navamsa", "Navamsa")],
    [g("dignity", "Dignity")], [g("gate", "Gate")], [g("design", "Design gate")], [g("tarot", "Cards")]];
  const rows = BODIES.map(b => {
    const l = C.sid[b], ru = WyrdWheel.runeAt(C, l), d = dignity(b);
    return `<tr><th scope="row">${GLYPH[b]} ${b}${retro(b) ? ` <span class="rx" title="retrograde">℞</span>` : ""}</th><td>${fmt(l)}</td><td>${fmt(C.trop[b])}</td>
      <td>${station(l)}</td><td>${houseOf(l, C.ascS)}</td>${PL ? `<td>${PL.houses[b]}</td>` : ""}<td>${ru.glyph} ${ru.name}</td>
      <td>${C.nav && C.nav[b] != null ? signOf(C.nav[b]) : "—"}</td><td>${d ? `<span class="dg ${d.k}">${d.label}</span>` : ""}</td><td>${gl(NP[b])}</td><td class="des">${gl(ND[b])}</td><td data-card="${l}" data-trop="${C.trop[b]}">…</td></tr>`;
  }).join("");
  const dash = n => `<td>—</td>`.repeat(n);
  const angRow = (n, l, lt, mansion) => { const ru = WyrdWheel.runeAt(C, l);
    return `<tr class="ang"><th scope="row">${g(n === "Ascendant" ? "asc" : "mc", n)}</th><td>${fmt(l)}</td><td>${fmt(lt)}</td><td>${mansion}</td>
      <td>${houseOf(l, C.ascS)}</td>${PL ? `<td>${n === "Ascendant" ? 1 : 10}</td>` : ""}<td>${ru.glyph} ${ru.name}</td><td>${n === "Ascendant" && C.navAsc != null ? signOf(C.navAsc) : "—"}</td>${dash(3)}<td data-card="${l}" data-trop="${lt}">…</td></tr>`; };
  $("posTable").innerHTML = `<caption>Sidereal is Lahiri; the gates run on the tropical wheel. Cards: the Buddhist deck at the sidereal place, then the Nordic deck at the tropical place. ℞ marks a planet that was retrograde.</caption>
    <tr>${head.map(h => `<th scope="col">${h[0]}</th>`).join("")}</tr>
    ${rows}
    <tr><th scope="row">⊕ Earth</th>${dash(PL ? 8 : 7)}<td>${gl(NP.Earth)}</td><td class="des">${gl(ND.Earth)}</td><td>—</td></tr>
    ${unknown ? "" : angRow("Ascendant", C.ascS, C.ascT, station(C.ascS)) + angRow("Midheaven", C.mcS, C.mcT, NAKSHATRA[nakIndex(C.mcS)][0])}`;

  /* the mandala's cards for each placement: the Buddhist deck at its sidereal place, the Nordic deck at its tropical place */
  if (window.WyrdTarot) WyrdTarot.load().then(T => document.querySelectorAll("#posTable [data-card]").forEach(td => {
    const c = WyrdTarot.at(T, +td.dataset.card, +td.dataset.trop);
    td.innerHTML = c ? `<span title="Buddhist deck, sidereal">${c.buddhist.minor} <small>· ${c.buddhist.trump}</small></span><br><span title="Nordic deck, tropical">${c.nordic.minor} <small>· ${c.nordic.trump}</small></span>` : "—"; }));
  const rv = WyrdWheel.rave(C), P = X.panchanga;
  /* the karakas in both zodiacs: the same rank by degree within the sign, among the stars and among the seasons */
  const SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const rank = L => SEVEN.map(b => [b, norm(L[b]) % 30]).sort((a, b) => b[1] - a[1]).map(r => r[0]);
  /* in rank order, Atma first (the server's JSON arrives with its keys sorted A to Z) */
  const ROLES = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"];
  const KT = rank(C.trop), the = b => b === "Sun" || b === "Moon" ? "the " + b : b;
  const kar = ROLES.map((k, i) => { const b = C.karaka[k]; return `<tr${b !== KT[i] ? ' class="kar-diff"' : ""}><th>${k === "Atmakaraka" ? g("atmakaraka", "Atma") : k.replace("karaka", "")}</th>
    <td>${GLYPH[b]} ${b}</td><td>${GLYPH[KT[i]]} ${KT[i]}</td></tr>`; }).join("");
  const karNote = C.karaka.Atmakaraka === KT[0] ? `${the(KT[0])[0].toUpperCase() + the(KT[0]).slice(1)} leads in both zodiacs.`
    : `The soul-planet is ${the(C.karaka.Atmakaraka)} among the stars and ${the(KT[0])} among the seasons. The sidereal order is the Jyotish reading.`;
  /* the body map: the stations on the body, sized; which planets land where, and what it means, is in the reading */
  const BM = C.bodyMap;
  /* the numbers: what they are and which planets they sit on; what they mean is in the reading */
  const NB = window.WyrdNumbers, nums = NB ? NB.of(birth.date, birth.full_name, new Date().getFullYear()) : null;
  const numRows = nums ? NB.KINDS.filter(k => k in nums).map(k => { const n = nums[k], p = NB.planets(n);
    return `<tr><th>${g(NB.GLOSS[k], NB.LABEL[k])}</th><td><b>${n}</b>${n > 9 ? ` <small>(${g("masternum", p.root)})</small>` : ""}</td><td>${GLYPH[p.stavefall]} ${p.stavefall} <small>${p.station}</small></td><td>${GLYPH[p.vedic]} ${p.vedic}</td></tr>`; }).join("") : "";
  const asp = [];
  for (let i = 0; i < BODIES.length; i++) for (let k = i + 1; k < BODIES.length; k++){
    const [a, b] = [BODIES[i], BODIES[k]]; if (a === "Rahu" && b === "Ketu") continue;
    const x = aspectBetween(C.sid[a], C.sid[b]);
    if (x) asp.push(`<li><span>${GLYPH[a]} ${a} · ${GLYPH[b]} ${b}</span><span style="color:${x.col}">${x.name}</span><span>${x.orb.toFixed(1)}°</span></li>`);
  }
  /* what the chart is first (the day, the karakas, the aspects), then the design and the body it maps, then the numbers */
  $("facts").innerHTML = `
    ${P ? `<div class="fact"><h3>${g("panchanga", "Your birth day")}</h3>
      <dl><dt>${g("vara")}</dt><dd>${P.vara} <small>(${P.varaLord})</small></dd><dt>${g("tithi")}</dt><dd>${P.paksha} ${P.tithiName} <small>(${P.tithi} of 30)</small></dd>
      <dt>Mansion</dt><dd>${unknown && C.moonSpan && C.moonSpan.length > 1 ? C.moonSpan.join(" or ") : P.nakshatra}</dd><dt>${g("yoga")}</dt><dd>${P.yoga}</dd><dt>${g("karana")}</dt><dd>${P.karana}</dd>
      ${P.sunrise && !unknown ? `<dt>Sunrise</dt><dd>${P.sunrise}${P.beforeSunrise ? " <small>(born before it: still the previous Vedic day)</small>" : ""}</dd>` : ""}</dl></div>` : ""}
    <div class="fact"><h3>${g("karaka", "The seven karakas")}</h3>
      <table class="mini kar-both"><tr><th></th><th>Sidereal</th><th>Tropical</th></tr>${kar}</table>
      <p class="fine">${karNote}${ROLES.some((k, i) => C.karaka[k] !== KT[i]) ? " Marked rows differ." : ""}</p>
    </div>
    <div class="fact"><h3>${g("aspect", "Aspects")}</h3><ul class="kar asp">${asp.join("") || "<li>None within orb</li>"}</ul></div>
    <div class="fact"><h3>Your Birth Design</h3>
      <dl><dt>${g("type")}</dt><dd>${rv.type}</dd><dt>${g("strategy")}</dt><dd>${rv.strategy}</dd><dt>${g("authority")}</dt><dd>${rv.authority}</dd>
      <dt>${g("definition")}</dt><dd>${rv.definition}</dd><dt>${g("profile")}</dt><dd>${rv.profile}</dd><dt>${g("cross", "Cross gates")}</dt><dd>${rv.cross}</dd>
      <dt>${g("centre", "Defined")}</dt><dd>${rv.centres.join(", ") || "—"}</dd><dt>Open</dt><dd>${rv.open.join(", ") || "—"}</dd>
      <dt>${g("channel", "Channels")}</dt><dd>${rv.channels.join(", ") || "—"}</dd></dl>
      <p class="fine">Drawn on your body and explained in <a href="#design">Your design →</a></p></div>
    ${BM ? `<div class="fact wide body-fig"><h3>${g("bodymap", "Your body map")}</h3>
      <p class="bm-line">${BM.line}</p><p class="bm-free"${MEMBER ? " hidden" : ""}><a href="#design/harmonic">See your stations on the Harmonic Body →</a></p><div class="bm-full"${MEMBER ? "" : " hidden"}>${BM.full || ""}</div>
      <p class="fine bm-note"${MEMBER ? " hidden" : ""}>${BM.note}</p><p class="fine bm-member"${MEMBER ? "" : " hidden"}>${BM.memberNote || ""}</p></div>` : ""}
    ${nums ? `<div class="fact"><h3>Your numbers</h3>
      <table class="mini"><tr><th></th><th></th><th>${g("stavefall", "Stavefall")}</th><th>${g("vedicnum", "Vedic")}</th></tr>${numRows}</table>
      <p class="fine">${birth.full_name ? "" : "Add your full name at birth when you cast your chart for three more: expression, soul urge and personality. "}What each number means, and where your life path's planets stand in your chart, is in your reading. <a href="/learn/numbers">How the numbers and their two planets work →</a></p></div>` : ""}
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

/* ---------- Your design: the Birth Design and the Dharma Design, one switch for the whole land ----------
   The Dharma Design's meaning (its readout, and the Rashi-to-Dharma prose) is the reading's; members see it here. */
let DESIGN = null;
function designLand(){
  const has = !!C.dharma;
  $("designIntro").innerHTML = `
    <p>Your <b>Birth Design</b> is how your energy runs; your <b>Dharma Design</b> is where it is heading. Switch between them, or see both at once.</p>
    ${unknown ? `<p class="unknown-note">Without a birth time your Moon's gate and line may be off, and the Dharma Sun moves about 9° a day, so read the details lightly.</p>` : ""}
    ${has ? `<div class="dg-ctl dg-master" role="group" aria-label="Which design to show">
      <button class="hb-btn" data-dgv="birth" aria-pressed="true">Birth Design</button><button class="hb-btn" data-dgv="dharma" aria-pressed="false">Dharma Design</button><button class="hb-btn" data-dgv="both" aria-pressed="false">Both together</button></div>` : ""}`;
  const D = DESIGN = WyrdDesign.mount($("designHost"), { C, full: () => MEMBER });
  if (window.WyrdBody) WyrdBody.mount($("bodyHost"), C);
  WyrdDharma.what($("whatDharmaHost"), { C, unknown });
  if (has) WyrdDharma.mount($("dharmaHost"), { C, unknown }); else $("weave").hidden = true;
  if (has) WyrdVargas.thread($("threadHost"), C, { unknown, full: MEMBER }); else { $("thread").hidden = true; }
  const set = v => { D.set(v); if (window.WyrdBody) WyrdBody.setDesign(v);
    $("designIntro").querySelectorAll("[data-dgv]").forEach(b => b.setAttribute("aria-pressed", b.dataset.dgv === v)); };
  $("designIntro").addEventListener("click", e => { const b = e.target.closest("[data-dgv]"); if (b) set(b.dataset.dgv); });
  set("birth");
}

/* ---------- Now and next: today's sky around the Earth, the birth chart inside it ---------- */
function skyTorus(){
  if (!window.WyrdSkyTorus || !C.transits || !C.transits.rows){ $("chSkyOpen").hidden = true; return; }
  let ST = null;
  const open = () => {
    $("chSky").hidden = false; $("chSkyOpen").parentNode.hidden = true;
    const go = tarot => {
      if (!ST) ST = WyrdSkyTorus.mount($("chSkyHost"), { rows: C.transits.rows, natal: { sid: C.sid }, ay: C.ay, caption: $("chSkyCap"), mode: "3d", tarot,
        onMode: v => document.querySelectorAll("#chSky [data-st]").forEach(b => b.setAttribute("aria-pressed", b.dataset.st === v)) });
      else ST.resize();
      $("chSky").classList.add("big"); setTimeout(() => ST.setMode("3d"), 60);
    };
    window.WyrdTarot ? WyrdTarot.load().then(go) : go(null);
  };
  $("chSkyOpen").addEventListener("click", open);
  $("chSky").querySelector(".st-ctl").addEventListener("click", e => {
    const b = e.target.closest("[data-st]"); if (!b || !ST) return;
    if (b.dataset.st === "close"){ $("chSky").hidden = true; $("chSkyOpen").parentNode.hidden = false; ST.stop(); return; }
    ST.setMode(b.dataset.st);
  });
}

/* ---------- each land, built on first visit ---------- */
let learn = null, MAND = null;
const BUILD = {
  learn: () => { learn = WyrdLearn.mount($("learnHost"), { C, birth, unknown, name: birth.name, dignity, retro, onStep: drawStart }); },
  chart: () => { chartLand(); WyrdVargas.mount($("vargaHost"), C, { unknown }); },
  clock: () => { window.WyrdDasha && WyrdDasha.mount($("dashaHost"));
    if (unknown) $("dashaHost").insertAdjacentHTML("afterbegin", `<p class="unknown-note">The clock is set by the Moon. Without a birth time your Moon could be anywhere in a day's travel, so these dates may be out by months.</p>`); },
  design: designLand,
  runes: () => WyrdRunes.mount($("runesHost"), C, { all: MEMBER }),
  mandala: () => {
    const pl = Object.fromEntries(BODIES.map(b => [b, C.sid[b]]));
    if (!unknown){ pl.Ascendant = C.ascS; pl.Midheaven = C.mcS; }
    MAND = WyrdMandala.mount($("mandalaHost"), { planets: pl, theme: "site", hash: false,
      onSelect: s => { if (location.hash.startsWith("#mandala")) history.replaceState(null, "", "#mandala" + (s ? "/" + s.code.toLowerCase() : "")); } });
  },
  armillary: () => { $("armHostWrap").innerHTML = Wyrd.armillary(); watchArmillary($("p-armillary")); },
  sky: () => { WyrdNow.mount({ C, birth, unknown, top: $("nowHost"), list: $("calHost") }); skyTorus(); },
  colour: () => WyrdColour.mount($("colourHost"), C),
  bench: () => WyrdBench.mount($("benchHost")),
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
  const raw = location.hash.slice(1).split("/")[0];
  if (raw in ALIAS){ history.replaceState(null, "", "#" + ALIAS[raw]); }
  const [id, arg] = location.hash.slice(1).split("/");
  const here = ORDER.some(l => l.id === id) ? id : "map";
  if (Wyrd.pulse && here !== prevLand){ Wyrd.pulse("land", here); if (prevLand) Wyrd.pulse("move", `${prevLand}-${here}`); }
  prevLand = here;
  const land = ORDER.find(l => l.id === id);
  $("skyHost").hidden = !!land; $("tabs").hidden = !land; $("landNav").hidden = !land;
  ORDER.forEach(l => { $("p-" + l.id).hidden = l !== land; });
  document.querySelectorAll("[data-tab]").forEach(t =>
    t.dataset.tab === id ? t.setAttribute("aria-current", "page") : t.removeAttribute("aria-current"));
  if (!land){ drawStart(); Wyrd.sky.start(); startHub(); document.title = `${birth.name ? birth.name + "'s chart" : "Your chart"} · The Wyrd Console`; return; }
  Wyrd.sky.stop(); stopHub();
  if (!built.has(id)){ built.add(id); if (land !== LEARN) decorate(land); BUILD[id](); }
  if (id === "learn" && arg && learn) learn.show(+arg - 1);
  if (id === "mandala" && MAND && /^s\d{3}$/.test(arg || "")){ MAND.select(+arg.slice(1)); scrollTo(0, 0); }
  /* along the path: learn … compare, then the reading, then the rooms to explore; never wrapping round */
  const SEQ = [...PATH, ...LANDS.filter(l => l.gold), ...LANDS.filter(l => l.explore)];
  const i = SEQ.indexOf(land), prev = SEQ[i - 1], next = SEQ[i + 1];
  const often = (NEXT[id] || []).map(n => ORDER.find(l => l.id === n)).filter(l => l && l.id !== id);
  $("landNav").innerHTML = (often.length ? `<p class="often">People here often go on to ${often.map(l => `<a href="#${l.id}">${l.name}</a>`).join(" or ")}.</p>` : "")
    + `${prev ? `<a href="#${prev.id}">← ${prev.path ? PATH.indexOf(prev) + 1 + ". " : ""}${prev.name}</a>` : "<span></span>"}<a href="#" class="to-map">◎ Back to the map</a>${next ? `<a href="#${next.id}">${next.path ? PATH.indexOf(next) + 1 + ". " : next.gold ? "Then: " : ""}${next.name} →</a>` : "<span></span>"}`;
  document.title = `${land.name} · The Wyrd Console`;
  const tab = document.querySelector(`[data-tab="${id}"]`); if (tab) tab.scrollIntoView({ block: "nearest", inline: "center" });
  const sub = arg && id !== "learn" && document.getElementById(arg);
  if (sub){ if (sub.tagName === "DETAILS") sub.open = true; setTimeout(() => sub.scrollIntoView({ block: "start" }), 60); } else scrollTo(0, 0);
  $("lands").focus({ preventScroll: true });
}

drawMap();
mountHub();
addEventListener("hashchange", go);
go();

/* ---------- the reading ---------- */
/* a taste: the first lines of their own story, fading out, right above the button */
if (C.teaser) { const t = $("readingTaste"); t.querySelector(".rd-taste-body").innerHTML = C.teaser; t.hidden = false; }

$("buyBtn").addEventListener("click", async () => {
  if (Wyrd.pulseNow) Wyrd.pulseNow("act", "buy");
  const err = $("buyErr"), btn = $("buyBtn"); err.textContent = "";
  btn.disabled = true; btn.textContent = "Opening checkout…";
  try {
    const r = await fetch("/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(birth) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "Checkout couldn't open.");
    location.href = j.url;
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = buyLabel; }
});
/* members see more on their chart: every rune in full, the planets on the body map, and their Dharma Design read */
function becomeMember(){
  MEMBER = true;
  for (const [sel, show] of [[".bm-free", false], [".bm-full", true], [".bm-note", false], [".bm-member", true]]) { const el = document.querySelector(sel); if (el) el.hidden = !show; }
  const rh = $("runesHost"); if (rh && rh.innerHTML.trim()) WyrdRunes.mount(rh, C, { all: true });
  if (DESIGN) DESIGN.redraw();
  const th = $("threadHost"); if (th && th.innerHTML.trim() && C.dharma) WyrdVargas.thread(th, C, { unknown, full: true });
}

/* members pay less: say so on the button before they click */
let buyLabel = $("buyBtn").textContent;
fetch("/api/me").then(r => r.json()).then(d => {
  for (const el of document.querySelectorAll("[data-price]")) if (d.prices && d.prices[el.dataset.price]) el.textContent = d.prices[el.dataset.price];
  if (d.readingPrice) buyLabel = d.member ? `Get my reading — ${d.readingPrice}, your Order price` : `Get my reading — ${d.readingPrice}`;
  $("buyBtn").textContent = buyLabel;
  if (d.member) { document.querySelector(".offer-member").hidden = true; becomeMember(); }
}).catch(() => {});
if (new URLSearchParams(location.search).get("cancelled")) $("buyErr").textContent = "Checkout was cancelled — your chart is still here whenever you're ready.";
})();
