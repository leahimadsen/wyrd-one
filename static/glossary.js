'use strict';
/* ============================================================
   THE GLOSSARY
   One plain definition per term: what the thing IS, never what it
   means for a particular chart (that is the reading's work).
   Edit the wording freely. Anywhere on the site,
     Wyrd.gloss("pada")            -> the term, tappable
     Wyrd.gloss("pada", "Pada")    -> custom label
   opens a small card with the definition.
   ============================================================ */
(() => {
const G = {
  /* the two zodiacs */
  sidereal: ["Sidereal zodiac", "The zodiac measured against the fixed stars. It is the zodiac of Jyotish (Vedic astrology), and the one this console reads signs, houses, mansions and runes from."],
  tropical: ["Tropical zodiac", "The zodiac measured from the spring equinox, used by most Western astrology. It slowly drifts from the stars; today it sits about 24° ahead of the sidereal zodiac. The 64 gates run on this wheel."],
  ayanamsa: ["Ayanamsa", "The gap between the tropical and sidereal zodiacs, about 24° today and growing by roughly a degree every 72 years. This console uses the Lahiri ayanamsa."],
  sign: ["Sign", "One of the twelve 30° divisions of the zodiac, from Aries to Pisces. A planet's sign is the first thing any chart tells you about it."],
  /* the frame */
  house: ["House", "One of twelve areas of life the chart is divided into, counted from the rising sign. Here the houses are whole signs: the rising sign is the 1st house, the next sign the 2nd, and so on."],
  wholesign: ["Whole-sign houses", "The oldest way to divide the houses: each house is one complete sign, starting with the rising sign. Simple, and unaffected by latitude."],
  placidus: ["Placidus houses", "The house system most Western software uses. It divides the sky by time, so houses come out unequal in size, and it breaks down near the poles. Shown here for comparison."],
  asc: ["Ascendant (rising sign)", "The degree of the zodiac rising on the eastern horizon at the moment of birth. It sets the 1st house, so it depends on an accurate birth time; it moves about one degree every four minutes."],
  mc: ["Midheaven (MC)", "The highest point of the zodiac overhead at birth, due south. Its opposite, below the horizon, is the IC."],
  dsc: ["Descendant (DSC)", "The point setting on the western horizon at birth, exactly opposite the ascendant."],
  ic: ["IC", "The lowest point of the zodiac, directly below the birthplace, opposite the midheaven."],
  angles: ["The angles", "The ascendant, descendant, midheaven and IC: the four points where the horizon and the meridian cross the zodiac. All four need a birth time."],
  /* the bodies */
  graha: ["Graha (planet)", "The bodies the chart tracks: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, the two lunar nodes, and the three outer planets. Graha means 'that which seizes'."],
  nodes: ["Rahu and Ketu", "The two points where the Moon's path crosses the Sun's. Rahu is the north node, Ketu the south; they always sit exactly opposite each other. They are where eclipses happen."],
  retro: ["Retrograde (℞)", "A planet that appears, from Earth, to be moving backwards through the zodiac. It is an optical effect of the two orbits; every planet except the Sun and Moon does it regularly."],
  dignity: ["Dignity", "How comfortable a planet is in the sign it occupies, by the classical rules: its own sign, its sign of exaltation (strongest), its sign of debilitation (weakest), or neutral ground."],
  exalted: ["Exalted", "The sign where a planet is classically at its strongest. Each planet has one, and its debilitation is the opposite sign."],
  debilitated: ["Debilitated", "The sign where a planet is classically at its weakest, opposite its exaltation."],
  ownsign: ["Own sign", "A sign the planet rules. The Sun and Moon rule one sign each; the other five classical planets rule two."],
  tarot: ["Cards", "The Völva's mandala reads the tarot's 36 decans on both rings. The Buddhist deck (Double Vajras, Jewels, Vajras, Lotuses) runs on the sidereal ring, where a planet's influence comes from; the Nordic deck (Wands, Shields, Swords, Cups) runs on the tropical ring, where it is received. So each planet has two cards: one for its sidereal place, one for its tropical place. The Fool stands at the gate, 0° sidereal Aries."],
  moolatrikona: ["Root sign", "A stretch of a planet's own sign where it works most purely as itself (in Sanskrit, moolatrikona). Between exalted and own sign in strength."],
  karaka: ["Karakas", "In Jyotish, the seven classical planets ranked by how far each has travelled through its sign. The furthest is the atmakaraka, the significator of the self; the rest follow in order. Jyotish ranks them in the sidereal signs; ranked in the tropical signs instead, the order can change, so the console shows both."],
  atmakaraka: ["Atmakaraka", "The planet furthest through its sign. In Jyotish it is the significator of the soul."],
  /* the mansions */
  nakshatra: ["Mansion (nakshatra)", "One of twenty-seven 13°20′ divisions of the sidereal zodiac, older than the signs. The Moon spends about a day in each. Each has a ruling planet and a deity."],
  pada: ["Pada", "A quarter of a mansion, 3°20′ wide. There are 108 padas in the zodiac."],
  navamsa: ["Navamsa (D9)", "The ninth-harmonic chart: each sign is split into nine parts and each part is mapped to a sign. Jyotish reads it alongside the birth chart, especially for the strength of each planet."],
  moonmansion: ["The Moon's mansion", "The mansion the Moon stood in at birth. Jyotish treats it as one of the most personal points in the chart, and it sets the Vimshottari clock."],
  /* the runes */
  rune: ["Runes", "The twenty-four runes of the Elder Futhark, seated two to a house in the console's order: the first rune of a house opens its first 15°, the second closes it. A rune is lit when a planet stands in it."],
  ingress: ["Opening rune", "The first rune of a house, covering its first 15°: the way into that house."],
  egress: ["Closing rune", "The second rune of a house, covering its last 15°: the way out of it."],
  /* the gates and the rave */
  gate: ["Gate", "One of sixty-four 5°37′ divisions of the tropical zodiac, each matched to a hexagram of the I Ching. A planet activates the gate it stands in."],
  line: ["Line", "Each gate is divided into six lines, about 56′ each. A position is written gate.line, so 41.3 is gate 41, line 3."],
  personality: ["Birth (personality)", "The planets at the moment of birth. In the rave, these are the conscious side, drawn in ivory on the wheel."],
  design: ["Design", "The planets at the moment the Sun stood exactly 88° earlier than at birth, about three months before. In your Birth Design these are the unconscious side, drawn in teal."],
  profile: ["Profile", "Two numbers: the line of the birth Sun and the line of the design Sun. There are twelve possible profiles."],
  type: ["Type", "One of five kinds of design, worked out from which centres are defined and how they connect: Generator, Manifesting Generator, Manifestor, Projector or Reflector."],
  strategy: ["How it engages", "How each type's energy naturally meets the world: a description of the current, not a rule."],
  authority: ["Authority", "Where clarity forms in the body, in the Human Design tradition. It follows from the centres: emotional first, then sacral, splenic, and so on."],
  definition: ["Definition", "Whether the defined centres form one connected whole (single), two separate groups (split), three, or four."],
  centre: ["Centres", "The nine hubs of the design: Head, Ajna, Throat, G, Heart, Spleen, Solar plexus, Sacral and Root. A centre is defined when a complete channel runs into it."],
  channel: ["Channel", "A link between two gates in two different centres. When both of its gates are activated, by birth or design, the channel is complete and both centres are defined."],
  cross: ["Cross gates", "The gates of the four Suns and Earths: birth Sun / birth Earth | design Sun / design Earth. Together they name a person's incarnation cross."],
  /* the Dharma Weave */
  dharmaweave: ["Dharma Design", "A second design made from the same two moments as the Birth Design, with every sidereal position passed through the navamsa (multiplied by nine). It is the chart of what the life ripens into. The Dharma Weave is the method that makes it."],
  pentagram: ["Pentagram Cross", "The two dharma Suns always sit exactly 72° apart, one fifth of the wheel, because the 88° between birth and design multiplied by nine is 792°, which is two circles and 72°."],
  dharmaprofile: ["Dharma profile", "The line of the dharma Sun and the line of the dharma design Sun, written like the Birth Design profile."],
  band: ["Seam and echo", "The two bands of the dharma Sun's line. If the Sun is in the last 11.25′ of its line it is an echo; anywhere earlier it is the seam."],
  magenta: ["The magenta point", "The dharma profile 6/1: the exact centre of the band of pairings that cannot occur at birth."],
  /* Sukuyō */
  sukuyo: ["Sukuyō (宿曜)", "The Japanese school of the twenty-seven lunar mansions, brought from India through China by the monk Kūkai in the ninth century. It reads relationships by how far apart two people's mansions lie."],
  shuku: ["Shuku (宿)", "One of Sukuyō's twenty-seven mansions. A person's birth shuku comes from the day of the old Japanese lunar calendar they were born on, so it can differ from the mansion their Moon was measured in."],
  sanku: ["Sanku (三九の秘法)", "Sukuyō's method of reading two people: count from one shuku to the other. The twenty-seven positions fall into three rounds of nine, and every position has a name: Life, Karma and Womb, and the pairs Prosperity–Intimacy, Friendship–Decline, Peace–Destruction and Danger–Completion."],
  distance: ["Near, middle and far", "In Sukuyō, how many shuku apart two people lie within their relation. Near bonds are felt most strongly and most quickly; far ones work slowly and quietly."],
  /* aspects */
  aspect: ["Aspect", "An angle between two planets that astrology treats as meaningful: conjunction (0°), sextile (60°), square (90°), trine (120°) and opposition (180°)."],
  orb: ["Orb", "How far an aspect is from exact. A trine with a 2° orb means the planets are 118° or 122° apart."],
  /* time */
  vimshottari: ["Vimshottari dasha", "The main timing system of Jyotish: a 120-year cycle of nine planetary periods, set at birth by the Moon's mansion."],
  mahadasha: ["Mahadasha", "A major period of the Vimshottari clock, between 6 and 20 years long, ruled by one planet."],
  antardasha: ["Antardasha", "A chapter inside a major period, ruled by one planet in the same fixed order."],
  pratyantar: ["Pratyantardasha", "A passage inside a chapter: the third level of the clock, from days to months long."],
  transit: ["Transit", "Where a planet is now, compared with where the planets stood at birth. A transit 'hits' a birth planet when it reaches it or an exact aspect to it."],
  sadesati: ["Sade Sati", "The roughly seven and a half years Saturn takes to cross the sign before the birth Moon, the Moon's sign, and the sign after."],
  station: ["Station", "The day a planet appears to stop before turning retrograde or direct. Stations are when a planet moves slowest and is easiest to feel."],
  ingressT: ["Ingress", "The moment a planet enters a new sign."],
  /* the birth day */
  panchanga: ["Panchanga", "The 'five limbs' of the Vedic day: the weekday (vara), the lunar day (tithi), the Moon's mansion, the yoga and the karana. Every Vedic calendar is built from them."],
  tithi: ["Tithi", "A lunar day: each 12° the Moon gains on the Sun. There are thirty in a lunar month, fifteen waxing (Shukla) and fifteen waning (Krishna)."],
  yoga: ["Yoga (panchanga)", "One of twenty-seven divisions of the combined longitudes of the Sun and Moon. Not the practice; a measure of the day."],
  karana: ["Karana", "Half a tithi. There are eleven karanas; seven repeat through the month and four occur once."],
  vara: ["Vara", "The weekday, each ruled by a planet: Sunday by the Sun, Monday by the Moon, and so on. The Vedic day begins at sunrise."],
  /* the console's own lands */
  station7: ["The seven stations", "The harmonic body's seven points from crown to root, each fed by one planet. Tap a station to wake it."],
  armillary: ["Armillary", "A model of the sky built from rings. Here each ring is a different frame of the chart: the two zodiacs, the gates, the runes and the mansions, tilted apart so you can see how they sit against each other."],
  synastry: ["Synastry", "Comparing two charts by laying one over the other: where one person's planets fall in the other's houses, and the aspects and channels between them."],
};

let pop = null, opener = null;
function close(){ if (pop){ pop.remove(); pop = null; } if (opener){ opener.setAttribute("aria-expanded", "false"); opener = null; } }
function open(btn){
  const key = btn.dataset.gl, e = G[key]; if (!e) return;
  if (opener !== btn && window.Wyrd && Wyrd.pulse) Wyrd.pulse("gloss", key);
  if (opener === btn){ close(); return; }
  close(); opener = btn; btn.setAttribute("aria-expanded", "true");
  pop = document.createElement("div");
  pop.className = "gl-pop"; pop.setAttribute("role", "dialog"); pop.setAttribute("aria-label", e[0]);
  pop.innerHTML = `<b>${e[0]}</b><p>${e[1]}</p><button type="button" class="gl-x" aria-label="Close">×</button>`;
  document.body.appendChild(pop);
  const r = btn.getBoundingClientRect(), w = Math.min(320, innerWidth - 24);
  pop.style.width = w + "px";
  pop.style.left = Math.max(12, Math.min(innerWidth - w - 12, r.left + r.width / 2 - w / 2)) + scrollX + "px";
  const below = r.bottom + 8 + pop.offsetHeight < innerHeight;
  pop.style.top = (below ? r.bottom + 8 : r.top - 8 - pop.offsetHeight) + scrollY + "px";
  pop.querySelector(".gl-x").focus({ preventScroll: true });
}
document.addEventListener("click", e => {
  const b = e.target.closest("[data-gl]");
  if (b){ e.preventDefault(); e.stopPropagation(); open(b); return; }
  if (pop && (!pop.contains(e.target) || e.target.closest(".gl-x"))){ const o = opener; close(); if (e.target.closest(".gl-x") && o) o.focus(); }
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && pop){ const o = opener; close(); if (o) o.focus(); } });
addEventListener("resize", close);

const gloss = (key, label) => G[key]
  ? `<button type="button" class="gl" data-gl="${key}" aria-expanded="false">${label || G[key][0]}<span class="gl-i" aria-hidden="true">i</span></button>`
  : (label || key);
/* a row of term chips: "Terms on this page" */
const terms = keys => `<div class="gl-row"><span>Terms here:</span>${keys.map(k => gloss(k)).join("")}</div>`;
/* the whole glossary, for the end of the learning path */
const all = () => `<dl class="gl-all">${Object.entries(G).map(([k, [t, d]]) => `<div id="gl-${k}"><dt>${t}</dt><dd>${d}</dd></div>`).join("")}</dl>`;

window.Wyrd = Object.assign(window.Wyrd || {}, { gloss, glossTerms: terms, glossAll: all, GLOSSARY: G });
})();
