/* ============================================================
   THE MEMBERS' ROOMS, ETHERIC
   On the Hall (the Order) and the practice desk (the Inner Circle):
   a marble colonnade at the edges, a marble statue on each side
   (static/look/statues, cut from their photographs),
   mist drifting through and motes of light rising. The columns' marble
   is drawn: SVG turbulence makes its veins. Everything
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
`;

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

function side(which){
  const s = document.createElementNS(NS, "svg");
  const h = 1000;
  s.setAttribute("viewBox", `0 0 330 ${h}`);
  s.setAttribute("preserveAspectRatio", which === "l" ? "xMinYMax meet" : "xMaxYMax meet");
  s.setAttribute("class", `rm-side rm-${which}`);
  s.setAttribute("aria-hidden", "true");
  s.innerHTML = `<defs>${which === "l" ? defs : ""}</defs>
    <g transform="${which === "r" ? "translate(330,0) scale(-1,1)" : ""}">
      ${column(h)}</g>`;
  return s;
}

const room = document.createElement("div");
room.className = "rm-bg"; room.setAttribute("aria-hidden", "true");
room.innerHTML = `<div class="rm-mist m1"></div><div class="rm-mist m2"></div><div class="rm-mist m3"></div><div class="rm-sweep"></div><canvas class="rm-motes"></canvas>`;
room.append(side("l"), side("r"));
/* the statues: real marble, two to a room, each on a pedestal of light */
const STATUES = body.classList.contains("room-circle")
  ? [["zeus", "Zeus, his arm raised"], ["athena", "Athena, at rest"]]
  : [["undine", "a veiled figure rising"], ["muse", "a muse, arms open"]];
STATUES.forEach(([name], i) => {
  const f = document.createElement("figure");
  f.className = `rm-statue rm-s${i ? "r" : "l"}`;
  f.innerHTML = `<span class="rm-halo"></span><img src="/static/look/statues/${name}.webp" alt="" decoding="async"><span class="rm-pedestal"></span>`;
  room.append(f);
});
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
