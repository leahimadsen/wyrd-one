'use strict';
/* ============================================================
   YOUR DESIGN
   The Human Design chart read as energy: which centres run on their own
   current, which receive, how the current travels along your channels and
   where it surfaces. Shown for the birth design and the Dharma design,
   on a bodygraph whose live channels carry moving light.
   Nothing prescriptive here: no diets, no environments, no rules.
   The words are drafts for The Völva to edit.
   ============================================================ */
(() => {
const { esc } = WyrdCommon;
const NS = "http://www.w3.org/2000/svg";
const CENTRES = WyrdBody.centres, CHANNELS = WyrdBody.channels;
const CENTRE_OF = {}; for (const k in CENTRES) for (const g of CENTRES[k].gates) CENTRE_OF[g] = k;
const MOTORS = ["heart", "solar", "sacral", "root"];
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* the bodygraph, laid out as it is usually drawn */
const POS = { head: [200, 46], ajna: [200, 118], throat: [200, 200], g: [200, 292], heart: [268, 322],
  spleen: [78, 382], solar: [322, 382], sacral: [200, 410], root: [200, 500] };
const SHAPE = { head: "up", ajna: "down", throat: "sq", g: "dia", heart: "heart", spleen: "right", solar: "left", sacral: "sq", root: "sq" };
function shapePath(k){
  const [x, y] = POS[k], h = k === "heart" ? 16 : 26;
  switch (SHAPE[k]){
    case "up": return `M${x},${y - h} L${x + h},${y + h} L${x - h},${y + h} Z`;
    case "down": return `M${x},${y + h} L${x + h},${y - h} L${x - h},${y - h} Z`;
    case "dia": return `M${x},${y - h} L${x + h},${y} L${x},${y + h} L${x - h},${y} Z`;
    case "heart": return `M${x - h},${y + h * .8} L${x},${y - h} L${x + h},${y + h * .8} Z`;
    case "right": return `M${x + h},${y} L${x - h},${y - h} L${x - h},${y + h} Z`;
    case "left": return `M${x - h},${y} L${x + h},${y - h} L${x + h},${y + h} Z`;
    default: return `M${x - h},${y - h} L${x + h},${y - h} L${x + h},${y + h} L${x - h},${y + h} Z`;
  }
}

/* ---------- the reading of one rave ---------- */
function analyse(rave){
  const gates = new Set([rave.personality, rave.design].flatMap(c => Object.values(c).map(v => v.gate)));
  const live = CHANNELS.filter(([a, b]) => gates.has(a) && gates.has(b));
  const defined = new Set(live.flatMap(([a, b]) => [CENTRE_OF[a], CENTRE_OF[b]]));
  const adj = {}; for (const k in CENTRES) adj[k] = new Set();
  for (const [a, b] of live){ adj[CENTRE_OF[a]].add(CENTRE_OF[b]); adj[CENTRE_OF[b]].add(CENTRE_OF[a]); }
  const dist = { throat: 0 }, q = ["throat"];          // how far each defined centre is from the throat, along live channels
  while (q.length){ const c = q.shift(); for (const n of adj[c]) if (!(n in dist)){ dist[n] = dist[c] + 1; q.push(n); } }
  const seen = new Set(); let parts = 0;
  for (const c of defined){ if (seen.has(c)) continue; parts++; const st = [c]; while (st.length){ const x = st.pop(); if (seen.has(x)) continue; seen.add(x); st.push(...adj[x]); } }
  const motorToThroat = defined.has("throat") && MOTORS.some(m => m in dist && dist[m] > 0);
  const type = !defined.size ? "Reflector" : defined.has("sacral") ? (motorToThroat ? "Manifesting Generator" : "Generator") : motorToThroat ? "Manifestor" : "Projector";
  const authority = !defined.size ? "Lunar" : defined.has("solar") ? "Emotional" : defined.has("sacral") ? "Sacral" : defined.has("spleen") ? "Splenic"
    : defined.has("heart") ? ("heart" in dist ? "Ego manifested" : "Ego projected") : defined.has("g") && adj.g.has("throat") ? "Self-projected" : "Outer";
  const definition = ["No definition", "Single definition", "Split definition", "Triple split", "Quadruple split"][parts] || "Split definition";
  return { rave, gates, live, defined, dist, type, authority, definition, parts, motorToThroat, profile: rave.profile };
}

/* ---------- the drawing ---------- */
function channelGeom(live, mode){
  /* several channels can join the same two centres: fan them out side by side */
  const bundles = {};
  for (const ch of CHANNELS){ const k = [CENTRE_OF[ch[0]], CENTRE_OF[ch[1]]].sort().join("|"); (bundles[k] = bundles[k] || []).push(ch); }
  const out = [];
  for (const k in bundles){
    const list = bundles[k], [c1, c2] = k.split("|"), [x1, y1] = POS[c1], [x2, y2] = POS[c2];
    const len = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / len, ny = (x2 - x1) / len;
    list.forEach((ch, i) => { const o = (i - (list.length - 1) / 2) * 7; out.push({ ch, c1, c2, x1: x1 + nx * o, y1: y1 + ny * o, x2: x2 + nx * o, y2: y2 + ny * o }); });
  }
  return out;
}
function graph(A, B){                          // A: birth, B: dharma (either may be null)
  const key = ch => ch.join("-");
  const inA = new Set(A ? A.live.map(key) : []), inB = new Set(B ? B.live.map(key) : []);
  let lines = "", flows = "";
  for (const g of channelGeom()){
    const k = key(g.ch), a = inA.has(k), b = inB.has(k);
    const cls = a && b ? "both" : a ? "birth" : b ? "dharma" : "idle";
    /* the current runs toward the throat, by the circuit of the chart the channel is live in */
    let [x1, y1, x2, y2] = [g.x1, g.y1, g.x2, g.y2];
    if (!WyrdBody.runsFrom((a || !B ? A || B : B).dist, g.c1, g.c2)) [x1, y1, x2, y2] = [x2, y2, x1, y1];
    lines += `<line class="dg-ch ${cls}" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"><title>Channel ${g.ch[0]}–${g.ch[1]}</title></line>`;
    if (cls !== "idle" && !reduce){
      const dur = (Math.hypot(x2 - x1, y2 - y1) / 38).toFixed(2);
      for (let i = 0; i < 3; i++)
        flows += `<circle class="dg-spark ${cls}" r="3.2"><animateMotion dur="${dur}s" begin="${(i * dur / 3).toFixed(2)}s" repeatCount="indefinite" path="M${x1.toFixed(1)},${y1.toFixed(1)} L${x2.toFixed(1)},${y2.toFixed(1)}"/></circle>`;
    }
  }
  let centres = "";
  for (const k in POS){
    const a = A && A.defined.has(k), b = B && B.defined.has(k);
    const cls = a && b ? "both" : a ? "birth" : b ? "dharma" : "open";
    centres += `<g class="dg-c ${cls}${MOTORS.includes(k) ? " motor" : ""}"><path d="${shapePath(k)}"/><text x="${POS[k][0]}" y="${POS[k][1] + (k === "heart" ? 4 : 5)}">${CENTRES[k].label}</text></g>`;
  }
  return `<svg class="dg-svg" viewBox="0 0 400 560" role="img" aria-label="Bodygraph: defined centres filled, live channels carrying moving light toward the throat">
    <g class="dg-lines">${lines}</g><g class="dg-flows">${flows}</g><g class="dg-centres">${centres}</g></svg>`;
}

/* ---------- the words (drafts) ---------- */
const TYPE = {
  "Generator": "Your sacral centre is defined: a renewable motor in the belly that builds energy and gives it out through work you are drawn into. The current here is steady and responsive; it rises toward what lights it and sinks away from what does not. When it is spent on what it answers to, it renews itself overnight.",
  "Manifesting Generator": "Your sacral motor is defined and its current reaches the throat directly. The energy builds like a Generator's and leaves the body fast, often in several directions at once, skipping steps the way water takes the quickest way downhill. Speed and range are its nature, not its fault.",
  "Manifestor": "A motor other than the sacral feeds your throat directly. The current does not wait to build: it arrives as impulse and leaves as action, starting things, moving through and on. It comes in bursts with rests between, more like weather than a tide.",
  "Projector": "Your sacral is open and no motor reaches your throat. You do not run on a constant engine; your current is the current of perception. Energy moves through you from others, and you see how it moves through them, often more clearly than they can.",
  "Reflector": "No centre in your body is defined. Every current that passes through you is borrowed, sampled and returned, so you mirror the place and the people you are with, and the Moon's passage through the gates over a month is your own steady rhythm.",
};
const AUTH = {
  "Emotional": "Clarity forms in waves. Your solar plexus rises and falls, and what you know becomes clear only as the wave settles over time.",
  "Sacral": "Clarity arrives in the gut as a sound or a pull, in the moment, before the mind has its say.",
  "Splenic": "Clarity is a quiet, single instinct in the body, here once and then gone. It speaks in the now, for your survival and wellbeing.",
  "Ego manifested": "Clarity comes through the heart's will spoken aloud: you hear what you want as you say it.",
  "Ego projected": "Clarity comes from the heart's will, what you truly want for yourself, recognised in conversation with others.",
  "Self-projected": "Clarity comes from your identity speaking: you hear your direction in your own voice as you talk it through.",
  "Outer": "Clarity does not come from inside the body. It forms by talking through and sensing the right places and people, and you see best for others.",
  "Lunar": "Clarity forms over a full lunar cycle, as the Moon passes through every gate and you sample your life from each.",
};
const DEFN = {
  "Single definition": "All your defined centres are joined into one circuit. The current moves through you as one continuous flow; you tend to feel whole on your own.",
  "Split definition": "Your defined centres form two separate circuits. Energy moves in two islands, and people or transits that carry the bridging gates feel like connection.",
  "Triple split": "Your defined centres form three separate circuits. Your current lives in three places at once, and moving among many people lets them meet.",
  "Quadruple split": "Your defined centres form four separate circuits, a rare and fixed design whose parts take their time to speak to each other.",
  "No definition": "No circuits of your own: the field is entirely receptive.",
};
const CEN = {
  head: ["Pressure to know and to wonder.", "The crown"], ajna: ["Thinking, concepts, certainty.", "The brow and eyes"],
  throat: ["Where energy becomes voice and action.", "The throat"], g: ["Identity, love and direction.", "The heart region"],
  heart: ["Willpower, worth and the material.", "The heart, stomach and gall bladder"], spleen: ["Instinct, health and timing.", "The spleen and lymph"],
  solar: ["Emotion, desire and sensitivity.", "The solar plexus and nerves"], sacral: ["Life force, sexuality and sustained work.", "The sacrum and the gut"],
  root: ["Pressure, adrenaline and the drive to move.", "The adrenals and the base of the spine"],
};


/* each channel as a current: what moves along it (drafts for The Völva to edit) */
const CHANNEL = {
  "1-8": "Your self-expression reaches the world as a contribution: what is uniquely yours wants to be shown, and showing it is the gift.",
  "2-14": "The direction your higher self knows is powered by your gut's resources: you steer energy and money toward where life wants to go.",
  "3-60": "Pressure to change meets the urge to order something new: energy that mutates, in pulses, and sometimes waits a long time to arrive.",
  "4-63": "Doubt in the head becomes formulas in the mind: a current that questions, then answers, then questions the answer.",
  "5-15": "Your rhythms run in time with the flow of life itself: energy that keeps habits and brings others into a natural tempo.",
  "6-59": "Emotional friction meets the drive to bond: energy for intimacy that opens doors between people, closely and physically.",
  "7-31": "Your sense of direction speaks as influence: energy that leads by being heard at the right moment.",
  "9-52": "Root stillness feeds sacral focus: energy that can stay with one thing for a long time.",
  "10-20": "The love of being yourself comes out in the present tense: awakeness, voiced now.",
  "10-34": "Self-love is powered by sacral strength: you follow your own convictions and explore by doing.",
  "10-57": "The body's instinct protects the way you live: intuition shaping a life worth living, in the moment.",
  "11-56": "Ideas become stories: a current of curiosity that looks for things to say and teaches by telling.",
  "12-22": "Feeling opens the voice: energy that speaks with grace when the mood is right, and goes quiet when it is not.",
  "13-33": "What you listen to becomes memory and is retold later: energy that witnesses, keeps, and gives back the meaning of experience.",
  "16-48": "Depth of understanding becomes skill: energy that practises until talent turns into mastery.",
  "17-62": "Opinions are organised into detail: a current that sees patterns and explains them precisely.",
  "18-58": "Joy in life pushes to correct what is not working: energy that improves things, and needs somewhere worthy to aim.",
  "19-49": "Needs meet principles: energy that bonds people by what they need from each other and the terms they keep.",
  "20-34": "Raw sacral power goes straight to the voice: a current that is busy, visible and acts in the now.",
  "20-57": "Instant intuition speaks: energy that knows and says it in the same moment.",
  "21-45": "Will and control meet the voice of having: energy for managing resources and the material life of a group.",
  "23-43": "Inner insight becomes clear statement: a current that thinks differently, and lands when the moment is ripe.",
  "24-61": "Mystery in the head is turned over and over in the mind: energy that ponders until a knowing arrives.",
  "25-51": "Innocent love meets the shock of initiation: energy that leaps, competes and wakes others up.",
  "26-44": "Instinct for patterns feeds the will to persuade: energy that transmits, sells and brings the past's lessons forward.",
  "27-50": "Caring is held by values: energy that nourishes and protects, and keeps others alive.",
  "28-38": "The search for purpose meets the will to fight: energy that struggles for what makes life meaningful.",
  "29-46": "Saying yes is carried by the body: energy that commits fully and discovers through what it agreed to.",
  "30-41": "The fire of desire is fed from the root of contraction: energy for new experiences, felt fully before they begin.",
  "32-54": "Ambition is tested against what lasts: energy that drives upward and transforms what it touches.",
  "34-57": "Sacral power is guided by instinct: energy that survives, acts and knows how in the moment.",
  "35-36": "Hunger for change passes through emotional crisis: energy that goes into experience to learn what it is.",
  "37-40": "Friendship meets the will to be alone after work: energy for community, bargains and keeping one's word.",
  "39-55": "Provocation stirs the spirit: energy of moods that rise and fall, and of feeling deeply moved.",
  "42-53": "Beginnings are fed until they mature: energy that starts cycles and carries them through to completion.",
  "47-64": "Images from the head are made sense of in the mind: a current that turns confusion into realisation over time.",
};


const LEX = () => (window.WyrdDesignChart && window.WyrdDesignChart.lex) || {};
const gName = g => { const x = (LEX().gate || {})[g]; return x ? `${x.name}${x.title && x.title !== x.name ? ` · ${x.title}` : ""}` : ""; };
function carriers(R, g){
  const out = [];
  for (const [side, col] of [["conscious", R.rave.personality], ["unconscious", R.rave.design]])
    for (const [b, v] of Object.entries(col || {})) if (v && v.gate === g) out.push(`${side} ${b} (line ${v.line})`);
  return out;
}
function chanItem(R, [a, b]){
  /* the current runs from the centre farther from the throat toward the nearer */
  const ca = CENTRE_OF[a], cb = CENTRE_OF[b], fromA = WyrdBody.runsFrom(R.dist, ca, cb);
  const [g1, c1, g2, c2] = fromA ? [a, ca, b, cb] : [b, cb, a, ca];
  return `<li><b>${a}–${b}</b> · ${CENTRES[c1].label} → ${CENTRES[c2].label}
    <p>${CHANNEL[`${Math.min(a, b)}-${Math.max(a, b)}`] || ""}</p>
    <p class="fine">The current leaves your ${CENTRES[c1].label} through gate ${g1}${gName(g1) ? ` (${gName(g1)})` : ""}, carried by your ${carriers(R, g1).join(" and ")},
    and arrives in your ${CENTRES[c2].label} through gate ${g2}${gName(g2) ? ` (${gName(g2)})` : ""}, carried by your ${carriers(R, g2).join(" and ")}.</p></li>`;
}
function gatesList(R){
  const order = ["head", "ajna", "throat", "g", "heart", "spleen", "solar", "sacral", "root"];
  const inLive = new Set(R.live.flat());
  return order.map(k => {
    const gs = [...R.gates].filter(g => CENTRE_OF[g] === k).sort((x, y) => x - y);
    if (!gs.length) return "";
    return `<div class="dg-gates"><h5>${CENTRES[k].label}${R.defined.has(k) ? " · defined" : " · open"}</h5><ul>${gs.map(g => {
      const x = (LEX().gate || {})[g];
      return `<li><b>Gate ${g}${gName(g) ? ` · ${gName(g)}` : ""}</b>${inLive.has(g) ? ' <span class="dg-tag">in a channel</span>' : ' <span class="dg-tag open">open thread</span>'}
        <br><span class="fine">${carriers(R, g).join(", ")}</span>${x && x.gist ? `<p>${x.gist}</p>` : ""}</li>`; }).join("")}</ul></div>`;
  }).join("");
}

function readout(R, label){
  const order = ["head", "ajna", "throat", "g", "heart", "spleen", "solar", "sacral", "root"];
  const reached = MOTORS.filter(m => R.defined.has(m) && m in R.dist && R.dist[m] > 0);
  const route = R.defined.has("throat")
    ? reached.length ? `The current rises from your ${reached.map(m => CENTRES[m].label).join(" and ")} and surfaces at your throat as voice and action.`
      : "Your throat is defined, but no motor reaches it: what you say and do is shaped by the centres joined to it, and moved by energy around you."
    : "Your throat is open: energy reaches expression through others and through the moment, rather than along a fixed route of your own.";
  return `<div class="dg-read">
    <h3>${label}</h3>
    <dl class="dg-facts"><dt>Type</dt><dd>${R.type}</dd><dt>Authority</dt><dd>${R.authority}</dd><dt>Definition</dt><dd>${R.definition}</dd><dt>Profile</dt><dd>${esc(R.profile || "")}</dd></dl>
    <p>${TYPE[R.type]}</p><p>${AUTH[R.authority]}</p><p>${DEFN[R.definition] || ""}</p><p><b>How it flows:</b> ${route}</p>
    <details class="dg-fold"><summary>Your nine centres: ${R.defined.size} defined, ${9 - R.defined.size} open</summary>
    <ul class="dg-cen">${order.map(k => `<li class="${R.defined.has(k) ? "on" : ""}"><b>${CENTRES[k].label}</b> · ${R.defined.has(k) ? "defined, runs on its own current" : "open, takes in and amplifies the current around it"}<br><span class="fine">${CEN[k][0]} ${CEN[k][1]}.</span></li>`).join("")}</ul></details>
    <h4>Your channels: the currents</h4>
    ${R.live.length ? `<ul class="dg-chs">${R.live.map(ch => chanItem(R, ch)).join("")}</ul>` : "<p>No complete channels: every gate in you is an open thread, waiting for its partner in someone else or in the sky.</p>"}
    <details class="dg-fold"><summary>Your ${R.gates.size} gates, centre by centre</summary>
    <p class="fine">Each gate is a single doorway of energy, switched on by a planet. Conscious gates (personality) you know as yourself; unconscious ones (design) run in the body whether you notice or not. A gate on its own is an open thread; two gates at either end of a channel make a current.</p>
    ${gatesList(R)}</details>
  </div>`;
}

function mount(host, { C }){
  window.WyrdDesignChart = C;
  const birth = analyse(C.natal), dharma = C.dharma ? analyse(C.dharma) : null;
  let view = "birth";
  const draw = () => {
    const A = view !== "dharma" ? birth : null, B = view !== "birth" ? dharma : null;
    host.querySelector("#dgGraph").innerHTML = graph(A, B);
    host.querySelector("#dgRead").innerHTML = view === "both"
      ? `<div class="dg-two">${readout(birth, "Your Birth Design")}${readout(dharma, "Your Dharma Design")}</div>`
      : readout(view === "birth" ? birth : dharma, view === "birth" ? "Your Birth Design" : "Your Dharma Design");
  };
  host.innerHTML = `
    <div class="dg-wrap"><div class="dg-graph" id="dgGraph"></div><div id="dgRead"></div></div>
    <p class="fine">Filled centres run on their own steady current; open ones take in and amplify the current around them. The moving light shows which way it runs: up from the motors toward the throat, where it becomes voice and action.</p>
    <p class="dg-key"><span class="k birth"></span> Birth Design <span class="k dharma"></span> Dharma Design <span class="k both"></span> both <span class="k open"></span> open</p>
    <p class="fine">To read the Dharma design in depth, see <a href="/learn/dharma">Learn the Dharma Design</a>.</p>`;
  draw();
  return { set(v){ view = dharma || v === "birth" ? v : "birth"; draw(); } };
}

window.WyrdDesign = { mount, analyse, graph };
})();
