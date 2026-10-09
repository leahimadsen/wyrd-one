'use strict';
/* The public Today page: the sky right now, nobody's chart required. */
(async () => {
const $ = id => document.getElementById(id);
const { signOf, degIn, nakIndex, norm, GLYPH, NAKSHATRA } = Wyrd.helpers;
const g = (k, l) => Wyrd.gloss(k, l);
const dm = l => { const d = degIn(l); let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60){ a++; m = 0; } return `${a}°${String(m).padStart(2, "0")}′`; };
const pada = l => Math.floor((norm(l) % (360/27)) / (360/108)) + 1;
const day = jd => new Date((jd - 2440587.5) * 864e5).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
Wyrd.sky.start();
if (Wyrd.pulse) Wyrd.pulse("act", "today");

let D;
try { const r = await fetch("/api/today"); D = await r.json(); if (!r.ok) throw new Error(D.error); }
catch (x) { $("tdFacts").innerHTML = `<p class="err">Today's sky couldn't be loaded. Try again in a minute.</p>`; return; }

$("when").textContent = new Date().toLocaleString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" });
const row = b => D.rows.find(r => r.body === b);
const moon = row("Moon"), sun = row("Sun"), P = D.panchanga;

/* a plain zodiac wheel: the twelve sidereal signs with Aries at nine o'clock */
const SG = SIGN_GLYPH.map(x => x + "︎");
const pt = (r, l) => { const a = Math.PI + l * Math.PI / 180; return [500 + r * Math.cos(a), 500 - r * Math.sin(a)]; };
let s = `<circle cx="500" cy="500" r="480" class="wh-back"/>`;
for (let i = 0; i < 12; i++){
  const [x0, y0] = pt(330, i * 30), [x1, y1] = pt(480, i * 30), [gx, gy] = pt(440, i * 30 + 15), [ax, ay] = pt(380, i * 30 + 15);
  s += `<line x1="${x0}" y1="${y0}" x2="${x1}" y2="${y1}" class="wh-ang"/><text x="${gx}" y="${gy}" class="wh-badge-g td-sg">${SG[i]}</text><text x="${ax}" y="${ay}" class="wh-abbr">${SIGNS[i].slice(0, 3).toUpperCase()}</text>`;
}
s += `<circle cx="500" cy="500" r="330" class="wh-aspring"/><circle cx="500" cy="500" r="400" class="wh-aspring"/>`;
const placed = D.rows.map(r => ({ r, a: r.sid })).sort((p, q) => p.a - q.a);
placed.forEach((p, i) => { p.at = p.a; if (i && p.at - placed[i - 1].at < 9) p.at = placed[i - 1].at + 9; });
for (const p of placed){
  const [x, y] = pt(270, p.at), [tx, ty] = pt(330, p.a), [lx, ly] = pt(312, p.a);
  s += `<line x1="${tx}" y1="${ty}" x2="${lx}" y2="${ly}" class="wh-tick"/><text x="${x}" y="${y}" class="wh-glyph${p.r.retro ? " des" : ""}">${GLYPH[p.r.body]}</text>`;
}
s += `<circle cx="500" cy="500" r="190" class="wh-core"/><text x="500" y="470" class="wh-c2">the Moon in</text><text x="500" y="508" class="wh-c1">${moon.nak}</text>
  <text x="500" y="548" class="wh-c4">${P.paksha} ${P.tithiName}</text>`;
const flatSVG = `<svg class="wwheel" viewBox="0 0 1000 1000" role="img" aria-label="Today's planets on the sidereal zodiac">${s}</svg>`;
/* the sky around the Earth: flat as a wheel, or opened out into three dimensions; the plain wheel stays as the fallback */
const TAROT = window.WyrdTarot ? await WyrdTarot.load() : null;
try {
  const ST = WyrdSkyTorus.mount($("tdWheel"), { rows: D.rows, tarot: TAROT, caption: $("tdCap"), onMode: v => {
    document.querySelectorAll("[data-st]").forEach(b => b.setAttribute("aria-pressed", b.dataset.st === v));
    $("tdSky").classList.toggle("big", v === "3d"); setTimeout(() => ST.resize(), 360);
    if (Wyrd.pulse) Wyrd.pulse("act", "sky-" + v);
  } });
  document.querySelector(".st-ctl").addEventListener("click", e => { const b = e.target.closest("[data-st]"); if (b) ST.setMode(b.dataset.st); });
} catch (_) { $("tdWheel").innerHTML = flatSVG; document.querySelector(".st-ctl").hidden = true; $("tdCap").hidden = true; }

$("tdFacts").innerHTML = `
  <div class="fact"><h3>The Moon today</h3><dl><dt>${g("sidereal", "Sign")}</dt><dd>${signOf(moon.sid)} ${dm(moon.sid)}</dd>
    <dt>${g("nakshatra", "Mansion")}</dt><dd>${moon.nak}, ${g("pada", "pada")} ${pada(moon.sid)} <small>· ruled by ${NAKSHATRA[nakIndex(moon.sid)][1]}</small></dd>
    <dt>Phase</dt><dd>${Math.round(P.phase)}° from the Sun, ${P.phase < 180 ? "waxing" : "waning"}</dd></dl></div>
  <div class="fact"><h3>${g("panchanga", "The day")}</h3><dl><dt>${g("tithi")}</dt><dd>${P.paksha} ${P.tithiName} <small>(${P.tithi} of 30)</small></dd>
    <dt>${g("yoga")}</dt><dd>${P.yoga}</dd><dt>${g("karana")}</dt><dd>${P.karana}</dd></dl>
    <p class="fine">The weekday and sunrise depend on where you are, so they're left out here.</p></div>
  <div class="fact"><h3>The Sun today</h3><dl><dt>${g("sidereal", "Sidereal")}</dt><dd>${signOf(sun.sid)} ${dm(sun.sid)}</dd><dt>${g("tropical", "Tropical")}</dt><dd>${signOf(sun.trop)} ${dm(sun.trop)}</dd>
    <dt>${g("gate")}</dt><dd>${sun.gate}.${sun.line}${GATE_NAME[sun.gate] ? " · " + GATE_NAME[sun.gate] : ""}</dd></dl></div>`;

$("tdTable").innerHTML = `<caption>Teal glyphs on the wheel are ${g("retro", "retrograde")}.</caption>
  <tr><th scope="col">Planet</th><th scope="col">${g("sidereal", "Sidereal")}</th><th scope="col">${g("tropical", "Tropical")}</th><th scope="col">${g("nakshatra", "Mansion")}</th><th scope="col">${g("gate", "Gate")}</th>${TAROT ? `<th scope="col">${g("tarot", "Card")}</th>` : ""}</tr>
  ${D.rows.map(r => `<tr><th scope="row">${GLYPH[r.body]} ${r.body}${r.retro ? ` <span class="rx" title="retrograde">℞</span>` : ""}</th>
    <td>${signOf(r.sid)} ${dm(r.sid)}</td><td>${signOf(r.trop)} ${dm(r.trop)}</td><td>${r.nak} ${pada(r.sid)}</td><td>${r.gate}.${r.line}</td>${TAROT ? `<td>${WyrdTarot.minor(WyrdTarot.at(TAROT, r.sid))}</td>` : ""}</tr>`).join("")}`;

$("tdNext").innerHTML = D.upcoming.length ? [...D.upcoming].sort((a, b) => a.jd - b.jd).map(e => `<li class="cal-${e.kind}"><time>${day(e.jd)}</time><span>${GLYPH[e.body]} ${e.body} ${
  e.kind === "ingress" ? `enters ${e.sign}` : `stations ${e.turns} in ${e.sign}`}</span></li>`).join("") : `<li><span>No sign changes or stations in the next thirty days.</span></li>`;
})();
