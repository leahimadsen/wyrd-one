'use strict';
/* ============================================================
   THE HARMONIC BODY
   The proportional figure with its seven stations, the planet
   that feeds each one, the two zodiacs around it and the two
   rave definitions laid over it. Tap a station (or its planet)
   to wake it: the feeding planet's current runs down its thread
   into the station, then along the axis from the last station
   woken. Drag to turn the figure; the three layers sit at
   different depths, so they part as it turns.
   Depends on viz.js for STATIONS, NAKSHATRA, ENGINE, NAK_ARC,
   GLYPH, HOUSES, HOUSE_ONE_ANGLE, norm, signOf, degIn, houseOf, Sound.
   ============================================================ */
(() => {
const NS = "http://www.w3.org/2000/svg";
const FIGURE = `<g class="geom">
              <circle cx="450" cy="380" r="300"/>
              <rect x="200" y="180" width="500" height="500"/>
            </g>
            <g class="geom-faint">
              <line x1="200" y1="244" x2="700" y2="244"/>
              <line x1="200" y1="266" x2="700" y2="266"/>
              <line x1="176" y1="380" x2="724" y2="380"/>
              <line x1="200" y1="430" x2="700" y2="430"/>
              <line x1="232" y1="556" x2="668" y2="556"/>
            </g>
            <g class="fig-second">
              <path d="M400,258 C382,247 352,229 327,216 C305,205 282,197 263,191 C250,187 237,183 228,179"/>
              <path d="M229,188 C243,193 251,197 258,204 C277,215 300,228 317,238 C339,250 367,270 387,289"/>
              <path d="M228,178 C219,171 209,167 201,167 C195,167 193,171 199,175 C193,176 193,180 199,182 C195,184 197,187 203,188 C211,189 221,187 228,185"/>
              <path d="M500,258 C518,247 548,229 573,216 C595,205 618,197 637,191 C650,187 663,183 672,179"/>
              <path d="M671,188 C657,193 649,197 642,204 C623,215 600,228 583,238 C561,250 533,270 513,289"/>
              <path d="M672,178 C681,171 691,167 699,167 C705,167 707,171 701,175 C707,176 707,180 701,182 C705,184 703,187 697,188 C689,189 679,187 672,185"/>
              <path d="M396,420 C381,448 357,486 331,520 C313,544 296,572 281,599"/>
              <path d="M447,438 C433,464 411,498 387,532 C367,560 345,586 320,607"/>
              <path d="M281,599 C273,605 263,609 257,613 C252,616 255,620 261,621 C271,622 285,622 295,620 C301,618 303,612 301,606"/>
              <path d="M504,420 C519,448 543,486 569,520 C587,544 604,572 619,599"/>
              <path d="M453,438 C467,464 489,498 513,532 C533,560 555,586 580,607"/>
              <path d="M619,599 C627,605 637,609 643,613 C648,616 645,620 639,621 C629,622 615,622 605,620 C599,618 597,612 599,606"/>
            </g>
            <g class="fig">
          <path d="M450,244 C442,244 435,239 431,232 C427,226 424,219 422,211 C416,209 412,204 412,197 C411,188 419,181 431,178 C437,176 444,175 450,175 C456,175 463,176 469,178 C481,181 489,188 488,197 C488,204 484,209 478,211 C476,219 473,226 469,232 C465,239 458,244 450,244 Z"/>
          <path d="M412,196 C400,186 402,167 416,159 C428,152 440,150 450,150 C460,150 472,152 484,159 C498,167 500,186 488,196"/>
          <path d="M414,206 C403,204 395,194 397,181"/>
          <path d="M486,206 C497,204 505,194 503,181"/>
          <path d="M414,204 C409,214 409,226 415,236"/>
          <path d="M486,204 C491,214 491,226 485,236"/>
          <path d="M436,241 C434,249 432,255 428,259 C420,263 404,264 392,268"/>
          <path d="M464,241 C466,249 468,255 472,259 C480,263 496,264 508,268"/>
          <path d="M392,268 C385,272 381,277 382,284 C384,293 388,299 393,303 C389,311 386,320 388,332 C390,345 396,355 400,366 C403,375 404,381 403,389 C401,399 395,405 393,415 C392,426 400,433 410,437 C424,441 436,444 444,451 C447,454 453,454 456,451 C464,444 476,441 490,437 C500,433 508,426 507,415 C505,405 499,399 497,389 C496,381 497,375 500,366 C504,355 510,345 512,332 C514,320 511,311 507,303 C512,299 516,293 518,284 C519,277 515,272 508,268"/>
          <path d="M392,266 C376,261 360,258 344,257 C330,256 320,257 313,258 C296,258 272,257 250,257"/>
          <path d="M250,271 C272,272 296,274 313,275 C323,276 333,278 345,282 C361,287 378,293 394,301"/>
          <path d="M250,257 C240,254 228,252 218,252 C206,251 194,252 184,254 C176,256 175,259 182,261 C172,262 171,265 180,267 C173,269 175,272 183,273 C177,275 181,277 190,277 C202,277 214,276 224,274 C236,272 245,270 250,269"/>
          <path d="M508,266 C524,261 540,258 556,257 C570,256 580,257 587,258 C604,258 628,257 650,257"/>
          <path d="M650,271 C628,272 604,274 587,275 C577,276 567,278 555,282 C539,287 522,293 506,301"/>
          <path d="M650,257 C660,254 672,252 682,252 C694,251 706,252 716,254 C724,256 725,259 718,261 C728,262 729,265 720,267 C727,269 725,272 717,273 C723,275 719,277 710,277 C698,277 686,276 676,274 C664,272 655,270 650,269"/>
          <path d="M396,437 C390,453 388,473 391,494 C394,514 400,536 404,556 C407,569 404,580 402,590 C401,604 406,626 410,652"/>
          <path d="M443,450 C446,466 446,482 443,500 C441,519 438,538 436,556 C434,570 437,582 439,592 C440,608 434,634 430,652"/>
          <path d="M410,653 C410,662 407,669 400,674 C392,679 383,681 378,683 C375,685 379,686 386,686 C400,686 417,685 429,684 C433,681 433,670 430,653"/>
          <path d="M504,437 C510,453 512,473 509,494 C506,514 500,536 496,556 C493,569 496,580 498,590 C499,604 494,626 490,652"/>
          <path d="M457,450 C454,466 454,482 457,500 C459,519 462,538 464,556 C466,570 463,582 461,592 C460,608 466,634 470,652"/>
          <path d="M490,653 C490,662 493,669 500,674 C508,679 517,681 522,683 C525,685 521,686 514,686 C500,686 483,685 471,684 C467,681 467,670 470,653"/>
            </g>
            <g class="fig-muscle">
          <path d="M438,244 C434,252 428,258 421,262"/>
          <path d="M462,244 C466,252 472,258 479,262"/>
          <path d="M430,258 C416,262 404,266 396,271"/>
          <path d="M470,258 C484,262 496,266 504,271"/>
          <path d="M392,270 C387,278 386,288 390,296"/>
          <path d="M508,270 C513,278 514,288 510,296"/>
          <path d="M398,278 C404,282 410,285 415,286"/>
          <path d="M502,278 C496,282 490,285 485,286"/>
          <path d="M400,282 C410,300 424,310 440,312 C446,313 449,312 450,309"/>
          <path d="M500,282 C490,300 476,310 460,312 C454,313 451,312 450,309"/>
          <path d="M406,292 C416,298 428,302 438,302"/>
          <path d="M494,292 C484,298 472,302 462,302"/>
          <path d="M392,312 C397,315 401,319 404,323"/>
          <path d="M391,321 C396,324 400,328 403,332"/>
          <path d="M392,330 C397,333 401,336 404,340"/>
          <path d="M508,312 C503,315 499,319 496,323"/>
          <path d="M509,321 C504,324 500,328 497,332"/>
          <path d="M508,330 C503,333 499,336 496,340"/>
          <path d="M450,318 C450,336 450,356 450,376"/>
          <path d="M430,326 C438,329 462,329 470,326"/>
          <path d="M429,344 C438,347 462,347 471,344"/>
          <path d="M430,362 C438,365 462,365 470,362"/>
          <path d="M404,344 C410,356 414,368 414,380"/>
          <path d="M496,344 C490,356 486,368 486,380"/>
          <path d="M406,392 C420,406 436,420 448,434"/>
          <path d="M494,392 C480,406 464,420 452,434"/>
          <path d="M400,276 C374,278 350,278 332,276"/>
          <path d="M500,276 C526,278 550,278 568,276"/>
          <path d="M316,264 C300,266 284,268 270,268"/>
          <path d="M584,264 C600,266 616,268 630,268"/>
          <path d="M404,452 C401,478 402,506 407,532"/>
          <path d="M436,452 C438,478 437,506 433,532"/>
          <path d="M496,452 C499,478 498,506 493,532"/>
          <path d="M464,452 C462,478 463,506 467,532"/>
          <path d="M410,552 C416,547 428,547 434,552 C428,562 416,562 410,552 Z"/>
          <path d="M490,552 C484,547 472,547 466,552 C472,562 484,562 490,552 Z"/>
          <path d="M407,572 C404,584 405,596 408,606"/>
          <path d="M434,566 C438,580 437,594 433,604"/>
          <path d="M493,572 C496,584 495,596 492,606"/>
          <path d="M466,566 C462,580 463,594 467,604"/>
          <path d="M419,600 C419,618 419,636 419,650"/>
          <path d="M481,600 C481,618 481,636 481,650"/>
          </g>
          <g class="fig-fine">
          <path d="M423,206 C429,202 438,202 444,205"/>
          <path d="M456,205 C462,202 471,202 477,206"/>
          <path d="M426,213 C431,209 440,209 445,213 C440,217 431,217 426,213 Z"/>
          <path d="M455,213 C460,209 469,209 474,213 C469,217 460,217 455,213 Z"/>
          <path d="M434,213 a2.4,2.4 0 1,0 .1,0"/>
          <path d="M466,213 a2.4,2.4 0 1,0 .1,0"/>
          <path d="M450,210 C449,218 447,225 446,229 C447,231 451,232 454,231"/>
          <path d="M444,231 C446,233 449,233 451,232 M456,231 C454,233 452,233 451,232"/>
          <path d="M441,238 C444,236 448,235 450,236 C452,235 456,236 459,238
          C456,241 452,242 450,242 C448,242 444,241 441,238 Z"/>
          <path d="M450,236 C450,237 450,238 450,239"/>
          <path d="M424,218 C426,224 429,229 433,232"/>
          <path d="M476,218 C474,224 471,229 467,232"/>
          <path d="M398,272 C416,266 433,264 450,264 C467,264 484,266 502,272"/>
          <path d="M450,276 C450,296 450,318 450,338"/>
          <path d="M404,286 C410,302 422,312 438,314 C444,315 448,313 450,310"/>
          <path d="M496,286 C490,302 478,312 462,314 C456,315 452,313 450,310"/>
          <path d="M414,332 C424,336 434,338 442,338"/>
          <path d="M486,332 C476,336 466,338 458,338"/>
          <path d="M450,344 C450,360 450,368 450,374"/>
          <path d="M450,388 C450,402 450,414 450,424"/>
          <path d="M428,348 C428,356 428,364 429,370"/>
          <path d="M472,348 C472,356 472,364 471,370"/>
          <path d="M400,398 C416,414 484,414 500,398"/>
          <path d="M416,424 C428,433 472,433 484,424"/>
          <path d="M183,255 C194,256 206,257 216,258"/>
          <path d="M181,261 C193,262 207,264 218,265"/>
          <path d="M180,267 C192,268 206,270 217,271"/>
          <path d="M717,255 C706,256 694,257 684,258"/>
          <path d="M719,261 C707,262 693,264 682,265"/>
          <path d="M720,267 C708,268 694,270 683,271"/>
          <path d="M402,556 C412,560 428,560 438,556"/>
          <path d="M498,556 C488,560 472,560 462,556"/>
            </g>`;

/* ---------- Human Design centres, as the console drew them on the body ---------- */
const HB_CENTRES = {
  head:  { label:"Head",   gates:[64,61,63] },
  ajna:  { label:"Ajna",   gates:[47,24,4,17,43,11] },
  throat:{ label:"Throat", gates:[62,23,56,35,12,45,33,8,31,20,16] },
  g:     { label:"G",      gates:[1,13,25,46,2,15,10,7] },
  heart: { label:"Heart",  gates:[21,40,26,51] },
  spleen:{ label:"Spleen", gates:[48,57,44,50,32,28,18] },
  solar: { label:"Solar",  gates:[36,22,37,6,49,55,30] },
  sacral:{ label:"Sacral", gates:[34,5,14,29,59,9,3,42,27] },
  root:  { label:"Root",   gates:[53,60,52,19,39,41,58,38,54] }
};
const HB_CHANNELS = [[1,8],[2,14],[3,60],[4,63],[5,15],[6,59],[7,31],[9,52],[10,20],[10,34],
  [10,57],[11,56],[12,22],[13,33],[16,48],[17,62],[18,58],[19,49],[20,34],[20,57],[21,45],
  [23,43],[24,61],[25,51],[26,44],[27,50],[28,38],[29,46],[30,41],[32,54],[34,57],[35,36],
  [37,40],[39,55],[42,53],[47,64]];
const HB_GATE_CENTRE = {};
for (const k in HB_CENTRES) for (const g of HB_CENTRES[k].gates) HB_GATE_CENTRE[g] = k;
const HB_GEOM = {
  head:  { x:450, y:172, shape:"tri-up",    s:25 },
  ajna:  { x:450, y:212, shape:"tri-down",  s:23 },
  throat:{ x:450, y:254, shape:"square",    s:27 },
  g:     { x:450, y:308, shape:"diamond",   s:26 },
  heart: { x:497, y:322, shape:"tri-left",  s:17 },
  spleen:{ x:396, y:346, shape:"tri-right", s:20 },
  solar: { x:504, y:356, shape:"tri-left",  s:20 },
  sacral:{ x:450, y:404, shape:"square",    s:27 },
  root:  { x:450, y:456, shape:"square",    s:27 }
};
function shape(g){
  const { x, y, s } = g, h = s / 2;
  switch (g.shape){
    case "tri-up":    return `M${x},${y-h} L${x+h},${y+h} L${x-h},${y+h} Z`;
    case "tri-down":  return `M${x},${y+h} L${x+h},${y-h} L${x-h},${y-h} Z`;
    case "tri-left":  return `M${x-h},${y} L${x+h},${y-h} L${x+h},${y+h} Z`;
    case "tri-right": return `M${x+h},${y} L${x-h},${y-h} L${x-h},${y+h} Z`;
    case "diamond":   return `M${x},${y-h} L${x+h},${y} L${x},${y+h} L${x-h},${y} Z`;
    default:          return `M${x-h},${y-h} L${x+h},${y-h} L${x+h},${y+h} L${x-h},${y+h} Z`;
  }
}
const gatesOf = rave => [rave.personality, rave.design].flatMap(col => Object.values(col).map(v => v.gate));
/* which way the current runs along a live channel, shared by every bodygraph on the site
   (and by wyrd/bodygraph.py): toward the throat along the circuit, from the centre
   farther from it to the nearer; where the circuit doesn't decide, toward the throat's
   place in the body. */
const THROAT_GAP = { throat: 0, ajna: 82, g: 92, heart: 122, head: 154, spleen: 182, solar: 182, sacral: 210, root: 300 };
function throatDist(gates){
  const have = new Set(gates), adj = {};
  for (const k in HB_CENTRES) adj[k] = new Set();
  for (const [a, b] of HB_CHANNELS) if (have.has(a) && have.has(b)){ adj[HB_GATE_CENTRE[a]].add(HB_GATE_CENTRE[b]); adj[HB_GATE_CENTRE[b]].add(HB_GATE_CENTRE[a]); }
  const dist = { throat: 0 }, q = ["throat"];
  while (q.length){ const c = q.shift(); for (const n of adj[c]) if (!(n in dist)){ dist[n] = dist[c] + 1; q.push(n); } }
  return dist;
}
function runsFrom(dist, c1, c2){            // true when the current runs c1 → c2
  const d1 = dist[c1] ?? 99, d2 = dist[c2] ?? 99;
  return d1 > d2 || (d1 === d2 && THROAT_GAP[c1] >= THROAT_GAP[c2]);
}
function defined(gates){
  const have = new Set(gates), out = new Set();
  for (const [a, b] of HB_CHANNELS) if (have.has(a) && have.has(b)){ out.add(HB_GATE_CENTRE[a]); out.add(HB_GATE_CENTRE[b]); }
  return out;
}

/* ---------- geometry ---------- */
const ZC = 450;
const R_TROP_OUT = 398, R_TROP_IN = 372, R_SID_OUT = 366, R_SID_IN = 340, R_NAK_OUT = 338, R_NAK_IN = 316;
const zp = (r, d) => [ZC + r * Math.cos(d * Math.PI / 180), ZC + r * Math.sin(d * Math.PI / 180)];
const f2 = n => n.toFixed(2);
function band(ri, ro, a0, a1){
  const [x1,y1] = zp(ro, a0), [x2,y2] = zp(ro, a1), [x3,y3] = zp(ri, a1), [x4,y4] = zp(ri, a0);
  const L = ((a1 - a0 + 360) % 360) > 180 ? 1 : 0;
  return `M${f2(x1)},${f2(y1)} A${ro},${ro} 0 ${L} 1 ${f2(x2)},${f2(y2)} L${f2(x3)},${f2(y3)} A${ri},${ri} 0 ${L} 0 ${f2(x4)},${f2(y4)} Z`;
}
function arc(r, a0, a1){
  const [x0,y0] = zp(r, a0), [x1,y1] = zp(r, a1);
  return `M${f2(x0)},${f2(y0)} A${r},${r} 0 ${((a1 - a0 + 360) % 360) > 180 ? 1 : 0} 1 ${f2(x1)},${f2(y1)}`;
}
const SIGN_GLYPH = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];

/* ---------- state ---------- */
let C = null, root = null, deck = null, read = null;
let woken = new Set(), last = null, nkFocus = null, showRave = false, showDharma = false, showZod = true, showTorus = true;
let scanIdx = 0, scanTimer = null;
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const pose = { tilt: 0, turn: 0 };
const cusp = () => Math.floor(norm(C.ascS) / 30) * 30;
const aSid = l => HOUSE_ONE_ANGLE + norm(norm(l) - cusp());
const aTrop = l => aSid(norm(l - C.ay));
const seatOf = b => STATIONS.find(s => s.feeder === b) || null;
const markXY = (b, i) => {
  const st = seatOf(b);
  if (st) return [st.x + (i % 2 === 0 ? -40 : 40), st.y - 6];
  return [450, b === "Rahu" ? 128 : 726];
};
const BODIES = () => Object.keys(GLYPH).filter(b => C.sid[b] != null);
/* the classical seven and the nodes stand on the body; the outer three ride the rings only */
const MARKS = () => ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"].filter(b => C.sid[b] != null);

/* ---------- layer 1: the two zodiacs ---------- */
function zodiacSVG(){
  const ay = C.ay;
  let o = `<circle class="arc trop" cx="450" cy="450" r="${R_TROP_OUT}"/><circle class="arc trop" cx="450" cy="450" r="${R_TROP_IN}"/>
    <circle class="arc sid" cx="450" cy="450" r="${R_SID_OUT}"/><circle class="arc sid" cx="450" cy="450" r="${R_SID_IN}"/>`;
  for (let i = 0; i < 12; i++){
    for (const [fr, ri, ro, a0] of [["trop", R_TROP_IN, R_TROP_OUT, aTrop(i * 30)], ["sid", R_SID_IN, R_SID_OUT, aSid(i * 30)]]){
      const [sx,sy] = zp(ri, a0), [ex,ey] = zp(ro, a0), [lx,ly] = zp((ri + ro) / 2, a0 + 15);
      o += `<line class="spoke ${fr}" x1="${f2(sx)}" y1="${f2(sy)}" x2="${f2(ex)}" y2="${f2(ey)}"/>
        <text class="sg ${fr}" x="${f2(lx)}" y="${f2(ly + 3)}">${SIGN_GLYPH[i]}</text>`;
    }
  }
  const [tnx,tny] = zp(R_TROP_OUT + 9, aTrop(0)), [snx,sny] = zp(R_SID_OUT - 6, aSid(0));
  o += `<text class="ring-name" x="${f2(tnx)}" y="${f2(tny)}" fill="#d9d4c4" opacity=".3">TROPICAL</text>
        <text class="ring-name" x="${f2(snx)}" y="${f2(sny)}" fill="#b8924a" opacity=".45">SIDEREAL</text>`;
  const a0 = aTrop(0);
  o += `<path class="ay-arc" d="${arc(R_SID_OUT + 4, a0, a0 + ay)}"/>`;
  const [ax,ayy] = zp(R_SID_OUT + 14, a0 + ay / 2);
  o += `<text class="ay-lbl" x="${f2(ax)}" y="${f2(ayy)}">AYANAMSA ${ay.toFixed(2)}°</text>`;
  for (let k = 0; k < 27; k++){
    const s0 = aSid(k * NAK_ARC), s1 = s0 + NAK_ARC, mid = s0 + NAK_ARC / 2;
    const [lx,ly] = zp((R_NAK_IN + R_NAK_OUT) / 2, mid), [tx1,ty1] = zp(R_NAK_IN, s0), [tx2,ty2] = zp(R_NAK_OUT, s0);
    let padas = "";
    for (let p = 1; p < 4; p++){
      const [p1x,p1y] = zp(R_NAK_IN, s0 + p * NAK_ARC / 4), [p2x,p2y] = zp(R_NAK_IN + 7, s0 + p * NAK_ARC / 4);
      padas += `<line class="pada" x1="${f2(p1x)}" y1="${f2(p1y)}" x2="${f2(p2x)}" y2="${f2(p2y)}"/>`;
    }
    const m = norm(mid), flip = m > 90 && m < 270;
    o += `<g class="znak" data-hb-nak="${k}" tabindex="0" role="button" aria-label="${NAKSHATRA[k][0]}">
      <path class="band" d="${band(R_NAK_IN, R_NAK_OUT, s0, s1)}"/>
      <line class="nk-tick" x1="${f2(tx1)}" y1="${f2(ty1)}" x2="${f2(tx2)}" y2="${f2(ty2)}"/>${padas}
      <text class="nk-lbl" x="${f2(lx)}" y="${f2(ly + 2)}" transform="rotate(${f2(flip ? m + 90 : m - 90)} ${f2(lx)} ${f2(ly)})">${NAKSHATRA[k][0].toUpperCase()}</text>
      <path class="arc" d="${arc(R_NAK_OUT, s0, s1)}" style="opacity:0"/></g>`;
  }
  BODIES().forEach((b, i) => {
    const a = aTrop(C.trop[b]), r = R_TROP_OUT + 12 + (i % 2) * 15;
    const [x,y] = zp(r, a), [sx,sy] = zp(R_TROP_OUT + 2, a);
    o += `<line class="zp-stem" x1="${f2(x)}" y1="${f2(y)}" x2="${f2(sx)}" y2="${f2(sy)}"/>
      <text class="zp" x="${f2(x)}" y="${f2(y + 3)}">${GLYPH[b]}</text>`;
  });
  return o;
}

/* ---------- layer 2: the figure, centres and thread ---------- */
/* the live channels as moving light between the centres, rising toward the throat */
function liveChannels(gates){ const have = new Set(gates); return HB_CHANNELS.filter(([a, b]) => have.has(a) && have.has(b)); }
function flowSVG(){
  const lr = showRave ? liveChannels(gatesOf(C.natal)).map(c => c.join("-")) : [];
  const ld = showDharma && C.dharma ? liveChannels(gatesOf(C.dharma)).map(c => c.join("-")) : [];
  const keys = [...new Set([...lr, ...ld])], bundle = {};
  const distR = throatDist(gatesOf(C.natal)), distD = C.dharma ? throatDist(gatesOf(C.dharma)) : {};
  let o = "";
  for (const k of keys){
    const [a, b] = k.split("-").map(Number), ca = HB_GATE_CENTRE[a], cb = HB_GATE_CENTRE[b];
    const pair = [ca, cb].sort().join("|"), i = (bundle[pair] = (bundle[pair] || 0) + 1) - 1;
    /* toward the throat (runsFrom), offset when several share a route */
    const [p, q] = runsFrom(lr.includes(k) ? distR : distD, ca, cb) ? [HB_GEOM[ca], HB_GEOM[cb]] : [HB_GEOM[cb], HB_GEOM[ca]];
    const len = Math.hypot(q.x - p.x, q.y - p.y) || 1, off = (i % 2 ? -1 : 1) * Math.ceil(i / 2) * 4;
    const nx = -(q.y - p.y) / len * off, ny = (q.x - p.x) / len * off;
    const cls = lr.includes(k) && ld.includes(k) ? "both" : lr.includes(k) ? "rave" : "dharma";
    const path = `M${(p.x + nx).toFixed(1)},${(p.y + ny).toFixed(1)} L${(q.x + nx).toFixed(1)},${(q.y + ny).toFixed(1)}`;
    o += `<path class="hb-chan ${cls}" d="${path}"><title>Channel ${a}–${b}</title></path>`;
    if (!reduce) for (let j = 0; j < 2; j++)
      o += `<circle class="hb-spark ${cls}" r="2.6"><animateMotion dur="${(len / 30).toFixed(2)}s" begin="${(j * len / 60).toFixed(2)}s" repeatCount="indefinite" path="${path}"/></circle>`;
  }
  return o;
}
function centresSVG(){
  const r = showRave ? defined(gatesOf(C.natal)) : new Set();
  const d = showDharma ? defined(gatesOf(C.dharma)) : new Set();
  let o = flowSVG();
  for (const k in HB_GEOM){
    const g = HB_GEOM[k], inR = r.has(k), inD = d.has(k);
    const cls = inR && inD ? "both" : inR ? "rave" : inD ? "dharma" : "undefined";
    o += `<g class="centre ${cls}"><path class="shape" d="${shape(g)}"/>
      <text class="lbl" x="${g.x}" y="${g.y + g.s / 2 + 9}">${HB_CENTRES[k].label}</text></g>`;
  }
  return o;
}

/* ---------- layer 3: stations, planets, and the current ---------- */
function stationsSVG(){
  let o = `<g class="thread"><line x1="450" y1="96" x2="450" y2="760"/>
    <circle class="cap" cx="450" cy="100" r="2.6"/><circle class="cap" cx="450" cy="756" r="2.6"/>
    <text x="450" y="88">RAHU</text><text x="450" y="778">KETU</text></g>
    <g class="hb-flow" id="hbFlow"></g>`;
  /* the planets, each tied by its thread to the station it feeds */
  MARKS().forEach((b, i) => {
    const st = seatOf(b), [x, y] = markXY(b, i), h = houseOf(C.sid[b], C.ascS);
    o += `<g class="g-mark" data-hb-graha="${b}" ${st ? `data-hb-station="${st.id}"` : ""} tabindex="0" role="button"
        aria-label="${b} in house ${h}${st ? ", feeds the " + st.station : ""}">
      ${st ? `<line class="thread" x1="${x}" y1="${y + 3}" x2="${st.x}" y2="${st.y}"/>` : ""}
      <circle class="ring" cx="${x}" cy="${y - 3}" r="9"/>
      <text class="gl" x="${x}" y="${y}">${GLYPH[b]}</text>
      <text class="gl sub" x="${x}" y="${y + 10}">H${h}</text>
      <circle cx="${x}" cy="${y - 3}" r="14" fill="transparent"/></g>`;
  });
  o += `<g class="stations" id="hbStations">`;
  for (const s of STATIONS){
    const dir = s.side === "L" ? -1 : 1, bendX = s.x + dir * 116, endX = s.x + dir * 172;
    o += `<g class="station" data-hb-station="${s.id}" tabindex="0" role="button" style="--band:${s.band}"
        aria-label="${s.station}, ${s.world}, fed by ${s.feeder}">
      <path class="lead" d="M${s.x + dir * 14},${s.y} L${bendX},${s.leadY} L${endX},${s.leadY}"/>
      <text class="tag" x="${endX + dir * 6}" y="${s.leadY - 5}" text-anchor="${s.side === "L" ? "end" : "start"}">${s.tag} · ${s.world}</text>
      <circle class="bloom" cx="${s.x}" cy="${s.y}" r="8"/>
      <circle class="halo" cx="${s.x}" cy="${s.y}" r="13"/>
      <circle class="ring" cx="${s.x}" cy="${s.y}" r="8"/>
      <circle class="core" cx="${s.x}" cy="${s.y}" r="2.2"/>
      ${s.axis ? "" : `<line class="bar" x1="${s.x - 13}" y1="${s.y}" x2="${s.x - 9}" y2="${s.y}"/><line class="bar" x1="${s.x + 9}" y1="${s.y}" x2="${s.x + 13}" y2="${s.y}"/>`}
      <circle cx="${s.x}" cy="${s.y}" r="16" fill="transparent"/></g>`;
  }
  return o + `</g>`;
}

/* ---------- the current ---------- */
function stream(x1, y1, x2, y2, color, ms, cls){
  const g = root.querySelector("#hbFlow");
  if (!g) return Promise.resolve();
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (reduce || len < 1) return Promise.resolve();
  const p = document.createElementNS(NS, "line");
  p.setAttribute("x1", x1); p.setAttribute("y1", y1); p.setAttribute("x2", x2); p.setAttribute("y2", y2);
  p.setAttribute("class", "hb-current " + (cls || ""));
  p.style.stroke = color;
  const head = document.createElementNS(NS, "circle");
  head.setAttribute("r", "3.4"); head.setAttribute("class", "hb-head"); head.style.fill = color;
  g.append(p, head);
  return new Promise(done => {
    const t0 = performance.now();
    (function step(t){
      const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      head.setAttribute("cx", x1 + (x2 - x1) * e); head.setAttribute("cy", y1 + (y2 - y1) * e);
      p.style.strokeDashoffset = String(-t / 18);
      p.style.opacity = String(k < .85 ? .9 : .9 * (1 - (k - .85) / .15));
      if (k < 1) requestAnimationFrame(step);
      else { head.remove(); setTimeout(() => p.remove(), 60); done(); }
    })(t0);
  });
}

/* a standing current along the axis between woken stations */
function paintSpine(){
  const g = root.querySelector("#hbSpine");
  if (!g) return;
  const ys = STATIONS.filter(s => woken.has(s.id)).map(s => s.y);
  if (ys.length < 2){ g.innerHTML = ""; return; }
  const lit = STATIONS.filter(s => woken.has(s.id));
  let o = "";
  for (let i = 0; i < lit.length - 1; i++){
    const a = lit[i], b = lit[i + 1];
    o += `<line class="hb-spine" x1="450" y1="${a.y}" x2="450" y2="${b.y}" style="stroke:${b.band}"/>`;
  }
  g.innerHTML = o;
}

async function wake(id, opts){
  const s = STATIONS.find(x => x.id === id); if (!s) return;
  const quiet = opts && opts.quiet;
  const node = root.querySelector(`.station[data-hb-station="${id}"]`);
  const stG = root.querySelector("#hbStations");
  stG.classList.add("dimmed");
  root.querySelectorAll(".station.live").forEach(n => n.classList.remove("live"));
  node.classList.add("live");
  /* the feeder's current runs down its thread first */
  const i = MARKS().indexOf(s.feeder), [mx, my] = markXY(s.feeder, i);
  const mark = root.querySelector(`.g-mark[data-hb-graha="${s.feeder}"]`);
  if (mark) mark.classList.add("feeding");
  if (!quiet) Sound.chord(s.ratios.map(r => s.hz * r[0]));
  paintStation(s);
  const from = last ? STATIONS.find(x => x.id === last) : null;
  await Promise.all([
    stream(mx, my + 3, s.x, s.y, s.band, 1100, "feed"),
    from && from.id !== s.id ? stream(450, from.y, 450, s.y, s.band, 1400, "axis") : null
  ]);
  if (mark) setTimeout(() => mark.classList.remove("feeding"), 400);
  node.classList.remove("bloomed"); void node.getBBox(); node.classList.add("bloomed");
  woken.add(id); node.classList.add("woken");
  last = id;
  paintSpine();
}

function sleepAll(){
  stopScan();
  woken.clear(); last = null;
  root.querySelectorAll(".station").forEach(n => n.classList.remove("live", "woken", "bloomed"));
  root.querySelector("#hbStations").classList.remove("dimmed");
  paintSpine();
  read.innerHTML = idleRead();
}

/* the descent scan, crown to root, as the console ran it */
function stepScan(){
  if (scanIdx >= STATIONS.length){ stopScan(); return; }
  wake(STATIONS[scanIdx].id);
  scanIdx++;
  scanTimer = setTimeout(stepScan, 4200);
}
function stopScan(){
  clearTimeout(scanTimer); scanTimer = null;
  const b = root && root.querySelector("[data-hb-scan]");
  if (b){ b.classList.remove("on"); b.textContent = "Descent scan"; }
}

/* ---------- readouts ---------- */
function idleRead(){
  return `<p class="hb-idle">Tap a station, or the planet beside it, to wake it. The planet's current runs down its thread into the station it feeds. Wake a second and the current crosses the axis between them. Tap a mansion on the inner ring to isolate it.</p>`;
}
function paintStation(s){
  const supply = houseOf(C.sid[s.feeder], C.ascS), hh = HOUSES[supply - 1], pos = C.sid[s.feeder];
  const max = Math.max(...s.ratios.map(r => r[0]));
  const bars = s.ratios.map(([r, lab]) =>
    `<div class="hb-barrow"><div class="hb-track"><i style="width:${(r / max * 100).toFixed(1)}%;background:${s.band}"></i></div><span>${lab} · ${(s.hz * r).toFixed(1)} Hz</span></div>`).join("");
  read.innerHTML = `
    <div class="hb-card" style="--band:${s.band}">
      <div class="hb-chip">${s.roman} · ${s.place}</div>
      <h3>${s.world}</h3>
      <div class="hb-rom">${s.station} · ${s.bifrost}</div>
      <p class="kenning">${s.kenning}</p>
      <dl>
        <dt>Operator</dt><dd>${s.operator}<small>${s.opGloss}</small></dd>
        <dt>Fed by</dt><dd>${GLYPH[s.feeder]} ${s.feeder} · ${s.hz.toFixed(2)} Hz<small>Planetary ladder</small></dd>
        <dt>Supply line</dt><dd>House ${supply}${hh && hh.color ? " · " + hh.color : ""}<small>${s.feeder} at ${signOf(pos)} ${degIn(pos).toFixed(2)}°. This station eats that house's colour.</small></dd>
        <dt>Design centre</dt><dd>${s.hd}</dd>
      </dl>
      <div class="hb-ask"><b>Descent scan</b><p>${s.ask}</p></div>
      <div class="hb-bars"><h4>Chord · ratio staff</h4>${bars}</div>
      <button class="hb-btn" data-hb-replay="${s.id}">Sound the chord again</button>
    </div>`;
  drawBars();
}
/* the bars grow one after another, in step with the chord blooming */
function drawBars(){
  const rows = read.querySelectorAll(".hb-barrow");
  rows.forEach(r => r.classList.remove("drawn"));
  rows.forEach((r, i) => setTimeout(() => r.classList.add("drawn"), 60 + i * 90));
}
function paintNak(){
  root.querySelectorAll(".znak").forEach(n => {
    const on = nkFocus !== null && +n.dataset.hbNak === nkFocus;
    n.classList.toggle("lit", on); n.classList.toggle("dim", nkFocus !== null && !on);
  });
  if (nkFocus === null){ read.innerHTML = idleRead(); return; }
  const k = nkFocus, e = ENGINE[k], nk = NAKSHATRA[k], a0 = k * NAK_ARC, a1 = a0 + NAK_ARC;
  const padaOf = l => Math.floor((norm(l) % NAK_ARC) / (NAK_ARC / 4)) + 1;
  const inside = BODIES().filter(b => { const s = norm(C.sid[b]); return s >= a0 && s < a1; });
  const asc = norm(C.ascS) >= a0 && norm(C.ascS) < a1;
  const here = (asc ? [`Lagna · pada ${padaOf(C.ascS)}`] : []).concat(inside.map(b => `${GLYPH[b]} ${b} · pada ${padaOf(C.sid[b])}`));
  read.innerHTML = `
    <div class="hb-card" style="--band:var(--jade)">
      <div class="hb-chip">Mansion ${k + 1} of 27</div>
      <h3>${nk[0]}</h3>
      <div class="hb-rom">${signOf(a0)} ${degIn(a0).toFixed(0)}° to ${signOf(a1)} ${degIn(a1).toFixed(0)}° · lord ${nk[1]} · ${nk[4]}</div>
      <dl>
        ${e && e[1] ? `<dt>Shakti</dt><dd>${e[1]}<small>${e[2]}</small></dd>` : ""}
        ${e && e[3] ? `<dt>Above / below</dt><dd>${e[3]} over ${e[4]}</dd>` : ""}
        ${e && e[5] ? `<dt>Result</dt><dd>${e[5]}</dd>` : ""}
        <dt>Standing here</dt><dd>${here.length ? here.join("<br>") : "nothing in this chart"}</dd>
      </dl>
    </div>`;
}

/* ---------- moving it ---------- */
function setPose(tilt, turn, animate){
  pose.tilt = Math.max(-78, Math.min(0, tilt));
  pose.turn = Math.max(-50, Math.min(50, turn));
  deck.style.transition = animate ? "transform 1200ms var(--ease)" : "none";
  deck.style.transform = `rotateX(${pose.tilt}deg) rotateY(${pose.turn}deg)`;
  root.querySelectorAll("[data-hb-view]").forEach(b => {
    const v = b.dataset.hbView;
    b.classList.toggle("on", (v === "up" && pose.tilt === 0 && pose.turn === 0) || (v === "tilt" && pose.tilt === -52 && pose.turn === 0));
  });
}
function bindDrag(stage){
  let start = null;
  stage.addEventListener("pointerdown", e => {
    start = { x: e.clientX, y: e.clientY, tilt: pose.tilt, turn: pose.turn, moved: false, touch: e.pointerType === "touch" };
  });
  addEventListener("pointermove", e => {
    if (!start) return;
    const dx = e.clientX - start.x, dy = e.clientY - start.y;
    if (!start.moved && Math.hypot(dx, dy) < 6) return;
    if (!start.moved){
      /* on a phone, a mostly vertical drag is a page scroll, so only turn */
      if (start.touch && Math.abs(dy) > Math.abs(dx)){ start = null; return; }
      start.moved = true; stage.classList.add("dragging");
    }
    setPose(start.touch ? start.tilt : start.tilt - dy * 0.35, start.turn + dx * 0.25, false);
  }, { passive: true });
  const end = () => {
    if (start && start.moved){ stage.dataset.justDragged = "1"; setTimeout(() => delete stage.dataset.justDragged, 50); }
    stage.classList.remove("dragging"); start = null;
  };
  addEventListener("pointerup", end); addEventListener("pointercancel", end);
}

/* ---------- the torus field ----------
   The body's own field: it bursts from the crown, falls around both sides in
   nested loops, is drawn back in beneath the feet and rises up the central axis
   to the crown again. Bursts mark where it breaks out: crown, root and feet. */
const AXIS = { x: 450, crown: 150, root: 445, feet: 640 };
function torusSVG(){
  const { x, crown, feet } = AXIS, loops = [95, 150, 205, 262, 320];
  let o = `<defs><radialGradient id="hbBurst"><stop offset="0" stop-color="rgba(222,236,228,.9)"/><stop offset=".35" stop-color="rgba(95,156,134,.45)"/>
    <stop offset="1" stop-color="rgba(95,156,134,0)"/></radialGradient></defs>`;
  loops.forEach((w, i) => {
    for (const side of [1, -1]){
      const X = k => (x + side * w * k).toFixed(1);
      const d = `M${x},${crown} C${X(.55)},${crown - 120 + i * 8} ${X(1.12)},${crown + 40} ${X(1)},${(crown + feet) / 2} C${X(.92)},${feet - 40} ${X(.5)},${feet + 70 - i * 6} ${x},${feet}`;
      o += `<path d="${d}" class="tf-line"/><path d="${d}" pathLength="200" class="tf-flow" style="animation-delay:${(-i * 1.1 - (side > 0 ? 0 : .55)).toFixed(2)}s"/>`;
    }
  });
  o += `<path d="M${x},${feet} L${x},${crown}" class="tf-line axis"/><path d="M${x},${feet} L${x},${crown}" pathLength="200" class="tf-flow axis"/>`;
  for (const [y, r] of [[crown, 46], [AXIS.root, 30], [feet, 40]])
    o += `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#hbBurst)" class="tf-burst"/>`;
  return o;
}

/* ---------- mount ---------- */
function mount(host, chart){
  C = chart; root = host; woken = new Set(); last = null; nkFocus = null; stopScan();
  host.classList.add("hb");
  host.innerHTML = `
    <p class="hb-intro">The same body seen another way. The Harmonic Body is a proportional figure with seven stations from crown to root, each fed by one of your planets, standing beside it on its own thread; the label under each planet is the house it stands in, which gives that station its colour. Your design's centres and live channels sit on the figure too, following the Birth / Dharma switch above. The seven stations and the nine design centres are different maps: the Heart station is not the Heart centre. Around the figure is its torus field, and the two zodiacs: tropical outside, sidereal inside, offset by the ayanamsa, with the twenty-seven mansions on the inner ring.</p>
    <div class="hb-ctl">
      <button class="hb-btn on" data-hb-view="up">Upright</button>
      <button class="hb-btn" data-hb-view="tilt">Tilted</button>
      <button class="hb-btn on" data-hb-toggle="zod" aria-pressed="true">Two zodiacs</button>
      <button class="hb-btn on" data-hb-toggle="torus" aria-pressed="true">Torus field</button>
      <button class="hb-btn" data-hb-scan>Descent scan</button>
      <button class="hb-btn" data-hb-clear>Clear</button>
    </div>
    <div class="hb-stage" id="hbStage">
      <div class="hb-deck" id="hbDeck">
        <svg class="hb-layer hb-zod" viewBox="0 0 900 900" aria-label="The two zodiacs around the body">${zodiacSVG()}</svg>
        <svg class="hb-layer hb-torus" viewBox="0 0 900 900" aria-hidden="true">${torusSVG()}</svg>
        <svg class="hb-layer hb-fig" viewBox="0 0 900 900" role="img" aria-label="The harmonic body">
          ${FIGURE}<g class="hb-centres" id="hbCentres">${centresSVG()}</g></svg>
        <svg class="hb-layer hb-top" viewBox="0 0 900 900" aria-label="The seven stations and the planets that feed them">
          <g id="hbSpine"></g>${stationsSVG()}</svg>
      </div>
    </div>
    <p class="hb-hint">Drag to turn the figure${matchMedia("(pointer:fine)").matches ? " and tip it back" : ""}. The rings, the body and the stations sit at different depths.</p>
    <div class="hb-strip" role="group" aria-label="The seven stations">${STATIONS.map(s =>
      `<button class="hb-chipbtn" data-hb-station="${s.id}" style="--band:${s.band}"><i></i>${s.roman} · ${s.station}<span>${GLYPH[s.feeder]} ${s.feeder}</span></button>`).join("")}</div>
    <div class="hb-read" id="hbRead" aria-live="polite">${idleRead()}</div>`;
  deck = host.querySelector("#hbDeck"); read = host.querySelector("#hbRead");
  host.querySelector(".hb-zod").classList.toggle("off", !showZod);
  host.querySelector(".hb-torus").classList.toggle("off", !showTorus);
  host.querySelector('[data-hb-toggle="torus"]').classList.toggle("on", showTorus);
  host.querySelector('[data-hb-toggle="torus"]').setAttribute("aria-pressed", showTorus);
  host.querySelector(".hb-centres").classList.toggle("on", showRave || showDharma);
  host.querySelector('[data-hb-toggle="zod"]').classList.toggle("on", showZod);
  setPose(0, 0, false);
  bindDrag(host.querySelector("#hbStage"));
}

/* one listener for the whole section */
document.addEventListener("click", e => {
  if (!root || !root.contains(e.target)) return;
  const stage = root.querySelector("#hbStage");
  if (stage && stage.dataset.justDragged) return;
  const t = e.target;
  const v = t.closest("[data-hb-view]");
  if (v){ setPose(v.dataset.hbView === "tilt" ? -52 : 0, 0, true); return; }
  const tg = t.closest("[data-hb-toggle]");
  if (tg){
    const k = tg.dataset.hbToggle;
    if (k === "zod"){ showZod = !showZod; root.querySelector(".hb-zod").classList.toggle("off", !showZod); tg.classList.toggle("on", showZod); tg.setAttribute("aria-pressed", showZod); root.classList.toggle("zod-on", showZod); return; }
    if (k === "torus"){ showTorus = !showTorus; root.querySelector(".hb-torus").classList.toggle("off", !showTorus); tg.classList.toggle("on", showTorus); tg.setAttribute("aria-pressed", showTorus); return; }
    if (k === "rave") showRave = !showRave; else showDharma = !showDharma;
    const on = k === "rave" ? showRave : showDharma;
    tg.classList.toggle("on", on); tg.setAttribute("aria-pressed", on);
    root.querySelector("#hbCentres").innerHTML = centresSVG();
    root.querySelector("#hbCentres").classList.toggle("on", showRave || showDharma);
    return;
  }
  if (t.closest("[data-hb-scan]")){
    if (scanTimer){ stopScan(); return; }
    sleepAll(); scanIdx = 0;
    const b = t.closest("[data-hb-scan]"); b.classList.add("on"); b.textContent = "Stop scan";
    stepScan(); return;
  }
  if (t.closest("[data-hb-clear]")){ nkFocus = null; paintNak(); sleepAll(); return; }
  const rp = t.closest("[data-hb-replay]");
  if (rp){ const s = STATIONS.find(x => x.id === rp.dataset.hbReplay); if (s){ Sound.chord(s.ratios.map(r => s.hz * r[0])); drawBars(); } return; }
  const st = t.closest("[data-hb-station]");
  if (st){ stopScan(); nkFocus = null; root.querySelectorAll(".znak").forEach(n => n.classList.remove("lit", "dim")); wake(st.dataset.hbStation); return; }
  const nk = t.closest("[data-hb-nak]");
  if (nk){ const k = +nk.dataset.hbNak; nkFocus = nkFocus === k ? null : k; paintNak(); return; }
});
document.addEventListener("keydown", e => {
  if (!root || !root.contains(e.target) || (e.key !== "Enter" && e.key !== " ")) return;
  const el = e.target.closest("g[data-hb-station], g[data-hb-nak]");
  if (el){ e.preventDefault(); el.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
});

/* the Your design land's switch: which design's centres and channels sit on the figure */
function setDesign(v){
  showRave = v !== "dharma"; showDharma = v !== "birth" && !!(C && C.dharma);
  const g = root && root.querySelector("#hbCentres"); if (!g) return;
  g.innerHTML = centresSVG(); g.classList.toggle("on", showRave || showDharma);
}
window.WyrdBody = { mount, setDesign, centres: HB_CENTRES, channels: HB_CHANNELS, runsFrom };
})();
