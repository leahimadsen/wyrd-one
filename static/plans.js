'use strict';
/* ============================================================
   THE PLANS AS TAROT CARDS
   Each .plan on the offers and Order pages becomes a card: its face
   shows a numeral, the emblem, the name, the price and one line
   (data-line); click or tap and it turns over to the full plan.
   Without this script the plans stay plain cards.
   ============================================================ */
(() => {
const plans = document.querySelectorAll(".plans > .plan");
if (!plans.length) return;
const ROMAN = ["I", "II", "III", "IV", "V", "VI"];
plans.forEach((plan, i) => {
  const name = plan.querySelector("h2"), price = plan.querySelector(".price");
  const back = document.createElement("div"); back.className = "tc-back";
  while (plan.firstChild) back.appendChild(plan.firstChild);
  const turnBack = document.createElement("button");
  turnBack.type = "button"; turnBack.className = "tc-turn tc-turn-back"; turnBack.textContent = "↺ Turn back";
  back.appendChild(turnBack);
  const face = document.createElement("button");
  face.type = "button"; face.className = "tc-face";
  face.setAttribute("aria-label", `${name ? name.textContent : "Plan"}: turn the card over to see what's in it`);
  face.innerHTML = `<span class="tc-num">${ROMAN[i] || i + 1}</span>
    <img class="tc-emblem" src="/static/look/emblem.png" alt="" width="120" height="120">
    <span class="tc-name">${name ? name.textContent : ""}</span>
    <span class="tc-price">${price ? price.innerHTML : ""}</span>
    <span class="tc-line">${plan.dataset.line || ""}</span>
    <span class="tc-turn">Turn the card ↻</span>`;
  const inner = document.createElement("div"); inner.className = "tc-inner";
  inner.append(face, back);
  plan.appendChild(inner);
  plan.classList.add("tc");
  back.setAttribute("aria-hidden", "true"); back.inert = true;
  const flip = on => {
    plan.classList.toggle("flipped", on);
    back.setAttribute("aria-hidden", on ? "false" : "true"); back.inert = !on;
    face.setAttribute("aria-hidden", on ? "true" : "false"); face.inert = on;
    (on ? back.querySelector("a, button:not(.tc-turn-back)") || turnBack : face).focus({ preventScroll: true });
  };
  face.addEventListener("click", () => flip(true));
  turnBack.addEventListener("click", () => flip(false));
});
/* a card named in the address (#pro) starts turned over */
const named = location.hash.length > 1 && document.querySelector(`.plans > .plan#${CSS.escape(location.hash.slice(1))}`);
if (named) named.querySelector(".tc-face").click();
})();
