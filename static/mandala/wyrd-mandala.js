/* ============================================================
   WYRD MANDALA · engine
   Reads WYRD (wyrd-data.js) and WyrdGlyphs (wyrd-glyphs.js).
   Holds no cosmology of its own.

   1. GEOMETRY      pure functions: angles, points, sectors, arcs
   2. PRESENTATION  ring renderers, the station record
   3. INTERACTION   selection, hover, focus, rotation, layers, navigation

   Angles: 0° sidereal Aries at the top, longitude increasing clockwise.
   Rotation turns the dial; text and glyphs stay upright.

   WyrdMandala.mount(host, opts) builds one instrument inside host:
     opts.planets  { Sun: 123.4, … } sidereal longitudes to stand on the dial
     opts.start    station to open on (else #s037 in the address, the Moon's, or 1)
     opts.hash     false to leave the address alone (default true)
     opts.onSelect called with the station (or null) on every selection
     opts.theme    "site" for the Wyrd Console's dark palette
   It returns { select, state }.
   ============================================================ */
(function (root) {
  "use strict";
  const D = root.WYRD, G = root.WyrdGlyphs;
  const S = D.stations;
  const instances = [];

  /* ---------- shared helpers: no state ---------- */
  const f = n => n.toFixed(2);
  const mid = s => (s.zodiacStart + s.zodiacEnd) / 2;
  const norm = d => ((d % 360) + 360) % 360;
  const dms = d => { const s = Math.round(d * 3600), deg = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), sec = s % 60;
    return `${deg}°${String(m).padStart(2, "0")}′${sec ? String(sec).padStart(2, "0") + "″" : ""}`; };
  const inSign = d => { const s = D.SIGNS[Math.floor(norm(d) / 30)]; return `${dms(norm(d) % 30)} ${s.name}`; };
  const stationAt = lon => S[Math.floor(norm(lon) / D.PADA) % 108];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const ring = id => D.LAYERS.find(l => l.id === id).ring;
  const GLYPH = { Sun: "☉", Moon: "☽", Mars: "♂", Mercury: "☿", Jupiter: "♃", Venus: "♀", Saturn: "♄", Rahu: "☊", Ketu: "☋",
    Uranus: "♅", Neptune: "♆", Pluto: "♇", Ascendant: "AC", Midheaven: "MC" };
  const NA = `<span class="na">Not yet assigned</span>`;

  /* the instrument's controls, dial and record: one copy per mount, found by data-wm, never by global id */
  let seq = 0;
  const template = n => `
    <div class="wm-work">
      <div class="wm-dial-col">
        <div class="wm-ctl" role="group" aria-label="Navigate stations">
          <span class="wm-lab">Station</span>
          <button type="button" data-wm="prev" aria-label="Previous station">← Prev</button>
          <button type="button" data-wm="next" aria-label="Next station">Next →</button>
          <select data-wm="nak" aria-label="Choose a nakshatra"></select>
          <span class="wm-pads" data-wm="padas" role="group" aria-label="Pada">${[1, 2, 3, 4].map(p => `<button type="button" data-p="${p}">${p}</button>`).join("")}</span>
          <input type="search" data-wm="search" list="wm-list-${n}" placeholder="Search: 37, Magha 1, Leo…" aria-label="Search for a station">
          <datalist id="wm-list-${n}" data-wm="list"></datalist>
          <button type="button" data-wm="reset">Reset</button>
        </div>
        <div class="wm-dial">
          <svg class="wm-svg" data-wm="svg" tabindex="0" role="img" viewBox="-560 -560 1120 1120"
            aria-label="The Wyrd Mandala: 108 pada stations around the sidereal zodiac. Use the arrow keys to step between stations."></svg>
        </div>
        <ul class="wm-key" aria-label="Key">
          <li><i style="border-color: var(--wm-ink)"></i>Nakshatra boundary</li>
          <li><i style="border-color: var(--wm-brass); border-top-style: dashed"></i>Sign boundary, drawn through</li>
          <li><i style="border-color: var(--wm-brass)"></i>Triangle: where sign and mansion boundaries meet (0°, 120°, 240°)</li>
          <li><i style="border-color: var(--wm-ink-2)"></i>Cross: the four cardinal sign starts</li>
          <li><span style="color: var(--wm-brass)">○</span> vargottama pada</li>
          <li><span class="key-void"></span> Asura void: the tunnels, thirty-six dark padas on a 3-2-4 spacing</li>
          <li><span class="key-card"></span> Outside the rim: the Nordic deck's planetary trumps, each at its planet's exaltation</li>
          <li><i style="border-color: var(--wm-verd); border-top-width: 6px"></i>Tropical rings, outside: the Nordic cards and the tropical signs, turned by the ayanamsa</li>
          <li><i style="border-color: var(--wm-verd); border-top-style: dashed"></i>The equinox: 0° tropical Aries</li>
          <li data-wm="plKey" hidden><span style="color: var(--wm-pl)">☉</span> your planets, at their sidereal places</li>
        </ul>
        <div class="wm-ctl" role="group" aria-label="Layers"><span class="wm-lab">Layers</span><span data-wm="layers" class="wm-ctl"></span></div>
        <div class="wm-ctl" role="group" aria-label="Instrument">
          <span class="wm-lab">Dial</span>
          <label for="wm-rot-${n}">Rotate</label><input type="range" id="wm-rot-${n}" data-wm="rot" min="0" max="359" step="1" value="0">
          <button type="button" data-wm="align">Bring selected station to the top</button>
        </div>
        <div class="wm-ctl" role="group" aria-label="The two rotors">
          <span class="wm-lab">Year</span>
          <label for="wm-year-${n}">Turn the tropical ring through time</label>
          <input type="range" id="wm-year-${n}" data-wm="year" min="285" max="2700" step="1" value="${D.EPOCH}">
          <output class="wm-year" data-wm="yearOut">${D.EPOCH}</output>
          <button type="button" data-wm="now">Back to ${D.EPOCH}</button>
          <p class="wm-rel-note" data-wm="yearNote"></p>
        </div>
        <div class="wm-ctl" role="group" aria-label="Focus mode">
          <span class="wm-lab">Focus</span>
          <label class="wm-chk"><input type="checkbox" data-wm="focus"> Show relations from the selected station</label>
          <select data-wm="relation" aria-label="Relation"></select>
          <p class="wm-rel-note" data-wm="relNote"></p>
        </div>
      </div>
      <aside class="wm-record" data-wm="record" aria-live="polite"></aside>
    </div>`;

  function mount(host, opts = {}) {
    if (!host) host = document.getElementById("wyrd-mandala");
    host.classList.add("wm");
    if (opts.theme) host.dataset.wmTheme = opts.theme;
    const n = ++seq;
    host.innerHTML = template(n);
    const q = k => host.querySelector(`[data-wm="${k}"]`);
    const svg = q("svg"), panel = q("record");
    const els = { nak: q("nak"), padas: q("padas"), rot: q("rot"), search: q("search"), list: q("list"), layers: q("layers"),
      focus: q("focus"), relation: q("relation"), relNote: q("relNote") };
    const useHash = opts.hash !== false;

    /* your planets: which stand where */
    const planets = Object.entries(opts.planets || {}).filter(([, l]) => typeof l === "number")
      .map(([name, lon]) => ({ name, lon: norm(lon), glyph: GLYPH[name] || name.slice(0, 2), st: stationAt(lon).id }));
    const byStation = {};
    planets.forEach(p => { (byStation[p.st] = byStation[p.st] || []).push(p); });
    if (planets.length) q("plKey").hidden = false;

    /* ============ 1. GEOMETRY ============ */
    const state = { rot: 0, sel: null, hov: null, focus: false, relation: "navamsa", layers: {} };
    const rad = lon => ((lon + state.rot) - 90) * Math.PI / 180;
    const pt = (r, lon) => [r * Math.cos(rad(lon)), r * Math.sin(rad(lon))];
    /* an annular sector from longitude a to b, between radii r0 and r1 */
    function sector(r0, r1, a, b) {
      const [x0, y0] = pt(r1, a), [x1, y1] = pt(r1, b), [x2, y2] = pt(r0, b), [x3, y3] = pt(r0, a), big = (b - a) > 180 ? 1 : 0;
      return `M${f(x0)} ${f(y0)}A${r1} ${r1} 0 ${big} 1 ${f(x1)} ${f(y1)}L${f(x2)} ${f(y2)}A${r0} ${r0} 0 ${big} 0 ${f(x3)} ${f(y3)}Z`;
    }
    /* colour: the console's twelve house colours round the wheel, Aries red to Pisces magenta (the gate station is
       red, house 1). A ring of signs takes each sign's colour; the mansions, which cross the signs, take the colour
       of where their middle stands, blended between the signs' colours. */
    const HUE = ["#ff3b4e", "#ff6a1f", "#ff8c1a", "#ffb31a", "#ffd400", "#a3e635", "#22e07a", "#14e0c0", "#22b8ff", "#6b6bff", "#b05cff", "#ff2fa8"];
    const hx = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
    const hueOf = sign => HUE[((sign % 12) + 12) % 12];
    function hueAt(lon) {
      const x = norm(lon) / 30 - .5, i = Math.floor(x), t = x - i, a = hx(hueOf(i)), b = hx(hueOf(i + 1));
      return "#" + a.map((v, k) => Math.round(v + (b[k] - v) * t).toString(16).padStart(2, "0")).join("");
    }
    const tint = h => ` style="--h:${h}"`;
    /* a card glyph, upright, centred at radius r and longitude lon */
    const card = (code, r, lon, w, cls, data = "") => { if (!G.get(code)) return ""; const h = w * 1.5, [x, y] = pt(r, lon);
      return `<use href="#tarot-${code}" x="${f(x - w / 2)}" y="${f(y - h / 2)}" width="${f(w)}" height="${f(h)}" class="t-glyph ${cls}"${data}/>`; };
    /* the Asura voids: the tunnels, thirty-six on a 3-2-4 spacing; pada 90's has never been named */
    const voidOf = s => s.cards && s.cards.void ? (s.cards.void === "UNNAMED" ? "the unnamed void, the open seat" : s.cards.void) : "";
    /* a radial boundary at longitude a */
    const radial = (r0, r1, a) => { const [x0, y0] = pt(r0, a), [x1, y1] = pt(r1, a); return `M${f(x0)} ${f(y0)}L${f(x1)} ${f(y1)}`; };
    /* an arc for text: runs left-to-right whichever half of the dial it sits on */
    function textArc(r, a, b) {
      const m = norm((a + b) / 2 + state.rot), bottom = m > 90 && m < 270;
      const [p, q2] = bottom ? [b, a] : [a, b], [x0, y0] = pt(r, p), [x1, y1] = pt(r, q2);
      return `M${f(x0)} ${f(y0)}A${r} ${r} 0 0 ${bottom ? 0 : 1} ${f(x1)} ${f(y1)}`;
    }

    /* ============ 2. PRESENTATION ============ */
    function drawField() {
      const [, R] = ring("field");
      let o = `<circle r="${R}" class="f-edge"/><circle r="${R * .62}" class="f-inner"/>`;
      /* the cardinal cross: the four movable-sign starts, each a vargottama station */
      for (const a of [0, 90, 180, 270]) o += `<path d="${radial(22, R, a)}" class="f-axis"/>`;
      /* the 120° triangle: the only three points where sign and nakshatra boundaries coincide (lcm of 30° and 13°20′) */
      const T = [0, 120, 240].map(a => pt(R * .96, a));
      o += `<path d="M${T.map(p => p.map(f).join(" ")).join("L")}Z" class="f-tri"/>`;
      for (const a of [0, 120, 240]) { const [x, y] = pt(R * .96, a); o += `<circle cx="${f(x)}" cy="${f(y)}" r="3.2" class="f-node"/>`; }
      o += `<circle r="12" class="f-bindu-ring"/><circle r="4.5" class="f-bindu"/>`;
      o += card("MB00", R * .76, 0, 20, "trump-glyph gate-glyph", ` data-trump="gate"`);
      return o;
    }
    function drawZodiac(arcDefs) {
      const [r0, r1] = ring("zodiac");
      let o = "";
      for (const s of D.SIGNS) {
        o += `<path d="${sector(r0, r1, s.start, s.end)}" class="z-sec ${s.index % 2 ? "alt" : ""}" data-sign="${s.index}"${tint(hueOf(s.index))}/>`;
        const [gx, gy] = pt((r0 + r1) / 2 + 2, s.start + 6.2), id = `wm${n}-zn-${s.index}`, dec = root.WYRD_MANSIONS && root.WYRD_MANSIONS.cards.decans;
        o += card("MB" + String(s.index + 1).padStart(2, "0"), (r0 + r1) / 2 + 1, s.start + 15, 16, "trump-glyph", ` data-trump="b${s.index}"`);
        o += `<text x="${f(gx)}" y="${f(gy)}" class="z-glyph" text-anchor="middle" dominant-baseline="central">${s.glyph}</text>`;
        arcDefs.push(`<path id="${id}" d="${textArc(r0 + 10, s.start + 1, s.end - 1)}"/>`);
        o += `<text class="z-name"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${s.name.toUpperCase()}</textPath></text>`;
        if (dec) { arcDefs.push(`<path id="${id}-t" d="${textArc(r1 - 7, s.start + 1, s.end - 1)}"/>`);
          o += `<text class="z-trump"><textPath href="#${id}-t" startOffset="50%" text-anchor="middle">${esc(dec[s.index * 3].buddhist.trump)}</textPath></text>`; }
      }
      for (const s of D.SIGNS) o += `<path d="${radial(r0, r1, s.start)}" class="z-div"/>`;
      return o;
    }
    function drawNakshatras(arcDefs) {
      const [r0, r1] = ring("nakshatras");
      let o = "";
      for (const k of D.NAKSHATRAS) {
        o += `<path d="${sector(r0, r1, k.start, k.end)}" class="n-sec ${k.index % 2 ? "alt" : ""}" data-nak="${k.index}"${tint(hueAt((k.start + k.end) / 2))}/>`;
        const id = `wm${n}-nk-${k.index}`;
        arcDefs.push(`<path id="${id}" d="${textArc((r0 + r1) / 2 + 9, k.start + .4, k.end - .4)}"/>`);
        arcDefs.push(`<path id="${id}-b" d="${textArc((r0 + r1) / 2 - 11, k.start + .4, k.end - .4)}"/>`);
        o += `<text class="n-name${k.short.length > 9 ? " long" : ""}"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${k.short}</textPath></text>`;
        o += `<text class="n-num"><textPath href="#${id}-b" startOffset="50%" text-anchor="middle">${String(k.number).padStart(2, "0")} · ${k.ruler}</textPath></text>`;
      }
      for (const k of D.NAKSHATRAS) o += `<path d="${radial(r0, r1, k.start)}" class="n-div"/>`;
      return o;
    }
    function drawPadas() {
      const [r0, r1] = ring("padas");
      let o = "";
      for (const s of S) {
        o += `<path d="${sector(r0, r1, s.zodiacStart, s.zodiacEnd)}" class="p-sec${byStation[s.id] ? " has-pl" : ""}${s.pada % 2 ? "" : " alt"}${voidOf(s) ? " p-void" : ""}" data-st="${s.id}"${tint(hueOf(Math.floor(mid(s) / 30)))}/>`;
        const [x, y] = pt(r0 + 15, mid(s));
        o += `<text x="${f(x)}" y="${f(y)}" class="p-num" text-anchor="middle" dominant-baseline="central">${s.pada}</text>`;
        if (s.vargottama) { const [vx, vy] = pt(r1 - 12, mid(s)); o += `<circle cx="${f(vx)}" cy="${f(vy)}" r="2.6" class="p-varg"/>`; }
        if (voidOf(s)) { const [vx, vy] = pt(r0 + 26, mid(s)); o += `<circle cx="${f(vx)}" cy="${f(vy)}" r="3.6" class="void-mouth"/>`; }
      }
      for (const s of S) o += `<path d="${radial(r0, r1, s.zodiacStart)}" class="${s.pada === 1 ? "p-div-nak" : "p-div"}"/>`;
      /* where the sign boundaries cross the mansion and pada rings: drawn through, so the misalignment shows */
      for (const z of D.SIGNS) o += `<path d="${radial(ring("nakshatras")[0], r1, z.start)}" class="z-through"/>`;
      return o;
    }
    function drawTarot() {
      const [r0, r1] = ring("tarot"), gw = 17, gh = 25.5;
      let o = D.SIGNS.map(z => `<path d="${sector(r0, r1, z.start, z.end)}" class="t-sec${z.index % 2 ? " alt" : ""}"${tint(hueOf(z.index))}/>`).join("")
        + `<circle r="${r0}" class="t-edge"/><circle r="${r1}" class="t-edge"/>`;
      for (const s of S) {
        const [x, y] = pt((r0 + r1) / 2, mid(s));
        o += `<use href="#tarot-${s.tarot.glyph}" x="${f(x - gw / 2)}" y="${f(y - gh / 2)}" width="${gw}" height="${gh}" class="t-glyph${s.tarot.status === "unassigned" ? " unassigned" : ""}" data-st="${s.id}"/>`;
      }
      return o;
    }
    /* the tropical rotor: the Nordic deck's 36 decans, and the tropical signs, turned back from 0° sidereal Aries by the ayanamsa */
    const AY = () => D.FRAME.ayanamsa.degrees;
    function drawNordic(arcDefs) {
      const [r0, r1] = ring("nordic"), dec = root.WYRD_MANSIONS && root.WYRD_MANSIONS.cards.decans;
      let o = "";
      for (let k = 0; k < 36; k++) {
        const a = k * 10 - AY(), b = a + 10, d = dec && dec[k];
        o += `<path d="${sector(r0, r1, a, b)}" class="tz-sec tz-dec ${k % 2 ? "alt" : ""}" data-dec="${k}"${tint(hueOf(Math.floor(k / 3)))}/>`;
        if (d) o += card("N" + String(k + 1).padStart(2, "0"), (r0 + r1) / 2, a + 5, 17, "nd-glyph", ` data-dec="${k}"`);
      }
      for (let k = 0; k < 36; k++) o += `<path d="${radial(r0, r1, k * 10 - AY())}" class="${k % 3 ? "tz-div-t" : "tz-div"}"/>`;
      return o;
    }
    function drawTropical(arcDefs) {
      const [r0, r1] = ring("tropical"), dec = root.WYRD_MANSIONS && root.WYRD_MANSIONS.cards.decans;
      let o = "";
      for (const s of D.SIGNS) {
        const a = s.start - AY(), b = s.end - AY(), id = `wm${n}-tz-${s.index}`;
        o += `<path d="${sector(r0, r1, a, b)}" class="tz-sec ${s.index % 2 ? "alt" : ""}" data-tsign="${s.index}"${tint(hueOf(s.index))}/>`;
        const [gx, gy] = pt((r0 + r1) / 2, s.start + 3.2 - AY());
        o += `<text x="${f(gx)}" y="${f(gy)}" class="tz-glyph" text-anchor="middle" dominant-baseline="central">${s.glyph}</text>`;
        o += card("MN" + String(s.index + 1).padStart(2, "0"), (r0 + r1) / 2, s.start + 7.6 - AY(), 17, "trump-glyph", ` data-trump="n${s.index}"`);
        arcDefs.push(`<path id="${id}" d="${textArc((r0 + r1) / 2 - 3, a + 10.4, b - 1)}"/>`);
        o += `<text class="tz-name"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${s.name.toUpperCase()}${dec ? " · " + dec[s.index * 3].nordic.trump.replace(/^The /, "").toUpperCase() : ""}</textPath></text>`;
      }
      for (const s of D.SIGNS) o += `<path d="${radial(r0, r1, s.start - AY())}" class="tz-div-s"/>`;
      /* the equinox: 0° tropical Aries, where the receiving ring begins */
      const [ex, ey] = pt(ring("tropical")[1] + 44, 4 - AY());   /* set a little east of the line, clear of the Empress at 27° Pisces */
      o += `<path d="${radial(ring("nordic")[0] - 4, r1 + 22, -AY())}" class="eq"/><text x="${f(ex)}" y="${f(ey)}" class="eq-lab" text-anchor="middle" dominant-baseline="central">EQUINOX</text>`;
      return o;
    }
    function drawRim() {
      const r = ring("tropical")[1] + 6, ex = (D.TRUMP_EXALT || []).map(x => norm(x.trop - AY()));
      let o = `<circle r="${r}" class="rim"/><circle r="${r + 16}" class="rim"/>`;
      for (let d = 0; d < 360; d++) {
        const len = d % 10 === 0 ? 11 : d % 5 === 0 ? 7 : 3.5;
        o += `<path d="${radial(r, r + len, d)}" class="${d % 10 === 0 ? "rim-t10" : "rim-t"}"/>`;
      }
      for (let d = 0; d < 360; d += 30) { if (ex.some(a => Math.abs(((a - d + 540) % 360) - 180) < 7)) continue;
        const [x, y] = pt(r + 30, d); o += `<text x="${f(x)}" y="${f(y)}" class="rim-lab" text-anchor="middle" dominant-baseline="central">${d}°</text>`; }
      /* the Nordic planetary trumps, outside the rim, each at its planet's exaltation on the tropical ring */
      (D.TRUMP_EXALT || []).forEach((x, i) => { const a = norm(x.trop - AY());
        o += `<path d="${radial(ring("tropical")[1], r + 24, a)}" class="ex-tick"/>` + card("MX" + String(i + 1).padStart(2, "0"), r + 38, a, 17, "trump-glyph ex-glyph", ` data-exalt="${x.planet}"`); });
      return o;
    }
    /* your planets, inside the field: a tick to the exact degree at the zodiac's edge, the glyph stepped inward when two crowd */
    function drawPlanets() {
      if (!planets.length) return "";
      const R = ring("field")[1], placed = [];
      let o = "";
      for (const p of [...planets].sort((a, b) => a.lon - b.lon)) {
        let r = R - 26;
        while (placed.some(x => x.r === r && Math.abs(((p.lon - x.lon + 540) % 360) - 180) < 8.5)) r -= 25;
        placed.push({ r, lon: p.lon });
        const [x, y] = pt(r, p.lon);
        o += `<path d="${radial(r + 11, R, p.lon)}" class="pl-tick"/>
          <g class="pl" data-st="${p.st}" tabindex="-1"><circle cx="${f(x)}" cy="${f(y)}" r="12" class="pl-disc"/>
          <text x="${f(x)}" y="${f(y)}" class="pl-glyph${p.glyph.length > 1 && !/[^\x00-\x7f]/.test(p.glyph) ? " pl-ab" : ""}" text-anchor="middle" dominant-baseline="central">${p.glyph}</text>
          <title>${esc(p.name)} · ${inSign(p.lon)} · station ${stationAt(p.lon).code.slice(1)}</title></g>`;
      }
      return o;
    }
    function drawHit() {
      const r0 = ring("zodiac")[0], r1 = ring("tropical")[1];
      return S.map(s => `<path d="${sector(r0, r1, s.zodiacStart, s.zodiacEnd)}" class="hit" data-st="${s.id}"><title>${s.code} · ${s.nakshatra} ${s.pada} · ${inSign(s.zodiacStart)}${voidOf(s) ? " · Asura void: " + esc(voidOf(s)) : ""}</title></path>`).join("");
    }
    function drawSelection() {
      const s = state.sel; if (!s) return "";
      const r0 = ring("zodiac")[0], r1 = ring("tropical")[1];
      /* the station's code stands outside the rim; it steps aside from a planetary trump seated there */
      let la = mid(s);
      for (const x of D.TRUMP_EXALT || []) { const e = norm(x.trop - AY()), d = ((la - e + 540) % 360) - 180;
        if (Math.abs(d) < 5.5) la = e + (d >= 0 ? 5.5 : -5.5); }
      const [lx, ly] = pt(r1 + 60, la);
      return `<path d="${sector(r0, r1, s.zodiacStart, s.zodiacEnd)}" class="sel-wedge"/>
        <path d="${radial(14, r0, mid(s))}" class="sel-ray"/>
        <text x="${f(lx)}" y="${f(ly)}" class="sel-code" text-anchor="middle" dominant-baseline="central">${s.code}</text>`;
    }
    /* correspondence lines: drawn from whatever a relation generator returns */
    function drawFocus() {
      const s = state.sel; if (!s || !state.focus) return "";
      const rel = D.RELATIONS[state.relation], to = rel.of(s, S), r = ring("padas")[0] + 30;
      const [x0, y0] = pt(r, mid(s));
      return to.map(t => { const [x1, y1] = pt(r, mid(t)), k = .28;
        return `<path d="M${f(x0)} ${f(y0)}Q${f((x0 + x1) * k)} ${f((y0 + y1) * k)} ${f(x1)} ${f(y1)}" class="rel"/><circle cx="${f(x1)}" cy="${f(y1)}" r="3.4" class="rel-node"/>`;
      }).join("");
    }
    function render() {
      const arcDefs = [];
      const body = { field: drawField(), zodiac: drawZodiac(arcDefs), nakshatras: drawNakshatras(arcDefs), padas: drawPadas(), tarot: drawTarot(),
        nordic: drawNordic(arcDefs), tropical: drawTropical(arcDefs) };
      svg.innerHTML = `<defs>${G.defs()}${arcDefs.join("")}</defs><g class="rim-g">${drawRim()}</g>
        ${["field", "zodiac", "nakshatras", "padas", "tarot", "nordic", "tropical"].map(id => `<g class="ring ring-${id}" data-layer="${id}"${state.layers[id] === false ? " hidden" : ""}>${body[id]}</g>`).join("")}
        <g class="focus-g">${drawFocus()}</g><g class="sel-g">${drawSelection()}</g><g class="hit-g">${drawHit()}</g><g class="pl-g">${drawPlanets()}</g>`;
      svg.classList.toggle("focusing", !!(state.focus && state.sel));
      paintMarks();
    }
    /* cheap updates that don't redraw geometry */
    function paintMarks() {
      const sel = state.sel, rel = sel && state.focus ? new Set(D.RELATIONS[state.relation].of(sel, S).map(t => t.id)) : null;
      svg.querySelectorAll("[data-st]").forEach(el => {
        const id = +el.dataset.st;
        el.classList.toggle("is-sel", !!sel && id === sel.id);
        el.classList.toggle("is-hov", !!state.hov && id === state.hov.id);
        el.classList.toggle("is-rel", !!rel && rel.has(id));
      });
      svg.querySelectorAll("[data-nak]").forEach(el => {
        const k = +el.dataset.nak;
        el.classList.toggle("is-hov", !!state.hov && k === state.hov.nakshatraIndex);
        el.classList.toggle("is-sel", !!sel && k === sel.nakshatraIndex);
      });
      svg.querySelectorAll("[data-sign]").forEach(el => el.classList.toggle("is-sel", !!sel && +el.dataset.sign === sel.signIndex));
      /* the tropical cells the selected station lands in */
      const ay = AY();
      const hit = (lo, w) => { if (!sel) return false; const s0 = norm(sel.zodiacStart + ay), s1 = s0 + D.PADA;
        return [lo, lo + 360, lo - 360].some(x => s0 < x + w && s1 > x); };
      svg.querySelectorAll("[data-dec]").forEach(el => el.classList.toggle("is-sel", hit(+el.dataset.dec * 10, 10)));
      svg.querySelectorAll("[data-tsign]").forEach(el => el.classList.toggle("is-sel", hit(+el.dataset.tsign * 30, 30)));
    }

    /* ---------- the station record ---------- */
    function mansionText(s) {
      const m = s.mansion; if (!m) return "";
      return `<section class="rec-sec rec-mansion">
          <h3>The mansion</h3>
          <p class="m-name">${esc(s.nakshatra)} <small>· ${esc(m.symbol)}</small></p>
          <p class="m-line">${esc(m.line)}</p>
          <p class="m-shakti"><i>${esc(m.shakti)}</i>, ${esc(m.power)}. Above, ${esc(m.above)}; below, ${esc(m.below)}; together, ${esc(m.result)}.</p>
          <p class="m-core">${esc(m.core)}</p>
          <p class="m-q">${esc(m.question)}</p>
          <p class="m-syl">This pada's sound: <b>${esc(s.syllable)}</b> <small>· the four padas of ${esc(s.nakshatra)} sound ${m.syllables.map(esc).join(" · ")}</small></p>
        </section>`;
    }
    /* the planetary trumps whose exaltation degree falls in this station, on the tropical ring */
    const exaltIn = (s, ay) => (D.TRUMP_EXALT || []).map((x, i) => ({ ...x, code: "MX" + String(i + 1).padStart(2, "0") }))
      .filter(x => { const lo = norm(s.zodiacStart + ay), d = norm(x.trop - lo); return d < s.zodiacEnd - s.zodiacStart; });
    /* the two decks, one per rotor: Buddhist on the sidereal ring (emanating), Nordic on the true tropical ring (receiving) */
    function cardsText(s) {
      const t = s.tarot, c = s.cards, ay = D.FRAME.ayanamsa;
      /* small cards, their size written on them so they never stretch to the column; a pair side by side, the words beside it */
      const CW = 28, CH = Math.round(CW * G.size.h / G.size.w);
      const glyph = (code, label) => G.get(code) ? `<svg class="c-glyph" width="${CW}" height="${CH}" viewBox="0 0 ${G.size.w} ${G.size.h}" role="img" aria-label="${esc(label)}"><use href="#tarot-${code}"/></svg>` : "";
      const row = (pair, words) => `<div class="c-row"><span class="c-pair">${pair}</span><div class="c-words">${words}</div></div>`;
      const deck = (name, ring, where, cards) => `<li><p class="c-deck">${name} · ${ring}</p>
        ${cards.map(x => row(`${glyph(x.glyph, x.minor)}${glyph(x.major, x.trump)}`,
          `<p class="c-name">${esc(x.minor)} <small>· ${esc(x.trump)}</small></p>
          <p class="c-det">${esc(x.sign)}${x.decan ? `, ${x.decan} decan` : ""}, ruled by ${esc(x.ruler)}</p>`)).join("")}<p class="c-det">${where}</p></li>`;
      return `<section class="rec-sec">
          <h3>Cards</h3>
          ${c ? `<ul class="cands">
              ${deck("Buddhist deck", "sidereal ring", `where it comes from: ${inSign(s.zodiacStart)} – ${inSign(s.zodiacEnd)}`, [{ ...c.buddhist, glyph: t.glyph }])}
              ${deck("Nordic deck", "tropical ring", `where it lands: ${inSign(s.zodiacStart + ay.degrees)} – ${inSign(s.zodiacEnd + ay.degrees)} (${ay.epoch})${c.nordic.length > 1 ? "; the pada crosses a decan line, so both cards" : ""}`, c.nordic)}
            </ul>
          ${c.gate ? `<div class="gate-card"><p class="c-deck">At the gate · 0° sidereal Aries</p>${row(glyph("MB00", c.gate.buddhist), `<p class="c-name">${esc(c.gate.buddhist)}</p>
            <p class="c-det">${esc(c.gate.reading)}. ${esc(c.gate.note)}</p>`)}</div>` : ""}
          ${exaltIn(s, ay.degrees).map(x => `<div class="gate-card"><p class="c-deck">Exaltation · tropical ring</p>${row(glyph(x.code, x.nordic),
            `<p class="c-name">${esc(x.nordic)} <small>· ${esc(x.planet)} exalted, ${inSign(x.trop)}</small></p>`)}</div>`).join("")}
          ${voidOf(s) ? `<dl class="kv"><dt>Asura void</dt><dd>${esc(voidOf(s))}</dd></dl>` : ""}`
          : `<dl class="kv"><dt>Card</dt><dd>${t.name ? esc(t.name) : NA}</dd></dl>`}
        </section>`;
    }
    function record(s) {
      if (!s) return `<div class="rec-empty"><p class="eyebrow">No station selected</p>
        <p>Read the wheel first. The rings are a complete reference chart and are meant to be studied as they stand.</p>
        <p>Select any of the 108 stations to open its record: tap a wedge, use the station search, or step with the arrows.</p></div>`;
      const nak = D.NAKSHATRAS[s.nakshatraIndex], sign = D.SIGNS[s.signIndex], ay = D.FRAME.ayanamsa;
      const trop = d => inSign(d + ay.degrees);
      const corr = Object.entries(s.correspondences), mine = byStation[s.id] || [];
      return `
        <header class="rec-head">
          <p class="eyebrow">Station</p>
          <h2 class="rec-code">${s.code.slice(1)}<span> of 108</span></h2>
          <p class="rec-sub">${esc(nak.name)}, pada ${s.pada} · ${inSign(s.zodiacStart)} – ${inSign(s.zodiacEnd)}</p>
        </header>
        ${mine.length ? `<section class="rec-sec rec-mine"><h3>In your chart</h3>
          <ul class="mine">${mine.map(p => `<li><span class="pl-g1">${p.glyph}</span> Your ${esc(p.name)} stands here, at ${inSign(p.lon)}</li>`).join("")}</ul></section>` : ""}
        ${mansionText(s)}
        <section class="rec-sec">
          <h3>Position</h3>
          <dl class="kv">
            <dt>Nakshatra</dt><dd>${esc(nak.name)} <small>· ${nak.number} of 27</small></dd>
            <dt>Pada</dt><dd>${s.pada} of 4</dd>
            <dt>Absolute degrees</dt><dd class="num">${dms(s.zodiacStart)} – ${dms(s.zodiacEnd)} <small>sidereal</small></dd>
            <dt>Zodiac sign</dt><dd>${sign.glyph} ${sign.name} <small>· ${dms(s.zodiacStart % 30)} – ${dms((s.zodiacEnd - 1e-9) % 30 + 1e-9)}</small></dd>
            <dt>Nakshatra ruler</dt><dd>${esc(s.nakshatraLord)}</dd>
            <dt>Nakshatra deity</dt><dd>${esc(s.deity)}${s.deityAlt ? ` <small>· also given as ${esc(s.deityAlt)}</small>` : ""}</dd>
            <dt>Navamsa</dt><dd>${s.navamsa}${s.vargottama ? ` <small class="mark">· vargottama</small>` : ""}</dd>
            <dt>Tropical projection</dt><dd class="num">${trop(s.zodiacStart)} – ${trop(s.zodiacEnd)} <small>· ${ay.name} ≈ ${dms(ay.degrees)}, ${ay.epoch}</small></dd>
          </dl>
        </section>
        ${cardsText(s)}
        <section class="rec-sec">
          <h3>Correspondences</h3>
          ${corr.length ? corr.map(([sys, rows], i) => `<details${i < 2 ? " open" : ""}><summary>${esc(sys)}</summary>
            <dl class="kv corr">${rows.map(r => `<dt>${esc(r.label)}</dt><dd>${esc(r.value)}</dd>`).join("")}</dl></details>`).join("")
            : `<p class="na-block">No correspondences have been mapped to this station yet.</p>`}
        </section>
        ${s.notes ? `<section class="rec-sec"><h3>Notes</h3>${s.notes.split(/\n\n+/).map(p => `<p class="note">${esc(p)}</p>`).join("")}
          ${s.source ? `<p class="src">Source: ${esc(s.source)}</p>` : ""}</section>` : ""}`;
    }

    /* ============ 3. INTERACTION ============ */
    function select(id, o = {}) {
      state.sel = id ? S[(id - 1 + 108) % 108] : null;
      if (o.align && state.sel) { state.rot = (360 - mid(state.sel)) % 360; els.rot.value = Math.round(state.rot); }
      render();
      panel.innerHTML = record(state.sel);
      panel.classList.toggle("has-sel", !!state.sel);
      els.nak.value = state.sel ? state.sel.nakshatraIndex : "";
      els.padas.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", !!state.sel && +b.dataset.p === state.sel.pada));
      if (useHash) try { history.replaceState(null, "", state.sel ? "#" + state.sel.code.toLowerCase() : location.pathname + location.search); } catch (_) {}
      if (opts.onSelect) opts.onSelect(state.sel);
      if (o.scroll && state.sel && matchMedia("(max-width: 899px)").matches) panel.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    const step = d => select(state.sel ? state.sel.id + d : (d > 0 ? 1 : 108));

    /* controls built from the data */
    els.nak.innerHTML = `<option value="">Nakshatra…</option>` + D.NAKSHATRAS.map(k => `<option value="${k.index}">${String(k.number).padStart(2, "0")} · ${k.name}</option>`).join("");
    els.list.innerHTML = S.map(s => `<option value="${s.code} · ${s.nakshatra} ${s.pada} · ${inSign(s.zodiacStart)}"></option>`).join("");
    els.layers.innerHTML = D.LAYERS.filter(l => l.toggle).map(l => `<label class="wm-chk"><input type="checkbox" data-layer="${l.id}" checked> ${l.label}</label>`).join("");
    els.relation.innerHTML = Object.entries(D.RELATIONS).map(([k, r]) => `<option value="${k}">${r.label}</option>`).join("");

    /* pointer on the dial: the whole radial wedge of a station is its target, so it stays tappable on a phone */
    svg.addEventListener("pointerover", e => { const h = e.target.closest(".hit, .pl"); if (!h) return; state.hov = S[+h.dataset.st - 1]; paintMarks(); });
    svg.addEventListener("pointerleave", () => { state.hov = null; paintMarks(); });
    svg.addEventListener("click", e => { const h = e.target.closest(".hit, .pl"); if (h) select(+h.dataset.st, { scroll: true }); });
    svg.addEventListener("keydown", e => {
      if (e.key === "ArrowRight" || e.key === "ArrowDown"){ e.preventDefault(); step(1); }
      if (e.key === "ArrowLeft" || e.key === "ArrowUp"){ e.preventDefault(); step(-1); }
      if (e.key === "Escape") select(null);
    });
    q("prev").addEventListener("click", () => step(-1));
    q("next").addEventListener("click", () => step(1));
    els.nak.addEventListener("change", () => { if (els.nak.value !== "") select(+els.nak.value * 4 + 1); });
    els.padas.addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (!b) return;
      select((state.sel ? state.sel.nakshatraIndex : 0) * 4 + +b.dataset.p); });
    els.search.addEventListener("change", () => {
      const v = els.search.value.trim(), m = v.match(/^s?0*(\d{1,3})\b/i);
      if (!v) return;
      let id = m ? +m[1] : null;
      if (!id){ const k = v.toLowerCase(); const hit = S.find(s => `${s.nakshatra} ${s.pada}`.toLowerCase() === k) || S.find(s => s.nakshatra.toLowerCase().startsWith(k) || s.sign.toLowerCase().startsWith(k)); id = hit && hit.id; }
      if (id >= 1 && id <= 108) select(id, { scroll: true });
      els.search.value = "";
    });
    els.layers.addEventListener("change", e => { const c = e.target.closest("[data-layer]"); if (!c) return; state.layers[c.dataset.layer] = c.checked;
      const g = svg.querySelector(`.ring-${c.dataset.layer}`); if (g) g.hidden = !c.checked; });
    els.rot.addEventListener("input", () => { state.rot = +els.rot.value; render(); });
    q("align").addEventListener("click", () => { if (state.sel) select(state.sel.id, { align: true }); });
    els.focus.addEventListener("change", () => { state.focus = els.focus.checked; els.relation.disabled = !state.focus; render(); });
    els.relation.addEventListener("change", () => { state.relation = els.relation.value; els.relNote.textContent = D.RELATIONS[state.relation].note; render(); });
    els.relNote.textContent = D.RELATIONS[state.relation].note;
    /* the year: turns the tropical ring against the sidereal one, and re-reads every station's tropical side */
    const yearNote = () => { const a = D.FRAME.ayanamsa, y = a.epoch;
      q("yearOut").textContent = y < 1 ? `${1 - y} BCE` : y;
      q("yearNote").textContent = `In ${y < 1 ? (1 - y) + " BCE" : y} the rings stand ${dms(Math.abs(a.degrees))} apart${a.degrees < 0 ? ", the tropical ring behind the sidereal" : ""}. `
        + (Math.abs(a.degrees) < .5 ? "This is about when the two zodiacs coincided." : `The equinox stands at ${inSign(-a.degrees)} sidereal.`); };
    const setYear = y => { D.setYear(y); q("year").value = y; yearNote(); select(state.sel ? state.sel.id : null); };
    q("year").addEventListener("input", () => setYear(+q("year").value));
    q("now").addEventListener("click", () => setYear(D.EPOCH));
    yearNote();
    q("reset").addEventListener("click", () => {
      D.setYear(D.EPOCH); q("year").value = D.EPOCH; yearNote();
      state.rot = 0; els.rot.value = 0; state.focus = false; els.focus.checked = false; els.relation.disabled = true;
      D.LAYERS.forEach(l => { state.layers[l.id] = true; }); els.layers.querySelectorAll("input").forEach(c => { c.checked = true; });
      select(null);
    });
    els.relation.disabled = true;

    /* open on the station asked for, one named in the address (#s037), your Moon's, or the first gate */
    const m = useHash && location.hash.match(/^#s(\d{3})$/), moon = planets.find(p => p.name === "Moon");
    select(opts.start || (m ? +m[1] : moon ? moon.st : 1));

    const api = { select, state, refresh: () => select(state.sel ? state.sel.id : null), geometry: { pt, sector, radial, textArc } };
    instances.push(api);
    return api;
  }

  root.WyrdMandala = { mount, stationAt, refreshGlyphs: () => instances.forEach(i => i.refresh()) };
})(window);
