'use strict';
/* The sky now, around the natal chart.
   Inner ring: natal bodies. Outer ring: where everything is today.
   Gold threads join a moving body to the natal point it sits on;
   a jade halo marks a moving body standing in a gate the person carries. */
(() => {
const NS = "http://www.w3.org/2000/svg";
const SIGN_GLYPH = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"].map(g => g + "\uFE0E");  /* text, not emoji */
const ORD = n => n + (["th","st","nd","rd"][(n % 100 - 20) % 10] || ["th","st","nd","rd"][n % 100] || "th");
let sel = null, C = null;

function xy(lon, r){
  const t = Math.PI + (lon - C.ascS) * Math.PI / 180;
  return [200 + r * Math.cos(t), 200 - r * Math.sin(t)];
}
/* spread glyphs that would sit on top of each other */
function spread(items, minGap){
  const s = items.slice().sort((a, b) => a.lon - b.lon);
  s.forEach(i => i.at = i.lon);
  for (let pass = 0; pass < 4; pass++)
    for (let i = 0; i < s.length; i++){
      const a = s[i], b = s[(i + 1) % s.length];
      let gap = ((b.at - a.at) + 360) % 360;
      if (s.length > 1 && gap < minGap){ const push = (minGap - gap) / 2; a.at -= push; b.at += push; }
    }
  return s;
}
function arc(r1, r2, a, b, fill, op){
  const [x1, y1] = xy(a, r2), [x2, y2] = xy(b, r2), [x3, y3] = xy(b, r1), [x4, y4] = xy(a, r1);
  return `<path d="M${x1} ${y1} A${r2} ${r2} 0 0 0 ${x2} ${y2} L${x3} ${y3} A${r1} ${r1} 0 0 1 ${x4} ${y4}Z" fill="${fill}" fill-opacity="${op}"/>`;
}

function wheel(){
  const { GLYPH, HOUSES } = Wyrd.helpers, T = C.transits;
  const ascSign = Math.floor(C.ascS / 30);
  let s = `<svg viewBox="0 0 400 400" id="trSVG" role="img" aria-label="Today's sky around your birth chart">`;
  for (let i = 0; i < 12; i++){                       /* whole-sign houses, in their colours */
    const sign = (ascSign + i) % 12, a = sign * 30, h = HOUSES[i];
    s += arc(150, 172, a, a + 30, h.hex, .28);
    const [lx, ly] = xy(a + 15, 186), [hx, hy] = xy(a + 15, 161);
    s += `<text x="${lx}" y="${ly}" class="tr-sign">${SIGN_GLYPH[sign]}</text>
          <text x="${hx}" y="${hy}" class="tr-house">${i + 1}</text>`;
    const [ox, oy] = xy(a, 198), [ix, iy] = xy(a, 60);
    s += `<line x1="${ox}" y1="${oy}" x2="${ix}" y2="${iy}" class="tr-div"/>`;
  }
  s += `<circle cx="200" cy="200" r="198" class="tr-ring"/><circle cx="200" cy="200" r="172" class="tr-ring"/>
        <circle cx="200" cy="200" r="150" class="tr-ring"/><circle cx="200" cy="200" r="60" class="tr-ring"/>`;
  const [ax, ay] = xy(C.ascS, 198), [aix, aiy] = xy(C.ascS, 60);
  s += `<line x1="${ax}" y1="${ay}" x2="${aix}" y2="${aiy}" class="tr-asc"/>`;

  const natal = spread(["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"]
    .map(b => ({ b, lon: C.sid[b] })), 9);
  const moving = spread(T.rows.map(r => ({ b: r.body, lon: r.sid, r })), 9);
  const natalAt = {}; natal.forEach(n => natalAt[n.b] = n.at);
  if (!C.unknownTime){ natalAt.Ascendant = C.ascS; natalAt.Midheaven = C.mcS; }

  /* threads first, so glyphs sit on top */
  moving.forEach(m => m.r.on.forEach(h => {
    const [x1, y1] = xy(m.at, 128), [x2, y2] = xy(natalAt[h.point], h.point === "Ascendant" || h.point === "Midheaven" ? 60 : 92);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="tr-thread${sel && sel !== m.b ? " dim" : ""}"/>`;
  }));
  natal.forEach(n => {
    const [x, y] = xy(n.at, 92);
    s += `<text x="${x}" y="${y}" class="tr-natal">${GLYPH[n.b]}</text>`;
  });
  moving.forEach(m => {
    const [x, y] = xy(m.at, 136), r = m.r;
    s += `<g class="tr-mov${sel === m.b ? " sel" : ""}${sel && sel !== m.b ? " dim" : ""}" data-tr="${m.b}" tabindex="0" role="button" aria-label="${m.b}">
      ${r.carried.length ? `<circle cx="${x}" cy="${y}" r="11" class="tr-halo"/>` : ""}
      <circle cx="${x}" cy="${y}" r="11" class="tr-hit"/>
      <text x="${x}" y="${y}" class="tr-glyph">${GLYPH[m.b]}</text>
      ${r.retro ? `<text x="${x + 10}" y="${y - 8}" class="tr-rx">℞</text>` : ""}</g>`;
  });
  s += `<text x="200" y="196" class="tr-c1">now</text><text x="200" y="212" class="tr-c2">around your birth</text></svg>`;
  return s;
}

function line(r){
  const { GLYPH, HOUSES, GATE_TITLE } = Wyrd.helpers, h = HOUSES[r.house - 1];
  const bits = [`in your ${ORD(r.house)} house, <span class="sw" style="background:${h.hex}"></span>${h.color.toLowerCase()}: ${h.phase.charAt(0).toLowerCase() + h.phase.slice(1)}`];
  bits.push(`gate ${r.gate}.${r.line}, ${GATE_TITLE[r.gate] || ""}` +
            (r.carried.length ? `, a gate you carry in your ${r.carried.slice(0, 3).join(", ")}` : ""));
  if (r.on.length) bits.push("sitting on your natal " + r.on.map(o => `${o.point} (${o.orb.toFixed(1)}°)`).join(" and "));
  if (r.inMoonMansion) bits.push("crossing your Moon's mansion");
  return `<li data-tr="${r.body}" class="${sel === r.body ? "sel" : ""}${r.on.length ? " lit" : ""}">
    <div class="tr-b">${GLYPH[r.body]} ${r.body}${r.retro ? " <small>retrograde</small>" : ""}</div>
    <div>${bits.join("; ")}.</div></li>`;
}

function paint(){
  const T = C.transits, host = document.getElementById("trHost");
  const rank = r => (r.on.length ? 0 : r.carried.length ? 1 : 2);
  const rows = T.rows.slice().sort((a, b) => rank(a) - rank(b));
  const lit = rows.filter(r => r.on.length).length;
  const when = new Date((T.jd - 2440587.5) * 86400000)
    .toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  host.innerHTML = `
    <p class="tr-when">The sky on ${when}. ${lit ? `${lit} moving ${lit === 1 ? "body sits" : "bodies sit"} on a point in your chart.` : "Nothing sits on a natal point right now."}
      Tap a planet on the wheel to follow it.</p>
    <div class="tr-wrap"><div class="tr-stage">${wheel()}
      <p class="fine tr-key">Inner ring: your birth chart. Outer ring: the sky now. Gold threads mark a planet sitting on one of yours; a green halo marks a planet in a gate you carry.</p></div>
      <ul class="tr-list">${rows.map(line).join("")}</ul></div>
    ${T.sadeSati ? `<p class="tr-note">Saturn is ${({12:"in the sign before your Moon's", 1:"in your Moon's sign", 2:"in the sign after your Moon's"})[T.saturnFromMoon]}. This is Sade Sati, the seven and a half years Saturn takes to cross the Moon's sign and the sign on either side.</p>` : ""}
    <p class="fine">Orbs: 4° for the Moon, 2½° for Jupiter and Saturn, 1½° for the nodes, 2° for the rest. Houses are whole-sign from your sidereal Ascendant.</p>`;
}

document.addEventListener("click", e => {
  const t = e.target.closest("[data-tr]"); if (!t || !C) return;
  sel = sel === t.dataset.tr ? null : t.dataset.tr; paint();
  const li = document.querySelector(`.tr-list li[data-tr="${sel}"]`);
  if (li && innerWidth < 900) li.scrollIntoView({ block: "nearest", behavior: "smooth" });
});
document.addEventListener("keydown", e => {
  if ((e.key === "Enter" || e.key === " ") && e.target.closest && e.target.closest("g[data-tr]")){ e.preventDefault(); e.target.click(); }
});

window.renderTransits = chart => { C = chart; sel = null; paint(); };
})();
