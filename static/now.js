'use strict';
/* NOW AND NEXT: the sky on the birth chart, on any day of the coming year.
   - The wheel: inner ring the birth chart, outer ring the sky on the chosen day.
     Gold threads join a moving planet to the birth point it sits on.
   - The cards beside it read that same day: what is touching the chart, the Moon,
     what is retrograde, where the clock stands. They follow as the day moves.
   - The year: one strip of lanes (touching you, your clock, the slow planets through
     your houses, the retrogrades) that is also a scrubber. Drag along it, or press play.
   - What's coming: the dated list, your own events first, the whole sky on request.
   The daily positions come from /api/calendar ("track"); today is the chart's own transits.
   Data only, like the rest of the free side. */
(() => {
const { GLYPH, HOUSES, GATE_TITLE, NAKSHATRA, norm, nakIndex, houseOf } = Wyrd.helpers;
const { esc } = WyrdCommon;
const g = (k, l) => Wyrd.gloss(k, l);

const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SG = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"].map(s => s + "︎");
const MOVING = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","Rahu","Ketu"];
const ORB = { Sun: 2, Moon: 4, Mercury: 2, Venus: 2, Mars: 2, Jupiter: 2.5, Saturn: 2.5, Uranus: 2, Neptune: 2, Pluto: 2, Rahu: 1.5, Ketu: 1.5 };
const RX_ROWS = ["Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"];
const HOUSE_ROWS = ["Sun","Mars","Jupiter","Saturn","Rahu"];
const DAYS = 365;
const ORD = n => n + (["th","st","nd","rd"][(n % 100 - 20) % 10] || ["th","st","nd","rd"][n % 100] || "th");
const wrap = d => ((d + 540) % 360) - 180;
const sep = (a, b) => Math.abs(wrap(a - b));
const PT = { Ascendant: "↑ Ascendant", Midheaven: "MC Midheaven" };
const pt = n => PT[n] || `${GLYPH[n] || ""} ${n}`;
const jdDate = jd => new Date((jd - 2440587.5) * 864e5);
const UTC = { timeZone: "UTC" };
const dayLong = jd => jdDate(jd).toLocaleDateString(undefined, { ...UTC, weekday: "short", day: "numeric", month: "long", year: "numeric" });
const dayShort = jd => jdDate(jd).toLocaleDateString(undefined, { ...UTC, month: "short", day: "numeric" });
const evDay = jd => jdDate(jd).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
const monthOf = jd => jdDate(jd).toLocaleDateString(undefined, { month: "long", year: "numeric" });
const inDays = n => n === 0 ? "today" : n === 1 ? "tomorrow" : `in ${n} days`;

let C, X, top, list;                       /* the chart, the mount options, the two hosts */
let start = null, track = null, events = [], day = 0, sel = null, timer = null;
let filter = "you", allMonths = false, loadErr = null;
let carried = {}, points = {};

/* ---------------- the sky on day d ---------------- */
function gateOf(trop){
  const off = norm(trop - 302), gi = Math.floor(off / 5.625);
  return { gate: GATE_ORDER[gi], line: Math.floor((off - gi * 5.625) / (5.625 / 6)) + 1 };
}
const lonOn = (b, d) => track.lon[b][Math.max(0, Math.min(track.lon[b].length - 1, d))];
function rowsOn(d){
  /* today is the chart's own transits, cast for the moment; other days come from the track */
  if (!track || (d === 0 && C.transits && Math.abs(C.transits.jd - Date.now() / 864e5 - 2440587.5) < 1)) return C.transits.rows;
  const moonNak = nakIndex(C.sid.Moon);
  return MOVING.map(b => {
    const sid = lonOn(b, d);
    const retro = !!(RX[b] && RX[b].some(s => d >= s.a && d <= s.b));
    const G = gateOf(sid + track.ay);
    const on = Object.entries(points).filter(([p, l]) => sep(sid, l) <= ORB[b] && !(p === b && (b === "Rahu" || b === "Ketu")))
      .map(([p, l]) => ({ point: p, orb: sep(sid, l) })).sort((a, b2) => a.orb - b2.orb);
    return { body: b, sid, house: houseOf(sid, C.ascS), gate: G.gate, line: G.line, carried: carried[G.gate] || [],
             on, retro, inMoonMansion: nakIndex(sid) === moonNak };
  });
}
const jdOf = d => (start ?? Math.floor(Date.now() / 864e5 + 2440587.5 - 0.5) + 0.5) + d;

/* ---------------- spans over the year, worked out once the track arrives ---------------- */
let RX = {}, SIGNSPAN = {}, CLOCK = { chapters: [], passages: [] }, MOONBACK = [];
function runs(n, key){
  const out = []; let cur = null;
  for (let d = 0; d < n; d++){
    const k = key(d);
    if (cur && cur.k === k){ cur.b = d; continue; }
    if (cur) out.push(cur);
    cur = { k, a: d, b: d };
  }
  if (cur) out.push(cur);
  return out;
}
function prepare(){
  RX = {}; SIGNSPAN = {};
  /* retrograde spans from the stations (worked out at full precision on the server), not from
     the rounded daily track, which can't tell a slow planet standing still from one turning */
  for (const b of RX_ROWS){
    const st = events.filter(e => e.kind === "station" && e.body === b);
    let on = st.length ? st[0].turns === "direct" : false, from = 0;
    const spans = [];
    for (const e of st){
      const d = e.jd - jdOf(0);
      if (e.turns === "retrograde"){ if (!on) from = d; on = true; }
      else { if (on) spans.push({ a: Math.max(0, Math.round(from)), b: Math.max(0, Math.round(d) - 1) }); on = false; }
    }
    if (on) spans.push({ a: Math.max(0, Math.round(from)), b: DAYS });
    RX[b] = spans;
  }
  for (const b of HOUSE_ROWS){
    const L = track.lon[b];
    SIGNSPAN[b] = runs(DAYS + 1, d => Math.floor(norm(L[d]) / 30));
  }
  const L = track.lon.Moon, mn = nakIndex(C.sid.Moon);
  MOONBACK = []; for (let d = 1; d <= DAYS; d++) if (nakIndex(L[d]) === mn && nakIndex(L[d - 1]) !== mn) MOONBACK.push(d);
  /* the clock's chapters and passages that touch the year */
  const T = C.dashaTree, a0 = jdOf(0), a1 = jdOf(DAYS);
  CLOCK = { chapters: [], passages: [] };
  for (const m of T.maha){
    if (m.to < a0 || m.from > a1) continue;
    for (const a of subPeriods(m.lord, m.from, m.years)){
      if (a.to < a0 || a.from > a1) continue;
      CLOCK.chapters.push({ ...a, era: m.lord });
      for (const p of subPeriods(a.lord, a.from, a.years))
        if (p.to >= a0 && p.from <= a1) CLOCK.passages.push({ ...p, era: m.lord, chapter: a.lord });
    }
  }
}
function clockAt(jd){
  const T = C.dashaTree;
  const m = T.maha.find(x => jd >= x.from && jd < x.to) || T.maha[0];
  const a = subPeriods(m.lord, m.from, m.years).find(x => jd >= x.from && jd < x.to);
  const p = a && subPeriods(a.lord, a.from, a.years).find(x => jd >= x.from && jd < x.to);
  return { m, a, p };
}

/* ---------------- the wheel ---------------- */
function xy(lon, r){
  const t = Math.PI + (lon - C.ascS) * Math.PI / 180;
  return [200 + r * Math.cos(t), 200 - r * Math.sin(t)];
}
function spread(items, minGap){
  const s = items.slice().sort((a, b) => a.lon - b.lon);
  s.forEach(i => i.at = i.lon);
  for (let pass = 0; pass < 4; pass++)
    for (let i = 0; i < s.length; i++){
      const a = s[i], b = s[(i + 1) % s.length];
      const gap = ((b.at - a.at) + 360) % 360;
      if (s.length > 1 && gap < minGap){ const push = (minGap - gap) / 2; a.at -= push; b.at += push; }
    }
  return s;
}
function arc(r1, r2, a, b, fill, op){
  const [x1, y1] = xy(a, r2), [x2, y2] = xy(b, r2), [x3, y3] = xy(b, r1), [x4, y4] = xy(a, r1);
  return `<path d="M${x1} ${y1} A${r2} ${r2} 0 0 0 ${x2} ${y2} L${x3} ${y3} A${r1} ${r1} 0 0 1 ${x4} ${y4}Z" fill="${fill}" fill-opacity="${op}"/>`;
}
let natalAt = {};
function wheelBase(){
  const ascSign = Math.floor(C.ascS / 30);
  let s = `<svg viewBox="0 0 400 400" class="nw-svg" role="img" aria-label="The sky on the chosen day around your birth chart">`;
  for (let i = 0; i < 12; i++){
    const sign = (ascSign + i) % 12, a = sign * 30, h = HOUSES[i];
    s += arc(150, 172, a, a + 30, h.hex, .3);
    const [lx, ly] = xy(a + 15, 186), [hx, hy] = xy(a + 15, 161);
    s += `<text x="${lx}" y="${ly}" class="tr-sign">${SG[sign]}</text><text x="${hx}" y="${hy}" class="tr-house">${i + 1}</text>`;
    const [ox, oy] = xy(a, 198), [ix, iy] = xy(a, 60);
    s += `<line x1="${ox}" y1="${oy}" x2="${ix}" y2="${iy}" class="tr-div"/>`;
  }
  s += `<circle cx="200" cy="200" r="198" class="tr-ring"/><circle cx="200" cy="200" r="172" class="tr-ring"/>
        <circle cx="200" cy="200" r="150" class="tr-ring"/><circle cx="200" cy="200" r="60" class="tr-ring"/>`;
  if (!C.unknownTime){ const [ax, ay] = xy(C.ascS, 198), [aix, aiy] = xy(C.ascS, 60); s += `<line x1="${ax}" y1="${ay}" x2="${aix}" y2="${aiy}" class="tr-asc"/>`; }
  const natal = spread(MOVING.map(b => ({ b, lon: C.sid[b] })), 9);
  natalAt = {}; natal.forEach(n => natalAt[n.b] = n.at);
  if (!C.unknownTime){ natalAt.Ascendant = C.ascS; natalAt.Midheaven = C.mcS; }
  natal.forEach(n => { const [x, y] = xy(n.at, 92); s += `<text x="${x}" y="${y}" class="tr-natal">${GLYPH[n.b]}</text>`; });
  return s + `<g class="nw-live"></g></svg>`;
}
function wheelLive(rows){
  let s = "";
  const moving = spread(rows.map(r => ({ b: r.body, lon: r.sid, r })), 9);
  moving.forEach(m => m.r.on.forEach(h => {
    const [x1, y1] = xy(m.at, 128), [x2, y2] = xy(natalAt[h.point], h.point === "Ascendant" || h.point === "Midheaven" ? 60 : 92);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="tr-thread${sel && sel !== m.b ? " dim" : ""}"/>`;
  }));
  moving.forEach(m => {
    const [x, y] = xy(m.at, 136), r = m.r;
    s += `<g class="tr-mov${sel === m.b ? " sel" : ""}${sel && sel !== m.b ? " dim" : ""}" data-nw-b="${m.b}" tabindex="0" role="button" aria-label="${m.b}${r.retro ? ", retrograde" : ""}">
      ${r.carried.length ? `<circle cx="${x}" cy="${y}" r="11" class="tr-halo"/>` : ""}
      ${sel === m.b ? `<circle cx="${x}" cy="${y}" r="12.5" class="nw-ring"/>` : ""}
      <circle cx="${x}" cy="${y}" r="11" class="tr-hit"/>
      <text x="${x}" y="${y}" class="tr-glyph">${GLYPH[m.b]}</text>
      ${r.retro ? `<text x="${x + 10}" y="${y - 8}" class="tr-rx">℞</text>` : ""}</g>`;
  });
  const now = day === 0 && rows === C.transits.rows;
  s += `<text x="200" y="196" class="tr-c1">${now ? "now" : esc(dayShort(jdOf(day)))}</text><text x="200" y="212" class="tr-c2">${now ? "around your birth" : inDays(day)}</text>`;
  return s;
}

/* ---------------- the cards for the chosen day ---------------- */
function nextTransit(){
  const j = jdOf(day) + 0.5;
  return events.find(e => (e.kind === "transit" || e.kind === "sadesati") && e.jd > j);
}
function moonPhase(rows){
  const sun = rows.find(r => r.body === "Sun").sid, moon = rows.find(r => r.body === "Moon").sid;
  const gap = norm(moon - sun), t = Math.floor(gap / 12) + 1;
  const name = gap < 6 || gap > 354 ? "new" : gap < 84 ? "a waxing crescent" : gap < 96 ? "at first quarter" : gap < 174 ? "waxing gibbous"
    : gap < 186 ? "full" : gap < 264 ? "waning gibbous" : gap < 276 ? "at last quarter" : "a waning crescent";
  return { name, tithi: t, paksha: t <= 15 ? "bright" : "dark", day: t <= 15 ? t : t - 15 };
}
function lineOf(r){
  const h = HOUSES[r.house - 1];
  const bits = [`${SIGNS[Math.floor(norm(r.sid) / 30)]}, in your ${ORD(r.house)} house <span class="sw" style="background:${h.hex}"></span>${h.color.toLowerCase()}: ${h.phase.charAt(0).toLowerCase() + h.phase.slice(1)}`];
  bits.push(`gate ${r.gate}.${r.line}, ${GATE_TITLE[r.gate] || ""}` + (r.carried.length ? `, a gate you carry in your ${r.carried.slice(0, 3).join(", ")}` : ""));
  if (r.on.length) bits.push("sitting on your birth " + r.on.map(o => `${o.point} (${o.orb.toFixed(1)}°)`).join(" and "));
  if (r.inMoonMansion) bits.push("crossing your Moon's mansion");
  return bits.join("; ") + ".";
}
function cards(rows){
  const jd = jdOf(day), out = [];
  if (sel){
    const r = rows.find(x => x.body === sel);
    let more = "";
    if (track && RX[sel]){
      const now = RX[sel].find(s => day >= s.a && day <= s.b), nx = RX[sel].find(s => s.a > day);
      more = now ? `Retrograde until ${esc(dayShort(jdOf(now.b + 1)))}.` : nx ? `Next turns retrograde ${esc(dayShort(jdOf(nx.a)))}.` : "";
    }
    if (r) out.push(`<section class="nw-card nw-sel"><h4>Following ${GLYPH[sel]} ${sel}${r.retro ? " <small>retrograde</small>" : ""}</h4>
      <p>${lineOf(r)}</p>${more ? `<p class="nw-fine">${more}</p>` : ""}
      <button type="button" class="nw-link" data-nw-b="${sel}">Stop following</button></section>`);
  }
  /* touching your chart */
  const lit = rows.filter(r => r.on.length);
  let touch = lit.length ? `<ul class="nw-hits">${lit.map(r => r.on.map(o =>
      `<li><button type="button" data-nw-b="${r.body}">${GLYPH[r.body]} ${r.body}</button> on your ${pt(o.point)} <small>${o.orb.toFixed(1)}° away${r.retro ? ", retrograde" : ""}</small></li>`).join("")).join("")}</ul>`
    : `<p>Nothing sits on one of your birth points ${day === 0 ? "today" : "this day"}.</p>`;
  const nt = nextTransit();
  if (nt){
    const d = Math.floor(nt.jd - jdOf(0));
    touch += `<p class="nw-fine">Next: <button type="button" class="nw-link" data-nw-day="${d}" data-nw-pick="${nt.body}">${esc(eventText(nt).replace(/<[^>]+>/g, ""))}, ${esc(evDay(nt.jd))}</button></p>`;
  }
  out.push(`<section class="nw-card nw-gold"><h4>Touching your chart</h4>${touch}
    <p class="nw-why">A gold thread on the wheel: a moving planet within its ${g("orb", "orb")} of one of yours.</p></section>`);
  /* the Moon */
  const mr = rows.find(r => r.body === "Moon"), ph = moonPhase(rows), nk = NAKSHATRA[nakIndex(mr.sid)][0];
  let back = "";
  if (track){ const nb = MOONBACK.find(d => d > day); if (nb !== undefined) back = `Back in your Moon's mansion <button type="button" class="nw-link" data-nw-day="${nb}" data-nw-pick="Moon">${esc(dayShort(jdOf(nb)))}</button>.`; }
  out.push(`<section class="nw-card"><h4>The Moon</h4>
    <p>☽ in ${SIGNS[Math.floor(norm(mr.sid) / 30)]}, in ${esc(nk)}, your ${ORD(mr.house)} house <span class="sw" style="background:${HOUSES[mr.house - 1].hex}"></span></p>
    <p class="nw-fine">${ph.name.charAt(0).toUpperCase() + ph.name.slice(1)}: day ${ph.day} of the ${ph.paksha} half, ${g("tithi", "tithi")} ${ph.tithi}.${mr.inMoonMansion ? " <b>Crossing your Moon's mansion.</b>" : ""} ${back}</p>
    <p class="nw-why">She moves about 13° a day, a sign every two and a half days. Step one day and watch her jump.</p></section>`);
  /* retrograde */
  const rx = rows.filter(r => r.retro);
  let rxs = rx.length ? `<ul class="nw-rx">${rx.map(r => {
      const sp = track && RX[r.body] && RX[r.body].find(s => day >= s.a && day <= s.b);
      return `<li><button type="button" data-nw-b="${r.body}">${GLYPH[r.body]} ${r.body}</button>${sp && sp.b < DAYS ? ` <small>direct ${esc(dayShort(jdOf(sp.b + 1)))}</small>` : ""}</li>`;
    }).join("")}</ul>` : `<p>Nothing is retrograde ${day === 0 ? "today" : "this day"}.</p>`;
  if (track){
    const nx = RX_ROWS.map(b => ({ b, s: RX[b].find(s => s.a > day) })).filter(x => x.s && !rx.some(r => r.body === x.b)).sort((a, b) => a.s.a - b.s.a)[0];
    if (nx) rxs += `<p class="nw-fine">Next to turn: <button type="button" class="nw-link" data-nw-day="${nx.s.a}" data-nw-pick="${nx.b}">${GLYPH[nx.b]} ${nx.b}, ${esc(dayShort(jdOf(nx.s.a)))}</button></p>`;
  }
  out.push(`<section class="nw-card"><h4>${g("retro", "Retrograde")}</h4>${rxs}
    <p class="nw-why">Seen from Earth a planet seems to walk backwards for a while as one of us overtakes the other. It hasn't turned; our view has.</p></section>`);
  /* the clock */
  const k = clockAt(jd + 0.5);
  if (k.a && k.p){
    const pc = x => Math.max(0, Math.min(100, (jd - x.from) / (x.to - x.from) * 100));
    const bar = (lbl, x, key) => `<div class="nw-clk"><span>${g(key, lbl)}</span><b>${GLYPH[x.lord]} ${x.lord}</b><i><em style="width:${pc(x).toFixed(1)}%"></em></i><small>until ${esc(dayShort(x.to))}${x.to - jdOf(0) > 330 ? `, ${jdDate(x.to).getUTCFullYear()}` : ""}</small></div>`;
    out.push(`<section class="nw-card nw-jade"><h4>Your clock</h4>${bar("Era", k.m, "mahadasha")}${bar("Chapter", k.a, "antardasha")}${bar("Passage", k.p, "pratyantar")}
      <p class="nw-why">Set by your Moon at birth. The sky moves for everyone; this clock is yours alone. <a href="#clock">Open the clock</a></p></section>`);
  }
  /* Saturn on the Moon */
  const sat = rows.find(r => r.body === "Saturn");
  const rel = (Math.floor(norm(sat.sid) / 30) - Math.floor(norm(C.sid.Moon) / 30) + 12) % 12 + 1;
  if ([12, 1, 2].includes(rel))
    out.push(`<section class="nw-card nw-gold nw-wide"><h4>${g("sadesati", "Sade Sati")}</h4><p>Saturn is ${({12: "in the sign before your Moon's", 1: "in your Moon's own sign", 2: "in the sign after your Moon's"})[rel]}: the ${({12: "first", 1: "second", 2: "last"})[rel]} of the three signs of Sade Sati, the seven and a half years Saturn takes to cross the Moon's sign and the sign on either side.</p></section>`);
  return out.join("");
}

/* ---------------- the year strip ---------------- */
const pct = d => (Math.max(0, Math.min(DAYS, d)) / DAYS * 100).toFixed(3) + "%";
const dOf = jd => Math.max(0, Math.min(DAYS, Math.floor(jd - jdOf(0))));
function yearStrip(){
  if (loadErr) return `<p class="err">${esc(loadErr)} <button type="button" class="link-btn" data-nw-retry>Try again</button></p>`;
  if (!track) return `<p class="cal-wait">Working out the next twelve months…</p>`;
  let months = "";
  for (let d = 0; d <= DAYS; d++){
    const dt = jdDate(jdOf(d));
    if (dt.getUTCDate() === 1 || (d === 0 && dt.getUTCDate() < 18))
      months += `<span style="left:${pct(d)}">${dt.toLocaleDateString(undefined, { ...UTC, month: "short" })}${dt.getUTCMonth() === 0 ? ` <b>${dt.getUTCFullYear()}</b>` : ""}</span>`;
  }
  /* touching you: dots, stacked so neighbours don't hide each other */
  const you = events.filter(e => e.kind === "transit" || e.kind === "sadesati");
  const rowEnd = [-99, -99, -99, -99]; let dots = "";
  you.forEach((e, i) => {
    const d = dOf(e.jd); let row = rowEnd.findIndex(x => d - x >= 12); if (row < 0) row = 3; rowEnd[row] = d;
    const txt = eventText(e).replace(/<[^>]+>/g, "");
    dots += `<button type="button" class="nw-dot${e.kind === "sadesati" ? " ss" : ""}" style="left:${pct(d)};top:${3 + row * 19}px" data-nw-ev="${i}" title="${esc(evDay(e.jd))}: ${esc(txt)}" aria-label="${esc(evDay(e.jd))}: ${esc(txt)}">${GLYPH[e.body] || "♄"}</button>`;
  });
  const youH = 6 + (rowEnd.filter(x => x > -99).length || 1) * 19;
  /* the clock: chapters above, passages below */
  const seg = (x, cls, title) => {
    const a = Math.max(0, x.from - jdOf(0)), b = Math.min(DAYS, x.to - jdOf(0));
    const w = (b - a) / DAYS * 100;
    return `<div class="nw-seg ${cls}" style="left:${pct(a)};width:${w.toFixed(3)}%" title="${esc(title)}"><span>${w > 4.5 ? GLYPH[x.lord] : ""}</span></div>`;
  };
  const chap = CLOCK.chapters.map(a => seg(a, "ch", `Chapter of ${a.lord}, ${dayShort(a.from)} to ${dayShort(a.to)}`)).join("");
  const pass = CLOCK.passages.map((p, i) => seg(p, "ps" + (i % 2), `Passage of ${p.lord}, ${dayShort(p.from)} to ${dayShort(p.to)}`)).join("");
  /* the slow planets through your houses, in your house colours */
  const houses = HOUSE_ROWS.map(b => `<div class="nw-row"><i>${GLYPH[b]}</i><div class="nw-rt">${SIGNSPAN[b].map(s => {
      const h = houseOf(s.k * 30 + 1, C.ascS), w = (s.b - s.a + 1) / DAYS * 100;
      return `<div class="nw-band" style="left:${pct(s.a)};width:${w.toFixed(3)}%;background:${HOUSES[h - 1].hex}" title="${b} in ${SIGNS[s.k]}, your ${ORD(h)} house, ${dayShort(jdOf(s.a))} to ${dayShort(jdOf(s.b))}"><span>${w > 6 ? h : ""}</span></div>`;
    }).join("")}</div></div>`).join("");
  /* retrogrades */
  const rx = RX_ROWS.filter(b => RX[b].length).map(b => `<div class="nw-row"><i>${GLYPH[b]}</i><div class="nw-rt">${RX[b].map(s =>
      `<div class="nw-rxbar" style="left:${pct(s.a)};width:${((s.b - s.a + 1) / DAYS * 100).toFixed(3)}%" title="${b} retrograde, ${dayShort(jdOf(s.a))} to ${dayShort(jdOf(s.b + 1))}"></div>`).join("")}</div></div>`).join("");
  return `<div class="nw-year" data-nw-strip>
    <div class="nw-axis"><div class="nw-rt">${months}</div></div>
    <div class="nw-lh">Touching your chart</div><div class="nw-row nw-you" style="height:${youH}px"><i></i><div class="nw-rt">${dots || `<small class="nw-none">nothing this year</small>`}</div></div>
    <div class="nw-lh">Your clock <small>chapters, then passages</small></div>
    <div class="nw-row"><i></i><div class="nw-rt">${chap}</div></div>
    <div class="nw-row"><i></i><div class="nw-rt">${pass}</div></div>
    <div class="nw-lh">Through your houses <small>each band in its house's colour</small></div>${houses}
    <div class="nw-lh">${g("retro", "Retrograde")}</div>${rx}
    <div class="nw-cur" aria-hidden="true"><b></b></div>
  </div>
  <p class="nw-fine">Drag along the strip, or tap a gold dot, to move the wheel to that day. The Sun walks through all twelve of your houses in a year; Saturn may not leave one.</p>`;
}

/* ---------------- the list ---------------- */
const KINDS = [["you", "For you"], ["all", "Everything"], ["ingress", "Sign changes"], ["station", "Retrogrades"]];
function eventText(e){
  switch (e.kind){
    case "transit": return `${GLYPH[e.body]} ${e.body} ${e.aspect === "conjunction" ? "reaches" : `makes ${/^[aeiou]/.test(e.aspect) ? "an" : "a"} ${e.aspect} to`} your ${pt(e.to)}${e.retro ? " <small>(retrograde)</small>" : ""}`;
    case "sadesati": return `♄ Saturn enters ${e.sign}: your Sade Sati ${e.phase}`;
    case "ingress": return `${GLYPH[e.body]} ${e.body} enters ${e.sign}${e.retro && !["Rahu", "Ketu"].includes(e.body) ? " <small>(retrograde)</small>" : ""}`;
    case "station": return `${GLYPH[e.body]} ${e.body} stations ${e.turns} in ${e.sign}`;
    case "clock": return `${GLYPH[e.lord]} Your ${e.level} of ${e.lord} begins${e.within ? ` <small>within ${e.within}</small>` : ""}`;
  }
  return "";
}
function clockEvents(a0, a1){
  const T = C.dashaTree, out = [];
  for (const m of T.maha){
    if (m.from > a0 && m.from < a1) out.push({ jd: m.from, kind: "clock", level: "era", lord: m.lord });
    if (m.to < a0 || m.from > a1) continue;
    for (const a of subPeriods(m.lord, m.from, m.years)){
      if (a.from > a0 && a.from < a1) out.push({ jd: a.from, kind: "clock", level: "chapter", lord: a.lord, within: m.lord });
      if (a.to < a0 || a.from > a1) continue;
      for (const p of subPeriods(a.lord, a.from, a.years))
        if (p.from > a0 && p.from < a1) out.push({ jd: p.from, kind: "clock", level: "passage", lord: p.lord, within: `${m.lord} / ${a.lord}` });
    }
  }
  return out;
}
function paintList(){
  if (!list) return;
  const shown = events.filter(e => filter === "all" || (filter === "you" ? ["transit", "sadesati", "clock"].includes(e.kind) : e.kind === filter));
  const cut = jdOf(0) + 92, some = allMonths ? shown : shown.filter(e => e.jd < cut);
  let html = `<div class="cal-filter" role="group" aria-label="Show">${KINDS.map(([k, l]) => `<button type="button" data-nw-f="${k}" aria-pressed="${k === filter}">${l}</button>`).join("")}</div>`;
  if (!track && !loadErr) html += `<p class="cal-wait">Working out the next twelve months…</p>`;
  else if (!shown.length) html += `<p class="cal-wait">Nothing of this kind in the next twelve months.</p>`;
  else {
    let month = "";
    for (const e of some){
      const m = monthOf(e.jd);
      if (m !== month){ if (month) html += "</ol>"; html += `<h4 class="cal-m">${m}</h4><ol class="cal-list nw-list">`; month = m; }
      const cls = e.kind === "transit" || e.kind === "sadesati" ? "you" : e.kind;
      html += `<li class="cal-${cls}"><button type="button" data-nw-day="${dOf(e.jd)}" data-nw-pick="${e.body || ""}" data-nw-scroll><time>${esc(evDay(e.jd))}</time><span>${eventText(e)}</span></button></li>`;
    }
    if (month) html += "</ol>";
    if (!allMonths && shown.length > some.length)
      html += `<p><button type="button" class="tz-chip" data-nw-more>Show all twelve months (${shown.length - some.length} more)</button></p>`;
  }
  if (X.unknown) html += `<p class="unknown-note">Without a birth time, transits to the rising sign and midheaven are left out, and the clock's dates may be out by months.</p>`;
  list.innerHTML = html;
}

/* ---------------- painting ---------------- */
function paint(){
  const rows = rowsOn(day);
  const live = top.querySelector(".nw-live");
  if (live) live.innerHTML = wheelLive(rows);
  top.querySelector(".nw-when").innerHTML = day === 0 && rows === C.transits.rows
    ? `<b>Today</b> <span>${esc(new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" }))}</span>`
    : `<b>${esc(dayLong(jdOf(day)))}</b> <span>${inDays(day)}</span>`;
  top.querySelector(".nw-cards").innerHTML = cards(rows);
  const r = top.querySelector(".nw-range"); if (r && +r.value !== day) r.value = day;
  r && r.setAttribute("aria-valuetext", dayLong(jdOf(day)));
  const cur = top.querySelector(".nw-cur");
  if (cur){ cur.style.left = `calc(22px + (100% - 22px) * ${day / DAYS})`; cur.classList.toggle("r", day > DAYS * .8); cur.querySelector("b").textContent = dayShort(jdOf(day)); }
  top.querySelector("[data-nw-today]").disabled = day === 0;
}
function setDay(d, pick){
  day = Math.max(0, Math.min(track ? DAYS : 0, d | 0));
  if (pick !== undefined) sel = pick || null;
  paint();
}
function play(on){
  const b = top.querySelector("[data-nw-play]");
  if (timer){ clearInterval(timer); timer = null; }
  if (on && track){
    if (day >= DAYS) day = 0;
    timer = setInterval(() => {
      if (document.getElementById("p-sky").hidden || day >= DAYS){ play(false); return; }
      setDay(day + 1);
    }, 70);
  }
  b.textContent = timer ? "❚❚ Pause" : "▶ Play the year";
  b.setAttribute("aria-pressed", !!timer);
}

/* ---------------- loading ---------------- */
function load(){
  loadErr = null; top.querySelector(".nw-strip").innerHTML = yearStrip(); paintList();
  fetch("/api/calendar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(X.birth) })
    .then(r => r.json().catch(() => ({})).then(j => { if (!r.ok) throw new Error(j.error || "The year couldn't be worked out."); return j; }))
    .then(j => {
      start = j.start; track = j.track || null;
      events = j.events.concat(clockEvents(start, start + DAYS)).sort((a, b) => a.jd - b.jd);
      if (track) prepare();
      top.querySelector(".nw-range").max = track ? DAYS : 0;
      top.querySelector(".nw-scrub").classList.toggle("off", !track);
      top.querySelector(".nw-strip").innerHTML = yearStrip(); paintList(); paint();
    })
    .catch(x => {
      loadErr = x instanceof TypeError ? "You're offline. The coming year needs a connection to work out." : x.message;
      top.querySelector(".nw-strip").innerHTML = yearStrip(); paintList();
    });
}

function mount(o){
  X = o; C = o.C; top = o.top; list = o.list;
  carried = {};
  for (const side of ["personality", "design"])
    for (const [body, gg] of Object.entries((C.natal || {})[side] || {})) (carried[gg.gate] = carried[gg.gate] || []).push(`${side} ${body}`);
  points = Object.fromEntries(MOVING.map(b => [b, C.sid[b]]));
  if (!C.unknownTime){ points.Ascendant = C.ascS; points.Midheaven = C.mcS; }

  top.innerHTML = `<div class="nw-head"><p class="nw-when" aria-live="polite"></p>
      <div class="nw-ctl" role="group" aria-label="Move through the year">
        <button type="button" class="tz-chip" data-nw-step="-1" aria-label="A day earlier">◀ Day</button>
        <button type="button" class="tz-chip nw-play" data-nw-play aria-pressed="false">▶ Play the year</button>
        <button type="button" class="tz-chip" data-nw-step="1" aria-label="A day later">Day ▶</button>
        <button type="button" class="tz-chip" data-nw-step="7" aria-label="A week later">Week ▶▶</button>
        <button type="button" class="tz-chip" data-nw-today>Back to today</button>
      </div></div>
    <div class="nw-grid">
      <div class="nw-stage">${wheelBase()}
        <div class="nw-scrub off"><input class="nw-range" type="range" min="0" max="0" step="1" value="0" aria-label="Day in the coming year"></div>
        <p class="nw-fine nw-key">Inner ring: your birth chart. Outer ring: the sky on this day. A gold thread marks a planet sitting on one of yours; a green halo, a planet in a gate you carry. Tap a planet to follow it.</p>
      </div>
      <div class="nw-cards" aria-live="polite"></div>
    </div>
    <h3 class="sec-h">The year ahead</h3>
    <div class="nw-strip"></div>`;
  paint();

  /* the controls */
  top.addEventListener("click", e => {
    const t = e.target;
    const b = t.closest("[data-nw-b]");
    if (b){ sel = sel === b.dataset.nwB ? null : b.dataset.nwB; paint(); return; }
    const st = t.closest("[data-nw-step]"); if (st){ play(false); setDay(day + +st.dataset.nwStep); return; }
    if (t.closest("[data-nw-play]")){ play(!timer); return; }
    if (t.closest("[data-nw-today]")){ play(false); setDay(0); return; }
    if (t.closest("[data-nw-retry]")){ load(); return; }
    const ev = t.closest("[data-nw-ev]");
    if (ev){ const e2 = events.filter(x => x.kind === "transit" || x.kind === "sadesati")[+ev.dataset.nwEv]; play(false); setDay(dOf(e2.jd), e2.body || "Saturn"); return; }
    const jd = t.closest("[data-nw-day]");
    if (jd){ play(false); setDay(+jd.dataset.nwDay, jd.dataset.nwPick || undefined); }
  });
  top.addEventListener("keydown", e => {
    if ((e.key === "Enter" || e.key === " ") && e.target.closest && e.target.closest("g[data-nw-b]")){ e.preventDefault(); e.target.closest("g[data-nw-b]").dispatchEvent(new MouseEvent("click", { bubbles: true })); }
  });
  top.addEventListener("input", e => { if (e.target.classList.contains("nw-range")){ play(false); setDay(+e.target.value); } });
  /* drag along the year strip */
  let drag = false;
  const at = ev => {
    const rt = top.querySelector(".nw-axis .nw-rt"); if (!rt) return;
    const r = rt.getBoundingClientRect();
    setDay(Math.round((ev.clientX - r.left) / r.width * DAYS));
  };
  top.addEventListener("pointerdown", e => {
    if (!track || !e.target.closest("[data-nw-strip]") || e.target.closest("button")) return;
    drag = true; play(false); at(e);
  });
  addEventListener("pointermove", e => { if (drag) at(e); });
  addEventListener("pointerup", () => { drag = false; });
  addEventListener("pointercancel", () => { drag = false; });

  list.addEventListener("click", e => {
    const f = e.target.closest("[data-nw-f]"); if (f){ filter = f.dataset.nwF; paintList(); if (Wyrd.pulse) Wyrd.pulse("calendar", filter); return; }
    if (e.target.closest("[data-nw-more]")){ allMonths = true; paintList(); return; }
    const d = e.target.closest("[data-nw-day]");
    if (d && track){
      play(false); setDay(+d.dataset.nwDay, d.dataset.nwPick || null);
      top.querySelector(".nw-head").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
  load();
}

window.WyrdNow = { mount };
})();
