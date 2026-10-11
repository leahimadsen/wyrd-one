'use strict';
/* ============================================================
   SYNASTRY, THE FACTS
   For Compare's pair view:
   - houses(A, B): every planet of each in the other's houses
   - design(A, B): how two Human Design charts meet: electromagnetic,
     companionship, dominance and compromise channels, who conditions whom,
     and what the two make together
   What the houses mean in words, and the bond's purpose and its higher and
   lower paths, are paid: wyrd/together.py writes them from lib/bond.json.
   ============================================================ */
(() => {
const { houseOf, GLYPH } = Wyrd.helpers;
const { esc } = WyrdCommon;
const D = () => window.WyrdDynamics;
const ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"];
const ORD = n => n + (n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th");

/* ---------- every planet in the other's houses ---------- */
function houses(A, B){
  const list = (P, Q) => ORDER.map(b => {
    const h = houseOf(P.C.sid[b], Q.C.ascS);
    return `<li><b>${esc(P.name)}'s ${GLYPH[b]} ${b}</b> in ${esc(Q.name)}'s ${ORD(h)} house <span class="fine">· ${D().ROLE[b]} · ${D().HOUSE[h - 1]}</span></li>`;
  }).join("");
  const note = A.C.unknownTime || B.C.unknownTime ? `<p class="unknown-note">A birth time is unknown, so that chart's houses are counted from its Sun.</p>` : "";
  return `${note}<p>Each of you lands in the other's life somewhere. A planet in someone's house is the part of you that walks into that room of their life.</p>
    <div class="sy-two"><div><h5>${esc(A.name)} in ${esc(B.name)}'s houses</h5><ul class="sy-houses">${list(A, B)}</ul></div>
    <div><h5>${esc(B.name)} in ${esc(A.name)}'s houses</h5><ul class="sy-houses">${list(B, A)}</ul></div></div>`;
}

/* ---------- two bodygraphs meeting ---------- */
const DESC = {
  em: "Electromagnetic: each of you holds one end of the channel. Together it lights up. This is attraction and friction both: the spark that draws you together and the place you most easily rub.",
  comp: "Companionship: you both have this channel. Here you understand each other without effort, and you share the same way of being.",
  dom: "Dominance: one of you has the whole channel and the other has neither gate. Here one leads and the other learns the current from the outside.",
  promise: "Compromise: one of you has the whole channel and the other has only one gate of it. The one with the channel's current tends to win; the other has to give way here.",
};
function design(A, B){
  if (!window.WyrdDesign) return "";
  const W = WyrdDesign, CH = WyrdBody.channels, CEN = WyrdBody.centres;
  const ra = W.analyse(A.C.natal), rb = W.analyse(B.C.natal);
  const ga = ra.gates, gb = rb.gates, full = (g, [p, q]) => g.has(p) && g.has(q), one = (g, [p, q]) => g.has(p) !== g.has(q), none = (g, [p, q]) => !g.has(p) && !g.has(q);
  const rows = { em: [], comp: [], dom: [], promise: [] };
  for (const ch of CH){
    if (full(ga, ch) && full(gb, ch)) rows.comp.push(ch);
    else if (full(ga, ch) || full(gb, ch)){ const other = full(ga, ch) ? gb : ga; (none(other, ch) ? rows.dom : rows.promise).push([...ch, full(ga, ch) ? A : B]); }
    else if (one(ga, ch) && one(gb, ch) && !(ga.has(ch[0]) && gb.has(ch[0])) && !(ga.has(ch[1]) && gb.has(ch[1]))) rows.em.push(ch);
  }
  const cname = k => CEN[k].label, ch = c => `${c[0]}–${c[1]}`;
  const condAB = [...ra.defined].filter(k => !rb.defined.has(k)), condBA = [...rb.defined].filter(k => !ra.defined.has(k));
  const union = [...new Set([...ga, ...gb])], comp = W.analyse({ personality: Object.fromEntries(union.map((g, i) => ["g" + i, { gate: g, line: 1 }])), design: {}, profile: "" });
  const sec = (k, list, fmt) => list.length ? `<li><b>${DESC[k].split(":")[0]}</b> · ${list.map(fmt).join(", ")}<br><span class="fine">${DESC[k].split(": ").slice(1).join(": ")}</span></li>` : "";
  return `<p>${esc(A.name)} is a ${ra.type} with ${ra.authority.toLowerCase()} authority; ${esc(B.name)} is a ${rb.type} with ${rb.authority.toLowerCase()} authority.
    Together, your two bodies make one field: a ${comp.type}${comp.defined.size === 9 ? " with every centre defined" : ""}.</p>
    <ul class="sy-hd">
      ${sec("em", rows.em, ch)}${sec("comp", rows.comp, ch)}
      ${sec("dom", rows.dom, c => `${ch(c)} (${esc(c[2].name)}'s)`)}${sec("promise", rows.promise, c => `${ch(c)} (${esc(c[2].name)}'s)`)}
    </ul>
    <h5>Who conditions whom</h5>
    <p>Where one of you is defined and the other open, the open one feels the defined one's energy amplified, and can mistake it for their own.</p>
    <ul>${condAB.length ? `<li>${esc(A.name)} conditions ${esc(B.name)}'s ${condAB.map(cname).join(", ")}.</li>` : ""}
      ${condBA.length ? `<li>${esc(B.name)} conditions ${esc(A.name)}'s ${condBA.map(cname).join(", ")}.</li>` : ""}
      ${!condAB.length && !condBA.length ? "<li>You are defined and open in the same centres: little amplification passes between you.</li>" : ""}</ul>
    ${["head", "ajna", "throat", "g", "heart", "spleen", "solar", "sacral", "root"].filter(k => !ra.defined.has(k) && !rb.defined.has(k)).length
      ? `<p>Open in both of you: ${["head", "ajna", "throat", "g", "heart", "spleen", "solar", "sacral", "root"].filter(k => !ra.defined.has(k) && !rb.defined.has(k)).map(cname).join(", ")}. Here the two of you take in the world together; other people and places set the tone.</p>` : ""}`;
}

window.WyrdSynastry = { houses, design };
})();
