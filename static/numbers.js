'use strict';
/* ============================================================
   NUMBERS: a person's numbers, from the birth date and the full birth name.
   The same sums as wyrd/numbers.py (tests/numbers_check.py keeps them in
   step). The free chart shows the numbers and their planets; what they mean
   is in the paid reading.
   ============================================================ */
(() => {
const MASTERS = [11, 22, 33];
const STAVEFALL = { 1: ["Sun", "Crown"], 2: ["Moon", "Brow"], 3: ["Saturn", "Throat"], 4: ["Jupiter", "Heart"], 5: ["Mars", "Solar plexus"],
  6: ["Venus", "Sacrum"], 7: ["Mercury", "Root"], 8: ["Rahu", "The pole above"], 9: ["Ketu", "The pole below"] };
const VEDIC = { 1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars" };
const LABEL = { life_path: "Life path", birthday: "Birthday", personal_year: "Personal year", expression: "Expression", soul_urge: "Soul urge", personality: "Personality" };
const KINDS = Object.keys(LABEL);

const digits = n => String(n).split("").reduce((s, c) => s + +c, 0);
const reduce = (n, masters = true) => { while (n > 9 && !(masters && MASTERS.includes(n))) n = digits(n); return n; };
const root = n => reduce(n, false);
const letters = name => (name || "").normalize("NFKD").replace(/[^\x00-\x7f]/g, "").toUpperCase().replace(/[^A-Z]+/g, " ").trim().split(" ").filter(Boolean);
const value = c => (c.charCodeAt(0) - 65) % 9 + 1;
const vowels = w => { const v = [...w].filter(c => "AEIOU".includes(c)); return v.length ? v : [...w].filter(c => c === "Y"); };

function nameNumbers(name){
  const words = letters(name); if (!words.length) return {};
  const total = pick => reduce(words.reduce((s, w) => s + reduce(pick(w).reduce((t, c) => t + value(c), 0)), 0));
  const con = w => { const v = vowels(w); return [...w].filter(c => !v.includes(c)); };
  return { expression: total(w => [...w]), soul_urge: total(vowels), personality: total(con) };
}
function of(date, fullName, year){
  const [y, m, d] = date.split("-").map(Number);
  const out = { life_path: reduce(reduce(m) + reduce(d) + reduce(digits(y))), birthday: reduce(d) };
  if (year) out.personal_year = reduce(reduce(m) + reduce(d) + reduce(digits(year)));
  return Object.assign(out, nameNumbers(fullName));
}
const planets = n => { const r = root(n); return { stavefall: STAVEFALL[r][0], station: STAVEFALL[r][1], vedic: VEDIC[r], root: r }; };

window.WyrdNumbers = { of, planets, LABEL, KINDS };
})();
