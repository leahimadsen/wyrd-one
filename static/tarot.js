'use strict';
/* ============================================================
   THE MANDALA'S CARDS
   The Völva's mandala (static/mandala.json, made from
   lib/wyrd-mandala-108.csv by scripts/mandala.py). One rule, the 36
   decans, read on two rings:
   - the Buddhist deck on the sidereal ring, where the wheel emanates;
   - the Nordic deck on the true tropical ring, where it is received.
   So a planet has two cards: its sidereal decan's, and its tropical
   decan's. The Fool stands at the gate, 0° sidereal Aries.
   - WyrdTarot.load(): Promise of the mandala
   - WyrdTarot.at(M, sid, trop): { buddhist, nordic, void, idx }
   - WyrdTarot.buddhist(c), .nordic(c): "2 of Double Vajras · The King"
   - WyrdTarot.minor(c): "2 of Double Vajras · 4 of Wands"
   ============================================================ */
(() => {
let cache = null;
const norm = d => ((d % 360) + 360) % 360;
function load(){
  if (!cache) cache = fetch("/static/mandala.json").then(r => r.json()).then(j => j.decans ? j : null).catch(() => { cache = null; return null; });
  return cache;
}
function at(M, sid, trop){
  if (!M) return null;
  const idx = Math.floor(norm(sid) / (10 / 3)) % 108, b = M.decans[Math.floor(norm(sid) / 10) % 36], n = M.decans[Math.floor(norm(trop) / 10) % 36];
  return { idx, void: M.padas[idx].void,
    buddhist: { minor: b.buddhist.minor, trump: b.buddhist.trump, ruler: b.ruler, sign: b.sign },
    nordic: { minor: n.nordic.minor, trump: n.nordic.trump, ruler: n.ruler, sign: n.sign } };
}
const buddhist = c => c ? `${c.buddhist.minor} · ${c.buddhist.trump}` : "";
const nordic = c => c ? `${c.nordic.minor} · ${c.nordic.trump}` : "";
const minor = c => c ? `${c.buddhist.minor} · ${c.nordic.minor}` : "";
window.WyrdTarot = { load, at, buddhist, nordic, minor, gate: M => M && M.gate };
})();
