/* ============================================================
   THE MEMBERS' ROOMS, ETHERIC
   On the Hall (the Order) and the practice desk (the Inner Circle):
   a carved marble column at each edge and a marble statue beside it
   (static/look/statues, cut from their photographs), mist drifting
   through and motes of light rising. Everything moves slowly, and
   stands still for anyone who asks for less motion.
   ============================================================ */
(() => {
const body = document.body;
if (!body.classList.contains("room")) return;
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
const room = document.createElement("div");
room.className = "rm-bg"; room.setAttribute("aria-hidden", "true");
room.innerHTML = `<div class="rm-mist m1"></div><div class="rm-mist m2"></div><div class="rm-mist m3"></div><div class="rm-sweep"></div><canvas class="rm-motes"></canvas>`;
["l", "r"].forEach(w => {                       /* a carved marble column at each edge */
  const c = document.createElement("img");
  c.className = `rm-column rm-c${w}`; c.src = "/static/look/statues/column.webp"; c.alt = ""; c.decoding = "async";
  room.append(c);
});
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
