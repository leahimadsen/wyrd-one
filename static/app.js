'use strict';
(() => {
const $ = id => document.getElementById(id);
let place = null;
/* /consultation is where a paid 1:1 client lands from Stripe: same form, but it unlocks their reading */
const consultSid = location.pathname === "/consultation" ? new URLSearchParams(location.search).get("session_id") : null;

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

/* ---------- casting: the chart opens on its own page ---------- */
if (consultSid){
  document.querySelector(".seat-in h1").textContent = "Your consultation";
  $("seatSub").textContent = "Your payment is confirmed. Give the moment and place of your birth and your reading opens.";
  $("nameNote").textContent = "it goes on your reading";
  $("castForm").querySelector("button").textContent = "Open my reading";
}

$("castForm").addEventListener("submit", async e => {
  e.preventDefault();
  const f = e.target, err = $("castErr"), btn = f.querySelector("button"), label = btn.textContent;
  err.textContent = "";
  if (!f.date.value || !f.time.value){ err.textContent = "Enter your date and time of birth."; return; }
  if (!place){ err.textContent = "Choose your birthplace from the list as you type."; input.focus(); return; }
  btn.disabled = true; btn.textContent = consultSid ? "Opening…" : "Casting…";
  const birth = { name: f.name.value.trim(), date: f.date.value, time: f.time.value, place_id: place.id,
                  lat: place.lat, lon: place.lon, tz: place.tz, place_label: place.label };
  try {
    const url = consultSid ? "/api/consultation-reading" : "/api/chart";
    const body = consultSid ? { ...birth, session_id: consultSid } : birth;
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "The chart couldn't be cast.");
    if (consultSid){ location.href = j.url; return; }
    try { sessionStorage.setItem("wyrdChart", JSON.stringify({ birth, result: j })); }
    catch (_) { throw new Error("Your browser blocked this page from keeping your chart. Allow site data and try again."); }
    location.href = "/chart";
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = label; }
});

function esc(s){ return String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c])); }
})();
