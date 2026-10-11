'use strict';
/* The body map on the free chart. Every map the console reads (sign, house, mansion,
   bodygraph centre, tropical sign) is laid onto the Planetary Ladder's seven stations,
   crown to root, so they can be read together. The tables are a copy of
   lib/medical.json's; grid() is the same as grid() in wyrd/medical.py, and
   tests/medical_check.py keeps both equal. What it means is in the reading. */
(() => {
const D = {"SIGN": {"Aries": "the head", "Taurus": "the throat", "Gemini": "the shoulders and arms", "Cancer": "the chest and stomach", "Leo": "the heart and back", "Virgo": "the belly", "Libra": "the kidneys and lower back", "Scorpio": "the pelvis", "Sagittarius": "the hips and thighs", "Capricorn": "the knees and bones", "Aquarius": "the calves and ankles", "Pisces": "the feet"}, "NAK": ["the knees", "the head", "the hips", "the shins", "the eyes", "the hair", "the fingers", "the mouth", "the nails", "the nose", "the sexual organs", "the sexual organs", "the hands", "the forehead", "the teeth", "the arms", "the chest", "the neck", "the feet", "the thighs", "the thighs", "the ears", "the back", "the jaw", "the sides", "the sides", "the belly"], "NAK_ZONE": ["root", "crown", "sacrum", "root", "brow", "crown", "heart", "throat", "heart", "brow", "sacrum", "sacrum", "heart", "brow", "throat", "heart", "heart", "throat", "root", "root", "root", "brow", "heart", "throat", "solar", "solar", "solar"], "ZONES": [{"key": "crown", "name": "The crown", "parts": "the top of the head, the skull and the brain", "signs": ["Aries"], "centre": ["Head"]}, {"key": "brow", "name": "The brow", "parts": "the face, eyes, ears and nose", "signs": ["Aries"], "centre": ["Ajna"]}, {"key": "throat", "name": "The throat", "parts": "the neck, mouth, jaw, teeth and voice", "signs": ["Taurus"], "centre": ["Throat"]}, {"key": "heart", "name": "The heart", "parts": "the chest, heart, lungs, arms, hands and upper back", "signs": ["Gemini", "Cancer", "Leo"], "centre": ["G", "Heart"]}, {"key": "solar", "name": "The solar plexus", "parts": "the stomach, belly, liver and digestion", "signs": ["Cancer", "Virgo"], "centre": ["Solar", "Spleen"]}, {"key": "sacrum", "name": "The sacrum", "parts": "the pelvis, hips, lower back, kidneys and reproductive organs", "signs": ["Libra", "Scorpio", "Sagittarius"], "centre": ["Sacral"]}, {"key": "root", "name": "The root", "parts": "the thighs, legs, knees, ankles, feet and bones", "signs": ["Sagittarius", "Capricorn", "Aquarius", "Pisces"], "centre": ["Root"]}]};
const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
const NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const norm = x => ((x % 360) + 360) % 360, si = l => Math.floor(norm(l) / 30);
const zonesOfSign = s => D.ZONES.filter(z => z.signs.includes(s)).map(z => z.key);
/* For each station, which planets land there by each map; AC is the rising sign. */
function grid(C, defined, unknown){
  const g = {}; for (const z of D.ZONES) g[z.key] = { sign: [], house: [], mansion: [], trop: [], centre: z.centre.map(c => [c, defined.includes(c)]) };
  const put = (col, zs, b) => zs.forEach(k => g[k][col].push(b));
  if (!unknown) put("sign", zonesOfSign(SIGNS[si(C.ascS)]), "AC");
  for (const b of NINE) {
    const l = C.sid[b];
    put("sign", zonesOfSign(SIGNS[si(l)]), b);
    if (!unknown) put("house", zonesOfSign(SIGNS[(si(l) - si(C.ascS) + 12) % 12]), b);
    put("mansion", [D.NAK_ZONE[Math.floor(norm(l) / (360 / 27)) % 27]], b);
    put("trop", zonesOfSign(SIGNS[si(C.trop[b])]), b);
  }
  return g;
}
window.WyrdMedical = Object.assign({ grid, NINE }, D);
})();
