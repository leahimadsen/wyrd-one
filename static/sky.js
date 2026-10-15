/* The sky behind Odin's Eye: the real stars, the Milky Way, and twelve constellations drawn as star maps.

   Behind everything, the real sky (J2000, from the Hipparcos compilation, sky-data.js), faint, seen as
   we see it about the north celestial pole, which this drawing sets above Asgard's crown.

   Round the tree, twelve star maps, spread through the margins (SLOT): each a window on one constellation,
   its stars in their true places to one another, north up, with its figure's lines (after the IAU).
   Where a Norse source names some of its stars, those stars and their lines are drawn in gold: Þjazi's
   eyes, the wolf's jaw, Lokabrenna, Frigg's distaff, the Wagon. The rest are the Greek constellations,
   in ice. Where each map sits and its size are composed; nothing is written on the sky, and tapping a map
   opens its record in the panel.

   WyrdSky.prepare(R, k)            build for a sky of radius scale R (scene units)
   WyrdSky.draw(ctx, pole, θ, sel)   draw the sky about the pole (turned by θ) and the maps
   WyrdSky.hit(x, y)                the map at a scene point, or null
   WyrdSky.figure(id)               its record, for the panel                                          */
(function () {
"use strict";
const D = window.WYRD_SKY_DATA, RAD = Math.PI / 180, TAU = Math.PI * 2;
if (!D) { window.WyrdSky = null; return; }

const NORSE = "norse", GREEK = "greek";
const LOOK = { [NORSE]: { line: "255,196,106", star: "255,226,170" }, [GREEK]: { line: "150,215,255", star: "226,240,255" } };
const GREEK_NOTE = "The constellation as the Greeks drew it; Ptolemy lists it in the Almagest.";

/* at: the star the map is drawn about [RA, Dec]; iau: its constellation's lines; mark: for a Norse name,
   the named stars' own lines, in degrees about that star (x west to the right, y north up) */
const FIGS = [
  { id: "eyes", kind: NORSE, name: "Þjaza augu", gloss: "Þjazi's eyes", tag: "Eddic", at: [113.65, 31.89], iau: "Gem",
    stars: "Castor and Pollux, in Gemini", note: "After the giant Þjazi was killed, Odin threw his eyes up into the sky and made two stars of them (Skáldskaparmál). In Hárbarðsljóð it is Thor who says he cast them up. Neither says which stars; Castor and Pollux, two equal stars side by side, is a modern reading.", mark: [[0, 0, -2.3, -3.9]] },
  { id: "wolf", kind: NORSE, name: "Úlfs kjǫptr", gloss: "the wolf's jaw", tag: "medieval Icelandic", at: [67.15, 19.18], iau: "Tau",
    stars: "the Hyades, with Aldebaran, in Taurus", note: "A 12th-century Icelandic glossary (GKS 1812 4to) gives ulfs keptr, the wolf's jaw, for the Hyades, the V of stars that opens toward Aldebaran; a 14th-century list repeats it as vlfs kiopt. It does not say which wolf.", mark: [[-1.7, -2.7, 0, -3.3, 2.1, -3.6, 1.3, -1.6, 0, 0]] },
  { id: "loki", kind: NORSE, name: "Lokabrenna", gloss: "Loki's brand", tag: "later Scandinavian", at: [101.29, -16.72], iau: "CMa",
    stars: "Sirius, in Canis Major", note: "Lokabrenna, Loki's brand or Loki's burning, is a Scandinavian name for Sirius. It comes down in later tradition (Rydberg gives it in 1889) and is not in the Eddas.", mark: [[0, 0]] },
  { id: "distaff", kind: NORSE, name: "Friggerock", gloss: "Frigg's distaff", tag: "Swedish folk", at: [84.05, -1.20], iau: "Ori",
    stars: "Orion's belt: Alnitak, Alnilam, Mintaka", note: "Friggerock, Frigg's distaff, is a Swedish folk name for the three stars of Orion's belt, recorded in later folk tradition. The oldest Norse name for this part of the sky is in the 12th-century Icelandic glossary (GKS 1812 4to), which calls Orion fiskikarlar, the fishermen.", mark: [[-1.1, -0.7, 0, 0, 1.1, 0.9]] },
  { id: "wagon", kind: NORSE, name: "Karlavagnen", gloss: "the Wagon", tag: "Scandinavian folk", at: [183.86, 57.03], iau: "UMa",
    stars: "the seven bright stars of Ursa Major", note: "Karlavagnen in Swedish, Karlsvognen in Danish: the man's wagon, the folk name across Scandinavia for these seven stars. The bowl is the wagon's box, the handle its shaft.", mark: [[0, 0, 9.8, 4.7, 10.0, -0.7, 2.9, -3.3, 0, 0, -5.3, -1.1, -9.3, -2.1, -12.5, -7.7]] },
  { id: "swan", kind: GREEK, name: "Cygnus", gloss: "the swan", tag: "Greek constellation", at: [305.56, 40.26], iau: "Cyg", stars: "Deneb, Sadr, Albireo" },
  { id: "lyre", kind: GREEK, name: "Lyra", gloss: "the lyre", tag: "Greek constellation", at: [279.23, 38.78], iau: "Lyr", stars: "Vega, Sheliak, Sulafat" },
  { id: "eagle", kind: GREEK, name: "Aquila", gloss: "the eagle", tag: "Greek constellation", at: [297.70, 8.87], iau: "Aql", stars: "Altair, Tarazed, Alshain" },
  { id: "dragon", kind: GREEK, name: "Draco", gloss: "the dragon", tag: "Greek constellation", at: [211.10, 64.38], iau: "Dra", stars: "Thuban, Eltanin, Rastaban" },
  { id: "horse", kind: GREEK, name: "Pegasus", gloss: "the winged horse", tag: "Greek constellation", at: [346.19, 15.21], iau: "Peg", stars: "the Great Square: Markab, Scheat, Algenib, with Alpheratz" },
  { id: "lion", kind: GREEK, name: "Leo", gloss: "the lion", tag: "Greek constellation", at: [152.09, 11.97], iau: "Leo", stars: "Regulus, Algieba, Denebola" },
  { id: "queen", kind: GREEK, name: "Cassiopeia", gloss: "the queen", tag: "Greek constellation", at: [14.18, 60.72], iau: "Cas", stars: "Schedar, Caph, Navi, Ruchbah, Segin" },
];

/* where each map sits round the tree: centre x, y, width and height in the eye's scene (1000 × 1280) */
const SLOT = {
  wagon:  [160, 118, 280, 190],  queen: [356, 64, 100, 92],  eyes: [500, 56, 150, 100],  dragon: [832, 122, 300, 196],
  swan:   [82, 395, 150, 185],   eagle: [918, 395, 150, 185],
  distaff:[52, 700, 96, 210],    lyre:  [961, 702, 70, 160],
  horse:  [168, 995, 300, 205],  lion:  [834, 995, 300, 195],
  loki:   [128, 1236, 240, 76],  wolf:  [872, 1236, 232, 84],
};

/* ---------------- geometry ---------------- */
let R = 325, built = null;
const proj = (ra, dec) => { const r = 2 * R * Math.tan((90 - dec) / 2 * RAD), a = ra * RAD; return [-r * Math.sin(a), r * Math.cos(a)]; };
const pairs = a => { const p = []; for (let i = 0; i < a.length; i += 2) p.push([a[i], a[i + 1]]); return p; };
/* a star's place about the map's own star, in degrees (x west to the right, y north up) */
const local = (f, ra, dec) => [-(((ra - f.at[0] + 540) % 360) - 180) * Math.cos(f.at[1] * RAD), dec - f.at[1]];

function buildFigure(f){
  const [sx, sy, sw, sh] = SLOT[f.id] || [500, 640, 200, 200];
  const lines = (D.lines[f.iau] || []).map(seg => pairs(seg).map(([ra, dec]) => local(f, ra, dec)));
  const marks = (f.mark || []).map(pairs);
  const all = [...lines.flat(), ...marks.flat()], xs = all.map(p => p[0]), ys = all.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const S = Math.min(sw / Math.max(1, x1 - x0), sh / Math.max(1, y1 - y0)) * .9, mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
  const scene = ([x, y]) => [sx + (x - mx) * S, sy - (y - my) * S];
  const box = { x0: sx - sw / 2, x1: sx + sw / 2, y0: sy - sh / 2, y1: sy + sh / 2 };
  /* every star in the window, in its true place */
  const stars = [], hot = marks.flat().map(scene);
  for (let i = 0; i < D.stars.length; i += 3){
    const [lx, ly] = local(f, D.stars[i], D.stars[i + 1]); if (Math.abs(lx) > 70 || Math.abs(ly) > 70) continue;
    const [x, y] = scene([lx, ly]); if (x < box.x0 - 8 || x > box.x1 + 8 || y < box.y0 - 8 || y > box.y1 + 8) continue;
    stars.push({ x, y, m: D.stars[i + 2], ph: (i * 7.31) % 1, named: hot.some(([hx, hy]) => Math.hypot(hx - x, hy - y) < 1.5) });
  }
  return { f, lines: lines.map(l => l.map(scene)), marks: marks.map(l => l.map(scene)), stars, box, c: [sx, sy], S, place: (ra, dec) => scene(local(f, ra, dec)) };
}

/* the sky behind the maps: the real stars, faint, and the Milky Way, about the pole above Asgard */
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

/* the maps' geometry alone, with no canvas (the tests use it) */
function build(r){ R = r; return FIGS.map(buildFigure); }

function prepare(r, k){
  built = { figs: build(r), stars: starPaths(), mw: milkyWay(k), k };
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
  const stroke = (list, rgb, a, w) => { ctx.strokeStyle = `rgba(${rgb},${a})`; ctx.lineWidth = w / sz; ctx.beginPath();
    for (const s of list) s.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.stroke(); };
  for (const G of built.figs){
    const on = sel === G.f.id, L = LOOK[G.f.kind];
    /* the figure's lines: the constellation faint, a Norse name's own stars in gold */
    stroke(G.lines, G.f.kind === NORSE ? LOOK[GREEK].line : L.line, on ? .7 : .38, on ? 1.3 : 1);
    if (G.marks.some(m => m.length > 1)){ ctx.save(); ctx.shadowColor = `rgba(${L.line},.9)`; ctx.shadowBlur = 6; stroke(G.marks, L.line, on ? 1 : .8, on ? 2 : 1.6); ctx.restore(); }
    ctx.globalCompositeOperation = "lighter";
    for (const s of G.stars){
      const r = Math.max(.6, 3.1 - s.m * .55), tint = s.named ? L.line : L.star;
      if (s.m < 2.8 || s.named){ const a = .55 + .45 * Math.sin(time * 1.3 + s.ph * 40), gl = r * (s.named ? 5.5 : 4);
        const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, gl); g.addColorStop(0, `rgba(${tint},${(s.named ? .7 : .45) * a})`); g.addColorStop(1, `rgba(${tint},0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s.x, s.y, gl, 0, TAU); ctx.fill();
        if (s.m < 1.8){ const l = (3 - s.m) * 3.6 * (.75 + .25 * a); ctx.strokeStyle = `rgba(${tint},${.5 * a})`; ctx.lineWidth = .8 / sz;
          ctx.beginPath(); ctx.moveTo(s.x - l, s.y); ctx.lineTo(s.x + l, s.y); ctx.moveTo(s.x, s.y - l); ctx.lineTo(s.x, s.y + l); ctx.stroke(); } }
      ctx.fillStyle = `rgba(${tint},${s.m < 3 ? 1 : s.m < 4 ? .78 : .5})`; ctx.beginPath(); ctx.arc(s.x, s.y, r, 0, TAU); ctx.fill();
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

window.WyrdSky = { prepare, build, draw, hit, figure, FIGS, SLOT, at: (ra, dec) => proj(ra, dec), get built(){ return built; } };
})();
