'use strict';
/* The landing page: the high seat, the birth form and the charts this browser has saved. */
(() => {
const $ = id => document.getElementById(id);
const { esc, placeSearch, cast, keep, current, savedList, removeSaved } = WyrdCommon;
let place = null;
/* /consultation is where a paid 1:1 client lands from Stripe: same form, but it unlocks their reading */
const consultSid = location.pathname === "/consultation" ? new URLSearchParams(location.search).get("session_id") : null;
const params = new URLSearchParams(location.search);

Wyrd.sky.start();
const f = $("castForm"), err = $("castErr"), btn = f.querySelector("button[type=submit]"), label = btn.textContent;
placeSearch($("placeInput"), $("placeList"), p => { place = p; });

/* ---------- unknown birth time ---------- */
const unk = $("unknownTime");
function syncUnknown(){
  f.time.disabled = unk.checked;
  if (unk.checked){ f.time.dataset.was = f.time.value; f.time.value = "12:00"; }
  else if (f.time.dataset.was != null){ f.time.value = f.time.dataset.was; }
}
unk.addEventListener("change", syncUnknown);

/* ---------- editing a chart already cast: fill the form back in ---------- */
function fill(b){
  f.name.value = b.name || ""; f.date.value = b.date || ""; f.time.value = b.time || "";
  unk.checked = !!b.unknown_time; syncUnknown();
  if (b.place_id != null){
    place = { id: b.place_id, label: b.place_label, lat: b.lat, lon: b.lon, tz: b.tz };
    $("placeInput").value = b.place_label || "";
  }
}
if (params.get("edit")){ const s = current(); if (s && s.birth) fill(s.birth); }

/* ---------- the consultation version of the form ---------- */
if (consultSid){
  document.querySelector(".seat-in h1").textContent = "Your consultation";
  $("seatSub").textContent = "Your payment is confirmed. Give the moment and place of your birth and your reading opens.";
  $("nameNote").textContent = "it goes on your reading";
  btn.textContent = "Open my reading";
  document.querySelector(".f-unknown").hidden = true;
  document.querySelector(".seat-links").hidden = true;
}

function birthFromForm(){
  return { name: f.name.value.trim(), date: f.date.value, time: unk.checked ? "12:00" : f.time.value,
           unknown_time: unk.checked || undefined, place_id: place.id, lat: place.lat, lon: place.lon, tz: place.tz,
           place_label: place.label };
}
async function open(birth, button){
  const was = button.textContent; button.disabled = true; button.textContent = "Casting…"; err.textContent = "";
  try {
    const j = await cast(birth);
    if (!keep(birth, j)) throw new Error("Your browser blocked this page from keeping your chart. Allow site data and try again.");
    location.href = "/chart";
  } catch (x) { err.textContent = x.message; button.disabled = false; button.textContent = was; }
}

f.addEventListener("submit", async e => {
  e.preventDefault(); err.textContent = "";
  if (!f.date.value || (!unk.checked && !f.time.value)){ err.textContent = "Enter your date of birth, and your time if you know it."; return; }
  if (!place){ err.textContent = "Choose your birthplace from the list as you type."; $("placeInput").focus(); return; }
  const birth = birthFromForm();
  if (!consultSid) return open(birth, btn);
  btn.disabled = true; btn.textContent = "Opening…";
  try {
    const r = await fetch("/api/consultation-reading", { method: "POST", headers: { "Content-Type": "application/json" },
                                                          body: JSON.stringify({ ...birth, session_id: consultSid }) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "Your reading couldn't be opened.");
    location.href = j.url;
  } catch (x) { err.textContent = x.message; btn.disabled = false; btn.textContent = label; }
});

/* ---------- charts saved in this browser ---------- */
function drawSaved(){
  const list = savedList(), box = $("savedBox");
  box.hidden = consultSid || !list.length;
  $("savedList").innerHTML = list.map((b, i) => `<li>
    <button type="button" class="sv-open" data-i="${i}"><b>${esc(b.name || "Unnamed chart")}</b>
      <span>${esc(b.date)}${b.unknown_time ? " · time unknown" : " · " + esc(b.time)} · ${esc((b.place_label || "").split(",")[0])}</span></button>
    <button type="button" class="sv-x" data-x="${i}" aria-label="Forget ${esc(b.name || "this chart")}">×</button></li>`).join("");
}
$("savedList").addEventListener("click", e => {
  const o = e.target.closest(".sv-open"), x = e.target.closest(".sv-x");
  if (o){ const b = savedList()[+o.dataset.i]; if (b){ const { savedAt, ...birth } = b; open(birth, o); } }
  if (x){ removeSaved(+x.dataset.x); drawSaved(); }
});
drawSaved();

if (params.get("cancelled")) err.textContent = "Checkout was cancelled — cast again whenever you're ready.";
})();
