'use strict';
/* ============================================================
   THE DHARMA WEAVE (free)
   How the dharma rave is made, worked through with this person's own
   numbers, like the clock's "how your clock was set": the two moments,
   the multiply-by-nine, the Pentagram Cross, the dharma profile and band,
   every dharma activation beside its birth one, and what the dharma rave
   defines. What it all MEANS is the reading's work (sections V and VI).
   ============================================================ */
(() => {
const { signOf, degIn, norm, GLYPH, HOUSES, houseOf } = Wyrd.helpers;
const g = (k, l) => Wyrd.gloss(k, l);
const LINE = 360 / 64 / 6;
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };
const lon = l => `${signOf(l)} ${dm(l)}`;
const day = jd => new Date((jd - 2440587.5) * 864e5).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
const BODIES = ["Sun", "Earth", "Moon", "Rahu", "Ketu", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"];

function pentagram(C){
  const D = C.dharma, P = (r, l) => { const a = (l - 90) * Math.PI / 180; return [200 + r * Math.cos(a), 200 + r * Math.sin(a)]; };
  const f = n => n.toFixed(1);
  let s = `<circle cx="200" cy="200" r="170" class="dw-ring"/><circle cx="200" cy="200" r="150" class="dw-ring"/>`;
  for (let i = 0; i < 12; i++){
    const [x0, y0] = P(150, i * 30), [x1, y1] = P(170, i * 30), [tx, ty] = P(186, i * 30 + 15);
    s += `<line x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}" class="dw-tick"/><text x="${f(tx)}" y="${f(ty)}" class="dw-sign">${SIGN_GLYPH[i]}︎</text>`;
  }
  const pts = [0, 1, 2, 3, 4].map(k => P(150, D.suns.p + k * 72));
  s += `<polygon points="${[0, 2, 4, 1, 3].map(k => pts[k].map(f).join(",")).join(" ")}" class="dw-star"/>`;
  for (const [k, l, cls] of [["Dharma Sun", D.suns.p, "p"], ["Dharma design Sun", D.suns.d, "d"]]){
    const [x, y] = P(150, l), [lx, ly] = P(118, l);
    s += `<circle cx="${f(x)}" cy="${f(y)}" r="7" class="dw-sun ${cls}"/><text x="${f(lx)}" y="${f(ly)}" class="dw-lbl ${cls}">☉ ${cls === "p" ? "P" : "D"}</text>`;
  }
  return `<svg viewBox="0 0 400 400" class="dw-svg" role="img" aria-label="The Pentagram Cross: the two dharma Suns ${D.suns.gap.toFixed(2)} degrees apart">${s}</svg>`;
}

function mount(host, X){
  const C = X.C, D = C.dharma, N = C.natal;
  if (!D){ host.innerHTML = `<p class="err">The Dharma Design isn't available for this chart.</p>`; return; }
  const bs = C.sid.Sun, ds = C.tropDes ? norm(C.tropDes.Sun - C.ay) : norm(bs - 88);   // sidereal, in the birth's frame
  const step = (n, title, body) => `<div class="dw-step"><span>${n}</span><div><h3>${title}</h3>${body}</div></div>`;
  const times9 = (l, label) => {
    const raw = l * 9, circles = Math.floor(raw / 360), res = norm(raw);
    return `<tr><th>${label}</th><td>${l.toFixed(2)}°</td><td>× 9 = ${raw.toFixed(2)}°</td><td>− ${circles} × 360°</td><td>= ${res.toFixed(2)}° <small>(${lon(res)})</small></td></tr>`;
  };
  const into = D.personality.Sun.intoLine, intoMin = into * 60, echo = D.band === "Echo";
  const rB = WyrdWheel.raveOf(N), rD = WyrdWheel.raveOf(D);
  const newly = rD.centres.filter(c => !rB.centres.includes(c)), lost = rB.centres.filter(c => !rD.centres.includes(c));
  const rows = BODIES.map(b => {
    const np = N.personality[b], dp = D.personality[b], nd = N.design[b], dd = D.design[b];
    const same = (a, c) => a && c && a.gate === c.gate;
    return `<tr><th scope="row">${GLYPH[b] || "⊕"} ${b}</th><td>${np.gate}.${np.line}</td><td class="${same(np, dp) ? "dw-rep" : ""}">${dp.gate}.${dp.line}</td>
      <td class="des">${nd.gate}.${nd.line}</td><td class="des ${same(nd, dd) ? "dw-rep" : ""}">${dd.gate}.${dd.line}</td></tr>`;
  }).join("");
  const reps = BODIES.filter(b => N.personality[b].gate === D.personality[b].gate || N.design[b].gate === D.design[b].gate);

  host.innerHTML = `
    ${Wyrd.glossTerms(["dharmaweave", "navamsa", "pentagram", "dharmaprofile", "band", "gate", "design"])}
    ${X.unknown ? `<p class="unknown-note">Without a birth time the dharma positions are uncertain: the Sun's dharma moves about 9° a day, so its gate and line, and the dharma Moon, may not be yours.</p>` : ""}
    <div class="vd-decode">
      <h3>What the Dharma Weave is</h3>
      <p>Your Birth Design reads two moments: your birth, and the design moment about three months before it, when the Sun stood exactly 88° earlier.
      The Dharma Weave takes those same two moments and passes every sidereal position through the ${g("navamsa", "navamsa")}, the ninth harmonic of Jyotish,
      which is the chart of what a life ripens into. The result is a second design, laid over the first: your Dharma Design.</p>
    </div>
    <h3 class="vd-h">How your Dharma Design was made</h3>
    ${step(1, "Two moments", `<p>Your birth, and your design moment on <b>${day(C.jdDes)}</b>.
      At birth your Sun stood at <b>${lon(bs)}</b> (sidereal); at the design moment, 88° earlier, at <b>${lon(ds)}</b>.</p>`)}
    ${step(2, "Multiply by nine", `<p>Every position at both moments is multiplied by nine and taken around the circle, which is what the navamsa does. Your two Suns:</p>
      <div class="tw"><table class="dw-calc">${times9(bs, "☉ Sun at birth")}${times9(ds, "☉ Sun at design")}</table></div>
      <p>So your dharma Sun is gate <b>${D.personality.Sun.gate}.${D.personality.Sun.line}</b>, and your dharma design Sun gate <b>${D.design.Sun.gate}.${D.design.Sun.line}</b>.
      The same is done for every planet; they are all in the table below.</p>`)}
    ${step(3, "The Pentagram Cross", `<div class="dw-pent">${pentagram(C)}<div>
      <p>Because both Suns are multiplied by nine, the 88° between them is multiplied too: 88 × 9 = 792°, and 792 less two full circles is exactly <b>72°</b>,
      one fifth of the wheel. Every dharma chart ever cast has its two Suns on two points of a pentagram. That is the ${g("pentagram", "Pentagram Cross")}.</p>
      <p>Your two dharma Suns are <b>${D.suns.gap.toFixed(4)}°</b> apart ${D.suns.holds ? "✓" : ""}.</p></div></div>`)}
    ${step(4, "The dharma profile and the band", `<p>As in the rave, the line of each Sun gives the profile. Your dharma Sun is in line ${D.personality.Sun.line} and your dharma design Sun in line ${D.design.Sun.line}:
      your ${g("dharmaprofile", "dharma profile")} is <b>${D.profile}</b>${D.mauve ? `, the ${g("magenta", "magenta point")}` : ""}. Your birth profile is ${N.profile}.</p>
      <p>The ${g("band")} is read from how far the dharma Sun has travelled into its line. A line is ${(LINE * 60).toFixed(2)}′ wide, and its last 11.25′ is the echo band.
      Your dharma Sun is <b>${intoMin.toFixed(1)}′</b> into its line, so your band is <b>${D.band}</b>${echo ? " (an echo)" : " (the seam)"}.</p>`)}
    ${step(5, "Every dharma activation", `<p>All thirteen bodies, at birth and in the dharma. A gate that repeats is outlined.</p>
      <div class="tw"><table class="dw-table"><tr><th scope="col">Body</th><th scope="col">Birth</th><th scope="col">Dharma</th><th scope="col">Design</th><th scope="col">Dharma design</th></tr>${rows}</table></div>
      <p class="fine">${reps.length ? `Repeating across both designs: ${reps.join(", ")}.` : "No gate repeats between your Birth and Dharma Designs."}</p>`)}
    ${step(6, "What the Dharma Design defines", `<dl class="ln-dl">
      <dt>${g("type")}</dt><dd>${rD.type} <small>(birth: ${rB.type})</small></dd>
      <dt>${g("authority")}</dt><dd>${rD.authority} <small>(birth: ${rB.authority})</small></dd>
      <dt>${g("definition")}</dt><dd>${rD.definition}</dd>
      <dt>${g("centre", "Defined")}</dt><dd>${rD.centres.join(", ") || "none"}</dd>
      <dt>${g("channel", "Channels")}</dt><dd>${rD.channels.join(", ") || "none"}</dd></dl>
      <p>${newly.length ? `The dharma defines ${newly.join(", ")}, which your Birth Design leaves open.` : ""} ${lost.length ? `Your Birth Design defines ${lost.join(", ")}, which the dharma leaves open.` : ""}
      ${!newly.length && !lost.length ? "Your dharma rave defines the same centres as your birth rave." : ""}</p>`)}
    ${step(7, "See it on the body", `<p>The Harmonic Body can lay your Dharma Design over the engraving: turn on <b>Dharma Design</b> there, alone or with your Birth Design, to see where they agree.</p>
      <p><a class="ln-deep" href="#design/harmonic">Open the Harmonic Body →</a></p>`)}`;
}

/* ============================================================
   WHAT IS DHARMA? WHAT IS SVADHARMA?
   The plain answer, before the Dharma Design is shown: the word, svadharma
   in the Gita, dharma among the four aims and its three houses, the navamsa
   as the chart of dharma, and what this system's Dharma Design is (marked as
   its construction). With the person's own houses of each aim to tap through.
   DRAFT wording for The Völva to edit. What dharma asks of THIS person stays
   in the reading.
   ============================================================ */
const AIMS = [
  { id: "dharma", name: "Dharma", gloss: "what upholds: purpose, right conduct, the teacher and the teaching", houses: [1, 5, 9] },
  { id: "artha", name: "Artha", gloss: "means: work, wealth, the material a life is lived with", houses: [2, 6, 10] },
  { id: "kama", name: "Kama", gloss: "desire: love, pleasure, what draws a life on", houses: [3, 7, 11] },
  { id: "moksha", name: "Moksha", gloss: "release: letting go, the way out of the wheel", houses: [4, 8, 12] },
];
const SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const ORDN = n => n + (["th","st","nd","rd"][(n % 100 - 20) % 10] || ["th","st","nd","rd"][n % 100] || "th");
function aimWheel(aim){
  const P = (r, d) => [150 + r * Math.cos(d * Math.PI / 180), 150 + r * Math.sin(d * Math.PI / 180)];
  const at = h => angleHouse(h) + 15, f = n => n.toFixed(1);
  let s = `<svg viewBox="0 0 300 300" class="wd-wheel" role="img" aria-label="The twelve houses, with the four triangles of the aims of life; ${aim.name} lit: houses ${aim.houses.join(", ")}">`;
  for (const a of AIMS){
    const pts = a.houses.map(h => P(104, at(h)).map(f).join(",")).join(" ");
    s += `<polygon points="${pts}" class="wd-tri${a === aim ? " on" : ""}"/>`;
  }
  for (let h = 1; h <= 12; h++){
    const [x, y] = P(104, at(h)), [tx, ty] = P(132, at(h)), lit = aim.houses.includes(h);
    s += `<circle cx="${f(x)}" cy="${f(y)}" r="${lit ? 15 : 10}" fill="${HOUSES[h - 1].hex}" class="wd-dot${lit ? " on" : ""}"/>
      <text x="${f(x)}" y="${f(y + 4)}" class="wd-n${lit ? " on" : ""}">${h}</text>`;
  }
  return s + `<text x="150" y="146" class="wd-c1">${aim.name.toUpperCase()}</text><text x="150" y="162" class="wd-c2">houses ${aim.houses.join(" · ")}</text></svg>`;
}
function aimYours(aim, C, unknown){
  const asc = Math.floor(norm(C.ascS) / 30);
  const rows = aim.houses.map(h => {
    const sign = (asc + h - 1) % 12;
    const here = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"].filter(b => houseOf(C.sid[b], C.ascS) === h);
    return `<li><span class="sw" style="background:${HOUSES[h - 1].hex}"></span><b>${ORDN(h)}</b> ${SIGN_NAMES[sign]}${here.length ? ` · ${here.map(b => `${GLYPH[b]} ${b}`).join(", ")}` : ""}</li>`;
  }).join("");
  const n = aim.houses.reduce((k, h) => k + ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"].filter(b => houseOf(C.sid[b], C.ascS) === h).length, 0);
  return `<p class="wd-aim"><b>${aim.name}</b> is ${aim.gloss}.</p>
    <p class="fine">In your chart${unknown ? " (counted from your Sun's sign, without a birth time)" : ""}:</p><ul class="wd-yours">${rows}</ul>
    <p class="fine">${n === 0 ? "None of your nine planets stands in these houses; the signs and their lords still carry this aim." : `${n} of your nine planets ${n === 1 ? "stands" : "stand"} in these houses.`}</p>`;
}
function what(host, X){
  const C = X.C;
  let aim = AIMS[0];
  host.innerHTML = `<div class="wd">
    <div class="wd-text">
      <p class="wd-lead"><b>Dharma</b> comes from the Sanskrit root <i>dhṛ</i>: to hold, to bear, to uphold. Dharma is what holds. It is the order that keeps the world together, the way of acting that keeps faith with that order, and a thing's own nature, what it cannot stop being and still be itself. Fire's dharma is to burn.</p>
      <p><b>Svadharma</b> (also written swadharma) is <i>sva</i>, one's own, and dharma: your own dharma, the way of living that fits your own nature (<i>svabhava</i>), rather than one borrowed from someone else. The Bhagavad Gita says it twice, in almost the same words (3.35 and 18.47):</p>
      <blockquote class="wd-gita"><p lang="sa-Latn"><i>śreyān svadharmo viguṇaḥ paradharmāt svanuṣṭhitāt</i></p>
        <p>Better your own dharma, done imperfectly, than another's done well.</p></blockquote>
      <p>Jyotish counts dharma first among the four aims of a life, with artha, kama and moksha, and gives each aim a triangle of houses. Dharma's are the 1st, 5th and 9th, and the 9th is called the house of dharma. Jyotish also reads the ${g("navamsa", "navamsa")}, the chart of the ninth division, as the chart of dharma. If your birth chart is what you are made of, the navamsa is what that material is for: what the life ripens into as it is lived.</p>
      <p>Your <b>Dharma Design</b> is this system's own construction. It takes the navamsa and applies it to the two moments of your Birth Design, so the Birth Design shows how your energy runs and the Dharma Design shows what it runs toward. It is not a second, better self to climb up to. It is the same life, read for what it is for. Living your svadharma is living the one through the other: your own nature, toward its own purpose.</p>
    </div>
    <div class="wd-aims">
      <div class="cr-btns" role="group" aria-label="The four aims of a life">${AIMS.map(a => `<button type="button" class="tz-chip" data-wd-aim="${a.id}" aria-pressed="${a === aim}">${a.name}</button>`).join("")}</div>
      <div class="wd-show"></div>
    </div></div>`;
  const show = () => {
    host.querySelector(".wd-show").innerHTML = aimWheel(aim) + aimYours(aim, C, X.unknown);
    host.querySelectorAll("[data-wd-aim]").forEach(b => b.setAttribute("aria-pressed", b.dataset.wdAim === aim.id));
  };
  show();
  host.addEventListener("click", e => { const b = e.target.closest("[data-wd-aim]"); if (b){ aim = AIMS.find(a => a.id === b.dataset.wdAim); show(); } });
}

window.WyrdDharma = { mount, what };
})();
