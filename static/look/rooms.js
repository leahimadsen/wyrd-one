/* ============================================================
   THE MEMBERS' ROOMS, ETHERIC
   On the Hall (the Order) and the practice desk (the Inner Circle):
   a marble colonnade at the edges, a bust in an arched niche on each
   side, mist drifting through and motes of light rising. The marble is
   drawn, not photographed: SVG turbulence makes its veins. Everything
   moves slowly, and stands still for anyone who asks for less motion.
   ============================================================ */
(() => {
const body = document.body;
if (!body.classList.contains("room")) return;
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
const NS = "http://www.w3.org/2000/svg";

/* one shared set of marble textures */
const defs = `
<filter id="rmMarble" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.03 0.004" numOctaves="5" seed="7" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.93  0 0 0 0 0.92  0 0 0 0 0.95  -2.4 0 0 0 1.55" result="veins"/>
  <feComposite in="veins" in2="SourceGraphic" operator="in"/>
</filter>
<linearGradient id="rmShaft" x1="0" x2="1">
  <stop offset="0" stop-color="#6d6676"/><stop offset=".18" stop-color="#d9d4df"/><stop offset=".42" stop-color="#f6f3f8"/>
  <stop offset=".7" stop-color="#bdb6c6"/><stop offset="1" stop-color="#4a4452"/></linearGradient>
<linearGradient id="rmFlute" x1="0" x2="1">
  <stop offset="0" stop-color="#000" stop-opacity=".0"/><stop offset=".5" stop-color="#000" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
<radialGradient id="rmStone" cx=".35" cy=".3" r=".9">
  <stop offset="0" stop-color="#fbf9fd"/><stop offset=".45" stop-color="#d8d2de"/><stop offset="1" stop-color="#5d5666"/></radialGradient>
<radialGradient id="rmNiche" cx=".5" cy=".35" r=".75">
  <stop offset="0" stop-color="var(--room)" stop-opacity=".28"/><stop offset=".6" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></radialGradient>`;

const flutes = (x, w, h) => Array.from({ length: 6 }, (_, i) => `<rect x="${x + 6 + i * (w - 12) / 6}" y="0" width="${(w - 12) / 6}" height="${h}" fill="url(#rmFlute)"/>`).join("");

/* an Ionic column, full height of the window */
function column(h){
  const w = 70, x = 20;
  return `<g class="rm-col">
    <rect x="${x - 10}" y="${h - 34}" width="${w + 20}" height="34" fill="url(#rmShaft)"/>
    <rect x="${x - 4}" y="${h - 50}" width="${w + 8}" height="16" rx="6" fill="url(#rmShaft)"/>
    <rect x="${x}" y="58" width="${w}" height="${h - 108}" fill="url(#rmShaft)"/>${flutes(x, w, h - 108).replace(/y="0"/g, 'y="58"')}
    <rect x="${x}" y="58" width="${w}" height="${h - 108}" fill="#fff" filter="url(#rmMarble)" opacity=".55"/>
    <rect x="${x - 14}" y="30" width="${w + 28}" height="16" fill="url(#rmShaft)"/>
    <circle cx="${x - 6}" cy="50" r="13" fill="url(#rmStone)"/><circle cx="${x + w + 6}" cy="50" r="13" fill="url(#rmStone)"/>
    <circle cx="${x - 6}" cy="50" r="5" fill="#6d6676"/><circle cx="${x + w + 6}" cy="50" r="5" fill="#6d6676"/>
    <rect x="${x - 20}" y="14" width="${w + 40}" height="16" fill="url(#rmShaft)"/></g>`;
}

/* a classical bust in profile, facing right, on a plinth, in an arched niche */
function niche(){
  return `<g class="rm-niche">
    <path d="M10,330 V120 A100,100 0 0 1 210,120 V330 Z" fill="url(#rmNiche)" stroke="var(--room)" stroke-opacity=".55" stroke-width="2"/>
    <path d="M10,120 A100,100 0 0 1 210,120" fill="none" stroke="#e9e4ee" stroke-opacity=".5" stroke-width="6"/>
    <g class="rm-bust">
      <path d="M48,300 C48,256 76,242 98,236 L100,212 C86,206 76,192 74,174 C66,156 67,130 77,112 C87,94 105,84 125,86
               C146,88 160,102 165,118 C168,128 167,138 171,146 L176,156 L182,170 L174,173 C174,178 177,180 174,184
               C172,188 174,191 170,194 C166,201 157,204 147,205 L145,221 C157,236 181,242 190,256 C199,270 201,286 201,300 Z"
            fill="url(#rmStone)"/>
      <path d="M48,300 C48,256 76,242 98,236 L100,212 C86,206 76,192 74,174 C66,156 67,130 77,112 C87,94 105,84 125,86
               C146,88 160,102 165,118 C168,128 167,138 171,146 L176,156 L182,170 L174,173 C174,178 177,180 174,184
               C172,188 174,191 170,194 C166,201 157,204 147,205 L145,221 C157,236 181,242 190,256 C199,270 201,286 201,300 Z"
            fill="#fff" filter="url(#rmMarble)" opacity=".5"/>
      <path d="M82,176 C66,160 62,128 72,106 C84,84 112,76 136,80 C152,84 162,96 162,108 C140,100 118,104 104,118 C96,134 96,156 100,170 Z" fill="url(#rmStone)"/>
      <g class="rm-hair">${[[96,92,12],[112,86,12],[128,85,12],[143,90,11],[155,100,9],[84,100,12],[75,114,12],[71,130,12],[72,146,11],[79,160,10],[90,172,9],[100,104,11],[116,98,11],[132,98,10],[88,118,11],[86,134,10],[90,150,10]]
        .map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#rmStone)" stroke="#6d6676" stroke-opacity=".3" stroke-width="1"/>`).join("")}</g>
      <path d="M100,150 C94,146 92,156 96,162 C99,168 106,166 107,160" fill="none" stroke="#6d6676" stroke-opacity=".6" stroke-width="2"/>
      <path d="M150,140 C146,144 141,145 137,143 M160,162 L168,163" stroke="#6d6676" stroke-opacity=".55" fill="none" stroke-width="2"/>
      <path d="M70,268 C100,252 130,252 170,266 M62,284 C100,270 140,272 186,286" stroke="#6d6676" stroke-opacity=".45" fill="none" stroke-width="2"/>
    </g>
    <rect x="44" y="300" width="132" height="14" fill="url(#rmShaft)"/><rect x="56" y="314" width="108" height="16" fill="url(#rmShaft)"/>
  </g>`;
}

function side(which){
  const s = document.createElementNS(NS, "svg");
  const h = 1000;
  s.setAttribute("viewBox", `0 0 330 ${h}`);
  s.setAttribute("preserveAspectRatio", which === "l" ? "xMinYMax meet" : "xMaxYMax meet");
  s.setAttribute("class", `rm-side rm-${which}`);
  s.setAttribute("aria-hidden", "true");
  s.innerHTML = `<defs>${which === "l" ? defs : ""}</defs>
    <g transform="${which === "r" ? "translate(330,0) scale(-1,1)" : ""}">
      ${column(h)}<g transform="translate(110,${h - 380})">${niche()}</g></g>`;
  return s;
}

const room = document.createElement("div");
room.className = "rm-bg"; room.setAttribute("aria-hidden", "true");
room.innerHTML = `<div class="rm-mist m1"></div><div class="rm-mist m2"></div><div class="rm-mist m3"></div><div class="rm-sweep"></div><canvas class="rm-motes"></canvas>`;
room.append(side("l"), side("r"));
body.prepend(room);

/* motes of light, rising */
const cv = room.querySelector("canvas"), cx = cv.getContext("2d");
const tint = getComputedStyle(body).getPropertyValue("--room").trim() || "#fff";
const lamp = getComputedStyle(body).getPropertyValue("--lamp").trim() || "#fff";
let W, H, motes;
const size = () => {
  const r = Math.min(devicePixelRatio || 1, 2);
  W = cv.width = innerWidth * r; H = cv.height = innerHeight * r; cv.style.width = innerWidth + "px"; cv.style.height = innerHeight + "px";
  motes = Array.from({ length: Math.round(Math.min(90, innerWidth / 14)) }, () => ({
    x: Math.random() * W, y: Math.random() * H, r: (0.6 + Math.random() * 1.8) * r, v: (0.08 + Math.random() * 0.35) * r,
    d: Math.random() * Math.PI * 2, c: Math.random() < 0.5 ? tint : (Math.random() < 0.5 ? lamp : "#ffffff") }));
};
size(); addEventListener("resize", size);
const draw = t => {
  cx.clearRect(0, 0, W, H);
  for (const m of motes){
    if (!still){ m.y -= m.v; m.x += Math.sin(t / 3000 + m.d) * 0.25; if (m.y < -10){ m.y = H + 10; m.x = Math.random() * W; } }
    const a = 0.35 + 0.35 * Math.sin(t / 900 + m.d * 3);
    cx.globalAlpha = a; cx.fillStyle = m.c; cx.shadowColor = m.c; cx.shadowBlur = m.r * 6;
    cx.beginPath(); cx.arc(m.x, m.y, m.r, 0, Math.PI * 2); cx.fill();
  }
  if (!still && !document.hidden) requestAnimationFrame(draw);
};
requestAnimationFrame(draw);
document.addEventListener("visibilitychange", () => { if (!document.hidden && !still) requestAnimationFrame(draw); });
})();
