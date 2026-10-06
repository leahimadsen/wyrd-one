'use strict';
(() => {
const $ = id => document.getElementById(id);
const H = () => Wyrd.helpers;
let place = null, lastBirth = null;

/* ---------- the sky behind the seat ---------- */
Wyrd.sky.start();

/* ---------- place search ---------- */
const input = $("placeInput"), list = $("placeList");
let timer = null, ctrl = null, active = -1, results = [];
function showList(items){
  results = items; active = -1;
  list.innerHTML = items.length ? items.map((p, i) =>
    `<li role="option" id="pl${i}" data-i="${i}"><b>${esc(p.name)}</b> <span>${esc(p.label.slice(p.name.length + 2))}</span></li>`).join("")
    : `<li class="none">No match yet. Try the nearest larger town, or add the country after a comma.</li>`;
  list.hidden = false; input.setAttribute("aria-expanded", "true");
}
function hideList(){ list.hidden = true; input.setAttribute("aria-expanded", "false"); }
function pick(i){
  place = results[i]; if (!place) return;
  input.value = place.label; hideList();
}
input.addEventListener("input", () => {
  place = null;
  clearTimeout(timer);
  const q = input.value.trim();
  if (q.length < 2){ hideList(); return; }
  timer = setTimeout(async () => {
    if (ctrl) ctrl.abort(); ctrl = new AbortController();
    try {
      const r = await fetch("/api/places?q=" + encodeURIComponent(q), { signal: ctrl.signal });
      showList(await r.json());
    } catch (_) {}
  }, 160);
});
input.addEventListener("keydown", e => {
  if (list.hidden) return;
  if (e.key === "ArrowDown" || e.key === "ArrowUp"){
    e.preventDefault();
    active = (active + (e.key === "ArrowDown" ? 1 : -1) + results.length) % results.length;
    list.querySelectorAll("li").forEach((li, i) => li.classList.toggle("on", i === active));
    input.setAttribute("aria-activedescendant", "pl" + active);
  } else if (e.key === "Enter" && active >= 0){ e.preventDefault(); pick(active); }
  else if (e.key === "Escape") hideList();
});
list.addEventListener("pointerdown", e => {
  const li = e.target.closest("li[data-i]"); if (li){ e.preventDefault(); pick(+li.dataset.i); }
});
input.addEventListener("blur", () => setTimeout(hideList, 120));

/* ---------- casting ---------- */
$("castForm").addEventListener("submit", async e => {
  e.preventDefault();
  const f = e.target, err = $("castErr"); err.textContent = "";
  if (!f.date.value || !f.time.value){ err.textContent = "Enter your date and time of birth."; return; }
  if (!place){ err.textContent = "Choose your birthplace from the list as you type."; input.focus(); return; }
  const btn = f.querySelector("button"); btn.disabled = true; btn.textContent = "Casting…";
  lastBirth = { name: f.name.value.trim(), date: f.date.value, time: f.time.value, place_id: place.id,
                lat: place.lat, lon: place.lon, tz: place.tz, place_label: place.label };
  try {
    const r = await fetch("/api/chart", { method: "POST", headers: { "Content-Type": "application/json" },
                                          body: JSON.stringify(lastBirth) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "The chart couldn't be cast.");
    render(j);
  } catch (x) { err.textContent = x.message; }
  finally { btn.disabled = false; btn.textContent = "Cast my chart"; }
});

function fmt(l){
  const { signOf, degIn } = H(); const d = degIn(l);
  let deg = Math.floor(d), min = Math.round((d - deg) * 60); if (min === 60){ deg++; min = 0; }
  return `${signOf(l)} ${deg}°${String(min).padStart(2, "0")}′`;
}
function render(j){
  const C = j.chart, { GLYPH, NAKSHATRA, nakIndex, houseOf, norm, GATE_NAME } = H();
  Wyrd.setChart(C);
  $("chartMeta").textContent = `${lastBirth.date} at ${lastBirth.time} (${j.utc}) · ${j.place.label}`;
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
  const D = C.dharma, T = C.dashaTree;
  const kar = Object.entries(C.karaka).map(([k, b]) => `<li><span>${k.replace("karaka", "")}</span>${GLYPH[b]} ${b}</li>`).join("");
  $("facts").innerHTML = `
    <div class="fact"><h3>The Dharma Weave</h3>
      <dl><dt>Dharma profile</dt><dd>${D.profile} · ${D.band}${D.mauve ? " · the magenta point" : ""}</dd>
      <dt>Birth profile</dt><dd>${C.natal.profile}</dd>
      <dt>Pentagram Cross</dt><dd>${D.suns.gap.toFixed(4)}° ${D.suns.holds ? "✓ holds" : "✗"}</dd>
      <dt>Dharma Sun</dt><dd>gate ${D.personality.Sun.gate}.${D.personality.Sun.line}</dd></dl></div>
    <div class="fact"><h3>The seven karakas</h3><ul class="kar">${kar}</ul></div>
    <div class="fact"><h3>Running now</h3>
      <dl><dt>Mahadasha</dt><dd>${GLYPH[T.cur.lord]} ${T.cur.lord}</dd>
      <dt>Antardasha</dt><dd>${GLYPH[T.curA.lord]} ${T.curA.lord}</dd>
      <dt>Pratyantar</dt><dd>${GLYPH[T.curP.lord]} ${T.curP.lord}</dd></dl></div>`;

  $("armHostWrap").innerHTML = Wyrd.armillary();
  $("colourHost").innerHTML = Wyrd.colour();
  setTimeout(() => Wyrd.afterColour(), 0);
  $("benchHost").innerHTML = Wyrd.bench();
  renderTransits(C);
  $("results").hidden = false;
  watchArmillary($("armBlk"));
  $("chartBlk").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
}

/* ---------- the reading ---------- */
$("buyBtn").addEventListener("click", async () => {
  const err = $("buyErr"), btn = $("buyBtn"); err.textContent = "";
  if (!lastBirth){ err.textContent = "Cast your chart first."; return; }
  btn.disabled = true; btn.textContent = "Opening checkout…";
  try {
    const r = await fetch("/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" },
                                             body: JSON.stringify(lastBirth) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "Checkout couldn't open.");
    location.href = j.url;
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = "Get my reading — $44"; }
});

/* ---------- music: browsers only allow sound after a tap, so it starts on the button ---------- */
(() => {
  const a = $("music"), b = $("musicBtn");
  fetch(a.getAttribute("src"), { method: "HEAD" }).then(r => { if (r.ok) b.hidden = false; }).catch(() => {});
  a.volume = 0.35;
  const set = on => { b.setAttribute("aria-pressed", on); b.textContent = on ? "♪ Music on" : "♪ Music"; };
  b.addEventListener("click", () => {
    if (a.paused){ a.play().then(() => set(true)).catch(() => {}); try { localStorage.setItem("wyrdMusic", "1"); } catch (_) {} }
    else { a.pause(); set(false); try { localStorage.setItem("wyrdMusic", "0"); } catch (_) {} }
  });
  /* if they turned it on last visit, resume on their first tap anywhere */
  let wanted = false; try { wanted = localStorage.getItem("wyrdMusic") === "1"; } catch (_) {}
  if (wanted) document.addEventListener("pointerdown", function once(e){
    if (e.target === b) return;
    a.play().then(() => set(true)).catch(() => {});
    document.removeEventListener("pointerdown", once);
  });
})();

function esc(s){ return String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c])); }
if (new URLSearchParams(location.search).get("cancelled")) $("castErr").textContent = "Checkout was cancelled — cast again whenever you're ready.";
})();
