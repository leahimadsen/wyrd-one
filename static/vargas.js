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
   The words live in lib/vargas.json (drafts for The Völva to edit), sent with the chart.
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
  [4,  "Chaturthamsha",   "home, land and settled fortune"],
  [5,  "Panchamsha",      "power, standing and recognition", "cyclical"],
  [6,  "Shashthamsha",    "health, illness and what you struggle against", "cyclical"],
  [7,  "Saptamsha",       "children, creation and what you pass on"],
  [8,  "Ashtamsha",       "sudden events, the hidden and long life", "cyclical"],
  [9,  "Navamsha",        "dharma, partnership and what the life ripens into"],
  [10, "Dashamsha",        "work, career and action in the world"],
  [11, "Rudramsa",       "gains, and the endings that make room for them", "cyclical"],
  [12, "Dvadashamsha",     "parents and lineage"],
  [16, "Shodashamsha",     "comforts, vehicles and ease"],
  [20, "Vimshamsha",       "spiritual practice and devotion"],
  [24, "Chaturvimshamsha", "learning and knowledge"],
  [27, "Bhamsha",         "strength, stamina and weak points"],
  [30, "Trimshamsha",      "misfortune and the shadow of character"],
  [40, "Khavedamsha",     "the mother's line and what it hands down"],
  [45, "Akshavedamsha",   "the father's line and character"],
  [60, "Shashtyamsha",    "past karma, the finest grain of the chart"],
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

/* dignity by sign, as the vargas are read: a ladder, not a switch. Exalted, its own sign, a friend's,
   a neutral's, an enemy's, debilitated; friend, neutral and enemy by the natural friendships
   (naisargika maitri, BPHS ch. 3). wyrd/vargas.py keeps the same ladder for the reading. */
const EXALT = { Sun: 0, Moon: 1, Mercury: 5, Venus: 11, Mars: 9, Jupiter: 3, Saturn: 6 };
const OWN = { Sun: [4], Moon: [3], Mercury: [2, 5], Venus: [1, 6], Mars: [0, 7], Jupiter: [8, 11], Saturn: [9, 10] };
const KIN = {
  Sun: { friend: ["Moon", "Mars", "Jupiter"], enemy: ["Venus", "Saturn"] },
  Moon: { friend: ["Sun", "Mercury"], enemy: [] },
  Mars: { friend: ["Sun", "Moon", "Jupiter"], enemy: ["Mercury"] },
  Mercury: { friend: ["Sun", "Venus"], enemy: ["Moon"] },
  Jupiter: { friend: ["Sun", "Moon", "Mars"], enemy: ["Mercury", "Venus"] },
  Venus: { friend: ["Mercury", "Saturn"], enemy: ["Sun", "Moon"] },
  Saturn: { friend: ["Mercury", "Venus"], enemy: ["Sun", "Moon", "Mars"] },
};
function dignityIn(b, s){
  if (!(b in EXALT)) return "";
  if (EXALT[b] === s) return "exalted";
  if ((EXALT[b] + 6) % 12 === s) return "debilitated";
  if (OWN[b].includes(s)) return "own sign";
  const l = LORD[s];
  return KIN[b].friend.includes(l) ? "friend's sign" : KIN[b].enemy.includes(l) ? "enemy's sign" : "neutral sign";
}
const RANK = { "exalted": 5, "own sign": 4, "friend's sign": 3, "neutral sign": 2, "enemy's sign": 1, "debilitated": 0, "": 2 };

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

/* the words: lib/vargas.json, sent with the chart (lex.vargas) */
const W = C => (C.lex && C.lex.vargas) || {};
const fill = (t, o) => String(t || "").replace(/\{(\w+)\}/g, (_, k) => o[k] ?? "");
const list = (C, bs) => bs.map(b => `${GLYPH[b] || ""} ${b}`).join(", ");

function mount(host, C, { unknown } = {}){
  const w = W(C); let n = 9;
  const draw = () => {
    const V = VARGAS.find(v => v[0] === n), T = (w.VARGAS || {})[n] || {};
    const kept = BODIES.filter(b => sign(C.sid[b], n) === sign(C.sid[b], 1));
    const strong = BODIES.filter(b => ["exalted", "own sign"].includes(dignityIn(b, sign(C.sid[b], n))));
    host.querySelector(".vg-one").innerHTML = `${grid(C, n, unknown)}
      <div class="vg-say"><h4>D${n} · ${V[1]}</h4><p class="vg-dom">${esc(T.domain || V[2])}</p>
      <p>${T.read || ""}${V[3] ? ` <span class="fine">${esc(w.CYCLICAL || "")}</span>` : ""}</p>
      ${n > 1 ? `<p>${kept.length ? fill(n === 9 ? w.KEPT_D9 : w.KEPT, { list: list(C, kept) }) : w.KEPT_NONE || ""}</p>` : ""}
      <p>${strong.length ? fill(w.STRONG, { list: strong.map(b => `${GLYPH[b]} ${b} <small>(${dignityIn(b, sign(C.sid[b], n))})</small>`).join(", ") }) : w.STRONG_NONE || ""}</p>
      ${T.ask ? `<p class="vg-ask">${esc(T.ask)}</p>` : ""}
      <p class="fine">${w.KEY || ""}</p></div>`;
    host.querySelectorAll("[data-vg]").forEach(b => b.setAttribute("aria-pressed", +b.dataset.vg === n));
  };
  const all = `<div class="tw"><table class="vg-all"><caption>Every planet in every body. Bold: the same sign as in the Rashi.</caption>
    <tr><th></th>${VARGAS.map(v => `<th scope="col" title="${v[1]}: ${esc(((w.VARGAS || {})[v[0]] || {}).domain || v[2])}">D${v[0]}</th>`).join("")}</tr>
    ${BODIES.map(b => `<tr><th scope="row">${GLYPH[b]} ${b}</th>${VARGAS.map(v => { const s = sign(C.sid[b], v[0]), dg = dignityIn(b, s);
      return `<td class="${s === sign(C.sid[b], 1) && v[0] > 1 ? "same" : ""}${dg ? " " + dg.replace(" ", "-") : ""}">${AB[s]}</td>`; }).join("")}</tr>`).join("")}
    ${unknown ? "" : `<tr><th scope="row">↑ Asc</th>${VARGAS.map(v => `<td>${AB[sign(C.ascS, v[0])]}</td>`).join("")}</tr>`}</table></div>`;
  host.innerHTML = `
    <p>${w.VIEW_INTRO || ""}</p>
    ${unknown ? `<p class="unknown-note">${w.VIEW_UNKNOWN || ""}</p>` : `<p class="fine">${w.VIEW_TIME || ""}</p>`}
    <div class="vg-chips" role="group" aria-label="Choose a divisional chart">${VARGAS.map(v => `<button type="button" class="vg-chip" data-vg="${v[0]}" title="${v[1]}: ${esc(((w.VARGAS || {})[v[0]] || {}).domain || v[2])}">D${v[0]}</button>`).join("")}</div>
    <div class="vg-one"></div>
    <details class="dg-fold"><summary>All twenty bodies at once</summary>${all}</details>`;
  host.addEventListener("click", e => { const b = e.target.closest("[data-vg]"); if (b){ n = +b.dataset.vg; draw(); } });
  draw();
}

/* ---------- from Rashi to Dharma: D1 → D9 → the Dharma Design → the body ---------- */
function thread(host, C, { unknown, full } = {}){
  if (!C.dharma || !window.WyrdDesign) { host.innerHTML = ""; return; }
  const w = W(C), DA = WyrdDesign.analyse(C.dharma), BA = WyrdDesign.analyse(C.natal);
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
  const step = r => `${GLYPH[r.b]} ${r.b} (${SIGNS[r.s1]} → ${SIGNS[r.s9]}${r.d9 ? ", " + r.d9 : ""})`;
  const vargo = rows.filter(r => r.s1 === r.s9), rise = rows.filter(r => r.move === "rises"), fall = rows.filter(r => r.move === "falls");
  const ak = C.karaka && C.karaka.Atmakaraka, kar = ak ? sign(C.sid[ak], 9) : null;
  const a9 = unknown ? null : sign(C.ascS, 9), l9 = a9 != null ? LORD[a9] : null;
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
    return from.length ? `<li><b>${CEN[k].label}</b> ← ${from.map(r => `${GLYPH[r.b] || "⊕"} ${r.side}${r.b} <small>(${SIGNS[r.s1]} → ${SIGNS[r.s9]}, gate ${r.g.gate}.${r.g.line})</small>`).join(", ")}${BA.defined.has(k) ? "" : ` <span class="dg-tag">${esc(w.OPEN_AT_BIRTH || "open at birth")}</span>`}</li>` : "";
  }).filter(Boolean);
  const el = rs => { const c = [0, 0, 0, 0]; rs.forEach(s => c[s % 4]++); return c; };
  const e1 = el(rows.map(r => r.s1)), e9 = el(rows.map(r => r.s9));
  /* one of their own planets stepping down without being debilitated, if there is one */
  const standing = (d, s) => fill(((w.STANDING || {})[d] || d), { lord: (["Sun", "Moon"].includes(LORD[s]) ? "the " : "") + LORD[s] });
  const egRow = rows.find(r => r.move === "falls" && r.d9 !== "debilitated");
  const ladderEg = egRow && w.LADDER_EG ? fill(w.LADDER_EG, { glyph: GLYPH[egRow.b], planet: egRow.b, s1: SIGNS[egRow.s1], s9: SIGNS[egRow.s9],
    p1: standing(egRow.d1, egRow.s1), p9: standing(egRow.d9, egRow.s9), steps: (w.STEPS || [])[RANK[egRow.d1] - RANK[egRow.d9]] || "" }) : "";
  const top = c => ELEMENT[c.indexOf(Math.max(...c))];
  const counts = ELEMENT.map((x, i) => `${x} ${e1[i]}→${e9[i]}`).join(", ");
  const wish = kar != null && C.lex && C.lex.karakamsa ? C.lex.karakamsa : "";
  const lifeOf = h => ((C.lex && C.lex.houseLife) || [])[h - 1] || "";
  host.innerHTML = `
    <p>${w.THREAD_INTRO || ""} <b>${w.THREAD_CHAIN || ""}</b></p>
    <div class="tw"><table class="vg-thread"><tr><th scope="col">Planet</th><th scope="col">Rashi (D1)</th><th scope="col">Navamsha (D9)</th><th scope="col">Dharma gate</th><th scope="col">Centre</th><th scope="col">Birth gate</th></tr>
      ${rows.map(r => `<tr${r.s1 === r.s9 ? ' class="same"' : ""}><th scope="row">${GLYPH[r.b]} ${r.b}</th>
        <td>${SIGNS[r.s1]}${house(r.s1) ? ` <small>${ord(house(r.s1))} house</small>` : ""}${r.d1 ? ` <small>· ${r.d1}</small>` : ""}</td>
        <td>${SIGNS[r.s9]}${r.d9 ? ` <small>· ${r.d9}</small>` : ""}${r.move === "rises" ? " ↑" : r.move === "falls" ? " ↓" : ""}</td>
        <td>${r.g.gate}.${r.g.line}</td><td>${CEN[r.k].label}${r.live ? " <small>· in a channel</small>" : ""}</td><td class="des">${NP[r.b].gate}.${NP[r.b].line}</td></tr>`).join("")}</table></div>
    <p class="fine">${w.THREAD_NOTE || ""}</p>
    ${w.LADDER ? `<details class="vg-ladder"><summary>${w.LADDER_H}</summary><p>${w.LADDER}</p>${ladderEg ? `<p>${ladderEg}</p>` : ""}</details>` : ""}
    ${full ? "" : `<p>${[rise.length && `${rise.length} of your planets ripen upward`, fall.length && `${fall.length} ripen${fall.length === 1 ? "s" : ""} slowly`, vargo.length && `${vargo.length} hold${vargo.length === 1 ? "s" : ""} steady`].filter(Boolean).join(", ") || "Your planets change sign as they ripen"}, and your Dharma Design gathers at ${DA.defined.size} centre${DA.defined.size === 1 ? "" : "s"}.</p>
    <div class="dg-lock"><b>How the tree becomes the fruit</b>
      <p>How each of your planets ripens, how the tree and the fruit interlock, where your soul is heading and what your Dharma Design gathers into are read in <a href="#reading">The Wyrd Reading</a>, in the Path of Dharma. Members of <a href="/membership">the Order</a> see it here in full.</p></div>`}
    ${full ? `<h4>${w.RIPEN_H || ""}</h4>
    <ul class="vg-read">${rows.map(r => `<li>${fill(w.RIPEN, { glyph: GLYPH[r.b], planet: r.b, matter: (w.PLANET || {})[r.b] || "", s1: SIGNS[r.s1], fruit: (r.s1 === r.s9 ? `stays in ${SIGNS[r.s9]} and deepens into ` : `ripens in ${SIGNS[r.s9]}, into `) + ((w.FRUIT || [])[r.s9] || "").replace(/^it ripens into /, "") })}</li>`).join("")}</ul>
    <h4>${w.INTERLOCK_H || ""}</h4>
    <ul class="vg-read">
      <li>${vargo.length ? fill(w.VARGOTTAMA, { list: vargo.map(r => `${GLYPH[r.b]} ${r.b} in ${SIGNS[r.s1]}`).join(", ") }) : w.VARGOTTAMA_NONE || ""}</li>
      ${rise.length ? `<li>${fill(w.RISE, { list: rise.map(step).join(", ") })}</li>` : ""}
      ${fall.length ? `<li>${fill(w.FALL, { list: fall.map(step).join(", ") })}</li>` : ""}
      ${ak ? `<li>${fill(w.KARAKAMSA, { glyph: GLYPH[ak] || "", planet: ak, sign: SIGNS[kar], wish })}</li>` : ""}
      ${a9 != null ? `<li>${fill(w.NAV_RISING, { sign: SIGNS[a9], glyph: GLYPH[l9], lord: l9, house: ord(house(sign(C.sid[l9], 1))), life: lifeOf(house(sign(C.sid[l9], 1))) })}</li>` : ""}
      <li>${top(e1) === top(e9) ? fill(w.ELEMENT_HOLD, { el: top(e1), counts }) : fill(w.ELEMENT_SHIFT, { e1: top(e1), e9: top(e9), counts })}</li>
    </ul>
    <h4>${w.CULMINATE_H || ""}</h4>
    ${feeds.length ? `<p>${fill(w.CULMINATE, { n: DA.defined.size, centres: DA.defined.size === 1 ? "centre" : "centres" })}</p><ul class="vg-read">${feeds.join("")}</ul>` : `<p>${w.CULMINATE_NONE || ""}</p>`}
    <p class="vg-close">${w.CLOSE || ""}</p>
    ${w.ASK ? `<p class="vg-ask">${esc(w.ASK)}</p>` : ""}` : ""}`;
}

window.WyrdVargas = { sign, VARGAS, dignityIn, mount, thread, SIGNS };
})();
