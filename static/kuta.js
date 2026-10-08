'use strict';
/* ============================================================
   KUTA
   Ashtakoota, the eight-fold Jyotish match (36 points), from the two Moons.
   Tradition reads it in a fixed order, one partner first; Varna, Vashya and
   Gana change with the order. The console reads it both ways and shows both,
   so no one has to be cast as "bride" or "groom".
   ============================================================ */
(() => {
const { norm } = Wyrd.helpers;
const NAK = 360 / 27;

const VARNA = s => [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4][s];           // 4 Brahmin … 1 Shudra, by Moon sign
const VASHYA = { 0: [4, 7], 1: [3, 6], 2: [5], 3: [7, 8], 4: [6], 5: [11, 2], 6: [5, 9], 7: [3], 8: [11], 9: [0, 10], 10: [0], 11: [9] };
const YONI_OF = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1];
const YONI = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"];
const YONI_SCORE = [
  [4,2,2,3,2,2,2,1,0,1,3,3,2,1],[2,4,3,3,2,2,2,2,3,1,2,3,2,0],[2,3,4,2,1,2,1,3,3,1,2,0,3,1],[3,3,2,4,2,1,1,1,1,2,2,2,0,2],
  [2,2,1,2,4,2,1,2,2,1,0,2,1,1],[2,2,2,1,2,4,0,2,2,1,3,3,2,1],[2,2,1,1,1,0,4,2,2,2,2,2,1,2],[1,2,3,1,2,2,2,4,3,0,3,2,2,1],
  [0,3,3,1,2,2,2,3,4,1,2,2,2,1],[1,1,1,2,1,1,2,0,1,4,1,1,2,1],[3,2,2,2,0,3,2,3,2,1,4,2,2,1],[3,3,0,2,2,3,2,2,2,1,2,4,3,2],
  [2,2,3,0,1,2,1,2,2,2,2,3,4,2],[1,0,1,2,1,1,2,1,1,1,1,2,2,4]];
const LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"];
const FRIENDS = { Sun: ["Moon", "Mars", "Jupiter"], Moon: ["Sun", "Mercury"], Mars: ["Sun", "Moon", "Jupiter"], Mercury: ["Sun", "Venus"],
  Jupiter: ["Sun", "Moon", "Mars"], Venus: ["Mercury", "Saturn"], Saturn: ["Mercury", "Venus"] };
const ENEMIES = { Sun: ["Venus", "Saturn"], Moon: [], Mars: ["Mercury"], Mercury: ["Moon"], Jupiter: ["Mercury", "Venus"], Venus: ["Sun", "Moon"], Saturn: ["Sun", "Moon", "Mars"] };
const GANA = ["Deva","Manushya","Rakshasa","Manushya","Deva","Manushya","Deva","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Rakshasa","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva"];
const GANA_SCORE = { Deva: { Deva: 6, Manushya: 6, Rakshasa: 1 }, Manushya: { Deva: 5, Manushya: 6, Rakshasa: 0 }, Rakshasa: { Deva: 1, Manushya: 0, Rakshasa: 6 } };
const NADI = ["Adi", "Madhya", "Antya"];
const NADI_OF = n => [0, 1, 2, 2, 1, 0][n % 6];

/* what each kuta weighs: drafts for The Völva to edit */
const ABOUT = {
  Varna: "temperament and spiritual footing: whether one can look up to the other",
  Vashya: "magnetism: who draws whom, and whether the pull is mutual",
  Tara: "the stars' goodwill: whether each birth star is kind to the other",
  Yoni: "instinct and intimacy, read through the animal of each birth star",
  "Graha Maitri": "the friendship of the two Moon-sign lords: how your minds get on",
  Gana: "nature: divine, human or fierce, and whether the two natures can live together",
  Bhakoot: "the distance between your Moon signs: love, money and the life you build",
  Nadi: "the pulse of the body: whether your constitutions balance or crowd each other",
};
const MAX = { Varna: 1, Vashya: 2, Tara: 3, Yoni: 4, "Graha Maitri": 5, Gana: 6, Bhakoot: 7, Nadi: 8 };

function relate(a, b){ return FRIENDS[a].includes(b) ? "friend" : ENEMIES[a].includes(b) ? "enemy" : "neutral"; }
function maitri(la, lb){
  if (la === lb) return 5;
  const x = [relate(la, lb), relate(lb, la)].sort().join("+");
  return { "friend+friend": 5, "friend+neutral": 4, "neutral+neutral": 3, "enemy+friend": 1, "enemy+neutral": .5, "enemy+enemy": 0 }[x];
}
function vashya(sa, sb){
  if (sa === sb) return 2;
  const ab = (VASHYA[sa] || []).includes(sb), ba = (VASHYA[sb] || []).includes(sa);
  return ab && ba ? 2 : ab || ba ? 1 : 0;
}
const taraOK = (from, to) => ![3, 5, 7].includes(((to - from + 27) % 27 + 1) % 9);

/* one reading, first person in the first position */
function read(ma, mb){
  const sa = Math.floor(norm(ma) / 30), sb = Math.floor(norm(mb) / 30), na = Math.floor(norm(ma) / NAK), nb = Math.floor(norm(mb) / NAK);
  const d = (sb - sa + 12) % 12 + 1, bh = [[2, 12], [12, 2], [5, 9], [9, 5], [6, 8], [8, 6]].some(([x, y]) => d === x);
  const rows = {
    Varna: VARNA(sa) >= VARNA(sb) ? 1 : 0,
    Vashya: vashya(sa, sb),
    Tara: (taraOK(nb, na) ? 1.5 : 0) + (taraOK(na, nb) ? 1.5 : 0),
    Yoni: YONI_SCORE[YONI_OF[na]][YONI_OF[nb]],
    "Graha Maitri": maitri(LORD[sa], LORD[sb]),
    Gana: GANA_SCORE[GANA[na]][GANA[nb]],
    Bhakoot: bh ? 0 : 7,
    Nadi: NADI_OF(na) === NADI_OF(nb) ? 0 : 8,
  };
  const facts = {
    Varna: `${["", "Shudra", "Vaishya", "Kshatriya", "Brahmin"][VARNA(sa)]} · ${["", "Shudra", "Vaishya", "Kshatriya", "Brahmin"][VARNA(sb)]}`,
    Vashya: "by Moon sign", Tara: "counted both ways between your birth stars",
    Yoni: `${YONI[YONI_OF[na]]} · ${YONI[YONI_OF[nb]]}`, "Graha Maitri": `${LORD[sa]} · ${LORD[sb]}`,
    Gana: `${GANA[na]} · ${GANA[nb]}`, Bhakoot: `Moon signs ${d} and ${(14 - d) % 12 || 12} apart`,
    Nadi: `${NADI[NADI_OF(na)]} · ${NADI[NADI_OF(nb)]}`,
  };
  return { rows, facts, total: Object.values(rows).reduce((a, b) => a + b, 0) };
}

function verdict(t){
  return t >= 28 ? "a strong match by the old count" : t >= 18 ? "a workable match by the old count" : "a demanding match by the old count: the bond asks for conscious work";
}

function html(A, B){
  const { esc } = WyrdCommon;
  const ab = read(A.C.sid.Moon, B.C.sid.Moon), ba = read(B.C.sid.Moon, A.C.sid.Moon);
  const same = ab.total === ba.total;
  const rows = Object.keys(MAX).map(k => `<tr><td><b>${k}</b><br><span class="fine">${ABOUT[k]}</span></td><td class="kt-f">${ab.facts[k]}</td>
    <td class="kt-n">${ab.rows[k]} / ${MAX[k]}</td>${same ? "" : `<td class="kt-n">${ba.rows[k]} / ${MAX[k]}</td>`}</tr>`).join("");
  const nadi = ab.rows.Nadi === 0, bhak = ab.rows.Bhakoot === 0;
  return `<p>Jyotish matches two people by their Moons: the sign and the birth star each was born under. Eight measures, called kutas, add up to 36 points.
    Tradition reads the match in a fixed order, one partner first. Three of the measures change with that order, so the console reads it both ways.</p>
    <div class="kt-score"><span class="kt-big">${ab.total}</span><span>/ 36</span>${same ? "" : `<span class="kt-or">read from ${esc(A.name)}</span><span class="kt-big">${ba.total}</span><span>/ 36</span><span class="kt-or">read from ${esc(B.name)}</span>`}</div>
    <p>${Math.max(ab.total, ba.total) >= 18 ? "This is" : "Read either way, this is"} ${verdict(Math.max(ab.total, ba.total))}.
    ${nadi ? " You share a Nadi, which the tradition treats as the most serious single mismatch: the two bodies run on the same pulse." : ""}
    ${bhak ? " Your Moon signs fall in one of the testing distances (2–12, 5–9 or 6–8), which the tradition weighs for money and family life." : ""}
    A score is a starting point, not a verdict: the Sukuyō bond, the aspects between your planets and how you complete each other's channels all count too.</p>
    <div class="rd-tw"><table class="kt"><tr><th>Kuta</th><th>${esc(A.name)} · ${esc(B.name)}</th><th>${same ? "Points" : `From ${esc(A.name)}`}</th>${same ? "" : `<th>From ${esc(B.name)}</th>`}</tr>${rows}</table></div>`;
}

window.WyrdKuta = { read, html, MAX, YONI_SCORE };
})();
