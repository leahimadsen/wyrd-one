/* The practice desk: place search for the client form. */
(() => {
  const f = document.getElementById("proForm"), err = document.getElementById("proErr");
  if (!f) return;
  let place = null;
  WyrdCommon.placeSearch(document.getElementById("proPlace"), document.getElementById("placeList"), p => {
    place = p;
    for (const [k, v] of [["place_id", p && p.id], ["lat", p && p.lat], ["lon", p && p.lon], ["tz", p && p.tz], ["place_label", p && p.label]]) f.elements[k].value = v ?? "";
  });
  f.addEventListener("submit", e => {
    err.textContent = "";
    if (!place){ e.preventDefault(); err.textContent = "Choose the birthplace from the list as you type."; }
  });
})();
