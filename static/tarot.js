'use strict';
/* ============================================================
   THE MANDALA'S CARDS
   The Völva's 108-pada mandala (static/mandala.json, made from
   lib/wyrd-mandala-108.csv by scripts/mandala.py): every pada of the
   sidereal zodiac carries a minor card in two decks (outer and inner),
   its decan ruler, and a trump in two decks. A planet's card is the
   card of the pada it stands in.
   - WyrdTarot.load(): Promise of the 108 padas
   - WyrdTarot.at(padas, sidLon): that pada's cards
   - WyrdTarot.minor(c), .trump(c): "10 of Cups · 10 of Lotuses", "The Moon · Nirvana"
   ============================================================ */
(() => {
let cache = null;
const norm = d => ((d % 360) + 360) % 360;
function load(){
  if (!cache) cache = fetch("/static/mandala.json").then(r => r.json()).then(j => j.padas).catch(() => { cache = null; return null; });
  return cache;
}
const at = (P, lon) => P ? { ...P[Math.floor(norm(lon) / (10 / 3)) % 108], idx: Math.floor(norm(lon) / (10 / 3)) % 108 } : null;
const minor = c => c ? `${c.minor} · ${c.minorInner}` : "";
const trump = c => c ? `${c.trump} · ${c.trumpInner}` : "";
window.WyrdTarot = { load, at, minor, trump };
})();
