'use strict';
/* ============================================================
   THE READING'S DRAWINGS
   The paid reading carries its chart as data (#rd-chart) and draws it
   here with the console's own drawings, so the two always match:
     [data-fig="wheel"]     the chart flat (wheel.js), tap a planet to follow it
     [data-fig="torus"]     the chart as a torus (torus.js), in either zodiac
     [data-fig="harmonic"]  the Harmonic Body (body.js)
   A reading without the data (the reading together) draws nothing.
   Depends on viz.js, body.js, wheel.js and torus.js.
   ============================================================ */
(() => {
const el = document.getElementById("rd-chart");
if (!el) return;
let C;
try { C = JSON.parse(el.textContent); } catch (_) { return; }
const unknown = !!C.unknownTime;
const fail = (host, x) => { console.error(x); host.closest(".rd-plate") && (host.closest(".rd-plate").hidden = true); };

/* the chart flat */
const wheel = document.querySelector('[data-fig="wheel"]');
if (wheel && window.WyrdWheel){
  try { WyrdWheel.mount(wheel, C, { level: "full", unknownTime: unknown }); } catch (x) { fail(wheel, x); }
}

/* the chart as a torus, with its zodiac and its layers to switch, turning only while it is in view */
const tz = document.querySelector('[data-fig="torus"]');
if (tz && window.WyrdTorus){
  try {
    const plate = tz.closest(".rd-plate"), cap = plate.querySelector("[data-tz-cap]");
    const T = WyrdTorus.mount(tz, C, { caption: cap });
    const zod = plate.querySelector("[data-tz-zodiac]"), lay = plate.querySelector("[data-tz-layers]");
    zod.innerHTML = ["sidereal", "tropical"].map(z => `<button type="button" class="tz-chip" data-zodiac="${z}" aria-pressed="${z === T.zodiac}">${z === "sidereal" ? "Sidereal" : "Tropical"}</button>`).join("");
    const chips = () => { lay.innerHTML = T.layers.map(l => `<button type="button" class="tz-chip" data-layer="${l.id}" aria-pressed="${l.on}">${l.name}</button>`).join(""); };
    chips();
    zod.addEventListener("click", e => {
      const b = e.target.closest("[data-zodiac]"); if (!b || b.dataset.zodiac === T.zodiac) return;
      T.setZodiac(b.dataset.zodiac); zod.querySelectorAll("[data-zodiac]").forEach(x => x.setAttribute("aria-pressed", x === b)); chips();
    });
    lay.addEventListener("click", e => {
      const b = e.target.closest("[data-layer]"); if (!b) return;
      const on = b.getAttribute("aria-pressed") !== "true"; b.setAttribute("aria-pressed", on); T.toggle(b.dataset.layer, on);
    });
    /* it builds straight away, so the page prints with it whole wherever the reader is; after that it turns only
       while it is in view (a stopped canvas keeps its last frame) */
    T.start();
    if ("IntersectionObserver" in window && new URLSearchParams(location.search).get("pdf") !== "1")
      setTimeout(() => new IntersectionObserver(es => es.forEach(x => x.isIntersecting ? T.start() : T.stop()), { rootMargin: "200px" }).observe(tz), 4000);
  } catch (x) { fail(tz, x); }
}

/* the Harmonic Body */
const hb = document.querySelector('[data-fig="harmonic"]');
if (hb && window.WyrdBody){
  try { WyrdBody.mount(hb, C, { intro: "" }); } catch (x) { fail(hb, x); }       /* the reading introduces it in its own words */
}
window.WyrdReadingFigs = { ready: true };
})();
