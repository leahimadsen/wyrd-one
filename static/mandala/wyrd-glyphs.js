/* ============================================================
   WYRD GLYPHS
   The vector glyph registry for the tarot ring: 108 SVG <symbol>s,
   T001 … T108, each drawn on a 24 × 36 card field.

   Until The Völva's artwork exists, each station carries a simple
   drawn glyph of its Buddhist (sidereal) card: the decan's number at
   the head, the suit's emblem in the middle (Double Vajra, Jewel,
   Vajra, Lotus), and the pada as dots at the foot. Station 001 also
   carries the gate's ring, for The Fool.

   To supply real artwork, register it:

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
  const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"];

  /* the four suit emblems, centred on (12, 18) */
  const EMBLEM = {
    /* Double Vajra (fire): the crossed thunderbolt */
    "Double Vajras": `<path d="M12 12.5V23.5M6.5 18H17.5" class="g-em"/><circle cx="12" cy="18" r="1.6" class="g-em"/>
      <circle cx="12" cy="11.6" r="1" class="g-em"/><circle cx="12" cy="24.4" r="1" class="g-em"/><circle cx="5.6" cy="18" r="1" class="g-em"/><circle cx="18.4" cy="18" r="1" class="g-em"/>`,
    /* Jewel (earth): the faceted stone */
    "Jewels": `<path d="M12 12L17 17.2L12 24.5L7 17.2Z" class="g-em"/><path d="M7 17.2H17M9.6 17.2L12 12L14.4 17.2L12 24.5L9.6 17.2" class="g-em g-thin"/>`,
    /* Vajra (air): the single thunderbolt */
    "Vajras": `<path d="M12 11V25" class="g-em"/><path d="M12 11.2C9.6 12.6 9.6 15 12 16.2C14.4 15 14.4 12.6 12 11.2ZM12 24.8C9.6 23.4 9.6 21 12 19.8C14.4 21 14.4 23.4 12 24.8Z" class="g-em"/><circle cx="12" cy="18" r="1.3" class="g-em"/>`,
    /* Lotus (water): three petals over the water line */
    "Lotuses": `<path d="M12 12.5C9.8 15.5 9.8 19.6 12 22C14.2 19.6 14.2 15.5 12 12.5Z" class="g-em"/><path d="M11.4 22C8 21.6 6.4 18.6 6.6 16.2C9 16.6 10.8 18.6 11.4 22ZM12.6 22C16 21.6 17.6 18.6 17.4 16.2C15 16.6 13.2 18.6 12.6 22Z" class="g-em"/><path d="M6.5 24.2H17.5" class="g-em g-thin"/>`,
  };
  function drawn(st) {
    const c = st && st.cards && st.cards.buddhist, m = c && c.minor.match(/^(\d+) of (.+)$/);
    if (!m) return null;
    const dots = Array.from({ length: st.pada }, (_, k) => `<circle cx="${12 + (k - (st.pada - 1) / 2) * 2.8}" cy="30.6" r=".8" class="g-dot"/>`).join("");
    return `<rect x=".75" y=".75" width="${W - 1.5}" height="${H - 1.5}" rx="1.6" class="g-card"/>
      <rect x="3" y="3" width="${W - 6}" height="${H - 6}" rx=".6" class="g-frame"/>
      <text x="12" y="6.9" class="g-rom" text-anchor="middle" dominant-baseline="central">${ROMAN[+m[1]]}</text>
      ${st.cards.gate ? `<circle cx="12" cy="18" r="8.2" class="g-em g-thin"/>` : ""}${EMBLEM[m[2]] || ""}${dots}`;
  }
  /* the fallback when no card data is loaded: a numbered field */
  const numbered = code => `<rect x=".75" y=".75" width="${W - 1.5}" height="${H - 1.5}" rx="1.6" class="g-card"/>
      <rect x="3" y="3" width="${W - 6}" height="${H - 6}" rx=".6" class="g-frame"/>
      <text x="${W / 2}" y="${H / 2}" class="g-num" text-anchor="middle" dominant-baseline="central">${code.slice(1)}</text>`;

  const registry = {};
  const S = root.WYRD ? root.WYRD.stations : [];
  for (let i = 1; i <= 108; i++) {
    const c = "T" + pad3(i);
    registry[c] = CUSTOM[c] ? { code: c, svg: CUSTOM[c], placeholder: false } : { code: c, svg: drawn(S[i - 1]) || numbered(c), placeholder: true };
  }

  root.WyrdGlyphs = {
    size: { w: W, h: H },
    get: code => registry[code] || null,
    define(code, svg) { registry[code] = { code, svg, placeholder: false }; if (root.WyrdMandala) root.WyrdMandala.refreshGlyphs(); },
    /* every glyph as <symbol>s, for one <defs> block */
    defs: () => Object.values(registry).map(g => `<symbol id="tarot-${g.code}" viewBox="0 0 ${W} ${H}">${g.svg}</symbol>`).join(""),
  };
})(window);
