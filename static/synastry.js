'use strict';
/* ============================================================
   SYNASTRY, DEEPER
   For Compare's pair view:
   - houses(A, B): every planet of each in the other's houses, and what it brings
   - paths(A, B, ctx): what the bond is for, its higher path, its lower path,
     and how to weave the two
   - design(A, B): how two Human Design charts meet: electromagnetic,
     companionship, dominance and compromise channels, who conditions whom,
     and what the two make together
   The words are drafts for The Völva to edit.
   ============================================================ */
(() => {
const { houseOf, GLYPH } = Wyrd.helpers;
const { esc } = WyrdCommon;
const D = () => window.WyrdDynamics;
const ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"];
const ORD = n => n + (n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th");
const LIFE = ["their body, name and how they arrive in the world", "their money, food, family and voice", "their effort, skills, siblings and courage",
  "their home, mother, roots and inner peace", "their creativity, romance, children and joy", "their daily work, health and service",
  "their partnerships and how they meet others", "their crises, shared resources and transformation", "their faith, teachers, travel and luck",
  "their career, reputation and public life", "their friends, networks, gains and hopes", "their solitude, dreams, losses and release"];
const BENEFIC = ["Jupiter", "Venus", "Moon"], HEAVY = ["Saturn", "Mars", "Rahu", "Ketu"];

/* ---------- every planet in the other's houses ---------- */
function houses(A, B){
  const list = (P, Q) => ORDER.map(b => {
    const h = houseOf(P.C.sid[b], Q.C.ascS);
    return `<li><b>${esc(P.name)}'s ${GLYPH[b]} ${b}</b> in ${esc(Q.name)}'s ${ORD(h)} house <span class="fine">· ${D().ROLE[b]}</span><br>
      ${esc(P.name)} ${D().IN_HOUSE[b]} ${LIFE[h - 1].replace(/^their/, `${esc(Q.name)}'s`)}.</li>`;
  }).join("");
  const note = A.C.unknownTime || B.C.unknownTime ? `<p class="unknown-note">A birth time is unknown, so that chart's houses are counted from its Sun.</p>` : "";
  return `${note}<p>Each of you lands in the other's life somewhere. A planet in someone's house is the part of you that walks into that room of their life.</p>
    <div class="sy-two"><div><h5>${esc(A.name)} in ${esc(B.name)}'s houses</h5><ul class="sy-houses">${list(A, B)}</ul></div>
    <div><h5>${esc(B.name)} in ${esc(A.name)}'s houses</h5><ul class="sy-houses">${list(B, A)}</ul></div></div>`;
}

/* ---------- higher path, lower path, the weave ---------- */
const BOND = {
  "命":   { high: "you recognise each other as kin: the same mansion, the same engine. Together you can do what neither could alone, because you never have to explain yourselves.",
            low: "you mirror each other's faults as exactly as your gifts, and two people with the same blind spot can walk off the same cliff together.",
            weave: "Name your shared weakness out loud and give each other permission to stop it when one of you starts down that road." },
  "業胎": { high: "the bond carries karma across lives: one of you shapes the other's path, the other gives the first a reason. It is a teaching bond.",
            low: "the debt can feel heavy and unchosen: obligation without warmth, or one person repeating an old story on the other.",
            weave: "Ask what each of you is here to learn from the other, and when the lesson is learned, let the bond change shape rather than end." },
  "栄親": { high: "you prosper each other: what you build together grows, and each brings out the other's warmth and success.",
            low: "comfort can turn into complacency, or into one person's success depending on the other's quiet support.",
            weave: "Keep growing separately as well as together, and make sure the prosperity flows both ways." },
  "友衰": { high: "this is friendship that steadies: easy company, honest counsel, a bond that rests rather than burns.",
            low: "one of you can drain the other without meaning to, or the ease can slide into neglect.",
            weave: "Tend the friendship on purpose: notice who is giving more energy this season and rebalance it." },
  "安壊": { high: "one of you brings safety and the other brings the shake-up that is needed: together you break what was stuck and build what holds.",
            low: "the breaking can become destruction: one person's stability crushed, or one person's need for change felt as an attack.",
            weave: "Agree what may be broken and what is sacred. Change one thing at a time, and repair as you go." },
  "危成": { high: "the bond is a crucible: risk and achievement together. What you attempt jointly can succeed beyond what either expected.",
            low: "the danger is real: reckless choices, or a bond that only feels alive in crisis.",
            weave: "Choose your risks together and on purpose. Build calm into the bond so it does not need danger to feel close." },
};

function paths(A, B, { cs, R, together, kuta }){
  const role = D().ROLE, name = P => esc(P.name);
  const soft = cs.filter(c => c.f === "soft" || (c.f === "conj" && !HEAVY.includes(c.p) && !HEAVY.includes(c.q))).slice(0, 4);
  const hard = cs.filter(c => c.f === "hard" || (c.f === "conj" && (HEAVY.includes(c.p) || HEAVY.includes(c.q)))).slice(0, 4);
  const gifts = [];
  for (const [P, Q] of [[A, B], [B, A]]) for (const b of ["Jupiter", "Venus", "Sun"]) {
    const h = houseOf(P.C.sid[b], Q.C.ascS);
    if ([1, 5, 7, 9, 10, 11].includes(h)) gifts.push(`${name(P)}'s ${b} (${role[b]}) blesses ${LIFE[h - 1].replace(/^their/, `${name(Q)}'s`)}`);
  }
  const weights = [];
  for (const [P, Q] of [[A, B], [B, A]]) for (const b of ["Saturn", "Mars", "Rahu"]) {
    const h = houseOf(P.C.sid[b], Q.C.ascS);
    if ([1, 4, 7, 8, 12].includes(h)) weights.push(`${name(P)}'s ${b} (${role[b]}) presses on ${LIFE[h - 1].replace(/^their/, `${name(Q)}'s`)}`);
  }
  const bond = R && BOND[R.pair];
  const asks = hard.map(c => { const k = ORDER.indexOf(c.p) <= ORDER.indexOf(c.q) ? `${c.p}-${c.q}` : `${c.q}-${c.p}`, e = D().PAIRS[k];
    return e && e.ask ? e.ask.replace(/the (\w+) person/g, (m, pl) => pl === c.p ? name(A) : pl === c.q ? name(B) : m) : null; }).filter(Boolean);
  const kn = kuta && kuta.rows.Nadi === 0, kb = kuta && kuta.rows.Bhakoot === 0;
  return `
    <h5>What this bond is for</h5>
    <p>${bond ? `By the lunar mansions, ${bond.high}` : ""}
    ${together.length ? ` Your bodies complete ${together.length} channel${together.length > 1 ? "s" : ""} neither of you has alone: there is energy available between you that is not in either of you.` : ""}</p>
    ${gifts.length ? `<ul>${gifts.map(x => `<li>${x}.</li>`).join("")}</ul>` : ""}
    <h5>The higher path</h5>
    <p>Grown well, this bond lifts both of you toward your higher purpose.</p>
    <ul>${soft.map(c => `<li>${name(A)}'s ${c.p} (${role[c.p]}) and ${name(B)}'s ${c.q} (${role[c.q]}) flow: ${c.p === c.q ? `you share the same ${role[c.p]}, and it is easy between you` : `${role[c.p]} and ${role[c.q]} feed each other`}. Lean on this when things are hard.</li>`).join("") || "<li>No easy contacts between the main planets: what lifts this bond is chosen, not given, and that makes it strong when it is chosen.</li>"}</ul>
    <h5>The lower path</h5>
    <p>${bond ? `Left unconscious, ${bond.low}` : "Left unconscious, the frictions below run the bond instead of the bond running them."}</p>
    <ul>${hard.map(c => `<li>${name(A)}'s ${c.p} (${role[c.p]}) and ${name(B)}'s ${c.q} (${role[c.q]}) grind: ${c.p === c.q ? `under stress your two kinds of ${role[c.p]} compete` : `under stress, ${role[c.p]} and ${role[c.q]} fight for the same ground`}.</li>`).join("")}
      ${weights.map(x => `<li>${x}: heavy, and lasting. Name it before it hardens.</li>`).join("")}
      ${kn ? "<li>You share a Nadi, the same bodily pulse: you can exhaust each other's constitution, especially when living closely.</li>" : ""}
      ${kb ? "<li>Your Moon signs sit at a testing distance: money and family life need care and clear agreements.</li>" : ""}</ul>
    <h5>Weaving the two</h5>
    <p>${bond ? bond.weave : ""} The higher path does not cancel the lower one; it uses it. Every friction above is also where you can grow most, if both of you agree to work on it.</p>
    ${asks.length ? `<ul class="sy-asks">${asks.map(a => `<li><em>${a}</em></li>`).join("")}</ul>` : ""}`;
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

window.WyrdSynastry = { houses, paths, design };
})();
