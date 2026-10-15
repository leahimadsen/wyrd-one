/* The sky behind Odin's Eye: the real stars, the Milky Way, and figures drawn round them in knotwork.

   The stars stand in their true places (J2000, from the Hipparcos compilation, sky-data.js), seen from
   inside the sky as we see it, turning slowly about the north celestial pole. Setting that pole above
   Asgard's crown is this drawing's choice: no source fixes the sky to the tree.

   The figures are of two kinds, and each says which it is:
     · Norse, in gold: names the Norse sources give these stars, marked Eddic, medieval Icelandic, or
       later folk tradition, as each is attested.
     · Greek, in ice: the classical figure, drawn in Norse ornament. Only the ornament is Norse.

   Each figure is authored in degrees about one of its stars (x west to the right, y north up, as the
   sky is seen), as ribbons: closed loops, open strands, rings, eyes, twists. Where ribbons cross, they
   go over and under in turn, as interlace does.

   WyrdSky.prepare(R, k)            build for a sky of radius scale R (scene units), k pixels per unit
   WyrdSky.draw(ctx, pole, θ, sel)   draw under the current transform, turned by θ (radians)
   WyrdSky.hit(x, y, pole, θ)       the figure at a scene point, or null
   WyrdSky.figure(id)               its record, for the panel                                          */
(function () {
"use strict";
const D = window.WYRD_SKY_DATA, RAD = Math.PI / 180, TAU = Math.PI * 2;
if (!D) { window.WyrdSky = null; return; }

const NORSE = "norse", GREEK = "greek";
const LOOK = {
  [NORSE]: { band: "#f4c46a", glow: "255,196,106", label: "rgba(255,214,140,.86)" },
  [GREEK]: { band: "#9fdcff", glow: "150,215,255", label: "rgba(175,225,255,.8)" },
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
      { o: [-0.2, -0.6, -1.6, -3.4, -3.0, -6.4, -3.9, -8.4] }, { ring: [-1.0, -2.0, .85] }, { ring: [-4.1, -8.9, .7] }] },

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
      { o: [-1.4, 1.0, -3.0, 1.7, -3.5, 0.4, -2.5, 0.1] },
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
      { o: [-21.9, -11.6, -19.4, -12.4, -17.8, -11.3] }, { o: [-19.6, -12.5, -17.5, -13.4] },
      { c: [17.2, 4.4, 19.8, 6.8, 21.6, 5.0, 20.2, 2.2, 17.6, 2.8] }, { dot: [-24.0, -10.6] }] },

  { id: "horse", kind: GREEK, name: "Pegasus", gloss: "the winged horse", tag: "Greek figure", at: [346.19, 15.21], lines: "Peg",
    stars: "the Great Square: Markab, Scheat, Algenib, with Alpheratz",
    parts: [
      { c: [1.2, -0.8, 1.0, 6.4, 1.3, 13.6, -7.2, 15.6, -14.6, 14.8, -17.1, 7.2, -17.4, -0.6, -8.0, -1.6] },
      { c: [-0.4, 1.0, 3.6, -3.6, 7.2, -7.0, 11.4, -9.6, 12.4, -7.6, 8.4, -5.0, 5.2, -1.8, 2.0, 2.4] },
      { c: [11.2, -9.8, 14.2, -10.4, 17.6, -8.2, 19.4, -5.3, 20.0, -4.0, 18.0, -3.6, 14.6, -5.6, 12.2, -6.8] },
      { o: [12.4, -9.4, 11.6, -11.8, 13.0, -10.8] },
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
      { o: [-18.0, 7.2, -21.4, 5.6, -24.6, 2.6, -25.4, 1.0] },
      { c: [-25.4, 1.0, -27.6, -0.4, -26.6, -2.2, -25.0, -0.8] }, { dot: [4.8, 12.0] }] },

  { id: "queen", kind: GREEK, name: "Cassiopeia", gloss: "the queen's throne", tag: "Greek figure", at: [14.18, 60.72], lines: "Cas",
    stars: "Schedar, Caph, Navi, Ruchbah, Segin",
    parts: [
      { c: [-4.4, 0.3, 0.2, 0.9, 6.3, -0.8, 6.1, -2.3, 0.0, -0.9, -4.1, -1.3] },
      { c: [-3.1, -0.1, -5.5, 1.7, -7.4, 3.9, -7.9, 2.5, -5.7, 0.2, -4.3, -0.9] },
      { o: [-8.7, 3.4, -8.6, 5.3, -7.7, 4.3, -7.0, 5.8, -6.5, 4.1, -5.9, 5.1, -6.0, 3.3] },
      { o: [-3.7, -1.0, -3.9, -3.4, -4.1, -5.7] }, { ring: [-4.1, -6.3, .7] },
      { o: [5.5, -1.9, 5.5, -4.0, 5.4, -6.1] }, { ring: [5.4, -6.7, .7] },
      { o: [-4.6, -3.9, -1.2, -4.1, 2.0, -4.2, 6.2, -4.5] }] },
];

/* ---------------- geometry ---------------- */
let R = 325, built = null;
const proj = (ra, dec) => { const r = 2 * R * Math.tan((90 - dec) / 2 * RAD), a = ra * RAD; return [-r * Math.sin(a), r * Math.cos(a)]; };
const toSky = (f, x, y) => { const s = f.s || 1; return [f.at[0] - x * s / Math.cos(f.at[1] * RAD), f.at[1] + y * s]; };
const at = (f, x, y) => proj(...toSky(f, x, y));
const pairs = a => { const p = []; for (let i = 0; i < a.length; i += 2) p.push([a[i], a[i + 1]]); return p; };

/* a smooth curve through the points (Catmull-Rom), in the figure's own degrees */
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
/* a two-strand twist along a path: the strands cross every half turn */
function twist(P, a, l){
  const C = spline(P, false, 8), len = [0];
  for (let i = 1; i < C.length; i++) len.push(len[i - 1] + Math.hypot(C[i][0] - C[i - 1][0], C[i][1] - C[i - 1][1]));
  const side = sgn => C.map((p, i) => { const q = C[Math.min(C.length - 1, i + 1)], o = C[Math.max(0, i - 1)];
    const dx = q[0] - o[0], dy = q[1] - o[1], m = Math.hypot(dx, dy) || 1, w = sgn * a * Math.sin(len[i] / l * TAU) * Math.min(1, len[i] / l, (len[len.length - 1] - len[i]) / l + .25);
    return [p[0] - dy / m * w, p[1] + dx / m * w]; });
  return [side(1), side(-1)];
}

/* where two polylines cross: segment against segment, skipping a strand's own neighbours */
function cross(A, B, same, closed){
  const out = [];
  for (let i = 0; i < A.length - 1; i++){
    const [ax, ay] = A[i], [bx, by] = A[i + 1];
    for (let j = same ? i + 2 : 0; j < B.length - 1; j++){
      if (same && closed && i === 0 && j === B.length - 2) continue;
      const [cx, cy] = B[j], [dx, dy] = B[j + 1], den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
      if (!den) continue;
      const t = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den, u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
      if (t >= 0 && t < 1 && u >= 0 && u < 1) out.push({ i: i + t, j: j + u, x: ax + (bx - ax) * t, y: ay + (by - ay) * t });
    }
  }
  return out;
}

function buildFigure(f){
  const strands = [], thin = [], dots = [];
  const add = (pts, closed) => strands.push({ pts: (closed ? [...pts, pts[0]] : pts).map(([x, y]) => at(f, x, y)), closed });
  for (const p of f.parts){
    if (p.c) add(spline(pairs(p.c), true), true);
    else if (p.o) add(spline(pairs(p.o), false), false);
    else if (p.ring) add(spline(ringPts(...p.ring), true, 4), true);
    else if (p.eye) add(spline(eyePts(...p.eye), true, 6), true);
    else if (p.eight) add(spline(eightPts(...p.eight), true, 4), true);
    else if (p.tw) for (const s of twist(pairs(p.tw), p.a, p.l)) strands.push({ pts: s.map(([x, y]) => at(f, x, y)), closed: false });
    else if (p.thin) thin.push(pairs(p.thin).map(([x, y]) => at(f, x, y)));
    else if (p.dot) dots.push(at(f, ...p.dot));
  }
  /* every crossing, then over and under in turn along each strand */
  const X = [];
  strands.forEach((A, a) => strands.forEach((B, b) => { if (b < a) return;
    for (const c of cross(A.pts, B.pts, a === b, A.closed)) X.push({ a, b, ta: c.i, tb: c.j, x: c.x, y: c.y, over: null }); }));
  strands.forEach((S, s) => {
    const mine = X.filter(c => c.a === s || c.b === s).map(c => ({ c, t: c.a === s ? c.ta : c.tb })).sort((p, q) => p.t - q.t);
    let next = null;
    for (const { c } of mine){
      const other = c.a === s ? c.b : c.a, me = c.a === s ? "a" : "b";
      if (c.over != null){ next = c.over === me ? "under" : "over"; continue; }
      if (next == null) next = "over";
      c.over = next === "over" ? me : (me === "a" ? "b" : "a");
      if (other === s && c.a === c.b) c.over = next === "over" ? "a" : "b";
      next = next === "over" ? "under" : "over";
    }
  });
  /* the over strand's piece at each crossing, redrawn on top */
  const pieces = X.map(c => { const S = strands[c.over === "a" ? c.a : c.b].pts, t = c.over === "a" ? c.ta : c.tb, i = Math.floor(t);
    const out = [], want = 7; let k = i;
    while (k > 0 && Math.hypot(S[k][0] - c.x, S[k][1] - c.y) < want) k--;
    out.push(S[k]); for (let m = k + 1; m < S.length; m++){ out.push(S[m]); if (m > i && Math.hypot(S[m][0] - c.x, S[m][1] - c.y) >= want) break; }
    return out; });
  const lines = [];
  if (typeof f.lines === "string") for (const seg of (D.lines[f.lines] || [])) lines.push(pairs(seg).map(([ra, dec]) => proj(ra, dec)));
  else for (const seg of (f.lines || [])) lines.push(pairs(seg).map(([x, y]) => at(f, x, y)));
  const all = strands.flatMap(s => s.pts), xs = all.map(p => p[0]), ys = all.map(p => p[1]);
  const box = { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
  const cx = (box.x0 + box.x1) / 2, cy = (box.y0 + box.y1) / 2;
  return { f, strands, pieces, thin, dots, lines, box, c: [cx, cy], r: Math.max(box.x1 - box.x0, box.y1 - box.y0) / 2, crossings: X.length };
}

/* each figure drawn once, opaque, on its own small canvas; the sky turns them as pictures */
const W = 5.2;
function paint(G, k){
  const pad = 8, bw = G.box.x1 - G.box.x0 + pad * 2, bh = G.box.y1 - G.box.y0 + pad * 2;
  const cv = document.createElement("canvas"); cv.width = Math.max(2, Math.ceil(bw * k)); cv.height = Math.max(2, Math.ceil(bh * k));
  const c = cv.getContext("2d"), L = LOOK[G.f.kind];
  c.setTransform(k, 0, 0, k, (pad - G.box.x0) * k, (pad - G.box.y0) * k);
  c.lineJoin = "round";
  const path = list => { const p = new Path2D(); for (const s of list) s.forEach((q, i) => i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])); return p; };
  const ribbon = (p, cap) => { c.lineCap = cap;
    c.strokeStyle = "#070320"; c.lineWidth = W + 2.6; c.stroke(p);
    c.strokeStyle = L.band; c.lineWidth = W; c.stroke(p);
    c.strokeStyle = "#0b0626"; c.lineWidth = W * .36; c.stroke(p); };
  ribbon(path(G.strands.map(s => s.pts)), "round");
  for (const piece of G.pieces) ribbon(path([piece]), "butt");
  c.lineCap = "round"; c.strokeStyle = L.band; c.lineWidth = 1.3; c.stroke(path(G.thin));
  c.fillStyle = L.band; for (const [x, y] of G.dots){ c.beginPath(); c.arc(x, y, 2.1, 0, TAU); c.fill(); }
  return { cv, x: G.box.x0 - pad, y: G.box.y0 - pad, w: bw, h: bh };
}

/* the stars, by brightness, as a few paths; the Milky Way as a soft glow, painted once */
function starPaths(){
  const groups = [[-2, 1, 3.1], [1, 2, 2.3], [2, 3, 1.7], [3, 4, 1.2], [4, 9, .8]].map(([lo, hi, r]) => ({ lo, hi, r, p: new Path2D() }));
  const bright = [];
  for (let i = 0; i < D.stars.length; i += 3){ const [x, y] = proj(D.stars[i], D.stars[i + 1]), m = D.stars[i + 2];
    const g = groups.find(g => m >= g.lo && m < g.hi) || groups[4];
    g.p.moveTo(x + g.r, y); g.p.arc(x, y, g.r, 0, TAU);
    if (m < 1.6) bright.push([x, y, m, (i * 7.31) % 1]); }
  return { groups, bright };
}
function milkyWay(k){
  const span = R * 2 * Math.tan(65 * RAD) * 2.05, q = Math.min(.5, k * .5), n = Math.ceil(span * q);
  const cv = document.createElement("canvas"); cv.width = cv.height = n;
  const c = cv.getContext("2d"); c.setTransform(q, 0, 0, q, n / 2, n / 2);
  c.filter = `blur(${Math.max(2, 14 * q)}px)`;
  for (const [lv, f] of D.mw){ c.fillStyle = `rgba(${130 + lv * 12},${140 + lv * 10},255,${.022 + lv * .012})`; c.beginPath();
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
  /* the stars' own figures, faint */
  for (const G of built.figs){ ctx.strokeStyle = `rgba(${LOOK[G.f.kind].glow},${sel === G.f.id ? .5 : .2})`; ctx.lineWidth = .9 / sz; ctx.beginPath();
    for (const s of G.lines) s.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); }
  for (const G of built.figs){ ctx.globalAlpha = sel === G.f.id ? .95 : .5; const I = G.img; ctx.drawImage(I.cv, I.x, I.y, I.w, I.h); }
  ctx.globalAlpha = 1;
  for (const g of built.stars.groups){ ctx.fillStyle = `rgba(232,240,255,${g.lo < 2 ? .95 : g.lo < 3 ? .8 : g.lo < 4 ? .62 : .42})`; ctx.save(); ctx.scale(1, 1); ctx.fill(g.p); ctx.restore(); }
  ctx.globalCompositeOperation = "lighter";
  for (const [x, y, m, ph] of built.stars.bright){
    const a = .5 + .5 * Math.sin(time * 1.1 + ph * 40), l = (4.2 - m) * 3.2 * (.7 + .3 * a);
    ctx.strokeStyle = `rgba(220,240,255,${.32 * a})`; ctx.lineWidth = .8 / sz;
    ctx.beginPath(); ctx.moveTo(x - l, y); ctx.lineTo(x + l, y); ctx.moveTo(x, y - l); ctx.lineTo(x, y + l); ctx.stroke();
  }
  ctx.globalCompositeOperation = "source-over";
  ctx.restore();
  /* names, upright wherever the sky has turned them */
  const cs = Math.cos(th), sn = Math.sin(th);
  ctx.textAlign = "center";
  for (const G of built.figs){
    const [bx, by] = [G.c[0], G.box.y1 + 4], x = pole[0] + bx * cs - by * sn, y = pole[1] + bx * sn + by * cs;
    const on = sel === G.f.id;
    ctx.fillStyle = on ? "#fff" : LOOK[G.f.kind].label; ctx.globalAlpha = on ? 1 : .78;
    ctx.font = `italic ${(on ? 14 : 12.5) / sz}px Georgia, 'Times New Roman', serif`;
    ctx.fillText(`${G.f.name} · ${G.f.gloss}`, x, y + 12 / sz);
    ctx.font = `${10 / sz}px ui-monospace, Menlo, monospace`; ctx.globalAlpha = on ? .95 : .6;
    ctx.fillText(G.f.tag, x, y + 25 / sz);
  }
  ctx.globalAlpha = 1;
}

function hit(x, y, pole, th){
  if (!built) return null;
  const dx = x - pole[0], dy = y - pole[1], bx = dx * Math.cos(-th) - dy * Math.sin(-th), by = dx * Math.sin(-th) + dy * Math.cos(-th);
  let best = null, bd = Infinity;
  for (const G of built.figs){ const d = Math.hypot(bx - G.c[0], by - G.c[1]); if (d < Math.max(26, G.r * .85) && d < bd){ bd = d; best = G.f.id; } }
  return best;
}

function figure(id){
  const f = FIGS.find(x => x.id === id); if (!f) return null;
  return { ...f, note: f.note || GREEK_NOTE, credit: D.credit };
}

window.WyrdSky = { prepare, build, draw, hit, figure, FIGS, at: (ra, dec) => proj(ra, dec), get built(){ return built; } };
})();
