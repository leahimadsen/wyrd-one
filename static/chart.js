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

/* ---------- the hub: a small wheel of the chart itself ---------- */
function wheel(){
  const SG = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"].map(g => g + "︎");
  const pt = (lon, r) => { const t = Math.PI + (lon - C.ascS) * Math.PI / 180; return [r * Math.cos(t), -r * Math.sin(t)]; };
  const f = n => n.toFixed(2);
  let s = `<circle r="96" class="w-ring"/><circle r="74" class="w-ring"/><circle r="40" class="w-ring w-in"/>`;
  for (let i = 0; i < 12; i++){
    const [x1, y1] = pt(i * 30, 74), [x2, y2] = pt(i * 30, 96), [gx, gy] = pt(i * 30 + 15, 85);
    s += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" class="w-div"/><text x="${f(gx)}" y="${f(gy)}" class="w-sign">${SG[i]}</text>`;
  }
  const [ax, ay] = pt(C.ascS, 96), [dx, dy] = pt(C.ascS + 180, 96);
  s += `<line x1="${f(ax)}" y1="${f(ay)}" x2="${f(dx)}" y2="${f(dy)}" class="w-hor"/>`;
  /* spread the bodies so glyphs don't sit on each other */
  const bodies = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]
    .map(b => ({ b, lon: norm(C.sid[b] - C.ascS) })).sort((a, b) => a.lon - b.lon);
  bodies.forEach((p, i) => { p.at = p.lon; if (i && p.at - bodies[i - 1].at < 13) p.at = bodies[i - 1].at + 13; });
  for (const p of bodies){
    const [x, y] = pt(p.at + C.ascS, 59), [tx, ty] = pt(p.lon + C.ascS, 74);
    s += `<circle cx="${f(tx)}" cy="${f(ty)}" r="1.6" class="w-tick"/><text x="${f(x)}" y="${f(y)}" class="w-body">${GLYPH[p.b]}</text>`;
  }
  s += `<text y="-13" class="w-core">☉ ${sid("Sun")}</text><text y="1" class="w-core">☽ ${sid("Moon")}</text><text y="15" class="w-core">↑ ${signOf(C.ascS)}</text>`;
  return `<svg viewBox="-100 -100 200 200" role="img" aria-label="Your chart: Sun in ${sid("Sun")}, Moon in ${sid("Moon")}, ${signOf(C.ascS)} rising">${s}</svg>`;
}

function drawMap(){
  const pos = LANDS.map((l, i) => {
    const a = i * Math.PI / 4;
    return { ...l, x: 50 + 40 * Math.sin(a), y: 50 - 40 * Math.cos(a) };
  });
  const paths = pos.map(p => `<line x1="50" y1="50" x2="${p.x.toFixed(2)}" y2="${p.y.toFixed(2)}"${p.gold ? ` class="gold"` : ""}/>`).join("");
  $("map").innerHTML = `
    <svg class="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <circle cx="50" cy="50" r="40" class="rail"/>${paths}</svg>
    <a class="map-core" href="#chart" aria-label="Open your chart">${wheel()}</a>
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
  const order = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
  const rows = order.map(b => {
    const g = C.natal.personality[b];
    return `<tr><th scope="row">${GLYPH[b] || ""} ${b}</th><td>${fmt(C.sid[b])}</td><td>${fmt(C.trop[b])}</td>
      <td>${NAKSHATRA[nakIndex(C.sid[b])][0]} ${pada(C.sid[b])}</td><td>${houseOf(C.sid[b], C.ascS)}</td>
      <td>${g.gate}.${g.line}</td></tr>`;
  }).join("");
  $("posTable").innerHTML = `<caption>Sidereal is Lahiri; the gates run on the tropical wheel.</caption>
    <tr><th scope="col">Body</th><th scope="col">Sidereal</th><th scope="col">Tropical</th><th scope="col">Mansion · pada</th><th scope="col">House</th><th scope="col">Gate</th></tr>
    ${rows}
    <tr class="ang"><th scope="row">Ascendant</th><td>${fmt(C.ascS)}</td><td>${fmt(C.ascT)}</td><td>${NAKSHATRA[nakIndex(C.ascS)][0]} ${pada(C.ascS)}</td><td>1</td><td>—</td></tr>
    <tr class="ang"><th scope="row">Midheaven</th><td>${fmt(C.mcS)}</td><td>${fmt(C.mcT)}</td><td>${NAKSHATRA[nakIndex(C.mcS)][0]}</td><td>${houseOf(C.mcS, C.ascS)}</td><td>—</td></tr>`;
  const D = C.dharma;
  const kar = Object.entries(C.karaka).map(([k, b]) => `<li><span>${k.replace("karaka", "")}</span>${GLYPH[b]} ${b}</li>`).join("");
  $("facts").innerHTML = `
    <div class="fact"><h3>The Dharma Weave</h3>
      <dl><dt>Dharma profile</dt><dd>${D.profile} · ${D.band}${D.mauve ? " · the magenta point" : ""}</dd>
      <dt>Birth profile</dt><dd>${C.natal.profile}</dd>
      <dt>Pentagram Cross</dt><dd>${D.suns.gap.toFixed(4)}° ${D.suns.holds ? "✓ holds" : "✗"}</dd>
      <dt>Dharma Sun</dt><dd>gate ${D.personality.Sun.gate}.${D.personality.Sun.line}</dd></dl></div>
    <div class="fact"><h3>The seven karakas</h3><ul class="kar">${kar}</ul></div>`;
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
