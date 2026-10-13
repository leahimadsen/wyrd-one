'use strict';
/* ============================================================
   THE PLANS AS TAROT CARDS
   Each .plan on the offers and Order pages becomes a card. Its face is a
   dark arcanum of its own: a numeral, a drawn emblem with a rune at its
   heart, the name, one line (data-line) and the price. Click or tap and it
   turns over to the full plan. Without this script the plans stay plain cards.

   Which card is which comes from data-arcanum on the .plan. To change a
   card's numeral, rune or emblem, edit ARCANA below; colours are in plans.css
   (.plan[data-arcanum=...]).
   ============================================================ */
(() => {
const plans = document.querySelectorAll(".plans > .plan");
if (!plans.length) return;

const ARCANA = {
  reading:  { n: "I",   rune: "perthro", emblem: "wheel" },   // your whole chart: the wheel of 12 signs and 27 mansions
  together: { n: "II",  rune: "gebo",    emblem: "rings" },   // two or more charts, one story: interlaced rings
  order:    { n: "III", rune: "jera",    emblem: "moons" },   // your weather, every week: seven moons
  circle:   { n: "IV",  rune: "kenaz",   emblem: "seats" },   // for those who read for others: nine seats in a ring
};
const ROMAN = ["I", "II", "III", "IV", "V", "VI"];

/* the runes, drawn as strokes so they never depend on a font, centred on (100, 100) */
const RUNE = {
  perthro: "M90 80V120M90 80L101 92L111 80M90 120L101 108L111 120",
  gebo:    "M87 80L113 120M113 80L87 120",
  jera:    "M99 80L88 91L99 102M101 98L112 109L101 120",
  kenaz:   "M109 82L91 100L109 118",
};

const f = x => +x.toFixed(2);
const at = (r, deg) => { const a = deg * Math.PI / 180; return [f(100 + r * Math.cos(a)), f(100 + r * Math.sin(a))]; };
const ring = (r, cls = "") => `<circle cx="100" cy="100" r="${r}" class="${cls}"/>`;

const EMBLEM = {
  wheel() {
    let s = ring(74) + ring(52) + ring(30, "core");
    for (let i = 0; i < 12; i++) { const [x1, y1] = at(52, i * 30 - 90), [x2, y2] = at(74, i * 30 - 90); s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`; }
    for (let i = 0; i < 27; i++) { const [x1, y1] = at(77, i * 360 / 27 - 90), [x2, y2] = at(83, i * 360 / 27 - 90); s += `<line class="fine" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`; }
    const [x, y] = at(74, 180); s += `<circle class="lit" cx="${x}" cy="${y}" r="4"/>`;
    return s;
  },
  rings() {
    const h = f(Math.sqrt(46 * 46 - 22 * 22));
    return `<circle cx="78" cy="100" r="46"/><circle cx="122" cy="100" r="46"/>${ring(80, "fine dash")}
      <circle class="lit" cx="100" cy="${f(100 - h)}" r="3.5"/><circle class="lit" cx="100" cy="${f(100 + h)}" r="3.5"/>${ring(20, "core")}`;
  },
  moons() {
    let s = ring(28, "core") + ring(66, "fine dash");
    for (let i = 0; i < 7; i++) {
      const [cx, cy] = at(66, i * 360 / 7 - 90), r = 10, k = i / 6, rx = f(r * Math.abs(1 - 2 * k));
      s += `<circle cx="${cx}" cy="${cy}" r="${r}" class="moon"/>`;
      if (k > 0) s += `<path class="lit" d="M${cx} ${f(cy - r)}A${r} ${r} 0 0 1 ${cx} ${f(cy + r)}A${rx} ${r} 0 0 ${k < .5 ? 0 : 1} ${cx} ${f(cy - r)}Z"/>`;
    }
    return s;
  },
  seats() {
    let s = ring(84, "fine") + ring(26, "core");
    for (let i = 0; i < 9; i++) {
      const d = i * 40 - 90, [cx, cy] = at(66, d), [x1, y1] = at(34, d), [x2, y2] = at(55, d);
      s += `<line class="fine" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/><circle cx="${cx}" cy="${cy}" r="10"/>`;
    }
    return s;
  },
};

/* a few stars behind each card, the same every visit */
function stars(seed) {
  let h = 2166136261;
  for (const c of seed) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  const rnd = () => ((h = Math.imul(h ^ (h >>> 15), 2246822507) ^ Math.imul(h ^ (h >>> 13), 3266489909)) >>> 0) / 4294967296;
  let s = "";
  for (let i = 0; i < 46; i++) s += `<circle cx="${f(rnd() * 70)}" cy="${f(rnd() * 120)}" r="${f(.12 + rnd() * .38)}" opacity="${f(.25 + rnd() * .65)}"/>`;
  return `<svg class="tc-stars" viewBox="0 0 70 120" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">${s}</svg>`;
}

const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

plans.forEach((plan, i) => {
  const key = plan.dataset.arcanum, A = ARCANA[key] || {};
  const name = plan.querySelector("h2"), price = plan.querySelector(".price");
  const back = document.createElement("div"); back.className = "tc-back";
  while (plan.firstChild) back.appendChild(plan.firstChild);
  const turnBack = document.createElement("button");
  turnBack.type = "button"; turnBack.className = "tc-turn tc-turn-back"; turnBack.textContent = "↺ Turn back";
  back.appendChild(turnBack);
  const emblem = EMBLEM[A.emblem] ? `<svg class="tc-sigil" viewBox="0 0 200 200" aria-hidden="true" focusable="false">
      <g class="tc-lines">${EMBLEM[A.emblem]()}</g>${RUNE[A.rune] ? `<path class="tc-rune" d="${RUNE[A.rune]}"/>` : ""}</svg>`
    : `<img class="tc-emblem" src="/static/look/emblem.png" alt="" width="120" height="120">`;
  const face = document.createElement("button");
  face.type = "button"; face.className = "tc-face";
  face.setAttribute("aria-label", `${name ? name.textContent : "Plan"}: turn the card over to see what's in it`);
  face.innerHTML = `${stars(key || String(i))}
    <span class="tc-num">${A.n || ROMAN[i] || i + 1}</span>
    ${emblem}
    <span class="tc-name">${name ? name.textContent : ""}</span>
    <span class="tc-line">${plan.dataset.line || ""}</span>
    <span class="tc-price">${price ? price.innerHTML : ""}</span>
    <span class="tc-turn">Turn the card ↻</span>`;
  const inner = document.createElement("div"); inner.className = "tc-inner";
  inner.append(face, back);
  plan.appendChild(inner);
  plan.classList.add("tc");
  back.setAttribute("aria-hidden", "true"); back.inert = true;
  const flip = on => {
    plan.classList.toggle("flipped", on);
    plan.style.removeProperty("--rx"); plan.style.removeProperty("--ry");
    back.setAttribute("aria-hidden", on ? "false" : "true"); back.inert = !on;
    face.setAttribute("aria-hidden", on ? "true" : "false"); face.inert = on;
    (on ? back.querySelector("a, button:not(.tc-turn-back)") || turnBack : face).focus({ preventScroll: true });
  };
  face.addEventListener("click", () => flip(true));
  turnBack.addEventListener("click", () => flip(false));

  /* the face leans toward the pointer and catches the light */
  if (!still) {
    face.addEventListener("pointermove", e => {
      if (e.pointerType !== "mouse" || plan.classList.contains("flipped")) return;
      const b = face.getBoundingClientRect(), x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height;
      plan.classList.add("leaning");
      plan.style.setProperty("--ry", `${f((x - .5) * 10)}deg`); plan.style.setProperty("--rx", `${f((.5 - y) * 8)}deg`);
      plan.style.setProperty("--mx", `${f(x * 100)}%`); plan.style.setProperty("--my", `${f(y * 100)}%`);
    });
    face.addEventListener("pointerleave", () => {
      plan.classList.remove("leaning"); plan.style.removeProperty("--rx"); plan.style.removeProperty("--ry");
    });
  }
});
/* a card named in the address (#pro) starts turned over */
const named = location.hash.length > 1 && document.querySelector(`.plans > .plan#${CSS.escape(location.hash.slice(1))}`);
if (named) named.querySelector(".tc-face").click();
})();
