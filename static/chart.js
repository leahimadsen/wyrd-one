'use strict';
/* The chart page. The landing page casts the chart and keeps it in this tab's
   sessionStorage; this page draws the map (the chart as the hub, the lands
   around it) and opens one land at a time. Lands are built the first time
   they are visited, so the page stays light. */
(() => {
const $ = id => document.getElementById(id);
const { signOf, degIn, nakIndex, houseOf, norm, GLYPH, NAKSHATRA } = Wyrd.helpers;

let saved = null;
try { saved = JSON.parse(sessionStorage.getItem("wyrdChart") || "null"); } catch (_) {}
if (!saved || !saved.result || !saved.result.chart){ location.replace("/"); return; }
const { birth, result: J } = saved, C = J.chart, T = C.dashaTree;
Wyrd.setChart(C);

/* ---------- the lands ---------- */
const sid = b => signOf(C.sid[b]);
const LANDS = [
  { id: "chart",     name: "Your chart",            mark: "☉", teaser: `${signOf(C.ascS)} rising · Moon in ${NAKSHATRA[nakIndex(C.sid.Moon)][0]}` },
  { id: "body",      name: "The harmonic body",     mark: "✶", teaser: "Seven stations, each fed by one of your planets" },
  { id: "clock",     name: "The Vimshottari clock", mark: "◷", teaser: `${T.cur.lord} era · ${T.curA.lord} chapter, running now` },
  { id: "armillary", name: "The armillary",         mark: "◎", teaser: "Your sky as a sphere you can open" },
  { id: "reading",   name: "Your full reading",     mark: "✦", teaser: "Eight movements, written for you · $44", gold: true },
  { id: "sky",       name: "The sky now",           mark: "☾", teaser: "Today's planets crossing yours" },
  { id: "colour",    name: "The colour room",       mark: "◐", teaser: "Your twelve houses as a colour wheel" },
  { id: "bench",     name: "The bench",             mark: "♪", teaser: "Hear two of your planets together" },
];

function drawMap(){
  const pos = LANDS.map((l, i) => {
    const a = i * Math.PI / 4;
    return { ...l, x: 50 + 40 * Math.sin(a), y: 50 - 40 * Math.cos(a) };
  });
  const paths = pos.map(p => `<line x1="50" y1="50" x2="${p.x.toFixed(2)}" y2="${p.y.toFixed(2)}"${p.gold ? ` class="gold"` : ""}/>`).join("");
  $("map").innerHTML = `
    <svg class="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <circle cx="50" cy="50" r="40" class="rail"/>${paths}</svg>
    <a class="map-core" href="#chart" aria-label="Open your chart">${WyrdWheel.svg(C, { compact: true })}</a>
    ${pos.map(p => `<a class="land${p.gold ? " gold" : ""}" href="#${p.id}" style="--x:${p.x.toFixed(2)}%;--y:${p.y.toFixed(2)}%">
      <span class="land-mark" aria-hidden="true">${p.mark}</span><b>${p.name}</b><small>${p.teaser}</small></a>`).join("")}`;
  $("tabsIn").innerHTML = `<a href="#map" class="tab tab-map">◎ Map</a>` +
    LANDS.map(l => `<a href="#${l.id}" class="tab${l.gold ? " gold" : ""}" data-tab="${l.id}">${l.name.replace(/^The |^Your /, "")}</a>`).join("");
}

/* ---------- each land, built on first visit ---------- */
function fmt(l){
  const d = degIn(l); let deg = Math.floor(d), min = Math.round((d - deg) * 60); if (min === 60){ deg++; min = 0; }
  return `${signOf(l)} ${deg}°${String(min).padStart(2, "0")}′`;
}
function chartTable(){
  const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;
  const NP = C.natal.personality, ND = C.natal.design;
  const gl = g => g ? `${g.gate}.${g.line}` : "—";
  $("chartWheel").innerHTML = WyrdWheel.svg(C, { name: birth.name || "Your chart", place: J.place.label.split(",")[0],
    when: `${birth.date} ${birth.time}` });

  const order = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
  const rows = order.map(b => {
    const l = C.sid[b], ru = WyrdWheel.runeAt(C, l);
    return `<tr><th scope="row">${GLYPH[b] || ""} ${b}</th><td>${fmt(l)}</td><td>${fmt(C.trop[b])}</td>
      <td>${NAKSHATRA[nakIndex(l)][0]} ${pada(l)}</td><td>${houseOf(l, C.ascS)}</td><td>${ru.glyph} ${ru.name}</td>
      <td>${C.nav && C.nav[b] != null ? signOf(C.nav[b]) : "—"}</td><td>${gl(NP[b])}</td><td class="des">${gl(ND[b])}</td></tr>`;
  }).join("");
  const angRow = (n, l, mansion) => { const ru = WyrdWheel.runeAt(C, l);
    return `<tr class="ang"><th scope="row">${n}</th><td>${fmt(l)}</td><td>${fmt(n === "Ascendant" ? C.ascT : C.mcT)}</td><td>${mansion}</td>
      <td>${houseOf(l, C.ascS)}</td><td>${ru.glyph} ${ru.name}</td><td>${n === "Ascendant" && C.navAsc != null ? signOf(C.navAsc) : "—"}</td><td>—</td><td>—</td></tr>`; };
  $("posTable").innerHTML = `<caption>Sidereal is Lahiri; the gates run on the tropical wheel. Design is the moment the Sun stood 88° earlier.</caption>
    <tr><th scope="col">Body</th><th scope="col">Sidereal</th><th scope="col">Tropical</th><th scope="col">Mansion · pada</th><th scope="col">House</th><th scope="col">Rune</th><th scope="col">Navamsa</th><th scope="col">Gate</th><th scope="col">Design gate</th></tr>
    ${rows}
    <tr><th scope="row">⊕ Earth</th><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>${gl(NP.Earth)}</td><td class="des">${gl(ND.Earth)}</td></tr>
    ${angRow("Ascendant", C.ascS, `${NAKSHATRA[nakIndex(C.ascS)][0]} ${pada(C.ascS)}`)}
    ${angRow("Midheaven", C.mcS, NAKSHATRA[nakIndex(C.mcS)][0])}`;

  const rv = WyrdWheel.rave(C);
  const kar = Object.entries(C.karaka).map(([k, b]) => `<li><span>${k.replace("karaka", "")}</span>${GLYPH[b]} ${b}</li>`).join("");
  const bodies = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"], asp = [];
  for (let i = 0; i < bodies.length; i++) for (let k = i + 1; k < bodies.length; k++){
    const [a, b] = [bodies[i], bodies[k]];
    if ((a === "Rahu" && b === "Ketu")) continue;
    const x = aspectBetween(C.sid[a], C.sid[b]);
    if (x) asp.push(`<li><span>${GLYPH[a]} ${a} · ${GLYPH[b]} ${b}</span><span style="color:${x.col}">${x.name}</span><span>${x.orb.toFixed(1)}°</span></li>`);
  }
  $("facts").innerHTML = `
    <div class="fact"><h3>The rave</h3>
      <dl><dt>Type</dt><dd>${rv.type}</dd><dt>Strategy</dt><dd>${rv.strategy}</dd><dt>Authority</dt><dd>${rv.authority}</dd>
      <dt>Definition</dt><dd>${rv.definition}</dd><dt>Profile</dt><dd>${rv.profile}</dd><dt>Cross gates</dt><dd>${rv.cross}</dd>
      <dt>Defined</dt><dd>${rv.centres.join(", ") || "—"}</dd><dt>Open</dt><dd>${rv.open.join(", ") || "—"}</dd>
      <dt>Channels</dt><dd>${rv.channels.join(", ") || "—"}</dd></dl></div>
    <div class="fact"><h3>The seven karakas</h3><ul class="kar">${kar}</ul>
      <h3 class="fact-h2">Aspects</h3><ul class="kar asp">${asp.join("") || "<li>None within orb</li>"}</ul></div>`;
}
const BUILD = {
  chart: chartTable,
  body: () => window.WyrdBody && WyrdBody.mount($("bodyHost"), C),
  clock: () => window.WyrdDasha && WyrdDasha.mount($("dashaHost")),
  armillary: () => { $("armHostWrap").innerHTML = Wyrd.armillary(); watchArmillary($("p-armillary")); },
  sky: () => renderTransits(C),
  colour: () => { $("colourHost").innerHTML = Wyrd.colour(); setTimeout(() => Wyrd.afterColour(), 0); },
  bench: () => { $("benchHost").innerHTML = Wyrd.bench(); },
  reading: () => {},
};
const built = new Set();

/* ---------- moving between the map and the lands ---------- */
function go(){
  const id = location.hash.slice(1);
  const land = LANDS.find(l => l.id === id);
  $("skyHost").hidden = !!land; $("tabs").hidden = !land; $("landNav").hidden = !land;
  LANDS.forEach(l => { $("p-" + l.id).hidden = l !== land; });
  document.querySelectorAll("[data-tab]").forEach(t =>
    t.dataset.tab === id ? t.setAttribute("aria-current", "page") : t.removeAttribute("aria-current"));
  if (!land){ Wyrd.sky.start(); document.title = "Your chart · The Wyrd Console"; return; }
  Wyrd.sky.stop();
  if (!built.has(id)){ built.add(id); BUILD[id](); }
  const i = LANDS.indexOf(land), prev = LANDS[(i + LANDS.length - 1) % LANDS.length], next = LANDS[(i + 1) % LANDS.length];
  $("landNav").innerHTML = `<a href="#${prev.id}">← ${prev.name}</a><a href="#map" class="to-map">◎ Back to the map</a><a href="#${next.id}">${next.name} →</a>`;
  document.title = `${land.name} · The Wyrd Console`;
  document.querySelector(`[data-tab="${id}"]`).scrollIntoView({ block: "nearest", inline: "center" });
  scrollTo(0, 0);
}

$("who").textContent = birth.name ? `${birth.name}'s chart` : "Your chart";
$("chartMeta").textContent = `${birth.date} at ${birth.time} (${J.utc}) · ${J.place.label}`;
drawMap();
addEventListener("hashchange", go);
go();

/* ---------- the reading ---------- */
$("buyBtn").addEventListener("click", async () => {
  const err = $("buyErr"), btn = $("buyBtn"); err.textContent = "";
  btn.disabled = true; btn.textContent = "Opening checkout…";
  try {
    const r = await fetch("/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" },
                                             body: JSON.stringify(birth) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "Checkout couldn't open.");
    location.href = j.url;
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = "Get my reading — $44"; }
});
if (new URLSearchParams(location.search).get("cancelled")) $("buyErr").textContent = "Checkout was cancelled — your chart is still here whenever you're ready.";
})();
