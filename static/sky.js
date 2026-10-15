/* The sky behind Odin's Eye: the real stars, the Milky Way, and figures drawn round their stars in knotwork.

   Behind everything, the real sky (J2000, from the Hipparcos compilation, sky-data.js), faint, seen as
   we see it about the north celestial pole, which this drawing sets above Asgard's crown.

   Over it, twelve figures, each a window on its own stars: within a figure the stars keep their true
   places to one another; where the figure sits round the tree, its size and its turn are composed, so
   the figures spread through the margins (SLOT). Nothing is written on the sky: tapping a figure opens
   its record in the panel.
     · Norse, in gold: names the Norse sources give these stars, marked Eddic, medieval Icelandic, or
       later folk tradition, as each is attested.
     · Greek, in ice: the classical figure, drawn in Norse ornament. Only the ornament is Norse.

   Each figure is authored in degrees about one of its stars (x west to the right, y north up). Its
   outlines become two-strand ropes of interlace, ends can close in a Norse scroll, and wherever
   ribbons cross they go over and under in turn.

   WyrdSky.prepare(R, k)            build for a sky of radius scale R (scene units), k pixels per unit
   WyrdSky.draw(ctx, pole, θ, sel)   draw the sky about the pole (turned by θ) and the figures
   WyrdSky.hit(x, y)                the figure at a scene point, or null
   WyrdSky.figure(id)               its record, for the panel                                          */
(function () {
"use strict";
const D = window.WYRD_SKY_DATA, RAD = Math.PI / 180, TAU = Math.PI * 2;
if (!D) { window.WyrdSky = null; return; }

const NORSE = "norse", GREEK = "greek";
const LOOK = {
  [NORSE]: { band: "#f8d48a", edge: "#2a1503", glow: "255,186,90" },
  [GREEK]: { band: "#d6f0ff", edge: "#071a33", glow: "130,205,255" },
};
const GREEK_NOTE = "The figure is Greek, as Ptolemy lists it; only the ornament is Norse.";

/* ---------------- the figures ----------------
   at: the star they are drawn about [RA, Dec]; s: a scale on the drawing; lines: the stars' own figure,
   drawn faint (an IAU id, or local points). Parts: c closed, o open, tw a two-strand twist, ring, eye,
   eight (a figure-of-eight), thin (a hairline), dot. */
const FIGS = [
  { id: "eyes", kind: NORSE, name: "Þjaza augu", gloss: "Þjazi's eyes", tag: "Eddic", at: [113.65, 31.89],
    stars: "Castor and Pollux",
    note: "After the giant Þjazi was killed, Odin threw his eyes up into the sky and made two stars of them (Skáldskaparmál). In Hárbarðsljóð it is Thor who says he cast them up. Neither says which stars; Castor and Pollux, two equal stars side by side, is a modern reading.",
    lines: [[0, 0, -2.3, -3.9]],
    parts: [{ eye: [0, 0, 239.5, 1.45, .62] }, { eye: [-2.3, -3.9, 239.5, 1.45, .62] }, { ring: [0, 0, .42] }, { ring: [-2.3, -3.9, .42] },
      { eight: [-1.15, -1.95, 239.5, 3.9, 1.5] }] },

  { id: "wolf", kind: NORSE, name: "Úlfs kjǫptr", gloss: "the wolf's jaw", tag: "medieval Icelandic", at: [67.15, 19.18],
    stars: "the Hyades, with Aldebaran",
    note: "A 12th-century Icelandic glossary (GKS 1812 4to) gives ulfs keptr, the wolf's jaw, for the Hyades, the V of stars that opens toward Aldebaran; a 14th-century list repeats it as vlfs kiopt. It does not say which wolf.",
    lines: [[-1.7, -2.7, 0, -3.3, 2.1, -3.6, 1.3, -1.6, 0, 0]],
    parts: [
      { c: [4.2, -1.0, 2.0, 0.0, 0.0, 0.8, -0.9, 0.1, 0.6, -1.4, 2.2, -2.9, 3.8, -2.7] },
      { c: [3.9, -3.8, 2.2, -3.5, 0.4, -3.0, -1.6, -2.4, -2.1, -3.2, -0.2, -4.2, 2.2, -4.8, 4.0, -4.6] },
      { c: [3.2, -0.6, 5.2, 0.6, 7.4, 0.1, 8.5, -2.6, 7.2, -5.1, 4.8, -5.3, 3.4, -4.4] },
      { c: [5.2, 0.0, 5.7, 2.7, 6.9, 0.5] },
      { thin: [0.6, -1.0, 0.3, -1.7, 0.95, -1.6, 0.8, -2.3, 1.5, -2.2] }, { thin: [-1.1, -2.7, -0.8, -2.1, -0.3, -2.9, 0.0, -2.3, 0.6, -3.1] },
      { dot: [5.1, -1.6] }] },

  { id: "loki", kind: NORSE, name: "Lokabrenna", gloss: "Loki's brand", tag: "later Scandinavian", at: [101.29, -16.72], s: .62,
    stars: "Sirius",
    note: "Lokabrenna, Loki's brand or Loki's burning, is a Scandinavian name for Sirius. It comes down in later tradition (Rydberg gives it in 1889) and is not in the Eddas.",
    parts: [
      { c: [-1.0, -0.2, -1.4, 1.8, -0.6, 4.0, 0.2, 6.2, 1.0, 4.0, 1.4, 1.8, 1.0, -0.2, 0.0, -0.9] },
      { c: [-0.3, 0.3, -1.8, 0.6, -2.9, 2.2, -2.6, 4.4, -1.6, 2.8, -0.6, 1.8, 0.3, 0.6] },
      { c: [0.3, 0.3, 1.8, 0.6, 2.9, 2.0, 2.7, 4.2, 1.8, 2.6, 0.6, 1.8, -0.3, 0.6] },
      { o: [-0.2, -0.6, -1.6, -3.4, -3.0, -6.4, -3.9, -8.4], curl: -1 }, { ring: [-1.0, -2.0, .85] }] },

  { id: "distaff", kind: NORSE, name: "Friggerock", gloss: "Frigg's distaff", tag: "Swedish folk", at: [84.05, -1.20], s: .82,
    stars: "Orion's belt: Alnitak, Alnilam, Mintaka",
    note: "Friggerock, Frigg's distaff, is a Swedish folk name for the three stars of Orion's belt, recorded in later folk tradition. The oldest Norse name for this part of the sky is in the 12th-century Icelandic glossary (GKS 1812 4to), which calls Orion fiskikarlar, the fishermen.",
    lines: [[-1.1, -0.7, 0, 0, 1.1, 0.9]],
    parts: [
      { o: [-7.8, -5.7, -4.4, -3.2, -1.1, -0.7, 0, 0, 1.1, 0.9, 3.6, 2.7] },
      { c: [2.6, 2.0, 5.6, 2.4, 8.6, 4.7, 10.0, 7.2, 8.0, 7.6, 5.3, 5.8, 3.0, 3.6] },
      { o: [3.6, 1.4, 4.3, 3.3, 4.0, 5.2] }, { o: [5.6, 1.9, 6.1, 4.0, 5.5, 6.6] }, { o: [7.6, 3.2, 7.9, 5.4, 7.1, 7.7] },
      { ring: [-8.3, -6.1, .95] },
      { thin: [9.6, 5.4, 11.4, 2.4, 12.3, -1.6] }, { o: [12.6, -0.9, 12.3, -3.5, 12.0, -5.8] }, { ring: [12.3, -3.1, .75] }] },

  { id: "wagon", kind: NORSE, name: "Karlavagnen", gloss: "the Wagon", tag: "Scandinavian folk", at: [183.86, 57.03],
    stars: "the seven bright stars of Ursa Major",
    note: "Karlavagnen in Swedish, Karlsvognen in Danish: the man's wagon, the folk name across Scandinavia for these seven stars. The bowl is the wagon's box, the handle its shaft.",
    lines: [[0, 0, 9.8, 4.7, 10.0, -0.7, 2.9, -3.3, 0, 0, -5.3, -1.1, -9.3, -2.1, -12.5, -7.7]],
    parts: [
      { c: [-0.9, 0.9, 4.6, 3.4, 10.5, 5.7, 10.9, 2.4, 11.1, -1.3, 7.0, -2.9, 2.9, -4.3, 0.9, -1.9] },
      { o: [0.6, -0.4, 5.4, 1.4, 10.0, 3.7] }, { o: [2.6, -2.9, 6.6, 1.4, 9.4, 4.6] },
      { ring: [9.0, -3.3, 1.7] }, { ring: [3.6, -6.0, 1.7] },
      { thin: [9.0, -1.6, 9.0, -5.0] }, { thin: [7.3, -3.3, 10.7, -3.3] }, { thin: [3.6, -4.3, 3.6, -7.7] }, { thin: [1.9, -6.0, 5.3, -6.0] },
      { o: [-0.6, -0.4, -5.3, -1.1, -9.3, -2.1, -11.4, -4.6, -12.5, -7.7] },
      { o: [-14.4, -6.4, -12.5, -7.7, -10.6, -9.0] }, { ring: [-12.9, -8.9, .9] }] },

  { id: "swan", kind: GREEK, name: "Cygnus", gloss: "the swan", tag: "Greek figure", at: [305.56, 40.26], lines: "Cyg",
    stars: "Deneb, Sadr, Albireo",
    parts: [
      { c: [-4.8, 6.6, -1.6, 4.4, 1.6, 1.7, 3.0, -1.6, 0.6, -2.9, -2.2, -1.2, -4.2, 2.6] },
      { o: [0.4, -0.4, 3.6, -3.0, 4.9, -5.2, 6.0, -7.8, 8.6, -10.0, 9.6, -11.4] },
      { c: [9.1, -11.3, 10.8, -11.5, 11.3, -12.8, 10.4, -13.7, 9.2, -13.0] }, { o: [10.9, -13.3, 12.2, -14.6, 13.2, -15.6] },
      { c: [1.0, 1.6, 4.0, 4.5, 7.1, 4.9, 9.4, 9.0, 10.0, 11.5, 12.4, 13.1, 13.6, 14.4, 14.0, 12.2, 12.4, 9.4, 10.4, 5.4, 7.4, 2.0, 3.6, 0.2] },
      { c: [2.0, 0.8, 5.2, 1.4, 9.0, 3.0, 11.6, 5.8, 12.2, 8.4, 10.0, 8.0, 7.0, 6.6, 4.0, 3.2] },
      { c: [-1.4, -0.8, -3.6, -3.6, -4.6, -6.3, -7.2, -8.2, -9.7, -10.0, -11.4, -11.0, -10.6, -8.6, -8.0, -5.4, -5.0, -2.4, -2.2, 0.4] },
      { c: [-0.6, -1.6, -2.0, -4.6, -4.2, -8.8, -6.6, -10.8, -6.2, -8.4, -4.6, -5.0, -2.4, -2.0] },
      { c: [-3.6, 4.6, -6.4, 7.0, -5.6, 8.8, -3.4, 7.6, -2.6, 5.8] }] },

  { id: "lyre", kind: GREEK, name: "Lyra", gloss: "the lyre", tag: "Greek figure", at: [279.23, 38.78], lines: "Lyr",
    stars: "Vega, Sheliak, Sulafat",
    parts: [
      { o: [-5.2, 0.5, -4.4, -1.6, -4.7, -3.8, -4.3, -6.0, -3.4, -7.3, -2.3, -6.8, -1.8, -4.6, -1.2, -2.4, -0.5, -0.6] },
      { ring: [-5.0, 0.9, .7] }, { ring: [0, 0, .8] },
      { o: [-5.3, -1.5, -3.0, -1.0, -0.6, -0.4] },
      { c: [-4.7, -5.6, -3.4, -5.1, -1.9, -5.6, -2.2, -7.1, -3.4, -7.7, -4.5, -7.0] },
      { thin: [-3.8, -1.4, -3.6, -6.4] }, { thin: [-3.0, -1.2, -2.9, -6.6] }, { thin: [-2.2, -1.0, -2.2, -6.4] }] },

  { id: "eagle", kind: GREEK, name: "Aquila", gloss: "the eagle", tag: "Greek figure", at: [297.70, 8.87], lines: "Aql",
    stars: "Altair, Tarazed, Alshain",
    parts: [
      { c: [-0.8, 1.6, 1.0, 2.3, 1.9, 0.4, 0.8, -1.6, -1.0, -1.2, -1.6, 0.4] },
      { o: [-1.4, 1.0, -3.0, 1.7, -3.5, 0.4, -2.5, 0.1], one: 1 },
      { c: [1.6, -0.6, 5.2, -3.2, 8.2, -6.6, 9.6, -9.8, 8.4, -10.8, 5.6, -8.6, 2.4, -5.0, 0.0, -1.8] },
      { c: [8.6, -10.2, 10.0, -13.0, 11.4, -14.6, 12.2, -13.0, 10.4, -10.4] },
      { c: [8.8, -10.6, 8.8, -13.6, 9.6, -15.4, 10.6, -14.4, 9.8, -11.6] },
      { c: [9.2, -10.0, 11.6, -11.8, 13.2, -12.4, 12.8, -11.0, 10.6, -9.6] },
      { c: [3.0, -2.0, 5.4, 0.8, 8.6, 3.6, 11.2, 5.0, 13.0, 6.0, 12.6, 3.4, 10.4, 0.8, 8.0, -1.6, 5.4, -3.6] },
      { c: [4.0, -2.6, 7.6, -0.6, 11.4, 1.4, 13.4, 1.8, 12.0, -0.4, 8.6, -2.6, 5.6, -4.4] },
      { c: [2.2, -3.2, -0.6, -5.0, -3.4, -7.6, -5.1, -9.7, -6.6, -11.2, -4.2, -11.0, -1.6, -9.4, 1.4, -7.0, 3.6, -5.2] },
      { c: [3.0, -4.4, 0.6, -8.0, -1.4, -11.4, -2.0, -13.2, 0.2, -12.4, 2.4, -9.6, 4.4, -6.4] }] },

  { id: "dragon", kind: GREEK, name: "Draco", gloss: "the dragon", tag: "Greek figure", at: [211.10, 64.38], lines: "Dra",
    stars: "Thuban, Eltanin, Rastaban",
    parts: [
      { tw: [-24.6, -8.2, -29.6, -3.2, -33.3, 3.3, -31.6, 6.6, -27.7, 7.0, -23.6, 4.6, -19.9, 1.3, -15.1, -2.9, -12.7, -5.8, -8.7, -5.4,
             -4.4, -3.6, 0, 0, 4.8, 3.6, 9.8, 5.4, 13.4, 5.6, 16.5, 5.0, 18.6, 3.8], a: .85, l: 4.2 },
      { c: [-25.9, -13.8, -22.0, -13.3, -21.5, -9.0, -24.4, -6.5, -26.7, -9.4] },
      { o: [-21.9, -11.6, -19.4, -12.4, -17.8, -11.3], one: 1, curl: 1 }, { o: [-19.6, -12.5, -17.5, -13.4], one: 1, curl: -1 },
      { c: [17.2, 4.4, 19.8, 6.8, 21.6, 5.0, 20.2, 2.2, 17.6, 2.8] }, { dot: [-24.0, -10.6] }] },

  { id: "horse", kind: GREEK, name: "Pegasus", gloss: "the winged horse", tag: "Greek figure", at: [346.19, 15.21], lines: "Peg",
    stars: "the Great Square: Markab, Scheat, Algenib, with Alpheratz",
    parts: [
      { c: [1.2, -0.8, 1.0, 6.4, 1.3, 13.6, -7.2, 15.6, -14.6, 14.8, -17.1, 7.2, -17.4, -0.6, -8.0, -1.6] },
      { c: [-0.4, 1.0, 3.6, -3.6, 7.2, -7.0, 11.4, -9.6, 12.4, -7.6, 8.4, -5.0, 5.2, -1.8, 2.0, 2.4] },
      { c: [11.2, -9.8, 14.2, -10.4, 17.6, -8.2, 19.4, -5.3, 20.0, -4.0, 18.0, -3.6, 14.6, -5.6, 12.2, -6.8] },
      { o: [12.4, -9.4, 11.6, -11.8, 13.0, -10.8], one: 1 },
      { c: [2.6, 0.2, 2.0, -4.2, 4.6, -7.6, 6.4, -5.6, 5.0, -2.8] }, { c: [6.0, -3.0, 6.4, -7.6, 9.2, -10.6, 10.4, -8.2, 8.6, -5.4] },
      { o: [0.6, 13.2, 5.2, 15.0, 9.0, 16.0, 13.2, 18.0] }, { ring: [14.2, 18.6, .9] },
      { o: [0.8, 9.6, 4.4, 8.4, 9.0, 9.4, 13.9, 10.1, 17.0, 10.4, 19.3, 10.4] }, { ring: [20.3, 10.6, .9] },
      { c: [-4.0, -1.0, -6.0, -5.0, -9.6, -8.4, -12.4, -9.4, -11.2, -6.6, -9.0, -3.2, -7.0, -0.8] },
      { c: [-6.0, -0.4, -7.4, -4.6, -8.0, -8.8, -7.0, -11.6, -5.6, -8.4, -4.4, -4.4, -3.2, -1.4] }, { dot: [14.8, -7.4] }] },

  { id: "lion", kind: GREEK, name: "Leo", gloss: "the lion", tag: "Greek figure", at: [152.09, 11.97], lines: "Leo",
    stars: "Regulus, Algieba, Denebola",
    parts: [
      { c: [1.4, 1.0, 0.8, 5.6, -2.6, 9.2, -9.4, 9.8, -16.4, 9.6, -18.6, 6.0, -17.2, 2.0, -11.0, 1.6, -4.0, 0.0, -0.6, -0.6] },
      { c: [1.0, 9.4, 2.4, 13.6, 5.4, 14.6, 7.6, 12.4, 6.6, 9.6, 3.6, 8.6] },
      { c: [0.2, 7.6, -1.8, 11.2, -0.8, 14.4, 2.0, 15.6, 2.4, 12.6, 1.6, 9.8] },
      { c: [-0.6, 9.6, -3.2, 12.6, -2.0, 16.2, 1.2, 17.0, 0.4, 13.6] },
      { o: [0.4, 0.4, 1.6, -2.6, 1.2, -5.0] }, { ring: [1.9, -5.6, .8] },
      { o: [-15.0, 2.6, -14.0, -0.6, -15.6, -3.6] }, { ring: [-14.9, -4.4, .8] },
      { o: [-18.0, 7.2, -21.4, 5.6, -24.6, 2.6, -26.2, 0.2], curl: 1 }, { dot: [4.8, 12.0] }] },

  { id: "queen", kind: GREEK, name: "Cassiopeia", gloss: "the queen's throne", tag: "Greek figure", at: [14.18, 60.72], lines: "Cas",
    stars: "Schedar, Caph, Navi, Ruchbah, Segin",
    parts: [
      { c: [-4.4, 0.3, 0.2, 0.9, 6.3, -0.8, 6.1, -2.3, 0.0, -0.9, -4.1, -1.3] },
      { c: [-3.1, -0.1, -5.5, 1.7, -7.4, 3.9, -7.9, 2.5, -5.7, 0.2, -4.3, -0.9] },
      { o: [-8.7, 3.4, -8.6, 5.3, -7.7, 4.3, -7.0, 5.8, -6.5, 4.1, -5.9, 5.1, -6.0, 3.3], one: 1 },
      { o: [-3.7, -1.0, -3.9, -3.4, -4.1, -5.7] }, { ring: [-4.1, -6.3, .7] },
      { o: [5.5, -1.9, 5.5, -4.0, 5.4, -6.1] }, { ring: [5.4, -6.7, .7] },
      { o: [-4.6, -3.9, -1.2, -4.1, 2.0, -4.2, 6.2, -4.5] }] },
];

/* ---------------- where each figure sits ----------------
   Composed round the tree so the figures spread evenly through the margins: centre x, y, width and
   height in the eye's scene (1000 × 1280), and a turn in degrees. Within a figure the stars keep their
   true places to one another; only its place, size and turn are composed. Pegasus is set upright. */
const SLOT = {
  wagon:  [160, 118, 280, 190, 0],   queen: [356, 64, 96, 92, 0],      eyes:  [500, 50, 180, 72, -59.5], dragon: [832, 122, 300, 196, 0],
  swan:   [82, 395, 150, 185, 0],    eagle: [918, 395, 150, 185, 0],
  loki:   [42, 700, 76, 200, 0],     lyre:  [961, 702, 70, 160, 0],
  horse:  [168, 995, 300, 205, 180], lion:  [834, 995, 300, 195, 0],
  distaff:[132, 1238, 240, 72, -36], wolf:  [872, 1238, 232, 84, 0],
};

/* ---------------- geometry ---------------- */
let R = 325, built = null;
const proj = (ra, dec) => { const r = 2 * R * Math.tan((90 - dec) / 2 * RAD), a = ra * RAD; return [-r * Math.sin(a), r * Math.cos(a)]; };
const pairs = a => { const p = []; for (let i = 0; i < a.length; i += 2) p.push([a[i], a[i + 1]]); return p; };
/* a star's place in a figure's own degrees (x west to the right, y north up) */
const local = (f, ra, dec) => { const s = f.s || 1; return [-(((ra - f.at[0] + 540) % 360) - 180) * Math.cos(f.at[1] * RAD) / s, (dec - f.at[1]) / s]; };

/* a smooth curve through the points (Catmull-Rom) */
function spline(P, closed, per = 7){
  const n = P.length, out = [], get = i => closed ? P[(i + n) % n] : P[Math.max(0, Math.min(n - 1, i))];
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++){
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    for (let k = 0; k < per; k++){ const t = k / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => .5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3))); }
  }
  if (!closed) out.push(P[n - 1]);
  return out;
}
function ringPts(cx, cy, r, n = 10){ return Array.from({ length: n }, (_, i) => [cx + r * Math.cos(i / n * TAU), cy + r * Math.sin(i / n * TAU)]); }
function eyePts(cx, cy, ang, hl, hh){ const u = [Math.cos(ang * RAD), Math.sin(ang * RAD)], v = [-u[1], u[0]];
  return [[1, 0], [.45, .9], [-.45, .9], [-1, 0], [-.45, -.9], [.45, -.9]].map(([a, b]) => [cx + u[0] * hl * a + v[0] * hh * b, cy + u[1] * hl * a + v[1] * hh * b]); }
function eightPts(cx, cy, ang, hl, hh){ const u = [Math.cos(ang * RAD), Math.sin(ang * RAD)], v = [-u[1], u[0]], out = [];
  for (let i = 0; i < 16; i++){ const t = i / 16 * TAU, a = Math.sin(t), b = Math.sin(t) * Math.cos(t) * 2;
    out.push([cx + u[0] * hl * a + v[0] * hh * b, cy + u[1] * hl * a + v[1] * hh * b]); }
  return out; }

/* even steps along a polyline (scene units) */
function resample(P, step, closed){
  const Q = closed ? [...P, P[0]] : P, out = [Q[0]]; let carry = 0;
  for (let i = 1; i < Q.length; i++){
    const [ax, ay] = Q[i - 1], [bx, by] = Q[i], L = Math.hypot(bx - ax, by - ay); let d = step - carry;
    while (d <= L){ out.push([ax + (bx - ax) * d / L, ay + (by - ay) * d / L]); d += step; }
    carry = L - (d - step);
  }
  if (!closed && out.length && Math.hypot(out[out.length - 1][0] - Q[Q.length - 1][0], out[out.length - 1][1] - Q[Q.length - 1][1]) > step * .3) out.push(Q[Q.length - 1]);
  if (closed) out.push(out[0]);
  return out;
}
const lengthOf = P => P.reduce((s, p, i) => i ? s + Math.hypot(p[0] - P[i - 1][0], p[1] - P[i - 1][1]) : 0, 0);
/* a two-strand rope along a path: the strands cross every half turn; a closed rope closes on a whole number of turns */
function rope(P, closed, a = 2.5, want = 13){
  const len = lengthOf(P), n = Math.max(closed ? 3 : 1, Math.round(len / want)), l = len / n, acc = [0];
  for (let i = 1; i < P.length; i++) acc.push(acc[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const side = sgn => P.map((p, i) => { const q = P[closed ? (i + 1) % (P.length - 1) : Math.min(P.length - 1, i + 1)], o = P[closed ? (i - 1 + P.length - 1) % (P.length - 1) : Math.max(0, i - 1)];
    const dx = q[0] - o[0], dy = q[1] - o[1], m = Math.hypot(dx, dy) || 1;
    const taper = closed ? 1 : Math.min(1, acc[i] / (l * .75), (len - acc[i]) / (l * .75));
    const w = sgn * a * Math.sin(acc[i] / l * Math.PI) * taper;
    return [p[0] - dy / m * w, p[1] + dx / m * w]; });
  return [side(1), side(-1)];
}
/* a Norse scroll at a strand's end: a spiral turning in from the line's own direction */
function curl(P, dir, r0 = 7){
  const e = P[P.length - 1], b = P[Math.max(0, P.length - 3)], dx = e[0] - b[0], dy = e[1] - b[1], m = Math.hypot(dx, dy) || 1;
  const t = [dx / m, dy / m], nrm = [-t[1] * dir, t[0] * dir], c = [e[0] + nrm[0] * r0, e[1] + nrm[1] * r0], a0 = Math.atan2(e[1] - c[1], e[0] - c[0]), out = [];
  for (let k = 1; k <= 26; k++){ const th = k / 26 * 1.35 * TAU, r = r0 * (1 - .78 * k / 26), a = a0 + th * dir;
    out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]); }
  return out;
}

/* where segments cross, found through a grid so only near neighbours are tested */
function crossings(strands){
  const G = 10, cells = new Map(), out = [];
  strands.forEach((S, s) => { for (let i = 0; i < S.pts.length - 1; i++){
    const [ax, ay] = S.pts[i], [bx, by] = S.pts[i + 1];
    for (let gx = Math.floor(Math.min(ax, bx) / G); gx <= Math.floor(Math.max(ax, bx) / G); gx++)
      for (let gy = Math.floor(Math.min(ay, by) / G); gy <= Math.floor(Math.max(ay, by) / G); gy++){
        const key = gx + "," + gy; (cells.get(key) || cells.set(key, []).get(key)).push([s, i]); } } });
  const seen = new Set();
  for (const list of cells.values()) for (let p = 0; p < list.length; p++) for (let q = p + 1; q < list.length; q++){
    let [s, i] = list[p], [u, j] = list[q];
    if (s > u || (s === u && i > j)) [s, i, u, j] = [u, j, s, i];
    const key = s + ":" + i + ":" + u + ":" + j; if (seen.has(key)) continue; seen.add(key);
    if (s === u){ const n = strands[s].pts.length - 1; if (Math.abs(i - j) < 3 || (strands[s].closed && n - Math.abs(i - j) < 3)) continue; }
    const A = strands[s].pts, B = strands[u].pts, [ax, ay] = A[i], [bx, by] = A[i + 1], [cx, cy] = B[j], [dx, dy] = B[j + 1];
    const den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx); if (!den) continue;
    const t = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den, v = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
    if (t >= 0 && t < 1 && v >= 0 && v < 1) out.push({ a: s, b: u, ta: i + t, tb: j + v, x: ax + (bx - ax) * t, y: ay + (by - ay) * t, over: null });
  }
  return out;
}

/* ---------------- knotwork ----------------
   A body is woven, not outlined: its shape is filled with a knot field, built as Celtic knotwork is
   drawn by hand from a grid of dots. Each edge between two dots inside the shape is a crossing; round
   each dot the strand turns from one edge's crossing to the next. Every arc goes over where it starts
   and under where it ends, so the whole field alternates over and under. A few edges are broken, and
   there the strands turn back on themselves in loops. Limbs, horns and tails are plaits of three
   strands; rings are two-strand ropes; the eyes are set into the weave. */
const pip = (P, x, y) => { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++){
  const [xi, yi] = P[i], [xj, yj] = P[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
const cubic = (a, b, c, d, n = 8) => Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t;
  return [0, 1].map(k => u * u * u * a[k] + 3 * u * u * t * b[k] + 3 * u * t * t * c[k] + t * t * t * d[k]); });
const unit = (x, y) => { const m = Math.hypot(x, y) || 1; return [x / m, y / m]; };
/* the strand round dot v, from the crossing m1 (edge at angle a1) to m2 (edge at a2, a2 > a1) */
function turnArc(v, m1, a1, m2, a2){
  const t1 = [Math.cos(a1), Math.sin(a1)], n1 = [-t1[1], t1[0]], t2 = [Math.cos(a2), Math.sin(a2)], n2 = [-t2[1], t2[0]];
  const d1 = unit(-t1[0] + n1[0], -t1[1] + n1[1]), d2 = unit(t2[0] + n2[0], t2[1] + n2[1]), span = a2 - a1;
  const anchors = [[m1, d1]], parts = Math.ceil(span / (100 * RAD));
  if (parts > 1){ const rho = (Math.hypot(m1[0] - v[0], m1[1] - v[1]) + Math.hypot(m2[0] - v[0], m2[1] - v[1])) / 2;
    for (let j = 1; j < parts; j++){ const a = a1 + span * j / parts; anchors.push([[v[0] + rho * Math.cos(a), v[1] + rho * Math.sin(a)], [-Math.sin(a), Math.cos(a)]]); } }
  anchors.push([m2, d2]);
  const out = [];
  for (let j = 0; j < anchors.length - 1; j++){
    const [p, dp] = anchors[j], [q, dq] = anchors[j + 1], L = Math.hypot(q[0] - p[0], q[1] - p[1]) * (parts > 1 ? .42 : .36);
    const seg = cubic(p, [p[0] + dp[0] * L, p[1] + dp[1] * L], [q[0] - dq[0] * L, q[1] - dq[1] * L], q); if (j) seg.shift(); out.push(...seg);
  }
  return out;
}
function knotField(polys, d, seed){
  const inside = (x, y) => polys.some(P => pip(P, x, y));
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const P of polys) for (const [x, y] of P){ x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  let sd = seed; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const nx = Math.floor((x1 - x0) / d) + 1, ny = Math.floor((y1 - y0) / d) + 1, ox = x0 + ((x1 - x0) - (nx - 1) * d) / 2, oy = y0 + ((y1 - y0) - (ny - 1) * d) / 2;
  const V = new Map();
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++){ const x = ox + i * d, y = oy + j * d;
    if (inside(x, y)) V.set(i + "," + j, { x: x + (rnd() - .5) * d * .16, y: y + (rnd() - .5) * d * .16, nb: [] }); }
  const E = [];
  for (const [key, v] of V){ const [i, j] = key.split(",").map(Number);
    for (const [di, dj] of [[1, 0], [0, 1]]){ const w = V.get((i + di) + "," + (j + dj));
      if (w && inside((v.x + w.x) / 2, (v.y + w.y) / 2)) E.push({ a: v, b: w }); } }
  E.forEach(e => { e.a.nb.push(e); e.b.nb.push(e); });
  /* breaks, for loops; never leaving a dot with fewer than two strands */
  for (const e of E){ if (rnd() < .26 && e.a.nb.length > 2 && e.b.nb.length > 2){ e.cut = true; e.a.nb = e.a.nb.filter(x => x !== e); e.b.nb = e.b.nb.filter(x => x !== e); } }
  const live = E.filter(e => !e.cut);
  live.forEach((e, k) => { e.id = k; e.m = [(e.a.x + e.b.x) / 2, (e.a.y + e.b.y) / 2]; e.starts = []; });
  const arcs = [];
  for (const v of V.values()){
    if (!v.nb.length) continue;
    const nb = v.nb.map(e => { const w = e.a === v ? e.b : e.a; return { e, ang: Math.atan2(w.y - v.y, w.x - v.x) }; }).sort((p, q) => p.ang - q.ang);
    nb.forEach((p, i) => {
      const q = nb[(i + 1) % nb.length]; let a2 = q.ang; if (nb.length === 1) a2 = p.ang + TAU; else if (a2 <= p.ang) a2 += TAU;
      const pts = turnArc([v.x, v.y], p.e.m, p.ang, q.e.m, a2), arc = { pts };
      arcs.push(arc); p.e.starts.push(arc);
    });
  }
  /* at each crossing the strand made of the two arcs that start there goes over */
  const lead = (P, want) => { const out = [P[0]]; let s = 0; for (let i = 1; i < P.length; i++){ s += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); out.push(P[i]); if (s >= want) break; } return out; };
  const overs = live.filter(e => e.starts.length === 2).map(e => [...lead(e.starts[0].pts, d * .55).reverse(), ...lead(e.starts[1].pts, d * .55).slice(1)]);
  return { arcs: arcs.map(a => a.pts), overs, dots: V.size };
}
/* a plait of three strands along a path; a two-strand rope round a closed one */
function plait(P, closed, a, want, n){
  const len = lengthOf(P), k = Math.max(closed ? 3 : 1, Math.round(len / want)), l = len / k, acc = [0];
  for (let i = 1; i < P.length; i++) acc.push(acc[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const N = P.length - (closed ? 1 : 0);
  return Array.from({ length: n }, (_, s) => P.map((p, i) => {
    const q = P[closed ? (i + 1) % N : Math.min(P.length - 1, i + 1)], o = P[closed ? (i - 1 + N) % N : Math.max(0, i - 1)];
    const [nx, ny] = unit(-(q[1] - o[1]), q[0] - o[0]);
    const taper = closed ? 1 : Math.min(1, acc[i] / (l * .6), (len - acc[i]) / (l * .6));
    const w = a * Math.sin(acc[i] / l * TAU * (n === 2 ? .5 : 1) + s * TAU / n) * taper;
    return [p[0] + nx * w, p[1] + ny * w]; }));
}
function alternate(strands){
  const X = crossings(strands);
  strands.forEach((_, s) => {
    const mine = X.filter(c => c.a === s || c.b === s).map(c => ({ c, t: c.a === s ? c.ta : c.tb })).sort((p, q) => p.t - q.t);
    let next = null;
    for (const { c, t } of mine){
      const me = c.a === s && (c.b !== s || t === c.ta) ? "a" : "b";
      if (c.over != null){ next = c.over === me ? "under" : "over"; continue; }
      if (next == null) next = "over";
      c.over = next === "over" ? me : (me === "a" ? "b" : "a");
      next = next === "over" ? "under" : "over";
    }
  });
  return X.map(c => { const P = strands[c.over === "a" ? c.a : c.b].pts, t = c.over === "a" ? c.ta : c.tb, i = Math.floor(t), want = 4.4;
    let k = i; while (k > 0 && Math.hypot(P[k][0] - c.x, P[k][1] - c.y) < want) k--;
    const out = [P[k]]; for (let m = k + 1; m < P.length; m++){ out.push(P[m]); if (m > i && Math.hypot(P[m][0] - c.x, P[m][1] - c.y) >= want) break; }
    return out; });
}

function buildFigure(f){
  const [sx, sy, sw, sh, rot] = SLOT[f.id] || [500, 640, 200, 200, 0];
  const cr = Math.cos(rot * RAD), srt = Math.sin(rot * RAD), turn = ([x, y]) => [x * cr - y * srt, x * srt + y * cr];
  const raw = [], thinL = [], dotL = [];
  for (const p of f.parts){
    if (p.c) raw.push({ kind: "body", pts: spline(pairs(p.c), true), closed: true });
    else if (p.o) raw.push({ kind: p.one ? "line" : "limb", pts: spline(pairs(p.o), false), closed: false, curl: p.curl });
    else if (p.tw) raw.push({ kind: "limb", pts: spline(pairs(p.tw), false, 8), closed: false, curl: p.curl, wide: true });
    else if (p.ring) raw.push({ kind: "ring", pts: spline(ringPts(...p.ring), true, 4), closed: true });
    else if (p.eye) raw.push({ kind: "ring", pts: spline(eyePts(...p.eye), true, 6), closed: true, eye: true });
    else if (p.eight) raw.push({ kind: "limb", pts: spline(eightPts(...p.eight), true, 5), closed: true });
    else if (p.thin) thinL.push(pairs(p.thin));
    else if (p.dot) dotL.push(p.dot);
  }
  raw.forEach(r => { r.pts = r.pts.map(turn); });
  const all = raw.flatMap(r => r.pts), xs = all.map(p => p[0]), ys = all.map(p => p[1]);
  const bx0 = Math.min(...xs), bx1 = Math.max(...xs), by0 = Math.min(...ys), by1 = Math.max(...ys);
  const S = Math.min(sw / (bx1 - bx0), sh / (by1 - by0)), mx = (bx0 + bx1) / 2, my = (by0 + by1) / 2;
  const scene = ([x, y]) => [sx + (x - mx) * S, sy - (y - my) * S];
  raw.forEach(r => { r.pts = resample(r.pts.map(scene), 2, r.closed); });
  /* the body: every broad closed shape woven together as one field, framed by its contour; a thin one
     (a wing, a flame, a feather) is a plaited loop that follows its own shape */
  const d = Math.max(8, Math.min(14, Math.min(sw, sh) / 9));
  const area = P => Math.abs(P.reduce((s, p, i) => { const q = P[(i + 1) % P.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0)) / 2;
  raw.forEach(r => { if (r.kind === "body" && 2 * area(r.pts) / lengthOf([...r.pts, r.pts[0]]) < 2.3 * d) r.kind = "loop"; });
  const bodies = raw.filter(r => r.kind === "body").map(r => r.pts);
  let seed = 7; for (const ch of f.id) seed = (seed * 31 + ch.charCodeAt(0)) % 2147483647;
  const field = bodies.length ? knotField(bodies, d, seed) : { arcs: [], overs: [], dots: 0 };
  const inBody = P => bodies.length && P.filter(([x, y]) => bodies.some(B => pip(B, x, y))).length / P.length > .6;
  /* limbs and rings: plaits and ropes over the body; a body too small to weave keeps its outline */
  const strands = [];
  if (field.dots < 4) for (const B of bodies) for (const s of plait([...B, B[0]], true, 2.2, 12, 2)) strands.push({ pts: s, closed: true });
  for (const r of raw){
    if (r.kind === "body") continue;
    if (r.kind === "loop"){ for (const s of plait([...r.pts, r.pts[0]], true, 2.3, 12, 2)) strands.push({ pts: s, closed: true }); continue; }
    if (r.kind === "limb" && !r.closed && inBody(r.pts)) continue;          /* lies on the body: the weave already shows it */
    const len = lengthOf(r.pts);
    if (r.kind === "limb" && len > 34) for (const s of plait(r.pts, r.closed, r.wide ? 3.6 : 2.9, r.wide ? 17 : 14, r.closed ? 2 : 3)) strands.push({ pts: s, closed: r.closed });
    else if (r.kind === "ring" && len > 26 && !r.eye) for (const s of plait(r.pts, true, 1.6, 9, 2)) strands.push({ pts: s, closed: true });
    else strands.push({ pts: r.pts, closed: r.closed });
    if (r.curl && !r.closed) strands.push({ pts: [r.pts[r.pts.length - 1], ...curl(r.pts, r.curl, r.wide ? 9 : 7)], closed: false });
  }
  const pieces = alternate(strands);
  const thin = thinL.map(l => l.map(turn).map(scene)), eyes = dotL.map(p => scene(turn(p)));
  /* the figure's own stars: every star in its window, in true places to one another */
  const win = { x0: sx - sw / 2 - 10, x1: sx + sw / 2 + 10, y0: sy - sh / 2 - 10, y1: sy + sh / 2 + 10 };
  const stars = [];
  for (let i = 0; i < D.stars.length; i += 3){
    const [lx, ly] = local(f, D.stars[i], D.stars[i + 1]); if (Math.abs(lx) > 60 || Math.abs(ly) > 60) continue;
    const [x, y] = scene(turn([lx, ly])); if (x < win.x0 || x > win.x1 || y < win.y0 || y > win.y1) continue;
    stars.push([x, y, D.stars[i + 2], (i * 7.31) % 1]);
  }
  const lines = [];
  const L = typeof f.lines === "string" ? (D.lines[f.lines] || []).map(seg => pairs(seg).map(([ra, dec]) => local(f, ra, dec))) : (f.lines || []).map(pairs);
  for (const seg of L) lines.push(seg.map(turn).map(scene));
  const box = { x0: sx - sw / 2, x1: sx + sw / 2, y0: sy - sh / 2, y1: sy + sh / 2 };
  return { f, d, field, bodies: field.dots >= 4 ? bodies : [], strands, pieces, thin, eyes, stars, lines, box, c: [sx, sy], crossings: field.overs.length + pieces.length, plaitCrossings: pieces.length };
}

/* each figure painted once, on its own small canvas: a glow, then the ribbons with dark edges */
function paint(G, k){
  const pts = [...G.field.arcs.flat(), ...G.strands.flatMap(s => s.pts)], pad = 14;
  const x0 = Math.min(G.box.x0, ...pts.map(p => p[0])) - pad, y0 = Math.min(G.box.y0, ...pts.map(p => p[1])) - pad;
  const x1 = Math.max(G.box.x1, ...pts.map(p => p[0])) + pad, y1 = Math.max(G.box.y1, ...pts.map(p => p[1])) + pad;
  const cv = document.createElement("canvas"); cv.width = Math.max(2, Math.ceil((x1 - x0) * k)); cv.height = Math.max(2, Math.ceil((y1 - y0) * k));
  const c = cv.getContext("2d"), L = LOOK[G.f.kind];
  c.setTransform(k, 0, 0, k, -x0 * k, -y0 * k); c.lineJoin = "round";
  const path = list => { const p = new Path2D(); for (const s of list) s.forEach((q, i) => i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])); return p; };
  const field = path(G.field.arcs), limbs = path(G.strands.map(s => s.pts));
  const Wk = G.d * .36, Wl = 2.8, edge = Math.max(.9, 1.1 / k);
  const body = new Path2D(); for (const B of G.bodies){ B.forEach((q, i) => i ? body.lineTo(q[0], q[1]) : body.moveTo(q[0], q[1])); body.closePath(); }
  c.save(); c.filter = `blur(${Math.max(1.5, 4 * k)}px)`; c.strokeStyle = `rgba(${L.glow},.5)`; c.lineCap = "round";
  c.lineWidth = Wk * 2.2; c.stroke(body); c.fillStyle = `rgba(${L.glow},.12)`; c.fill(body); c.lineWidth = Wl * 2.4; c.stroke(limbs); c.restore();
  const ribbon = (p, w, cap) => { c.lineCap = cap; c.strokeStyle = L.edge; c.lineWidth = w + edge * 2; c.stroke(p); c.strokeStyle = L.band; c.lineWidth = w; c.stroke(p); };
  c.save(); c.clip(body, "nonzero");
  ribbon(field, Wk, "round");
  for (const o of G.field.overs) ribbon(path([o]), Wk, "butt");
  c.restore();
  ribbon(body, Wk * 1.2, "round");
  ribbon(limbs, Wl, "round");
  for (const piece of G.pieces) ribbon(path([piece]), Wl, "butt");
  c.lineCap = "round"; c.strokeStyle = L.band; c.lineWidth = 1.2; c.stroke(path(G.thin));
  /* the eyes, set into the weave: an almond, a dark pupil, a glint */
  for (const [x, y] of G.eyes){
    const r = Math.max(3.2, G.d * .5);
    c.beginPath(); c.moveTo(x - r * 1.5, y); c.quadraticCurveTo(x, y - r * 1.25, x + r * 1.5, y); c.quadraticCurveTo(x, y + r * 1.25, x - r * 1.5, y); c.closePath();
    c.fillStyle = L.band; c.fill(); c.strokeStyle = L.edge; c.lineWidth = edge * 1.6; c.stroke();
    c.fillStyle = L.edge; c.beginPath(); c.arc(x, y, r * .55, 0, TAU); c.fill();
    c.fillStyle = "#fff"; c.beginPath(); c.arc(x - r * .18, y - r * .2, r * .17, 0, TAU); c.fill();
  }
  return { cv, x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}

/* the sky behind the figures: the real stars, faint, and the Milky Way, as seen about the pole above Asgard */
function starPaths(){
  const groups = [[-2, 2, 1.5, .55], [2, 3, 1.15, .45], [3, 4, .9, .36], [4, 9, .65, .28]].map(([lo, hi, r, a]) => ({ lo, hi, r, a, p: new Path2D() }));
  for (let i = 0; i < D.stars.length; i += 3){ const [x, y] = proj(D.stars[i], D.stars[i + 1]), m = D.stars[i + 2];
    const g = groups.find(g => m >= g.lo && m < g.hi) || groups[3]; g.p.moveTo(x + g.r, y); g.p.arc(x, y, g.r, 0, TAU); }
  return groups;
}
function milkyWay(k){
  const span = R * 2 * Math.tan(65 * RAD) * 2.05, q = Math.min(.5, k * .5), n = Math.ceil(span * q);
  const cv = document.createElement("canvas"); cv.width = cv.height = n;
  const c = cv.getContext("2d"); c.setTransform(q, 0, 0, q, n / 2, n / 2);
  c.filter = `blur(${Math.max(2, 14 * q)}px)`;
  for (const [lv, f] of D.mw){ c.fillStyle = `rgba(${130 + lv * 12},${140 + lv * 10},255,${.026 + lv * .014})`; c.beginPath();
    for (let i = 0; i < f.length; i += 2){ if (f[i + 1] < -55) continue; const [x, y] = proj(f[i], f[i + 1]); c.lineTo(x, y); } c.closePath(); c.fill(); }
  return { cv, s: span };
}

/* the figures' geometry alone, with no canvas (the tests use it) */
function build(r){ R = r; return FIGS.map(buildFigure); }

function prepare(r, k){
  const figs = build(r);
  figs.forEach(G => { G.img = paint(G, k); });
  built = { figs, stars: starPaths(), mw: milkyWay(k), k };
  return built;
}

/* ---------------- drawing ---------------- */
function draw(ctx, pole, th, sel, time = 0, z = 1){
  if (!built) return;
  const sz = Math.sqrt(z);
  ctx.save(); ctx.translate(pole[0], pole[1]); ctx.rotate(th);
  const M = built.mw; ctx.globalCompositeOperation = "lighter"; ctx.drawImage(M.cv, -M.s / 2, -M.s / 2, M.s, M.s);
  ctx.globalCompositeOperation = "source-over";
  for (const g of built.stars){ ctx.fillStyle = `rgba(226,236,255,${g.a})`; ctx.fill(g.p); }
  ctx.restore();
  for (const G of built.figs){
    const on = sel === G.f.id, L = LOOK[G.f.kind];
    ctx.strokeStyle = `rgba(${L.glow},${on ? .55 : .22})`; ctx.lineWidth = .9 / sz; ctx.beginPath();
    for (const s of G.lines) s.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke();
    ctx.globalAlpha = on ? 1 : .74; const I = G.img; ctx.drawImage(I.cv, I.x, I.y, I.w, I.h); ctx.globalAlpha = 1;
    /* its stars, the bright ones glinting */
    ctx.globalCompositeOperation = "lighter";
    for (const [x, y, m, ph] of G.stars){
      const r = Math.max(.7, 2.9 - m * .5);
      if (m < 2.6){ const a = .55 + .45 * Math.sin(time * 1.3 + ph * 40), l = (3.4 - m) * 3.4 * (.75 + .25 * a);
        const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4); g.addColorStop(0, `rgba(255,255,255,${.5 * a})`); g.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 4, 0, TAU); ctx.fill();
        ctx.strokeStyle = `rgba(235,245,255,${.5 * a})`; ctx.lineWidth = .8 / sz;
        ctx.beginPath(); ctx.moveTo(x - l, y); ctx.lineTo(x + l, y); ctx.moveTo(x, y - l); ctx.lineTo(x, y + l); ctx.stroke(); }
      ctx.fillStyle = `rgba(240,246,255,${m < 3 ? .95 : m < 4 ? .7 : .45})`; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    }
    ctx.globalCompositeOperation = "source-over";
  }
}

function hit(x, y){
  if (!built) return null;
  for (const G of built.figs){ const b = G.box; if (x >= b.x0 - 6 && x <= b.x1 + 6 && y >= b.y0 - 6 && y <= b.y1 + 6) return G.f.id; }
  return null;
}

function figure(id){
  const f = FIGS.find(x => x.id === id); if (!f) return null;
  return { ...f, note: f.note || GREEK_NOTE, credit: D.credit };
}

window.WyrdSky = { prepare, build, draw, hit, figure, FIGS, SLOT, at: (ra, dec) => proj(ra, dec), local: (id, ra, dec) => local(FIGS.find(f => f.id === id), ra, dec), get built(){ return built; } };
})();
