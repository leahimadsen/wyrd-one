'use strict';
/* ============================================================
   LEARN YOUR CHART
   A straight path through the console for someone who has never
   read a chart: thirteen short steps, each one ring of the wheel.
   Every step says what the thing is (in general), then shows the
   visitor's own placements, then gives one thing to try. What the
   placements MEAN is left to the reading.
   Progress is kept in this browser (localStorage "wyrdLearn").
   ============================================================ */
(() => {
const STORE = "wyrdLearn";
const g = (k, l) => Wyrd.gloss(k, l);
const { signOf, degIn, nakIndex, houseOf, norm, GLYPH, NAKSHATRA } = Wyrd.helpers;
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };
const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;
const BODIES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"];
const fmtDate = jd => new Date((jd - 2440587.5) * 864e5).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });

const LESSONS = [
  { id: "wheel", t: "The wheel", q: "What am I looking at?", level: "simple", focus: null,
    body: () => `<p>This wheel is the sky at the moment you were born, seen from the place you were born, laid flat as a circle.
      The bands around the edge are different ways of dividing that sky. The glyphs inside are the ${g("graha", "planets")}, each drawn where it stood.</p>
      <p>Nothing here is interpretation yet. It is a map, and every land in this console is another way of looking at the same map.
      The path you are on walks through it one ring at a time.</p>`,
    yours: X => `<dl class="ln-dl"><dt>☉ Sun</dt><dd>${signOf(X.C.sid.Sun)}</dd><dt>☽ Moon</dt><dd>${signOf(X.C.sid.Moon)}</dd>
      <dt>↑ Rising</dt><dd>${X.unknown ? "unknown without a birth time" : signOf(X.C.ascS)}</dd></dl>
      <p class="ln-small">These three, the Sun, the Moon and the ${g("asc", "rising sign")}, are the usual first things anyone asks about a chart.</p>`,
    tryIt: "Tap the ☉ glyph on the wheel. A card opens with everything about your Sun, and its place lights up in every ring." },

  { id: "zodiacs", t: "Two zodiacs", q: "Why are there two rings of signs?", level: "simple", focus: ["tro", "sid"],
    body: () => `<p>There are two ways to measure the zodiac. The ${g("tropical")} zodiac starts from the spring equinox and is used by most Western astrology.
      The ${g("sidereal")} zodiac is measured against the stars themselves and is used in Jyotish, the astrology of India.</p>
      <p>They were together about 1,700 years ago and have drifted apart ever since; the gap, the ${g("ayanamsa")}, is now about 24°.
      On the wheel, the purple badges are tropical and the gold ring inside them is sidereal.</p>`,
    yours: X => {
      const s = signOf(X.C.sid.Sun), t = signOf(X.C.trop.Sun);
      return `<dl class="ln-dl"><dt>Sun, tropical</dt><dd>${t} ${dm(X.C.trop.Sun)}</dd><dt>Sun, sidereal</dt><dd>${s} ${dm(X.C.sid.Sun)}</dd>
        <dt>Your ayanamsa</dt><dd>${X.C.ay.toFixed(2)}°</dd></dl>
        <p class="ln-small">${s === t ? `Your Sun is in ${s} in both zodiacs.` : `Your Sun is in ${t} by one zodiac and ${s} by the other. That is why the "sun sign" in a magazine may not match the one here.`}
        This console reads signs, houses, mansions and runes sidereally; the gates run tropically.</p>`;
    },
    tryIt: "Find your Sun's two signs: follow its line out to the gold ring, then to the purple badges." },

  { id: "houses", t: "The houses", q: "What are the coloured segments?", level: "simple", focus: ["hou", "ang"],
    body: () => `<p>The ${g("house", "houses")} divide the chart into twelve areas of life. They are counted from the ${g("asc", "rising sign")}, the sign coming up over the eastern horizon when you were born:
      that sign is the 1st house, the next is the 2nd, and on round. This is the oldest method, ${g("wholesign", "whole-sign houses")}.</p>
      <p>Each house has its colour, red at the 1st through violet and magenta at the 12th. The four lines are the ${g("angles")}: ascendant, descendant, midheaven and IC.</p>`,
    yours: X => {
      const by = {}; for (const b of BODIES) (by[houseOf(X.C.sid[b], X.C.ascS)] ||= []).push(GLYPH[b]);
      return `${X.unknown ? `<p class="ln-small">Without a birth time the houses here are counted from your Sun's sign (solar houses), and the angles are left out.</p>` :
        `<p>Your rising sign is <b>${signOf(X.C.ascS)}</b> at ${dm(X.C.ascS)}, so ${signOf(X.C.ascS)} is your 1st house.</p>`}
        <ul class="ln-houses">${Array.from({ length: 12 }, (_, i) => `<li><span style="background:${HOUSES[i].hex}">${i + 1}</span>${(by[i + 1] || []).join(" ") || "<i>empty</i>"}</li>`).join("")}</ul>
        <p class="ln-small">An empty house is common and normal: twelve houses, twelve bodies.</p>`;
    },
    tryIt: "Tap a coloured house on the wheel to see which sign fills it and who stands there." },

  { id: "planets", t: "The planets", q: "Which bodies does the chart track?", level: "simple", focus: ["pl"],
    body: () => `<p>Jyotish counts nine ${g("graha", "grahas")}: the Sun, Moon, Mercury, Venus, Mars, Jupiter and Saturn, and the two lunar nodes, ${g("nodes", "Rahu and Ketu")}.
      This console also tracks Uranus, Neptune and Pluto.</p>
      <p>Two more things are worth knowing about each one: whether it was ${g("retro", "retrograde")} (appearing to move backwards), and its ${g("dignity")}, how comfortable it is in its sign by the classical rules.</p>`,
    yours: X => `<table class="ln-t">${BODIES.map(b => {
        const d = X.dignity(b), r = X.retro(b);
        return `<tr><th>${GLYPH[b]} ${b}</th><td>${signOf(X.C.sid[b])} ${dm(X.C.sid[b])}${r ? ` <span class="rx" title="retrograde">℞</span>` : ""}</td><td>${d ? `<span class="dg ${d.k}">${d.label}</span>` : ""}</td></tr>`;
      }).join("")}</table>`,
    tryIt: "Tap any planet on the wheel and follow it through every ring." },

  { id: "aspects", t: "Aspects", q: "What are the lines in the middle?", level: "full", focus: ["asp", "pl"],
    body: () => `<p>An ${g("aspect")} is a meaningful angle between two planets: together (conjunction, 0°), opposite (180°), at right angles (square, 90°),
      a third of the circle apart (trine, 120°) or a sixth (sextile, 60°). The ${g("orb")} is how far from exact it is.</p>
      <p>The coloured lines in the middle of the full wheel are your aspects. The wheel has switched to its full view for this step.</p>`,
    yours: X => {
      const list = [];
      for (let i = 0; i < BODIES.length; i++) for (let k = i + 1; k < BODIES.length; k++){
        const [a, b] = [BODIES[i], BODIES[k]]; if (a === "Rahu" && b === "Ketu") continue;
        const x = aspectBetween(X.C.sid[a], X.C.sid[b]); if (x) list.push({ a, b, x });
      }
      list.sort((p, q) => p.x.orb - q.x.orb);
      return `<p>You have ${list.length} aspects within orb. The closest:</p><ul class="ln-list">${list.slice(0, 5).map(({ a, b, x }) =>
        `<li>${GLYPH[a]} ${a} <span style="color:${x.col}">${x.name.toLowerCase()}</span> ${GLYPH[b]} ${b} <small>orb ${x.orb.toFixed(1)}°</small></li>`).join("")}</ul>`;
    },
    tryIt: "The full list is under \"Every placement\" in Your chart." , deeper: "chart" },

  { id: "mansions", t: "The mansions", q: "What is the ring of names?", level: "full", focus: ["nak", "pl"], select: ["body", "Moon"],
    body: () => `<p>Before the twelve signs, the sky was divided into twenty-seven ${g("nakshatra", "mansions")}, one for each day of the Moon's circuit.
      Each mansion is 13°20′ wide, has a ruling planet and a deity, and is split into four ${g("pada", "padas")}.</p>
      <p>The Moon's mansion is one of the most personal points in a chart; it also sets the clock you'll meet later.</p>`,
    yours: X => {
      const m = nakIndex(X.C.sid.Moon), s = nakIndex(X.C.sid.Sun);
      return `<dl class="ln-dl"><dt>☽ Moon</dt><dd>${NAKSHATRA[m][0]}, pada ${pada(X.C.sid.Moon)} · ruled by ${NAKSHATRA[m][1]}</dd>
        <dt>☉ Sun</dt><dd>${NAKSHATRA[s][0]}, pada ${pada(X.C.sid.Sun)}</dd>
        ${X.unknown ? "" : `<dt>↑ Rising</dt><dd>${NAKSHATRA[nakIndex(X.C.ascS)][0]}</dd>`}</dl>
        ${X.unknown && X.C.moonSpan && X.C.moonSpan.length > 1 ? `<p class="ln-small">Without a birth time your Moon may have been in ${X.C.moonSpan.join(" or ")}.</p>` : ""}`;
    },
    tryIt: "Your Moon is lit on the wheel. Tap other names in the mansion ring." },

  { id: "runes", t: "The runes", q: "What are the runes doing on a chart?", level: "simple", focus: ["run", "pl"],
    body: () => `<p>The twenty-four ${g("rune", "runes")} of the Elder Futhark are seated two to a house, in order from Fehu at the start of the 1st house to Othala at the end of the 12th.
      The first rune of each house is its ${g("ingress", "opening rune")} (its first 15°), the second its ${g("egress", "closing rune")}.</p>
      <p>A rune is lit, outlined in white, when one of your planets stands in it.</p>`,
    yours: X => {
      const lit = {};
      for (const b of BODIES){ const r = WyrdWheel.runeAt(X.C, X.C.sid[b]); (lit[r.glyph + " " + r.name] ||= { h: r.house, b: [] }).b.push(GLYPH[b] + " " + b); }
      return `<p>${Object.keys(lit).length} of your runes are lit:</p><ul class="ln-list">${Object.entries(lit).map(([k, v]) =>
        `<li><span class="ln-rune">${k}</span> <small>house ${v.h}</small> · ${v.b.join(", ")}</li>`).join("")}</ul>`;
    },
    tryIt: "Tap a rune on the wheel, lit or not, to see its house." },

  { id: "gates", t: "The gates", q: "What are the numbers around the wheel?", level: "full", focus: ["gat", "des", "pl"],
    body: () => `<p>The sixty-four ${g("gate", "gates")} divide the tropical zodiac into the sixty-four hexagrams of the I Ching. Each gate has six ${g("line", "lines")},
      so a position is written as gate.line.</p>
      <p>Gates are lit by two moments: your birth (the ${g("personality", "personality")}, ivory) and the ${g("design")}, about three months before birth, when the Sun stood 88° earlier (teal glyphs and cells).</p>`,
    yours: X => {
      const P = X.C.natal.personality, D = X.C.natal.design;
      return `<dl class="ln-dl"><dt>☉ Sun at birth</dt><dd>${P.Sun.gate}.${P.Sun.line}</dd><dt>⊕ Earth at birth</dt><dd>${P.Earth.gate}.${P.Earth.line}</dd>
        <dt>☉ Design Sun</dt><dd>${D.Sun.gate}.${D.Sun.line}</dd><dt>⊕ Design Earth</dt><dd>${D.Earth.gate}.${D.Earth.line}</dd></dl>
        <p class="ln-small">Those four are your ${g("cross", "cross gates")}. Every activated gate is listed in Your chart.</p>`;
    },
    tryIt: "Tap a lit gate number to see which planets activate it." },

  { id: "rave", t: "The rave", q: "What do the gates add up to?", level: "full", focus: ["gat"],
    body: () => `<p>Gates join in pairs to make ${g("channel", "channels")}. When both gates of a channel are lit, the two ${g("centre", "centres")} it connects are defined.
      From which centres are defined, and how they connect, come your ${g("type")}, ${g("strategy")}, ${g("authority")} and ${g("definition")}. The two Sun lines make your ${g("profile")}.</p>`,
    yours: X => {
      const r = WyrdWheel.rave(X.C);
      return `<dl class="ln-dl"><dt>Type</dt><dd>${r.type}</dd><dt>Strategy</dt><dd>${r.strategy}</dd><dt>Authority</dt><dd>${r.authority}</dd>
        <dt>Definition</dt><dd>${r.definition}</dd><dt>Profile</dt><dd>${r.profile}</dd><dt>Channels</dt><dd>${r.channels.join(", ") || "none"}</dd></dl>`;
    },
    tryIt: "The harmonic body shows the centres on a figure. Turn on \"Body Rave\" there.", deeper: "body" },

  { id: "day", t: "Your birth day", q: "What kind of day were you born on?", level: "simple", focus: ["nak"],
    body: () => `<p>The Vedic calendar describes every day by its ${g("panchanga")}, five limbs: the weekday (${g("vara")}), the lunar day (${g("tithi")}),
      the Moon's mansion, the ${g("yoga")} and the ${g("karana")}. The Vedic day starts at sunrise, not midnight.</p>`,
    yours: X => {
      const P = X.C.extras && X.C.extras.panchanga; if (!P) return "";
      return `<dl class="ln-dl"><dt>Vara</dt><dd>${P.vara} <small>(ruled by ${P.varaLord})</small></dd>
        <dt>Tithi</dt><dd>${P.paksha} ${P.tithiName} <small>(lunar day ${P.tithi} of 30)</small></dd>
        <dt>Mansion</dt><dd>${P.nakshatra}</dd><dt>Yoga</dt><dd>${P.yoga}</dd><dt>Karana</dt><dd>${P.karana}</dd></dl>
        ${P.beforeSunrise ? `<p class="ln-small">You were born before sunrise (${P.sunrise}), so by Vedic reckoning it was still the previous day.</p>` : ""}`;
    },
    tryIt: "Your birth day is also listed in Your chart." , deeper: "chart" },

  { id: "clock", t: "The clock", q: "What chapter of life am I in?", level: "simple", focus: ["nak"], select: ["body", "Moon"],
    body: () => `<p>The ${g("vimshottari", "Vimshottari")} is the main timing system of Jyotish: a 120-year cycle of nine planetary periods.
      Where the Moon stood in its mansion at birth sets where your clock started. Each ${g("mahadasha", "major period")} divides into ${g("antardasha", "chapters")}, and each chapter into ${g("pratyantar", "passages")}.</p>`,
    yours: X => {
      const T = X.C.dashaTree;
      return `<dl class="ln-dl"><dt>Era</dt><dd>${GLYPH[T.cur.lord]} ${T.cur.lord}, until ${fmtDate(T.cur.to)}</dd>
        <dt>Chapter</dt><dd>${GLYPH[T.curA.lord]} ${T.curA.lord}, until ${fmtDate(T.curA.to)}</dd>
        <dt>Passage</dt><dd>${GLYPH[T.curP.lord]} ${T.curP.lord}, until ${fmtDate(T.curP.to)}</dd></dl>
        ${X.unknown ? `<p class="ln-small">The clock depends on the Moon, so without a birth time these dates may be out by months.</p>` : ""}`;
    },
    tryIt: "The clock land shows your whole 120 years and how your clock was set, step by step.", deeper: "clock" },

  { id: "now", t: "The sky now", q: "What is the sky doing to my chart?", level: "simple", focus: ["pl"],
    body: () => `<p>The planets keep moving. A ${g("transit")} is where a planet is today compared with where it was at your birth.
      When a moving planet reaches one of yours, or an exact aspect to it, that birth planet is being touched.</p>`,
    yours: X => {
      const rows = (X.C.transits && X.C.transits.rows) || [], hits = rows.filter(r => r.on && r.on.length);
      return `<p>${hits.length ? `Right now ${hits.length} moving planet${hits.length > 1 ? "s are" : " is"} touching your chart:` : "Right now no moving planet is close to one of yours."}</p>
        <ul class="ln-list">${hits.map(r => `<li>${GLYPH[r.body]} ${r.body} on ${r.on.map(h => h.point).join(", ")}</li>`).join("")}</ul>
        ${X.C.transits && X.C.transits.sadeSati ? `<p class="ln-small">Saturn is in its ${g("sadesati", "Sade Sati")} passage over your Moon.</p>` : ""}`;
    },
    tryIt: "What's coming lists the next twelve months of these, with dates.", deeper: "calendar" },

  { id: "next", t: "Where to go next", q: "What have I learned, and what's left?", level: "simple", focus: null,
    body: () => `<p>You can now read the map: two zodiacs, the houses, the planets and their aspects, the mansions, the runes, the gates and the rave,
      your birth day, your clock and today's sky. Every land on the map goes deeper into one of these.</p>
      <p>What none of them do is say what your placements <em>mean</em> together. That is the reading: eight movements written for your chart and nobody else's.</p>`,
    yours: () => `<p><a class="btn-buy ln-cta" href="#reading">See your full reading</a></p>
      <details class="ln-gl"><summary>The whole glossary</summary>${Wyrd.glossAll()}</details>`,
    tryIt: "" },
];

function mount(host, X){
  let step = X.step != null ? X.step : load();
  host.innerHTML = `<div class="ln">
    <ol class="ln-steps" aria-label="Steps">${LESSONS.map((l, i) => `<li><a href="#learn/${i + 1}" data-step="${i}"><span>${i + 1}</span>${l.t}</a></li>`).join("")}</ol>
    <div class="ln-main" tabindex="-1"></div>
    <div class="ln-wheel"></div></div>`;
  const main = host.querySelector(".ln-main");
  const W = WyrdWheel.mount(host.querySelector(".ln-wheel"), X.C, { level: "simple", noSwitch: true, unknownTime: X.unknown,
    name: X.name, idle: `<p class="wx-idle">Tap the wheel: planets, houses, runes, gates and mansions all open a card.</p>` });

  function show(i, focusText){
    step = Math.max(0, Math.min(LESSONS.length - 1, i)); save(step);
    if (Wyrd.pulse) Wyrd.pulse("learn", step + 1);
    const L = LESSONS[step], next = LESSONS[step + 1], prev = LESSONS[step - 1];
    host.querySelectorAll(".ln-steps a").forEach((a, k) => {
      a.classList.toggle("on", k === step); a.classList.toggle("done", k < maxReached());
      if (k === step) a.setAttribute("aria-current", "step"); else a.removeAttribute("aria-current");
    });
    main.innerHTML = `
      <p class="ln-count">Step ${step + 1} of ${LESSONS.length}</p>
      <div class="ln-bar" aria-hidden="true"><i style="width:${((step + 1) / LESSONS.length * 100).toFixed(1)}%"></i></div>
      <h3>${L.t}</h3><p class="ln-q">${L.q}</p>
      <div class="ln-body">${L.body(X)}</div>
      <div class="ln-yours"><h4>In your chart</h4>${L.yours(X)}</div>
      ${L.tryIt ? `<p class="ln-try"><b>Try it.</b> ${L.tryIt}</p>` : ""}
      <div class="ln-nav">
        ${prev ? `<a class="ln-prev" href="#learn/${step}">← ${prev.t}</a>` : "<span></span>"}
        ${L.deeper ? `<a class="ln-deep" href="#${L.deeper}">Go deeper →</a>` : ""}
        ${next ? `<a class="ln-next" href="#learn/${step + 2}">Next: ${next.t} →</a>` : ""}
      </div>`;
    if (W.level !== L.level) W.setLevel(L.level);
    W.focus(L.focus);
    if (L.select) W.select(L.select[0], L.select[1]); else W.clear();
    if (focusText) main.focus({ preventScroll: true });
    if (X.onStep) X.onStep(step, LESSONS.length);
  }
  show(step);
  return { show: i => show(i, true), get count(){ return LESSONS.length; } };
}

function load(){ try { const s = JSON.parse(localStorage.getItem(STORE) || "{}"); return Math.min(s.step || 0, LESSONS.length - 1); } catch (_) { return 0; } }
function maxReached(){ try { return JSON.parse(localStorage.getItem(STORE) || "{}").max || 0; } catch (_) { return 0; } }
function save(step){ try { localStorage.setItem(STORE, JSON.stringify({ step, max: Math.max(step, maxReached()) })); } catch (_) {} }
function progress(){ try { const s = JSON.parse(localStorage.getItem(STORE) || "null"); return s ? { step: s.step || 0, max: s.max || 0, total: LESSONS.length } : null; } catch (_) { return null; } }

window.WyrdLearn = { mount, progress, count: LESSONS.length };
})();
