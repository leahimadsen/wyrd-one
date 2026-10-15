/* ============================================================
   WYRD GLYPHS
   The vector glyph registry for the cards: SVG <symbol>s, each drawn
   on a 24 × 36 card field.
     T001 … T108   the Buddhist deck, one per station (sidereal ring)
     N01 … N36     the Nordic deck's minor cards, one per decan (tropical ring)
     MB00          The Fool, at the gate (0° sidereal Aries)
     MB01 … MB12   the Buddhist trumps, by sidereal sign
     MN01 … MN12   the Nordic trumps, by tropical sign
     MX01 … MX07   the Nordic planetary trumps, at their planets' exaltations

   Until The Völva's artwork exists, each station carries a simple
   drawn glyph of its Buddhist (sidereal) card: the decan's number at
   the head, the suit's emblem in the middle (Double Vajra, Jewel,
   Vajra, Lotus), and the pada as dots at the foot. Station 001 also
   carries the gate's ring, for The Fool.

   The Nordic cards have clipped corners; the trumps a double frame,
   their sign at the foot (and for the Nordic deck its numeral at the
   head). All are simple drawn placeholders until the artwork exists.

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

  /* ---- the Nordic deck's minor cards: the decan's number at the head, the suit's emblem, the decan as dots ---- */
  const NORDIC_EMBLEM = {
    /* the stave, notched */
    Wands: `<path d="M12 11.4V24.6" class="g-em"/><path d="M12 14.4L9.4 12.6M12 18L14.6 16.2M12 21.6L9.4 19.8" class="g-em g-thin"/>`,
    /* the round shield, its boss and planks */
    Shields: `<circle cx="12" cy="18" r="5.6" class="g-em"/><circle cx="12" cy="18" r="1.5" class="g-em"/><path d="M9.5 13.1V22.9M14.5 13.1V22.9" class="g-em g-thin"/>`,
    /* the sword */
    Swords: `<path d="M12 11V22.2" class="g-em"/><path d="M8.6 22.2H15.4M12 22.2V25" class="g-em"/><path d="M12 12.6V20.6" class="g-em g-thin"/>`,
    /* the cup */
    Cups: `<path d="M8.4 12.4H15.6C15.6 16.6 13.6 18.4 12 18.4C10.4 18.4 8.4 16.6 8.4 12.4Z" class="g-em"/><path d="M12 18.4V22.8M9.4 23.4H14.6" class="g-em"/>`,
  };
  const CLIPPED = `<path d="M3.4 .75H20.6L23.25 3.4V32.6L20.6 35.25H3.4L.75 32.6V3.4Z" class="g-card"/><path d="M4.4 3H19.6L21 4.4V31.6L19.6 33H4.4L3 31.6V4.4Z" class="g-frame"/>`;
  function nordicCard(d, k) {
    const m = d && d.nordic && d.nordic.minor.match(/^(\d+) of (.+)$/); if (!m) return null;
    const n = k % 3 + 1, dots = Array.from({ length: n }, (_, j) => `<circle cx="${12 + (j - (n - 1) / 2) * 2.8}" cy="30.6" r=".8" class="g-dot"/>`).join("");
    return `${CLIPPED}<text x="12" y="6.9" class="g-rom" text-anchor="middle" dominant-baseline="central">${ROMAN[+m[1]]}</text>${NORDIC_EMBLEM[m[2]] || ""}${dots}`;
  }

  /* ---- the trumps: a double frame, an emblem for the card, the sign at the foot ---- */
  const TRUMP_EMBLEM = {
    /* the Nordic row (Waite's names and numbers) */
    "The Emperor": `<path d="M7 22V15.5L9.6 18L12 13.5L14.4 18L17 15.5V22Z" class="g-em"/><path d="M7 24H17" class="g-em g-thin"/>`,
    "The Hierophant": `<path d="M12 11.5V25M9.2 14.2H14.8M8.2 17.4H15.8M9.2 20.6H14.8" class="g-em"/>`,
    "The Lovers": `<circle cx="10" cy="18" r="3.4" class="g-em"/><circle cx="14" cy="18" r="3.4" class="g-em"/>`,
    "The Chariot": `<circle cx="12" cy="18" r="5.4" class="g-em"/><circle cx="12" cy="18" r="1.2" class="g-em"/><path d="M12 12.6V23.4M6.6 18H17.4M8.2 14.2L15.8 21.8M15.8 14.2L8.2 21.8" class="g-em g-thin"/>`,
    "Strength": `<path d="M12 18C10.2 14.6 6.4 14.6 6.4 18C6.4 21.4 10.2 21.4 12 18C13.8 14.6 17.6 14.6 17.6 18C17.6 21.4 13.8 21.4 12 18Z" class="g-em"/>`,
    "The Hermit": `<path d="M9.8 15H14.2L15 22H9Z" class="g-em"/><path d="M10.6 15V13.6H13.4V15M12 13.6V12" class="g-em g-thin"/><path d="M12 16.6L12.9 18.5L12 20.4L11.1 18.5Z" class="g-em g-thin"/>`,
    "Justice": `<path d="M12 12V24.5M9.5 24.5H14.5M6.8 15.2H17.2" class="g-em"/><path d="M6.8 15.2L5.4 19.4H8.2ZM17.2 15.2L15.8 19.4H18.6Z" class="g-em g-thin"/>`,
    "Death": `<path d="M8.4 25L15.2 12" class="g-em"/><path d="M15.2 12C12.4 11.2 9.4 12.2 7.4 14.8C10 14 12.6 14 14.4 13.6" class="g-em"/>`,
    "Temperance": `<path d="M6.8 19H10.2L9.6 22.6H7.4ZM13.8 15H17.2L16.6 18.6H14.4Z" class="g-em"/><path d="M10 19.2C11.4 17.4 12.4 16.4 14 16.6" class="g-em g-thin"/>`,
    "The Devil": `<circle cx="12" cy="18.6" r="3.6" class="g-em"/><path d="M9.6 15.8L7.8 11.8L10.4 14.6M14.4 15.8L16.2 11.8L13.6 14.6" class="g-em"/><path d="M8.5 24.4H15.5" class="g-em g-thin"/>`,
    "The Star": `<path d="M12 11.6V24.4M5.6 18H18.4" class="g-em"/><path d="M7.5 13.5L16.5 22.5M16.5 13.5L7.5 22.5" class="g-em g-thin"/><circle cx="12" cy="18" r="1.4" class="g-em"/>`,
    "The Moon": `<path d="M14.6 12.4A6 6 0 1 0 14.6 23.6A4.6 4.6 0 1 1 14.6 12.4Z" class="g-em"/>`,
    /* the Buddhist row */
    "The King": `<path d="M6.4 16.6C8 12.6 16 12.6 17.6 16.6Z" class="g-em"/><path d="M12 16.6V24.6M12 12.4V11.4" class="g-em"/><path d="M7.6 16.6V18M10 16.6V17.8M14 16.6V17.8M16.4 16.6V18" class="g-em g-thin"/>`,
    "The Buddha": `<path d="M7.4 24.4H16.6M8.6 24.4C8.6 19.6 15.4 19.6 15.4 24.4" class="g-em"/><path d="M10.4 19.2H13.6M12 19V13.4M10.8 15H13.2M11.2 13.4H12.8" class="g-em g-thin"/><circle cx="12" cy="12.2" r=".8" class="g-dot"/>`,
    "The Two Paths": `<path d="M12 25V19.4M12 19.4L7.6 12.4M12 19.4L16.4 12.4" class="g-em"/><circle cx="7.6" cy="12.4" r="1" class="g-em"/><circle cx="16.4" cy="12.4" r="1" class="g-em"/>`,
    "The Chariot · Buddhist": `<circle cx="12" cy="18" r="5.4" class="g-em"/><circle cx="12" cy="18" r="1.4" class="g-em"/><path d="M12 12.6V23.4M6.6 18H17.4M8.2 14.2L15.8 21.8M15.8 14.2L8.2 21.8" class="g-em g-thin"/><circle cx="12" cy="11.6" r=".6" class="g-dot"/><circle cx="12" cy="24.4" r=".6" class="g-dot"/><circle cx="5.6" cy="18" r=".6" class="g-dot"/><circle cx="18.4" cy="18" r=".6" class="g-dot"/>`,
    "The Lion's Roar": `<circle cx="12" cy="18" r="3" class="g-em"/><path d="M12 12.2V13.8M12 22.2V23.8M6.2 18H7.8M16.2 18H17.8M7.9 13.9L9 15M15 21L16.1 22.1M16.1 13.9L15 15M9 21L7.9 22.1" class="g-em"/>`,
    "The Ascetic": `<path d="M7 18.6H17C17 22 14.8 23.6 12 23.6C9.2 23.6 7 22 7 18.6Z" class="g-em"/><path d="M8.6 18.6C9 16.6 15 16.6 15.4 18.6" class="g-em g-thin"/>`,
    "Karma": `<path d="M9 15H15V21H9Z" class="g-em"/><path d="M12 12.6L17.4 18L12 23.4L6.6 18Z" class="g-em g-thin"/>`,
    "Impermanence": `<path d="M16.4 14.6A5.6 5.6 0 1 0 17.4 19.6" class="g-em"/><circle cx="17.8" cy="16.4" r=".6" class="g-dot"/>`,
    "The Middle Way": `<path d="M8 12V24.4M16 12V24.4" class="g-em g-thin"/><path d="M12 12.6V23.8" class="g-em"/><circle cx="12" cy="18" r="1.3" class="g-em"/>`,
    "Mara": `<path d="M8.6 11.8C13.2 14.6 13.2 21.4 8.6 24.2" class="g-em"/><path d="M8.6 11.8V24.2" class="g-em g-thin"/><path d="M8.6 18H17.4M15.6 16.4L17.4 18L15.6 19.6" class="g-em"/>`,
    "The Tara": `<path d="M12 11.6L12.9 13.9L15.3 14L13.4 15.5L14.1 17.8L12 16.5L9.9 17.8L10.6 15.5L8.7 14L11.1 13.9Z" class="g-em g-thin"/><path d="M12 18.4C10.6 20.2 10.6 22.2 12 23.6C13.4 22.2 13.4 20.2 12 18.4ZM11.4 23.6C9 23.4 7.8 21.6 7.9 20.2C9.6 20.4 10.9 21.8 11.4 23.6ZM12.6 23.6C15 23.4 16.2 21.6 16.1 20.2C14.4 20.4 13.1 21.8 12.6 23.6Z" class="g-em g-thin"/>`,
    "Nirvana": `<path d="M8.4 21H15.6L14.2 24H9.8Z" class="g-em"/><path d="M12 21V19.4" class="g-em g-thin"/><path d="M12 18.6C10.8 17 13.2 15.6 12 13.6C11.2 12.4 12.4 11.8 12.6 11.4" class="g-em g-thin"/>`,
    /* the Nordic deck's planetary trumps (Golden Dawn), seated at their planets' exaltations */
    "The Magician": `<path d="M12 16V25" class="g-em"/><path d="M12 13.2C10.8 11.2 8.4 11.2 8.4 13.2C8.4 15.2 10.8 15.2 12 13.2C13.2 11.2 15.6 11.2 15.6 13.2C15.6 15.2 13.2 15.2 12 13.2Z" class="g-em g-thin"/><path d="M9.6 20H14.4" class="g-em g-thin"/>`,
    "The High Priestess": `<path d="M7.6 12.4V24.4M16.4 12.4V24.4" class="g-em"/><path d="M13.2 15.4A3 3 0 1 0 13.2 20.6A2.3 2.3 0 1 1 13.2 15.4Z" class="g-em g-thin"/>`,
    "The Empress": `<circle cx="12" cy="15.6" r="3.4" class="g-em"/><path d="M12 19V25M9.6 22.4H14.4" class="g-em"/>`,
    "Wheel of Fortune": `<circle cx="12" cy="18" r="5.6" class="g-em"/><circle cx="12" cy="18" r="2.2" class="g-em g-thin"/><path d="M12 12.4V15.8M12 20.2V23.6M6.4 18H9.8M14.2 18H17.6M8 14L10.4 16.4M13.6 19.6L16 22M16 14L13.6 16.4M10.4 19.6L8 22" class="g-em g-thin"/>`,
    "The Tower": `<path d="M9.4 24.6V14.4H14.6V24.6Z" class="g-em"/><path d="M9.4 14.4V12.8H10.7V14.4M11.35 14.4V12.8H12.65V14.4M13.3 14.4V12.8H14.6V14.4" class="g-em g-thin"/><path d="M18.2 10.6L15.6 15H17.2L14.8 19" class="g-em g-thin"/>`,
    "The Sun": `<circle cx="12" cy="18" r="3.2" class="g-em"/><path d="M12 11.6V13.4M12 22.6V24.4M5.6 18H7.4M16.6 18H18.4M7.5 13.5L8.8 14.8M15.2 21.2L16.5 22.5M16.5 13.5L15.2 14.8M8.8 21.2L7.5 22.5" class="g-em"/>`,
    "The World": `<ellipse cx="12" cy="18" rx="4.6" ry="6.4" class="g-em"/><ellipse cx="12" cy="18" rx="2.9" ry="4.7" class="g-em g-thin"/><circle cx="12" cy="18" r=".9" class="g-dot"/>`,
    /* at the gate: the nought, and the going-forth */
    "The Fool": `<path d="M15.8 14.2A5.4 5.4 0 1 0 17.2 19.6" class="g-em"/><path d="M13.6 18H19.2M17.6 16.4L19.2 18L17.6 19.6" class="g-em"/>`,
  };
  const WAITE = { "The Fool": "0", "The Magician": "I", "The High Priestess": "II", "The Empress": "III", "Wheel of Fortune": "X", "The Tower": "XVI", "The Sun": "XIX", "The World": "XXI", "The Emperor": "IV", "The Hierophant": "V", "The Lovers": "VI", "The Chariot": "VII", "Strength": "VIII", "The Hermit": "IX",
    "Justice": "XI", "Death": "XIII", "Temperance": "XIV", "The Devil": "XV", "The Star": "XVII", "The Moon": "XVIII" };
  const SIGN_GLYPH = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"].map(g => g + "︎");
  const DOUBLE = `<rect x=".75" y=".75" width="${W - 1.5}" height="${H - 1.5}" rx="1.6" class="g-card"/><rect x="2.6" y="2.6" width="${W - 5.2}" height="${H - 5.2}" rx=".6" class="g-frame"/><rect x="4" y="4" width="${W - 8}" height="${H - 8}" rx=".4" class="g-frame"/>`;
  function trumpCard(name, sign, nordic, footGlyph) {
    const em = TRUMP_EMBLEM[nordic ? name : (name === "The Chariot" ? "The Chariot · Buddhist" : name)]; if (!em) return null;
    const head = nordic && WAITE[name] ? `<text x="12" y="7.6" class="g-rom" text-anchor="middle" dominant-baseline="central">${WAITE[name]}</text>` : `<circle cx="12" cy="7.4" r=".9" class="g-dot"/>`;
    const foot = footGlyph ? `<text x="12" y="29.4" class="g-sign" text-anchor="middle" dominant-baseline="central">${footGlyph}︎</text>`
      : sign == null ? `<circle cx="12" cy="29.6" r="1.6" class="g-em g-thin"/>` : `<text x="12" y="29.4" class="g-sign" text-anchor="middle" dominant-baseline="central">${SIGN_GLYPH[sign]}</text>`;
    return `${DOUBLE}${head}${em}${foot}`;
  }
  const pad2 = n => String(n).padStart(2, "0");
  const DEC = root.WYRD_MANSIONS && root.WYRD_MANSIONS.cards ? root.WYRD_MANSIONS.cards.decans : [];
  DEC.forEach((d, k) => { const svg = nordicCard(d, k); if (svg) registry["N" + pad2(k + 1)] = { code: "N" + pad2(k + 1), svg, placeholder: true }; });
  for (let i = 0; i < 12; i++) {
    const d = DEC[i * 3]; if (!d) break;
    const b = trumpCard(d.buddhist.trump, i, false), nn = trumpCard(d.nordic.trump, i, true);
    if (b) registry["MB" + pad2(i + 1)] = { code: "MB" + pad2(i + 1), svg: b, placeholder: true, name: d.buddhist.trump };
    if (nn) registry["MN" + pad2(i + 1)] = { code: "MN" + pad2(i + 1), svg: nn, placeholder: true, name: d.nordic.trump };
  }
  /* the Nordic planetary trumps, MX01 … MX07, in the order of the wheel's TRUMP_EXALT table */
  ((root.WYRD && root.WYRD.TRUMP_EXALT) || []).forEach((x, i) => { const svg = trumpCard(x.nordic, null, true, x.glyph);
    if (svg) registry["MX" + pad2(i + 1)] = { code: "MX" + pad2(i + 1), svg, placeholder: true, name: x.nordic }; });
  const gate = root.WYRD_MANSIONS && root.WYRD_MANSIONS.cards && root.WYRD_MANSIONS.cards.gate;
  if (gate) registry.MB00 = { code: "MB00", svg: trumpCard(gate.buddhist, null, false), placeholder: true, name: gate.buddhist };
  for (const c of Object.keys(CUSTOM)) if (registry[c] && !/^T\d/.test(c)) registry[c] = { code: c, svg: CUSTOM[c], placeholder: false };

  /* Each glyph carries its own styling, written onto its shapes. A <use> copy is styled as a copy:
     since Chrome 144 (and always in Firefox), a rule like ".wm .g-card" no longer reaches inside it,
     so glyphs styled from the stylesheet drew as solid black. Colours still come from outside, by
     inheritance: currentColor from the <use>, and the --wm-* colours from the page.
     Artwork added with define() should carry its own fill and stroke the same way. */
  const STYLE = {
    "g-card": "fill:var(--wm-paper);stroke:currentColor;stroke-width:.9",
    "g-frame": "fill:none;stroke:currentColor;stroke-width:.35;opacity:.6",
    "g-em": "fill:none;stroke:currentColor;stroke-width:.9;stroke-linejoin:round;stroke-linecap:round",
    "g-thin": "stroke-width:.5;opacity:.75",
    "g-dot": "fill:currentColor;stroke:none",
    "g-rom": "font-family:var(--wm-serif);font-size:5.4px;fill:currentColor;stroke:none;letter-spacing:.02em",
    "g-num": "font-family:var(--wm-mono);font-size:7.4px;fill:currentColor;stroke:none;writing-mode:vertical-rl;letter-spacing:.02em",
    "g-sign": "font-family:'Segoe UI Symbol','Noto Sans Symbols 2','DejaVu Sans',sans-serif;font-size:6.4px;fill:currentColor;stroke:none",
  };
  const styled = svg => svg.replace(/class="([^"]*)"/g, (m, cls) => {
    const st = cls.split(/\s+/).map(c => STYLE[c]).filter(Boolean).join(";");
    return st ? `${m} style="${st}"` : m;
  });

  root.WyrdGlyphs = {
    size: { w: W, h: H },
    get: code => registry[code] || null,
    define(code, svg) { registry[code] = { code, svg, placeholder: false }; if (root.WyrdMandala) root.WyrdMandala.refreshGlyphs(); },
    /* every glyph as <symbol>s, for one <defs> block */
    defs: () => Object.values(registry).map(g => `<symbol id="tarot-${g.code}" viewBox="0 0 ${W} ${H}">${g.placeholder ? styled(g.svg) : g.svg}</symbol>`).join(""),
    style: STYLE,
  };
})(window);
