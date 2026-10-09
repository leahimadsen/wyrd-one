'use strict';
/* ============================================================
   THE DIVISIONAL CHARTS (vargas)
   Every sign split into N parts, each part mapped to a sign: D1 is the
   Rashi, D9 the navamsa, and so on to D60. The sixteen of Parashara use
   his own rules; D5, D6, D8 and D11, which he does not give, use the
   cyclical (parivritti) count. wyrd/vargas.py does the same arithmetic
   for the paid reading; tests/vargas_check.py proves they agree.
   - WyrdVargas.sign(lon, n): the sign index (0 = Aries) of a sidereal longitude in Dn
   - WyrdVargas.mount(host, C, { unknown }): the chart viewer, for Your chart
   - WyrdVargas.thread(host, C, { unknown }): from Rashi to Dharma, for Your design
   The words are drafts for The Völva to edit.
   ============================================================ */
(() => {
const { norm, GLYPH } = Wyrd.helpers;
const { esc } = WyrdCommon;
const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const AB = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"];
const LORD = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"];
const ELEMENT = ["Fire","Earth","Air","Water"];
const BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"];

/* [n, name, what it shows, how it is counted] */
const VARGAS = [
  [1,  "Rashi",          "the body and the whole life as it is lived"],
  [2,  "Hora",           "wealth, resources and what sustains you"],
  [3,  "Drekkana",       "siblings, courage and the will to begin"],
  [4,  "Chaturthamsa",   "home, land and settled fortune"],
  [5,  "Panchamsa",      "power, standing and recognition", "cyclical"],
  [6,  "Shashthamsa",    "health, illness and what you struggle against", "cyclical"],
  [7,  "Saptamsa",       "children, creation and what you pass on"],
  [8,  "Ashtamsa",       "sudden events, the hidden and long life", "cyclical"],
  [9,  "Navamsa",        "dharma, partnership and what the life ripens into"],
  [10, "Dasamsa",        "work, career and action in the world"],
  [11, "Rudramsa",       "gains, and the endings that make room for them", "cyclical"],
  [12, "Dwadasamsa",     "parents and lineage"],
  [16, "Shodasamsa",     "comforts, vehicles and ease"],
  [20, "Vimsamsa",       "spiritual practice and devotion"],
  [24, "Chaturvimsamsa", "learning and knowledge"],
  [27, "Bhamsa",         "strength, stamina and weak points"],
  [30, "Trimsamsa",      "misfortune and the shadow of character"],
  [40, "Khavedamsa",     "the mother's line and what it hands down"],
  [45, "Akshavedamsa",   "the father's line and character"],
  [60, "Shashtyamsa",    "past karma, the finest grain of the chart"],
];

/* ---------- the arithmetic ---------- */
function sign(lon, n){
  const L = norm(lon), s = Math.floor(L / 30), d = L - s * 30, odd = s % 2 === 0, mode = s % 3, el = s % 4;
  const part = Math.floor(d / (30 / n));
  const from = start => (start + part) % 12;
  switch (n){
    case 1:  return s;
    case 2:  return odd ? (d < 15 ? 4 : 3) : (d < 15 ? 3 : 4);                      // Leo (Sun) / Cancer (Moon)
    case 3:  return (s + 4 * part) % 12;
    case 4:  return (s + 3 * part) % 12;
    case 7:  return from(odd ? s : s + 6);
    case 9:  return from([0, 9, 6, 3][el]);                                         // fire Aries, earth Capricorn, air Libra, water Cancer
    case 10: return from(odd ? s : s + 8);
    case 12: return from(s);
    case 16: return from([0, 4, 8][mode]);                                          // movable Aries, fixed Leo, dual Sagittarius
    case 20: return from([0, 8, 4][mode]);                                          // movable Aries, fixed Sagittarius, dual Leo
    case 24: return from(odd ? 4 : 3);                                              // odd from Leo, even from Cancer
    case 27: return from([0, 3, 6, 9][el]);                                         // fire Aries, earth Cancer, air Libra, water Capricorn
    case 30: return odd ? (d < 5 ? 0 : d < 10 ? 10 : d < 18 ? 8 : d < 25 ? 2 : 6)  // Mars, Saturn, Jupiter, Mercury, Venus
                        : (d < 5 ? 1 : d < 12 ? 5 : d < 20 ? 11 : d < 25 ? 9 : 7); // Venus, Mercury, Jupiter, Saturn, Mars
    case 40: return from(odd ? 0 : 6);
    case 45: return from([0, 4, 8][mode]);
    case 60: return from(s);
    default: return Math.floor(norm(L * n) / 30);                                    // cyclical: D5, D6, D8, D11
  }
}

/* dignity by sign, as the vargas are read */
const EXALT = { Sun: 0, Moon: 1, Mercury: 5, Venus: 11, Mars: 9, Jupiter: 3, Saturn: 6 };
const OWN = { Sun: [4], Moon: [3], Mercury: [2, 5], Venus: [1, 6], Mars: [0, 7], Jupiter: [8, 11], Saturn: [9, 10] };
function dignityIn(b, s){
  if (!(b in EXALT)) return "";
  if (EXALT[b] === s) return "exalted";
  if ((EXALT[b] + 6) % 12 === s) return "debilitated";
  if (OWN[b].includes(s)) return "own sign";
  return "";
}
const RANK = { "exalted": 3, "own sign": 2, "": 1, "debilitated": 0 };

/* ---------- one chart, drawn South Indian style: the signs stay put, the planets move ---------- */
const CELL = { 11: [0, 0], 0: [0, 1], 1: [0, 2], 2: [0, 3], 10: [1, 0], 3: [1, 3], 9: [2, 0], 4: [2, 3], 8: [3, 0], 7: [3, 1], 6: [3, 2], 5: [3, 3] };
function grid(C, n, unknown){
  const by = {}; for (let s = 0; s < 12; s++) by[s] = [];
  for (const b of BODIES) by[sign(C.sid[b], n)].push(`<span class="vg-p${C.sid && dignityIn(b, sign(C.sid[b], n)) === "exalted" ? " ex" : dignityIn(b, sign(C.sid[b], n)) === "debilitated" ? " deb" : ""}" title="${b}">${GLYPH[b]}</span>`);
  const asc = unknown ? null : sign(C.ascS, n);
  const V = VARGAS.find(v => v[0] === n);
  let cells = "";
  for (let s = 0; s < 12; s++){
    const [r, c] = CELL[s];
    cells += `<div class="vg-cell${s === asc ? " asc" : ""}" style="grid-row:${r + 1};grid-column:${c + 1}">
      <small>${AB[s]}</small>${s === asc ? `<i class="vg-asc" title="Ascendant">Asc</i>` : ""}<div>${by[s].join(" ")}</div></div>`;
  }
  return `<div class="vg-grid" role="img" aria-label="D${n} ${V[1]}: ${BODIES.map(b => `${b} in ${SIGNS[sign(C.sid[b], n)]}`).join(", ")}${asc != null ? `, Ascendant in ${SIGNS[asc]}` : ""}">
    ${cells}<div class="vg-mid"><b>D${n}</b><span>${V[1]}</span></div></div>`;
}

function mount(host, C, { unknown } = {}){
  let n = 9;
  const draw = () => {
    const V = VARGAS.find(v => v[0] === n);
    const varg = BODIES.filter(b => sign(C.sid[b], n) === sign(C.sid[b], 1));
    const strong = BODIES.filter(b => ["exalted", "own sign"].includes(dignityIn(b, sign(C.sid[b], n))));
    host.querySelector(".vg-one").innerHTML = `${grid(C, n, unknown)}
      <div class="vg-say"><h4>D${n} · ${V[1]}</h4><p>The chart of ${V[2]}.${V[3] ? ` <span class="fine">Counted cyclically: Parashara gives no rule for D${n}, so each part follows the last around the zodiac.</span>` : ""}</p>
      ${n > 1 ? `<p>${varg.length ? `<b>Same sign as in your Rashi</b> (${n === 9 ? "vargottama" : "steady across the division"}): ${varg.map(b => `${GLYPH[b]} ${b}`).join(", ")}. What these are at birth, they stay in this part of life.` : "No planet keeps its Rashi sign here."}</p>` : ""}
      <p>${strong.length ? `<b>Strong here</b> (exalted or in its own sign): ${strong.map(b => `${GLYPH[b]} ${b} <small>(${dignityIn(b, sign(C.sid[b], n))})</small>`).join(", ")}.` : "No planet is exalted or in its own sign here."}</p>
      <p class="fine">Bright glyphs are exalted, dim ones debilitated.</p></div>`;
    host.querySelectorAll("[data-vg]").forEach(b => b.setAttribute("aria-pressed", +b.dataset.vg === n));
  };
  const all = `<div class="tw"><table class="vg-all"><caption>Every planet in every division. Bold: the same sign as in the Rashi.</caption>
    <tr><th></th>${VARGAS.map(v => `<th scope="col" title="${v[1]}: ${v[2]}">D${v[0]}</th>`).join("")}</tr>
    ${BODIES.map(b => `<tr><th scope="row">${GLYPH[b]} ${b}</th>${VARGAS.map(v => { const s = sign(C.sid[b], v[0]), dg = dignityIn(b, s);
      return `<td class="${s === sign(C.sid[b], 1) && v[0] > 1 ? "same" : ""}${dg ? " " + dg.replace(" ", "-") : ""}">${AB[s]}</td>`; }).join("")}</tr>`).join("")}
    ${unknown ? "" : `<tr><th scope="row">↑ Asc</th>${VARGAS.map(v => `<td>${AB[sign(C.ascS, v[0])]}</td>`).join("")}</tr>`}</table></div>`;
  host.innerHTML = `
    <p>The Rashi (D1) is your chart as you know it. Jyotish divides every sign again, into 2, 3, 4… up to 60 parts, and maps each part to a sign of its own. Each division is a chart of one part of life, read from the same moment.
    The navamsa (D9) matters most after the Rashi: it shows what the chart ripens into, and it is the chart your Dharma Design is built from.</p>
    ${unknown ? `<p class="unknown-note">Without a birth time there is no Ascendant in any of these, and the Moon's divisions may be off: it moves about 13° a day.</p>`
      : `<p class="fine">The higher the division, the more an exact birth time matters: the Ascendant crosses a D60 part in a few minutes.</p>`}
    <div class="vg-chips" role="group" aria-label="Choose a divisional chart">${VARGAS.map(v => `<button type="button" class="vg-chip" data-vg="${v[0]}" title="${v[1]}: ${v[2]}">D${v[0]}</button>`).join("")}</div>
    <div class="vg-one"></div>
    <details class="dg-fold"><summary>All twenty divisions at once</summary>${all}</details>`;
  host.addEventListener("click", e => { const b = e.target.closest("[data-vg]"); if (b){ n = +b.dataset.vg; draw(); } });
  draw();
}

/* ---------- from Rashi to Dharma: D1 → D9 → the Dharma Design → the body ---------- */
function thread(host, C, { unknown } = {}){
  if (!C.dharma || !window.WyrdDesign) { host.innerHTML = ""; return; }
  const DA = WyrdDesign.analyse(C.dharma), BA = WyrdDesign.analyse(C.natal);
  const CEN = WyrdBody.centres, centreOf = {}; for (const k in CEN) for (const g of CEN[k].gates) centreOf[g] = k;
  const DP = C.dharma.personality, NP = C.natal.personality;
  const rows = BODIES.map(b => {
    const s1 = sign(C.sid[b], 1), s9 = sign(C.sid[b], 9), d1 = dignityIn(b, s1), d9 = dignityIn(b, s9);
    const g = DP[b], k = centreOf[g.gate], live = DA.live.some(ch => ch.includes(g.gate));
    const move = RANK[d9] > RANK[d1] ? "rises" : RANK[d9] < RANK[d1] ? "falls" : s1 === s9 ? "holds" : "";
    return { b, s1, s9, d1, d9, g, k, live, move };
  });
  const house = s => unknown ? null : ((s - Math.floor(norm(C.ascS) / 30) + 12) % 12) + 1;
  const ord = n => n + (["th", "st", "nd", "rd"][(n % 100 - 20) % 10] || ["th", "st", "nd", "rd"][n % 100] || "th");
  const vargo = rows.filter(r => r.s1 === r.s9), rise = rows.filter(r => r.move === "rises"), fall = rows.filter(r => r.move === "falls");
  const ak = C.karaka && C.karaka.Atmakaraka, kar = ak ? sign(C.sid[ak], 9) : null;
  const a9 = unknown ? null : sign(C.ascS, 9), l9 = a9 != null ? LORD[a9] : null;
  /* which Rashi planets feed each centre the Dharma Design defines */
  /* both sides: the birth moment's Rashi, and the design moment's (its sidereal positions, in the birth's frame) */
  /* every body the Dharma Design is cast from: the nine, the outer three, and the Earth opposite the Sun */
  const ALL = [...BODIES, "Uranus", "Neptune", "Pluto", "Earth"];
  const lonAt = (src, b) => b === "Earth" ? (src.Sun != null ? norm(src.Sun + 180) : null) : src[b] != null ? src[b] : null;
  const desSid = {}; if (C.tropDes) for (const b in C.tropDes) desSid[b] = norm(C.tropDes[b] - C.ay);
  const sides = [];
  for (const [side, src, col] of [["", C.sid, C.dharma.personality], ["design ", desSid, C.dharma.design]])
    for (const b of ALL){ const l = lonAt(src, b), g = col[b]; if (l == null || !g) continue;
      sides.push({ b, side, s1: sign(l, 1), s9: sign(l, 9), g, k: centreOf[g.gate], live: DA.live.some(ch => ch.includes(g.gate)) }); }
  const feeds = ["head", "ajna", "throat", "g", "heart", "spleen", "solar", "sacral", "root"].filter(k => DA.defined.has(k)).map(k => {
    const from = sides.filter(r => r.k === k && r.live);
    return from.length ? `<li><b>${CEN[k].label}</b> ← ${from.map(r => `${GLYPH[r.b] || "⊕"} ${r.side}${r.b} <small>(${SIGNS[r.s1]} → ${SIGNS[r.s9]}, gate ${r.g.gate}.${r.g.line})</small>`).join(", ")}${BA.defined.has(k) ? "" : " <span class=\"dg-tag\">open at birth</span>"}</li>` : "";
  }).filter(Boolean);
  const el = rs => { const c = [0, 0, 0, 0]; rs.forEach(s => c[s % 4]++); return c; };
  const e1 = el(rows.map(r => r.s1)), e9 = el(rows.map(r => r.s9));
  const top = c => ELEMENT[c.indexOf(Math.max(...c))];
  host.innerHTML = `
    <p>Your Rashi (D1) is the life as it is lived, in the sidereal zodiac. Multiply every position by nine and you have the navamsa (D9): each sign split into nine, the chart of what the life ripens into.
    Your Dharma Design is built from exactly these D9 positions, laid on the gate wheel. So one thread runs through all three:
    <b>a planet in your Rashi → its navamsa sign → the gate it lights in your Dharma Design → the centre that gate feeds</b>.</p>
    <div class="tw"><table class="vg-thread"><tr><th scope="col">Planet</th><th scope="col">Rashi (D1)</th><th scope="col">Navamsa (D9)</th><th scope="col">Dharma gate</th><th scope="col">Centre</th><th scope="col">Birth gate</th></tr>
      ${rows.map(r => `<tr${r.s1 === r.s9 ? ' class="same"' : ""}><th scope="row">${GLYPH[r.b]} ${r.b}</th>
        <td>${SIGNS[r.s1]}${house(r.s1) ? ` <small>${ord(house(r.s1))} house</small>` : ""}${r.d1 ? ` <small>· ${r.d1}</small>` : ""}</td>
        <td>${SIGNS[r.s9]}${r.d9 ? ` <small>· ${r.d9}</small>` : ""}${r.move === "rises" ? " ↑" : r.move === "falls" ? " ↓" : ""}</td>
        <td>${r.g.gate}.${r.g.line}</td><td>${CEN[r.k].label}${r.live ? " <small>· in a channel</small>" : ""}</td><td class="des">${NP[r.b].gate}.${NP[r.b].line}</td></tr>`).join("")}</table></div>
    <p class="fine">These are the conscious (birth-moment) planets. The design side of your Dharma Design runs the same thread from the design moment, about three months before birth. ↑ the planet gains dignity in the navamsa; ↓ it loses it.</p>
    <h4>How they interlock</h4>
    <ul class="vg-read">
      ${vargo.length ? `<li><b>Holding steady (vargottama):</b> ${vargo.map(r => `${GLYPH[r.b]} ${r.b} in ${SIGNS[r.s1]}`).join(", ")}. The same sign in the life and in its ripening: what these planets are at birth is what they become, and the gates they light in your Dharma Design are fed by that one sign twice over.</li>` : `<li>No planet holds its sign from Rashi to navamsa: every planet ripens into something other than what it starts as.</li>`}
      ${rise.length ? `<li><b>Ripening upward:</b> ${rise.map(r => `${GLYPH[r.b]} ${r.b} (${SIGNS[r.s1]} → ${SIGNS[r.s9]}${r.d9 ? ", " + r.d9 : ""})`).join(", ")}. What is ordinary or hard-won in the life matures into strength.</li>` : ""}
      ${fall.length ? `<li><b>Ripening slowly:</b> ${fall.map(r => `${GLYPH[r.b]} ${r.b} (${SIGNS[r.s1]} → ${SIGNS[r.s9]}${r.d9 ? ", " + r.d9 : ""})`).join(", ")}. Strong in the life, these take longer to bear their fruit; the work they ask comes later.</li>` : ""}
      ${ak ? `<li><b>The soul's direction (karakamsa):</b> your Soul-Planet, ${GLYPH[ak]} ${ak}, ripens in <b>${SIGNS[kar]}</b>, ruled by ${LORD[kar]}. In Jyotish this is the sign the soul is travelling toward.</li>` : ""}
      ${a9 != null ? `<li><b>The ripening's own rising:</b> your navamsa rises in <b>${SIGNS[a9]}</b>. Its lord, ${GLYPH[l9]} ${l9}, stands in your Rashi's ${ord(house(sign(C.sid[l9], 1)))} house: that is the part of life where the ripening is worked out.</li>` : ""}
      <li>${top(e1) === top(e9) ? `<b>The element holds:</b> ${top(e1)} leads in both the Rashi and the navamsa` : `<b>The element shifts</b> from ${top(e1)} in the Rashi to ${top(e9)} in the navamsa`} (${ELEMENT.map((x, i) => `${x} ${e1[i]}→${e9[i]}`).join(", ")}).</li>
    </ul>
    <h4>Where it culminates in the body</h4>
    ${feeds.length ? `<p>Your Dharma Design defines ${DA.defined.size} centre${DA.defined.size === 1 ? "" : "s"}. Each is fed by planets whose navamsa gates sit in a live channel there. "Design" planets come from the design moment, about three months before birth, read the same way.</p><ul class="vg-read">${feeds.join("")}</ul>
      <p class="fine">"Open at birth" marks a centre your Birth Design leaves open and your Dharma Design defines: a current the life grows into rather than starts with.</p>`
      : `<p>Your Dharma Design completes no channel: its currents run through single gates, each one open-ended, met by other people and by the sky.</p>`}`;
}

window.WyrdVargas = { sign, VARGAS, dignityIn, mount, thread, SIGNS };
})();
