/* ============================================================
   WYRD GLYPHS
   The vector glyph registry for the tarot ring: 108 SVG <symbol>s,
   T001 … T108, each drawn on a 24 × 36 card field.

   Until a station's artwork exists, its symbol is a numbered
   placeholder. To supply real artwork, register it:

     WyrdGlyphs.define("T001", '<path d="…"/>');      // inner SVG markup, 24 × 36 field

   or add it to CUSTOM below. The renderer only ever writes
   <use href="#tarot-T001">, so the geometry never changes.
   ============================================================ */
(function (root) {
  "use strict";
  const W = 24, H = 36;
  const CUSTOM = {
    /* "T001": '<path d="…"/>', */
  };
  const pad3 = n => String(n).padStart(3, "0");

  /* the placeholder: a card field, a hairline inner frame, the station number set vertically */
  function placeholder(code) {
    const n = code.slice(1);
    return `<rect x=".75" y=".75" width="${W - 1.5}" height="${H - 1.5}" rx="1.6" class="g-card"/>
      <rect x="3" y="3" width="${W - 6}" height="${H - 6}" rx=".6" class="g-frame"/>
      <text x="${W / 2}" y="${H / 2}" class="g-num" text-anchor="middle" dominant-baseline="central">${n}</text>`;
  }

  const registry = {};
  for (let i = 1; i <= 108; i++) { const c = "T" + pad3(i); registry[c] = { code: c, svg: CUSTOM[c] || placeholder(c), placeholder: !CUSTOM[c] }; }

  root.WyrdGlyphs = {
    size: { w: W, h: H },
    get: code => registry[code] || null,
    define(code, svg) { registry[code] = { code, svg, placeholder: false }; if (root.WyrdMandala) root.WyrdMandala.refreshGlyphs(); },
    /* every glyph as <symbol>s, for one <defs> block */
    defs: () => Object.values(registry).map(g => `<symbol id="tarot-${g.code}" viewBox="0 0 ${W} ${H}">${g.svg}</symbol>`).join(""),
  };
})(window);
