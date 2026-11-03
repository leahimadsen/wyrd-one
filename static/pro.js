/* The practice desk: place search for the client form. */
(() => {
  const f = document.getElementById("proForm"), err = document.getElementById("proErr");
  if (!f) return;
  let place = null;
  const cal = WyrdCommon.calendarChoice(f.elements.date);
  WyrdCommon.placeSearch(document.getElementById("proPlace"), document.getElementById("placeList"), p => {
    place = p; cal.place(p);
    for (const [k, v] of [["place_id", p && p.id], ["lat", p && p.lat], ["lon", p && p.lon], ["tz", p && p.tz], ["place_label", p && p.label], ["cc", p && p.cc]]) f.elements[k].value = v ?? "";
  });
  if (f.elements.tz.value) cal.place({ cc: f.elements.cc.value, tz: f.elements.tz.value });     // a client's saved birthplace
  f.addEventListener("submit", e => {
    err.textContent = "";
    if (!place && !f.elements.lat.value){ e.preventDefault(); err.textContent = "Choose the birthplace from the list as you type."; }
  });
})();
