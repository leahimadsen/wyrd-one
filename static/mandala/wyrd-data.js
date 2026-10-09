/* ============================================================
   WYRD DATA
   The Wyrd Mandala's cosmological record, kept apart from the
   geometry, presentation and interaction (wyrd-mandala.js).

   What is here:
   - SIGNS, NAKSHATRAS: the source tables (sidereal frame)
   - buildStations(): the 108 pada stations, derived from the tables
   - RECORDS: station-specific data supplied by The Völva (tarot,
     correspondences, notes). Anything not supplied stays unassigned.
   - LAYERS: the rings the instrument can show, and slots for the
     layers still to come
   - RELATIONS: generators for Focus Mode lines. Only relations that
     follow from the arithmetic of the tables; nothing asserted.
   - PROVENANCE: the levels a correspondence can carry

   To add a system: put its data in RECORDS[n].correspondences (or a
   generator below), register a layer, and the instrument shows it.
   ============================================================ */
(function (root) {
  "use strict";

  const FRAME = {
    zodiac: "sidereal",
    ayanamsa: { name: "Lahiri", epoch: 2026, degrees: 24 + 13.5 / 60 },   // ≈ 24°13′–24°14′; shown as a projection only
    origin: "0° sidereal Aries (Ashwini, pada 1)",
  };

  /* ---------- source tables ---------- */
  const SIGNS = [
    ["Aries", "♈", "Mars"], ["Taurus", "♉", "Venus"], ["Gemini", "♊", "Mercury"], ["Cancer", "♋", "Moon"],
    ["Leo", "♌", "Sun"], ["Virgo", "♍", "Mercury"], ["Libra", "♎", "Venus"], ["Scorpio", "♏", "Mars"],
    ["Sagittarius", "♐", "Jupiter"], ["Capricorn", "♑", "Saturn"], ["Aquarius", "♒", "Saturn"], ["Pisces", "♓", "Jupiter"],
  ].map(([name, glyph, ruler], i) => ({ index: i, name, glyph: glyph + "︎", ruler, start: i * 30, end: i * 30 + 30,
    modality: ["movable", "fixed", "dual"][i % 3] }));

  /* name, short label for the ring, ruler (Vimshottari order), deity (standard Jyotish attribution), variant where traditions differ */
  const NAKSHATRAS = [
    ["Ashwini", "Ashwini", "Ketu", "the Ashvins"],
    ["Bharani", "Bharani", "Venus", "Yama"],
    ["Krittika", "Krittika", "Sun", "Agni"],
    ["Rohini", "Rohini", "Moon", "Prajapati", "Brahma"],
    ["Mrigashira", "Mrigashira", "Mars", "Soma"],
    ["Ardra", "Ardra", "Rahu", "Rudra"],
    ["Punarvasu", "Punarvasu", "Jupiter", "Aditi"],
    ["Pushya", "Pushya", "Saturn", "Brihaspati"],
    ["Ashlesha", "Ashlesha", "Mercury", "the Sarpas (Nagas)"],
    ["Magha", "Magha", "Ketu", "the Pitrs"],
    ["Purva Phalguni", "P. Phalguni", "Venus", "Bhaga", "Aryaman"],
    ["Uttara Phalguni", "U. Phalguni", "Sun", "Aryaman", "Bhaga"],
    ["Hasta", "Hasta", "Moon", "Savitr"],
    ["Chitra", "Chitra", "Mars", "Tvashtr", "Vishvakarma"],
    ["Swati", "Swati", "Rahu", "Vayu"],
    ["Vishakha", "Vishakha", "Jupiter", "Indra-Agni"],
    ["Anuradha", "Anuradha", "Saturn", "Mitra"],
    ["Jyeshtha", "Jyeshtha", "Mercury", "Indra"],
    ["Mula", "Mula", "Ketu", "Nirriti"],
    ["Purva Ashadha", "P. Ashadha", "Venus", "Apas"],
    ["Uttara Ashadha", "U. Ashadha", "Sun", "the Vishvedevas"],
    ["Shravana", "Shravana", "Moon", "Vishnu"],
    ["Dhanishta", "Dhanishta", "Mars", "the Vasus"],
    ["Shatabhisha", "Shatabhisha", "Rahu", "Varuna"],
    ["Purva Bhadrapada", "P. Bhadrapada", "Jupiter", "Aja Ekapada"],
    ["Uttara Bhadrapada", "U. Bhadrapada", "Saturn", "Ahirbudhnya"],
    ["Revati", "Revati", "Mercury", "Pushan"],
  ].map(([name, short, ruler, deity, deityAlt], i) => ({ index: i, number: i + 1, name, short, ruler, deity, deityAlt: deityAlt || null,
    start: i * 40 / 3, end: (i + 1) * 40 / 3 }));

  /* ---------- the 108 stations, derived ---------- */
  const PADA = 10 / 3;
  const pad3 = n => String(n).padStart(3, "0");
  function buildStations() {
    const out = [];
    for (let i = 0; i < 108; i++) {
      const start = i * PADA, end = (i + 1) * PADA, mid = start + PADA / 2;
      const nak = NAKSHATRAS[Math.floor(i / 4)], sign = SIGNS[Math.floor(mid / 30)];
      const navamsa = SIGNS[i % 12];                                    // the ninth-harmonic sign: pada n of the wheel → sign n mod 12
      const id = i + 1, rec = RECORDS[id] || {};
      out.push({
        id, code: "S" + pad3(id),
        zodiacStart: start, zodiacEnd: end,
        sign: sign.name, signIndex: sign.index,
        nakshatra: nak.name, nakshatraIndex: nak.index, pada: (i % 4) + 1,
        nakshatraLord: nak.ruler, deity: nak.deity, deityAlt: nak.deityAlt,
        navamsa: navamsa.name, vargottama: navamsa.index === sign.index,
        straddles: Math.floor(start / 30) !== Math.floor((end - 1e-9) / 30),     // a pada never crosses a sign boundary; kept as a check
        tarot: Object.assign({ id: "T" + pad3(id), glyph: "T" + pad3(id), name: null, deck: null, description: null, status: "unassigned" }, rec.tarot || {}),
        correspondences: rec.correspondences || {},
        notes: rec.notes || "",
        source: rec.source || null,
      });
    }
    return out;
  }

  /* ---------- provenance: how a correspondence is held ---------- */
  const PROVENANCE = {
    "attested-primary": { label: "Attested · primary", rank: 1 },
    "attested-traditional": { label: "Attested · traditional", rank: 2 },
    "computed": { label: "Computed", rank: 3 },
    "structural": { label: "Structural · this system's rules", rank: 4 },
    "constructed": { label: "Constructed · awaiting ruling", rank: 5 },
    "undetermined": { label: "Undetermined", rank: 6 },
  };

  /* ---------- station records supplied by The Völva ----------
     Station 001 is the worked example, populated only from "The First Gate"
     (The Völva's text). Every other station waits for its record. */
  const RECORDS = {
    1: {
      source: "The First Gate: Opening the Wyrd Mandala at 0° Sidereal Aries (The Völva)",
      tarot: {
        status: "candidates",
        name: null,
        description: "Two candidate assignments, one per rotor. Neither is yet ruled as this station's tarot identity.",
        candidates: [
          { deck: "Buddhist deck · sidereal ring", name: "The Fool", detail: "The Great Departure: the going-forth that begins with nothing", provenance: "constructed" },
          { deck: "Nordic deck · tropical ring", name: "The Emperor · Four of Wands", detail: "Týr; Venus in Aries, third decan, at the station's tropical address", provenance: "attested-primary" },
        ],
      },
      correspondences: {
        "Two rotors": [
          { label: "Sidereal address", value: "0°00′00″ Aries", provenance: "computed" },
          { label: "Tropical address", value: "24°14′ Aries (Lahiri, 2026)", provenance: "structural" },
          { label: "Reading of the offset", value: "The ayanamsa read as distance travelled from source (sidereal, emanating) to form (tropical, receiving)", provenance: "structural" },
        ],
        "Mansion": [
          { label: "Shakti", value: "śīghra-vyāpanī: swift pervasion", provenance: "attested-traditional" },
          { label: "Pada 1", value: "Aries navamsa; vargottama, the same address in D1 and D9", provenance: "attested-primary" },
        ],
        "Shukuyō": [
          { label: "Mansion", value: "婁宿 Rōshuku · the Bond", provenance: "attested-primary" },
          { label: "Lineage", value: "Xiuyao Jing, Amoghavajra, 759 CE: a documented translation, kept as the instrument's control case", provenance: "attested-primary" },
          { label: "Star name", value: "tatara-boshi, the bellows star (logged; not argued from)", provenance: "attested-traditional" },
        ],
        "Rune": [
          { label: "Rune", value: "Fehu, on the first-house cusp of the study wheel (0° sidereal Aries rising)", provenance: "structural" },
        ],
        "Colour": [
          { label: "House colour", value: "Red, house 1 of the twelve-hue wheel", provenance: "structural" },
        ],
        "Human Design (tropical ring)": [
          { label: "Gate", value: "42, line 4 · Sacral · channel 53–42", provenance: "structural" },
          { label: "Drift", value: "into line 5 around 2045; out of Gate 42 around 2200", provenance: "computed" },
        ],
        "Sound": [
          { label: "Sidereal pitch", value: "0 cents: the tonic of the 27-fold ring", provenance: "structural" },
          { label: "Tropical pitch", value: "+80.8 cents from the equinox (64-fold ring)", provenance: "computed" },
        ],
        "Open questions": [
          { label: "Ashvins and the Medicine Kings", value: "Bhaiṣajyarāja and Bhaiṣajyasamudgata: convergence or transmission, not determined", provenance: "undetermined" },
        ],
      },
      notes: "The first gate is an opening in the sense that a valve is an opening. Something comes through it, downward and outward, and turns into a body.\n\nIt is the only point on the 108-spine where the first mansion, the first pada, the first sign and the ninth-harmonic return all resolve to the same number. Everything after this station is degrees of separation from that identity.",
    },
  };

  /* ---------- layers: what the instrument can draw ----------
     ring: inner and outer radius in the 1000-unit drawing. status: "active" layers are drawn;
     "planned" layers are reserved slots with no mapping yet. */
  const LAYERS = [
    { id: "field", label: "Inner field", status: "active", ring: [0, 178], toggle: false },
    { id: "zodiac", label: "Zodiac", status: "active", ring: [186, 246], toggle: true },
    { id: "nakshatras", label: "Nakshatras", status: "active", ring: [252, 316], toggle: true },
    { id: "padas", label: "Padas", status: "active", ring: [322, 382], toggle: true },
    { id: "tarot", label: "Tarot", status: "active", ring: [390, 452], toggle: true },
    ...["Planets", "Planetary rulership", "Tattvas", "Chakras", "Human Design", "I Ching", "Runes", "Numerology",
      "Mythological structures", "Anatomical correspondences", "Harmonic relationships"]
      .map(label => ({ id: label.toLowerCase().replace(/[^a-z]+/g, "-"), label, status: "planned", ring: null, toggle: false })),
  ];

  /* ---------- relations for Focus Mode: generated from the tables, never asserted ---------- */
  const RELATIONS = {
    navamsa: { label: "Same navamsa sign", note: "Stations whose pada falls in the same ninth-harmonic sign (every twelfth pada).",
      of: (s, all) => all.filter(t => t.id !== s.id && t.navamsa === s.navamsa) },
    ruler: { label: "Same nakshatra ruler", note: "The padas of the three mansions that share a Vimshottari ruler.",
      of: (s, all) => all.filter(t => t.id !== s.id && t.nakshatraLord === s.nakshatraLord) },
    vargottama: { label: "Vargottama set", note: "The twelve padas whose navamsa repeats their own sign.",
      of: (s, all) => all.filter(t => t.id !== s.id && t.vargottama) },
  };

  root.WYRD = { FRAME, SIGNS, NAKSHATRAS, RECORDS, LAYERS, RELATIONS, PROVENANCE, PADA, stations: buildStations() };
})(window);
