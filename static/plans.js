'use strict';
/* ============================================================
   THE PLANS AS TAROT CARDS
   Each .plan on the offers and Order pages becomes a card from a hand-tinted
   deck: her paper washed in the card's colour, her knotwork at the corners,
   an engraved symbol inked in black and tinted in one pigment, the name, one
   line (data-line), the price, and the card's rune as the printer's mark.
   Click or tap and it turns over to the full plan. Without this script the
   plans stay plain cards.

   Which card is which comes from data-arcanum on the .plan. To change a
   card's numeral, rune or symbol, edit ARCANA below; colours are in plans.css
   (.plan[data-arcanum=...]).
   ============================================================ */
(() => {
const plans = document.querySelectorAll(".plans > .plan");
if (!plans.length) return;

const ARCANA = {
  reading:  { n: "I",   rune: "perthro", symbol: "sun" },        // your whole chart, read in full: the Sun, which lights all of it
  together: { n: "II",  rune: "gebo",    symbol: "cups" },       // two or more charts, one story: two cups raised together
  order:    { n: "III", rune: "othala",  symbol: "moon" },       // your weather, every week: the Moon and her dew
  circle:   { n: "IV",  rune: "kenaz",   symbol: "septagram" },  // for those who read for others: the seven-pointed star in its ring
};
const ROMAN = ["I", "II", "III", "IV", "V", "VI"];

/* the runes, drawn as strokes so they never depend on a font, centred on (100, 100) */
const RUNE = {
  perthro: "M90 80V120M90 80L101 92L111 80M90 120L101 108L111 120",
  gebo:    "M87 80L113 120M113 80L87 120",
  othala:  "M100 80L112 94L90 119M100 80L88 94L110 119",
  kenaz:   "M109 82L91 100L109 118",
};

const f = x => +x.toFixed(2);
const at = (r, deg, cx = 100, cy = 100) => { const a = deg * Math.PI / 180; return [f(cx + r * Math.cos(a)), f(cy + r * Math.sin(a))]; };

/* engraved symbols on a 200 x 200 plate. .ink is the black line, .tint the pigment, .wash the paler tint, .hatch the engraver's shading */
const SYMBOL = {
  sun(id) {
    let rays = "";
    for (let i = 0; i < 16; i++) {
      const a = i * 22.5 - 90;
      if (i % 2 === 0) {                                     // long straight rays, tapered
        const [x1, y1] = at(47, a - 6), [x2, y2] = at(86, a), [x3, y3] = at(47, a + 6);
        rays += `<path class="tint ink" d="M${x1} ${y1}L${x2} ${y2}L${x3} ${y3}Z"/>`;
      } else {                                               // shorter flames, curling the same way round
        const b1 = at(46, a - 5), b2 = at(46, a + 5), t = at(73, a + 7), c1 = at(62, a - 3), c2 = at(58, a + 12);
        rays += `<path class="tint ink thin" d="M${b1}Q${c1} ${t}Q${c2} ${b2}Z"/>`;
      }
    }
    return `<defs><clipPath id="sc-${id}"><circle cx="100" cy="100" r="40"/></clipPath></defs>${rays.replace(/,/g, " ")}
      <circle class="tint ink heavy" cx="100" cy="100" r="40"/>
      <g clip-path="url(#sc-${id})"><circle class="hatch-${id} ink-none" cx="122" cy="122" r="44"/><circle class="tint" cx="92" cy="92" r="36"/></g>
      <circle class="ink heavy" cx="100" cy="100" r="40"/><circle class="ink hair" cx="100" cy="100" r="34"/>`;
  },
  cups(id) {
    const cup = `<path class="tint ink heavy" d="M-24 -38C-24 -8 -13 6 0 8C13 6 24 -8 24 -38"/>
      <ellipse class="wash ink" cx="0" cy="-38" rx="24" ry="6"/>
      <path class="hatch-${id} ink-none" d="M4 -32C14 -30 20 -26 21 -24C19 -6 11 4 2 7Z"/>
      <path class="ink" d="M-4 8V34M4 8V34"/><ellipse class="tint ink" cx="0" cy="21" rx="7" ry="3.5"/>
      <path class="tint ink" d="M-4 34C-6 38 -14 41 -20 44H20C14 41 6 38 4 34Z"/><ellipse class="wash ink" cx="0" cy="44.5" rx="20" ry="4.5"/>`;
    return `<g transform="translate(61 112) rotate(13) scale(1.22)">${cup}</g><g transform="translate(139 112) rotate(-13) scale(1.22)">${cup}</g>
      <path class="tint ink thin" d="M100 36L103 47L114 50L103 53L100 64L97 53L86 50L97 47Z"/>`;
  },
  moon(id) {
    const crescent = "M96.14 42.15A58 58 0 1 0 142.58 128.39A49 49 0 1 1 96.14 42.15Z";
    let dew = "";
    [[58, 172], [80, 184], [102, 175], [124, 186], [146, 173]].forEach(([x, y]) => {
      dew += `<path class="tint ink thin" d="M${x} ${y - 7}C${x + 3.5} ${y - 1} ${x + 4.5} ${y + 2} ${x} ${y + 5.5}C${x - 4.5} ${y + 2} ${x - 3.5} ${y - 1} ${x} ${y - 7}Z"/>`;
    });
    return `<defs><clipPath id="mc-${id}"><path d="${crescent}"/></clipPath></defs>
      <path class="tint" d="${crescent}"/>
      <g clip-path="url(#mc-${id})"><circle class="ink hair" cx="92" cy="100" r="51"/><circle class="ink hair" cx="92" cy="100" r="44"/>
        <rect class="hatch-${id} ink-none" x="30" y="100" width="80" height="70"/></g>
      <path class="ink heavy" d="${crescent}" fill="none"/>${dew}`;
  },
  septagram(id) {
    let ticks = "";
    for (let i = 0; i < 40; i++) { const [x1, y1] = at(56, i * 9), [x2, y2] = at(62, i * 9); ticks += `<line class="ink hair" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`; }
    const p = [0, 3, 6, 2, 5, 1, 4].map(k => at(52, k * 360 / 7 - 90).join(" "));      // {7/3}: each point joined to the third along, the narrow pointed star
    return `<defs><clipPath id="pc-${id}"><circle cx="100" cy="100" r="52"/></clipPath></defs>
      <circle class="tint ink heavy" cx="100" cy="100" r="66"/><circle class="wash ink" cx="100" cy="100" r="52"/>
      <g clip-path="url(#pc-${id})"><circle class="hatch-${id} ink-none" cx="132" cy="132" r="58"/><circle class="wash" cx="92" cy="92" r="50"/></g>
      <circle class="ink" cx="100" cy="100" r="52"/>${ticks}
      <path class="tint ink heavy" d="M${p.join("L")}Z" fill-rule="nonzero"/>
      <circle class="ink hair" cx="100" cy="100" r="70"/>`;
  },
};

const hatchDef = id => `<defs><pattern id="hp-${id}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
  <line x1="0" y1="0" x2="0" y2="5" class="ink hair"/></pattern></defs><style>.tc-symbol .hatch-${id}{fill:url(#hp-${id})}</style>`;

const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

plans.forEach((plan, i) => {
  const key = plan.dataset.arcanum, A = ARCANA[key] || {}, id = (key || "c") + i;
  const name = plan.querySelector("h2"), price = plan.querySelector(".price");
  const back = document.createElement("div"); back.className = "tc-back";
  while (plan.firstChild) back.appendChild(plan.firstChild);
  const turnBack = document.createElement("button");
  turnBack.type = "button"; turnBack.className = "tc-turn tc-turn-back"; turnBack.textContent = "↺ Turn back";
  back.appendChild(turnBack);
  const symbol = SYMBOL[A.symbol] ? `<svg class="tc-symbol" viewBox="0 0 200 200" aria-hidden="true" focusable="false">${hatchDef(id)}${SYMBOL[A.symbol](id)}</svg>`
    : `<img class="tc-emblem" src="/static/look/emblem.png" alt="" width="120" height="120">`;
  const mark = RUNE[A.rune] ? `<svg class="tc-mark" viewBox="64 76 72 48" aria-hidden="true" focusable="false">
      <path d="M66 100H80M120 100H134"/><path class="tc-mark-rune" d="${RUNE[A.rune]}"/></svg>` : "";
  const face = document.createElement("button");
  face.type = "button"; face.className = "tc-face";
  face.setAttribute("aria-label", `${name ? name.textContent : "Plan"}: turn the card over to see what's in it`);
  face.innerHTML = `<span class="tc-knot tc-knot-tr" aria-hidden="true"></span><span class="tc-knot tc-knot-bl" aria-hidden="true"></span>
    <span class="tc-num">${A.n || ROMAN[i] || i + 1}</span>
    ${symbol}
    <span class="tc-name">${name ? name.textContent : ""}</span>
    <span class="tc-line">${plan.dataset.line || ""}</span>
    <span class="tc-price">${price ? price.innerHTML : ""}</span>
    ${mark}
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
