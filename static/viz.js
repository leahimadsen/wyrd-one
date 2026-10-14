/* Wyrd visuals — extracted from the Wyrd Console by build.js. */
'use strict';
const norm = d => ((d % 360) + 360) % 360;

/* ---- Human Design gate wheel ----
   Gate 41 opens at 02°00' Aquarius (302° tropical); 64 gates × 5.625°. */
const GATE_ORDER = [41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,27,24,2,23,
                    8,20,16,35,45,12,15,52,39,53,62,56,31,33,7,4,29,59,40,64,
                    47,6,46,18,48,57,32,50,28,44,1,43,14,34,9,5,26,11,10,58,
                    38,54,61,60];

/* ---- signs, nakshatras, houses ---- */
const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
               "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const signOf = l => SIGNS[Math.floor(norm(l) / 30)];
const degIn  = l => norm(l) % 30;
const houseOf = (l, ascLon) =>
  ((Math.floor(norm(l) / 30) - Math.floor(norm(ascLon) / 30) + 12) % 12) + 1;

/* ============================================================
   SEATING · runes locked to houses, two per house.
   Row order: Kylver, closing Dagaz (ingress) then Othala (egress).
   ============================================================ */
const HOUSES = [
  { n:1,  color:"Red",         hex:"#ff3b4e", phase:"Arrival; the self at the gate",
    ingress:["ᚠ","Fehu","wealth-fire at the gate"],   egress:["ᚢ","Uruz","the raw vitality behind it"] },
  { n:2,  color:"Red-orange",  hex:"#ff6a1f", phase:"Holding; resources and the voice",
    ingress:["ᚦ","Thurisaz","the thorn that defends the holdings"], egress:["ᚨ","Ansuz","the god-voice that spends them as speech"] },
  { n:3,  color:"Orange",      hex:"#ff8c1a", phase:"Effort; craft, siblings, movement",
    ingress:["ᚱ","Raidho","the road of effort"],      egress:["ᚲ","Kenaz","the torch of craft"] },
  { n:4,  color:"Yellow-orange",hex:"#ffb31a",phase:"The hearth; foundation and root",
    ingress:["ᚷ","Gebo","the gift-exchange of the hearth"], egress:["ᚹ","Wunjo","its joy"] },
  { n:5,  color:"Yellow",      hex:"#ffd400", phase:"Radiance; creation, children, merit",
    ingress:["ᚺ","Hagalaz","the hail that clears the creative field"], egress:["ᚾ","Nauthiz","the need-fire that disciplines it"] },
  { n:6,  color:"Yellow-green",hex:"#a3e635", phase:"Cultivation; service, the daily year",
    ingress:["ᛁ","Isa","stills the daily root"],      egress:["ᛃ","Jera","turns the daily year"] },
  { n:7,  color:"Green",       hex:"#22e07a", phase:"The covenant; the other, the heart-house",
    ingress:["ᛇ","Eihwaz","the axis arriving at the covenant door"], egress:["ᛈ","Perthro","the honest lot-cup of partnership"] },
  { n:8,  color:"Blue-green",  hex:"#14e0c0", phase:"The depths; shared resource, transformation",
    ingress:["ᛉ","Algiz","wards the descent"],        egress:["ᛋ","Sowilo","the sun found there"] },
  { n:9,  color:"Blue",        hex:"#22b8ff", phase:"Doctrine; the far view, dharma",
    ingress:["ᛏ","Tiwaz","the oath kept at cost"],    egress:["ᛒ","Berkano","the birch that regrows what the oath spent"] },
  { n:10, color:"Blue-violet", hex:"#6b6bff", phase:"The crown of work; vocation, authority",
    ingress:["ᛖ","Ehwaz","the horse that carries the work into public"], egress:["ᛗ","Mannaz","the human crown of the vocation"] },
  { n:11, color:"Violet",      hex:"#b05cff", phase:"The many; networks, gains, transmission",
    ingress:["ᛚ","Laguz","the water given to the many"], egress:["ᛜ","Ingwaz","the seed banked among them"] },
  { n:12, color:"Magenta",     hex:"#ff2fa8", phase:"The seam; dissolution, the hidden, release",
    ingress:["ᛞ","Dagaz","day-break; the seam where night trades places with morning"],
    egress:["ᛟ","Othala","the inheritance that closes the wheel"] }
];

/* ============================================================
   STATIONS · Codex XV, and the Planetary Ladder
   ============================================================ */
const STATIONS = [
  { id:"asgard", world:"Asgard", station:"Crown", tag:"Crown", place:"Axis", axis:true,
    x:450, y:186, side:"L", leadY:146, band:"#b05cff", roman:"I",
    operator:"Önd", opGloss:"the spark · breath-spirit, the intelligence that descends into a life",
    feeder:"Sun", hz:126.22, hd:"Head — pressure to know", bifrost:"Violet",
    kenning:"The seat above the seat. What descends here was decided before you arrived.",
    ask:"The scan opens at the brow. The crown is not interrogated — it is admitted.",
    ratios:[[0.5,"1:2"],[1,"1:1"],[1.5,"3:2"],[2,"2:1"],[3,"3:1"]] },
  { id:"alfheim", world:"Alfheim", station:"Brow", tag:"Brow", place:"Axis", axis:true,
    x:450, y:212, side:"R", leadY:238, band:"#6b6bff", roman:"II",
    operator:"Hugr", opGloss:"the mind · the commanding light of thought",
    feeder:"Moon", hz:210.42, hd:"Ajna — conceptualising", bifrost:"Blue-violet",
    kenning:"Light before form. The image arrives whole, and then asks to be argued with.",
    ask:"Is this thought ripe, or still under pressure?",
    ratios:[[0.5,"1:2"],[1,"1:1"],[1.125,"9:8"],[1.5,"3:2"],[2,"2:1"]] },
  { id:"vanaheim", world:"Vanaheim", station:"Throat", tag:"Throat", place:"Ring · west", axis:false,
    x:450, y:250, side:"L", leadY:294, band:"#22b8ff", roman:"III",
    operator:"Minni", opGloss:"memory sent · the one faculty whose whole purpose is to leave the body",
    feeder:"Saturn", hz:147.85, hd:"Throat — manifestation", bifrost:"Blue",
    kenning:"The narrow gate. Everything the body knows must fit through here to become real.",
    ask:"Was I called, or am I pushing?",
    ratios:[[0.25,"1:4"],[0.5,"1:2"],[1,"1:1"],[1.5,"3:2"],[2,"2:1"]] },
  { id:"midgard", world:"Midgard", station:"Heart", tag:"Heart", place:"Axis · hub", axis:true,
    x:450, y:305, side:"R", leadY:334, band:"#22e07a", roman:"IV",
    operator:"Hamr", opGloss:"the field · the integrating form, the heart's own torus",
    feeder:"Jupiter", hz:183.58, hd:"G centre — identity and direction", bifrost:"Green",
    kenning:"Where the axis crosses the ring. The master oscillator: strike this and the rest tunes itself.",
    ask:"What have I promised that was never mine to prove?",
    ratios:[[0.5,"1:2"],[1,"1:1"],[1.25,"5:4"],[1.5,"3:2"],[2,"2:1"],[3,"3:1"]] },
  { id:"muspelheim", world:"Muspelheim", station:"Solar plexus", tag:"Solar plexus", place:"Ring · south", axis:false,
    x:450, y:352, side:"L", leadY:398, band:"#ffd400", roman:"V",
    operator:"Óðr", opGloss:"the fire · the gut-burn that rises and will not be argued with",
    feeder:"Mars", hz:144.72, hd:"Solar plexus — the emotional wave", bifrost:"Yellow",
    kenning:"First fire, and it does not ask permission. The wave has to finish before the answer is true.",
    ask:"Whose emotion is this?",
    ratios:[[0.5,"1:2"],[1,"1:1"],[1.2,"6:5"],[1.5,"3:2"],[2,"2:1"]] },
  { id:"nidavellir", world:"Nidavellir", station:"Sacrum", tag:"Sacrum", place:"Axis", axis:true,
    x:450, y:406, side:"R", leadY:438, band:"#ff8c1a", roman:"VI",
    operator:"Hamingja", opGloss:"the forge · the inherited power and luck of the line",
    feeder:"Venus", hz:221.23, hd:"Sacral — life force and response", bifrost:"Orange",
    kenning:"The dwarves' forge under the mountain. Work is made here or it is not made.",
    ask:"What did I last respond to, and was there satisfaction?",
    ratios:[[0.5,"1:2"],[1,"1:1"],[1.25,"5:4"],[1.667,"5:3"],[2,"2:1"]] },
  { id:"hel", world:"Hel", station:"Root", tag:"Root", place:"Axis", axis:true,
    x:450, y:434, side:"L", leadY:498, band:"#ff3b4e", roman:"VII",
    operator:"Fylgja", opGloss:"the follower · the one that walks with every incarnation",
    feeder:"Mercury", hz:141.27, hd:"Root — adrenal pressure", bifrost:"Red",
    kenning:"The ancestral dead and the floor of the world. Nothing that ends here is lost; it is kept.",
    ask:"Whose deadline am I carrying?",
    ratios:[[0.25,"1:4"],[0.5,"1:2"],[1,"1:1"],[1.333,"4:3"],[2,"2:1"]] }
];

/* planetary tones — the nodes have none; they feed nothing */
const TONE = { Sun:126.22, Moon:210.42, Mercury:141.27, Venus:221.23,
               Mars:144.72, Jupiter:183.58, Saturn:147.85 };
const GLYPH = { Sun:"☉", Moon:"☽", Mercury:"☿", Venus:"♀", Mars:"♂",
                Jupiter:"♃", Saturn:"♄", Rahu:"☊", Ketu:"☋",
                Uranus:"♅", Neptune:"♆", Pluto:"♇" };
/* The classical seven plus the nodes. Everything Jyotish runs on this
   list: the dashas, the karakas, the Panchadha Maitri, the Planetary
   Ladder. The outer three are real bodies and are plotted everywhere,
   but they are not grahas and are kept out of those calculations. */
const CLASSICAL = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"];
const OUTER = ["Uranus","Neptune","Pluto"];
const BLOOM = 90;

/* ============================================================
   HARMONIC ENGINE
   ============================================================ */
const Sound = (() => {
  let ctx, master, lp, dry, wet, verb, comp, droneGain, droneLP, droneOscs = [],
      ready = false, enabled = true;

  const impulse = (secs, decay) => {
    const rate = ctx.sampleRate, len = Math.floor(rate * secs);
    const buf = ctx.createBuffer(2, len, rate);
    for (let c = 0; c < 2; c++){
      const ch = buf.getChannelData(c);
      for (let i = 0; i < len; i++) ch[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
    }
    return buf;
  };

  function init(){
    if (ready) return true;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    ctx = new AC();
    comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -16; comp.knee.value = 24; comp.ratio.value = 5;
    comp.attack.value = .012; comp.release.value = .5;
    master = ctx.createGain(); master.gain.value = enabled ? .9 : 0;
    lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 1150; lp.Q.value = .45;
    verb = ctx.createConvolver(); verb.buffer = impulse(7.5, 2.6);
    dry = ctx.createGain(); dry.gain.value = .55;
    wet = ctx.createGain(); wet.gain.value = .72;
    lp.connect(dry); dry.connect(master);
    lp.connect(verb); verb.connect(wet); wet.connect(master);
    master.connect(comp); comp.connect(ctx.destination);
    buildDrone(); ready = true; return true;
  }

  function buildDrone(){
    droneGain = ctx.createGain(); droneGain.gain.value = 0;
    droneLP = ctx.createBiquadFilter(); droneLP.type = "lowpass";
    droneLP.frequency.value = 300; droneLP.Q.value = .6;
    droneGain.connect(droneLP); droneLP.connect(lp);
    droneOscs = [36.96, 55.44, 73.92].map((f, i) => {
      const o = ctx.createOscillator();
      o.type = i === 2 ? "triangle" : "sine"; o.frequency.value = f;
      const g = ctx.createGain(); g.gain.value = i === 0 ? .5 : .17;
      o.connect(g); g.connect(droneGain); o.start(); return o;
    });
    const lfo = ctx.createOscillator(); lfo.frequency.value = .045;
    const lg = ctx.createGain(); lg.gain.value = .02;
    lfo.connect(lg); lg.connect(droneGain.gain); lfo.start();
    droneGain.gain.setTargetAtTime(.05, ctx.currentTime, 6);
  }

  function room(open){
    if (!ready) return;
    const t = ctx.currentTime;
    droneLP.frequency.cancelScheduledValues(t);
    droneLP.frequency.setTargetAtTime(open ? 640 : 300, t, open ? .9 : 1.6);
    wet.gain.setTargetAtTime(open ? .92 : .72, t, 1.2);
    droneOscs.forEach((o, i) => o.detune.setTargetAtTime(open ? (i - 1) * 9 : 0, t, 1.4));
  }

  function voice(freq, amp, when, hold){
    const g = ctx.createGain(); g.gain.value = 0;
    if (ctx.createStereoPanner){
      const p = ctx.createStereoPanner(); p.pan.value = (Math.random() * 2 - 1) * .45;
      g.connect(p); p.connect(lp);
    } else g.connect(lp);
    const oscs = [["sine",0,1],["triangle",5,.2],["sine",-7,.13]].map(([type,cents,level],i) => {
      const o = ctx.createOscillator();
      o.type = type; o.frequency.value = i === 2 ? freq * 2 : freq; o.detune.value = cents;
      const og = ctx.createGain(); og.gain.value = level;
      o.connect(og); og.connect(g); o.start(when); return o;
    });
    g.gain.setValueAtTime(0, when);
    g.gain.linearRampToValueAtTime(amp, when + .55);
    g.gain.setTargetAtTime(amp * .58, when + .55, 1.6);
    g.gain.setTargetAtTime(1e-4, when + hold, 1.44);
    oscs.forEach(o => o.stop(when + hold + 6.5));
  }

  function chord(freqs){
    if (!enabled || !init()) return;
    if (ctx.state === "suspended") ctx.resume();
    const t0 = ctx.currentTime + .04;
    lp.frequency.cancelScheduledValues(t0);
    lp.frequency.setValueAtTime(lp.frequency.value, t0);
    lp.frequency.linearRampToValueAtTime(2400, t0 + .5);
    lp.frequency.setTargetAtTime(1150, t0 + .9, 2.4);
    freqs.forEach((f, i) => voice(f, .17 / Math.pow(i + 1, .34), t0 + i * BLOOM / 1000, 2.2 + i * .18));
  }

  function portal(down){
    if (!enabled || !ready) return;
    const t0 = ctx.currentTime, len = Math.floor(ctx.sampleRate * 1.6);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < len; i++) ch[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3);
    const src = ctx.createBufferSource(); src.buffer = buf;
    const bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.Q.value = 1.4;
    bp.frequency.setValueAtTime(down ? 1700 : 240, t0);
    bp.frequency.exponentialRampToValueAtTime(down ? 220 : 1500, t0 + 1.2);
    const g = ctx.createGain(); g.gain.value = .085;
    src.connect(bp); bp.connect(g); g.connect(lp); src.start(t0);
  }

  function denied(){
    if (!init()) return;
    if (ctx.state === "suspended") ctx.resume();
    const t0 = ctx.currentTime;
    [73.9, 78.3].forEach(f => {
      const o = ctx.createOscillator(); o.type = "sine"; o.frequency.value = f;
      const g = ctx.createGain(); g.gain.value = 0;
      o.connect(g); g.connect(lp); o.start(t0);
      g.gain.linearRampToValueAtTime(.16, t0 + .05);
      g.gain.setTargetAtTime(1e-4, t0 + .18, .32);
      o.stop(t0 + 2.4);
    });
  }

  function unlock(){
    if (!init()) return;
    if (ctx.state === "suspended") ctx.resume();
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(0, ctx.currentTime);
    master.gain.linearRampToValueAtTime(.9, ctx.currentTime + 1.4);
    setTimeout(() => chord([63.11, 94.67, 126.22, 189.33, 252.44]), 400);
  }

  function toggle(on){
    enabled = on;
    if (!ready) return;
    const t = ctx.currentTime;
    master.gain.cancelScheduledValues(t);
    master.gain.setValueAtTime(master.gain.value, t);
    master.gain.linearRampToValueAtTime(on ? .9 : 0, t + .7);
    if (on && ctx.state === "suspended") ctx.resume();
  }

  return { chord, portal, denied, unlock, toggle, room,
           raw: () => { init(); return ctx; },
           into: node => { init(); if (node && lp) node.connect(lp); } };
})();


/* ============================================================
   THE HIGH SEAT SKY
   A nebula field behind Hliðskjálf. The clouds are drawn once into
   an offscreen canvas and never redrawn — only the starfield and
   the wheel's glow move, so the cost per frame stays near nothing
   and the 3D deck keeps its budget. Stops entirely when the seat is
   not on screen, and never starts under reduced motion.
   ============================================================ */
const HighSky = (() => {
  let cv = null, ctx2 = null, neb = null, stars = [], raf = null, t = 0, W = 0, H = 0;
  const reduced = () => window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function buildNebula(w, h){
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const g = c.getContext("2d");
    g.fillStyle = "#04030c"; g.fillRect(0, 0, w, h);
    const clouds = [
      ["rgba(84,42,148,0.33)", 0.26, 0.30, 0.46],
      ["rgba(38,44,150,0.30)", 0.72, 0.24, 0.42],
      ["rgba(22,58,132,0.27)", 0.52, 0.72, 0.50],
      ["rgba(112,50,160,0.20)", 0.14, 0.78, 0.38],
      ["rgba(30,30,110,0.26)", 0.88, 0.66, 0.40]
    ];
    for (const [col, fx, fy, fr] of clouds){
      for (let i = 0; i < 26; i++){
        const a = Math.random() * Math.PI * 2, d = Math.pow(Math.random(), 0.6) * fr * w * 0.5;
        const x = fx * w + Math.cos(a) * d, y = fy * h + Math.sin(a) * d * 0.62;
        const r = (0.08 + Math.random() * 0.16) * w * 0.5;
        const rg = g.createRadialGradient(x, y, 0, x, y, r);
        rg.addColorStop(0, col); rg.addColorStop(1, "rgba(0,0,0,0)");
        g.fillStyle = rg; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
      }
    }
    /* dust lanes, so the clouds have something to be behind */
    g.globalCompositeOperation = "multiply";
    for (let i = 0; i < 14; i++){
      const x = Math.random() * w, y = Math.random() * h, r = (0.05 + Math.random()*0.1) * w;
      const rg = g.createRadialGradient(x, y, 0, x, y, r);
      rg.addColorStop(0, "rgba(2,2,8,0.7)"); rg.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = rg; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
    }
    g.globalCompositeOperation = "source-over";
    return c;
  }

  function seed(){
    stars = [];
    const n = Math.min(320, Math.round(W * H / 5200));
    for (let i = 0; i < n; i++)
      stars.push({ x: Math.random()*W, y: Math.random()*H,
                   r: Math.random() < 0.86 ? Math.random()*0.9+0.25 : Math.random()*1.7+0.9,
                   p: Math.random()*6.28, s: 0.4 + Math.random()*1.6,
                   d: 0.006 + Math.random()*0.02 });
  }

  function size(){
    const host = document.getElementById("skyHost");
    if (!host || !cv) return;
    const r = host.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    cv.width = Math.round(W*dpr); cv.height = Math.round(H*dpr);
    cv.style.width = W+"px"; cv.style.height = H+"px";
    ctx2.setTransform(dpr,0,0,dpr,0,0);
    neb = buildNebula(W, H);
    seed();
  }

  function frame(){
    if (!ctx2){ raf = null; return; }
    t += 0.016;
    ctx2.clearRect(0,0,W,H);
    if (neb){
      /* the clouds only drift; they are never redrawn */
      const dx = Math.sin(t*0.035)*10, dy = Math.cos(t*0.027)*7;
      ctx2.globalAlpha = 1; ctx2.drawImage(neb, dx, dy, W, H);
    }
    for (const s of stars){
      const tw = 0.55 + 0.45*Math.sin(t*s.s + s.p);
      ctx2.globalAlpha = tw;
      ctx2.fillStyle = s.r > 1.1 ? "#dfe6ff" : "#b9c4ee";
      ctx2.beginPath(); ctx2.arc(s.x, s.y, s.r, 0, 7); ctx2.fill();
      s.x += s.d; if (s.x > W + 2) s.x = -2;
    }
    /* the wheel's glow, pulsing outward against the clouds */
    const cx = W/2, cy = H/2, pulse = 0.5 + 0.5*Math.sin(t*0.7);
    const R = Math.min(W,H) * (0.20 + 0.05*pulse);
    const g = ctx2.createRadialGradient(cx, cy, 0, cx, cy, R);
    g.addColorStop(0, "rgba(150,120,255,"+(0.16+0.10*pulse).toFixed(3)+")");
    g.addColorStop(0.55, "rgba(90,80,200,"+(0.07+0.05*pulse).toFixed(3)+")");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx2.globalAlpha = 1; ctx2.fillStyle = g;
    ctx2.beginPath(); ctx2.arc(cx, cy, R, 0, 7); ctx2.fill();
    raf = requestAnimationFrame(frame);
  }

  function start(){
    const host = document.getElementById("skyHost");
    if (!host || host.classList.contains("desk")) return;      /* the chart's hub has its own 90s wallpaper instead */
    if (!cv){
      cv = document.createElement("canvas");
      cv.className = "sky-cv";
      ctx2 = cv.getContext("2d");
      host.insertBefore(cv, host.firstChild);
      window.addEventListener("resize", () => { size(); }, { passive:true });
    }
    size();
    if (reduced()){ frame(); cancelAnimationFrame(raf); raf = null; return; }
    if (!raf) raf = requestAnimationFrame(frame);
  }
  function stop(){ if (raf){ cancelAnimationFrame(raf); raf = null; } }

  return { start, stop };
})();

/* ============================================================
   STATE
   ============================================================ */
let CHART = null, live = null, liveKind = null, view = "elevation", swapToken = 0;
const $ = id => document.getElementById(id);

/* ---- the 27 nakshatras ---- */
const NAKSHATRA = [
  ["Ashwini","Ketu","Ashwini Kumaras","Horse's head","Deva","Knees"],
  ["Bharani","Venus","Yama","Yoni","Manushya","Head"],
  ["Krittika","Sun","Agni","Razor, flame","Rakshasa","Waist"],
  ["Rohini","Moon","Brahma","Ox-cart, chariot","Manushya","Shins, forehead"],
  ["Mrigashira","Mars","Soma","Deer's head","Deva","Eyebrows"],
  ["Ardra","Rahu","Rudra","Teardrop, diamond","Manushya","Eyes"],
  ["Punarvasu","Jupiter","Aditi","Quiver of arrows","Deva","Fingers, nose"],
  ["Pushya","Saturn","Brihaspati","Cow's udder, lotus","Deva","Mouth, face"],
  ["Ashlesha","Mercury","Nagas","Coiled serpent","Rakshasa","Ears, joints"],
  ["Magha","Ketu","Pitris","Throne, palanquin","Rakshasa","Lips, chin"],
  ["Purva Phalguni","Venus","Bhaga","Front legs of a bed","Manushya","Right hand"],
  ["Uttara Phalguni","Sun","Aryaman","Back legs of a bed","Manushya","Left hand"],
  ["Hasta","Moon","Savitar","Open hand","Deva","Hands"],
  ["Chitra","Mars","Tvashtar","Bright jewel","Rakshasa","Neck, forehead"],
  ["Swati","Rahu","Vayu","Young shoot in wind","Deva","Chest"],
  ["Vishakha","Jupiter","Indra-Agni","Triumphal arch","Rakshasa","Arms, breasts"],
  ["Anuradha","Saturn","Mitra","Lotus, staff","Deva","Stomach, bowels"],
  ["Jyeshtha","Mercury","Indra","Circular amulet, umbrella","Rakshasa","Neck, right side"],
  ["Mula","Ketu","Nirriti","Tied roots","Rakshasa","Feet"],
  ["Purva Ashadha","Venus","Apas","Fan, winnowing basket","Manushya","Thighs"],
  ["Uttara Ashadha","Sun","Vishvadevas","Elephant tusk, planks","Manushya","Thighs"],
  ["Shravana","Moon","Vishnu","Ear, three footprints","Deva","Ears"],
  ["Dhanishta","Mars","Vasus","Drum","Rakshasa","Back"],
  ["Shatabhisha","Rahu","Varuna","Empty circle, hundred healers","Rakshasa","Jaw, thighs"],
  ["Purva Bhadrapada","Jupiter","Aja Ekapada","Front of funeral cot","Manushya","Sides, feet"],
  ["Uttara Bhadrapada","Saturn","Ahir Budhnya","Back of funeral cot","Manushya","Shins"],
  ["Revati","Mercury","Pushan","Fish, drum","Deva","Ankles, feet"]
];

/* ---- Human Design gate names ---- */
const GATE_NAME = {
  1:"Self-Expression",2:"Higher Knowing",3:"Ordering",4:"Formulisation",5:"Fixed Rhythms",
  6:"Friction",7:"The Role of the Self",8:"Contribution",9:"Focus",10:"Behaviour of the Self",
  11:"Ideas",12:"Caution",13:"The Listener",14:"Power Skills",15:"Extremes",16:"Skills",
  17:"Opinions",18:"Correction",19:"Wanting",20:"The Now",21:"The Hunter",22:"Openness",
  23:"Assimilation",24:"Rationalisation",25:"The Spirit of the Self",26:"The Egoist",
  27:"Caring",28:"The Game Player",29:"Saying Yes",30:"Recognition of Feelings",
  31:"Influence",32:"Continuity",33:"Privacy",34:"Power",35:"Change",36:"Crisis",
  37:"Friendship",38:"The Fighter",39:"Provocation",40:"Aloneness",41:"Contraction",
  42:"Growth",43:"Insight",44:"Alertness",45:"The Gatherer",46:"Determination of the Self",
  47:"Realisation",48:"Depth",49:"Principles",50:"Values",51:"Shock",52:"Stillness",
  53:"Beginnings",54:"Ambition",55:"Spirit",56:"Stimulation",57:"Intuitive Clarity",
  58:"Vitality",59:"Sexuality",60:"Acceptance",61:"Inner Truth",62:"Detail",
  63:"Doubt",64:"Confusion"
};/* names and the Taittiriya triad only; the interpretive text is server-side */
const ENGINE = [["Ashwini","shighra-vyapani","the power to reach quickly","those to be healed","the healing therapies","the world made free of disease","","","","",""],["Bharani","apabharani","the power to remove","the removal of life from the body","the carrying of the soul to the ancestors","passage to the next world","","","","",""],["Krittika","dahana","the power to burn","heat","light","purification","","","","",""],["Rohini","rohana","the power of growth","the plants","the waters","creation","","","","",""],["Mrigashira","prinana","the power of fulfilment","extension","weaving","the world made enjoyable","","","","",""],["Ardra","yatna","the power of effort","hunting","reaching the goal","achievement","","","","",""],["Punarvasu","vasutva-prapana","the power to regain substance","wind and rain","growth","the herbs and trees restored","","","","",""],["Pushya","brahmavarchasa","the power to create spiritual radiance","the worship","the worshipper","spiritual energy","","","","",""],["Ashlesha","visashleshana","the power to poison and entwine","the serpent's approach","the trembling of the victim","the overcoming of the target","","","","",""],["Magha","tyage kshepani","the power to leave the body","mourning","the leaving","union with the ancestors","","","","",""],["Purva Phalguni","prajanana","the power of procreation","the beloved","the lover","the conception","","","","",""],["Uttara Phalguni","chayani","the power of prosperity through union","wealth from one's own house","wealth from the partner's house","the accumulated estate","","","","",""],["Hasta","hasta-sthapaniya","the power to place what is sought in the hand","the seeking of the object","the process of gaining it","the thing, in the palm","","","","",""],["Chitra","punya-chayani","the power to accumulate merit","the law","the truth","honour through work","","","","",""],["Swati","pradhvamsa","the power to scatter","movement in all directions","change of form","transformation","","","","",""],["Vishakha","vyapana","the power to achieve many fruits","the plowing","the harvest","the fruit gathered","","","","",""],["Anuradha","radhana","the power of worship","ascension","descension","honour and abundance","","","","",""],["Jyeshtha","ārohana","the power to rise and conquer","the attack","the defence","the hero","","","","",""],["Mula","barhana","the power to ruin","the breaking apart","the crushing","the destruction that destroys destruction","","","","",""],["Purva Ashadha","varchograhana","the power of invigoration","strength","connection","luster","","","","",""],["Uttara Ashadha","apradhrishya","the power of unchallengeable victory","the strength that can win","the goal that can be won","the victory no one contests","","","","",""],["Shravana","samhanana","the power of connection","the seeking","the paths","the connection of all things","","","","",""],["Dhanishta","khyapayitri","the power to give abundance and renown","birth","prosperity","the world's wealth gathered into one place","","","","",""],["Shatabhisha","bheshaja","the power of healing","the pervasion over all things","the support","the world freed of calamity","","","","",""],["Purva Bhadrapada","yajamana-udyamana","the power to raise the sacrificer","what is good for all beings","what is good for the gods","the support of the entire world","","","","",""],["Uttara Bhadrapada","varshodyamana","the power to bring rain","the raining clouds","the growing plants","the stability of the three worlds","","","","",""],["Revati","kshiradyapani","the power of nourishing milk","the cows","the calves","the nourishment of the whole world","","","","",""]];


/* ============================================================
   THE COLOUR LAYER · from the house-colour wheel
   Two wheels of twelve. The anchor — red at the first house —
   is the one real choice in the system, and it is stated every
   time because everything rotates with it.
   ============================================================ */
const HUE_CLASS = ["primary","tertiary","secondary","tertiary","primary","tertiary",
                   "secondary","tertiary","primary","tertiary","secondary","tertiary"];
const HUE_ELEMENT = ["Fire","Earth","Air","Water","Fire","Earth","Air","Water","Fire","Earth","Air","Water"];

/* four grahas carry a hue; three change value and saturation instead */
const CHROMATIC = {
  Mars:    { hue:"Red",              hex:"#ff3b4e", seat:1 },
  Sun:     { hue:"Copper, red-orange", hex:"#ff6a1f", seat:2 },
  Jupiter: { hue:"Yellow, gold",     hex:"#ffd400", seat:5 },
  Mercury: { hue:"Green",            hex:"#22e07a", seat:7 }
};
/* four grahas carry no hue and work on the house's colour instead, on two scales:
   value, how light or dark (the Moon raises it, Saturn lowers it), and saturation, how vivid (Venus raises it,
   Rahu lowers it). Tint, shade and tone are colour theory's names for adding white,
   black and grey. The glaze is the painter's way of raising saturation, which no
   mixture can: a construction, given to Venus on the meaning of śukra, bright and clear. */
const ACHROMATIC = {
  Moon:   { adds:"White", op:"Tint", scale:"value", does:"raises the value",
            note:"Raises the value. The house's matter grows lighter, more visible, more receptive. Nothing is removed; everything is brought up into the light." },
  Saturn: { adds:"Black", op:"Shade", scale:"value", does:"lowers the value",
            note:"Lowers the value. The house's matter grows heavier, deeper, more contracted. The hue is still there and harder to see." },
  Venus:  { adds:"A clear glaze", op:"Glaze", scale:"saturation", does:"raises the saturation", constructed:true,
            note:"Raises the saturation. The house's matter grows richer and more lustrous, more fully its own colour. Nothing is added from outside; what is there is polished until it shines." },
  Rahu:   { adds:"Grey",  op:"Tone", scale:"saturation", does:"lowers the saturation",
            note:"Drops the saturation. The house's matter goes murky and hard to read. Not darker, not lighter — less certain what colour it was." }
};
const UNRESOLVED = {
  Ketu:  "Classically variegated — flag-coloured, many-hued. In colour terms that is not a hue but a prism: it splits the house's colour into components rather than mixing with it. Fitting for the graha that fragments, though it is construction, not lineage."
};

/* the glaze: the same hue, more saturated and a little deeper, as a transparent
   layer of colour over itself looks; with a sheen of light across it */
function hexHsl(hex){
  const [r, g, b] = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  if (!d) return [0, 0, l];
  const s = d / (1 - Math.abs(2 * l - 1));
  const h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return [(h * 60 + 360) % 360, s, l];
}
function hslHex(h, s, l){
  const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return "#" + [r, g, b].map(v => Math.round((v + m) * 255).toString(16).padStart(2, "0")).join("");
}
function glazeHex(hex){
  const [h, s, l] = hexHsl(hex);
  return hslHex(h, Math.min(1, s + (1 - s) * .7), l * .8);
}
const SHEEN = "linear-gradient(115deg,rgba(255,255,255,0) 56%,rgba(255,255,255,.38) 69%,rgba(255,255,255,0) 82%)";
/* Venus's disc: the house's own colour, glazed and polished into a bead */
function glazeDisc(hex){
  const g = glazeHex(hex);
  return `radial-gradient(circle at 34% 28%,#fff 0,rgba(255,255,255,.7) 8%,${g} 42%,${mixHex(g, "#000000", .42)} 100%)`;
}
/* what each hueless graha does to a house's colour */
function opAfter(graha, hex){
  return graha === "Moon" ? mixHex(hex, "#ffffff", .45) : graha === "Saturn" ? mixHex(hex, "#000000", .45)
       : graha === "Venus" ? glazeHex(hex) : mixHex(hex, "#7a7f79", .55);
}
const OP_DISC = { Moon: "#f2f4ef", Saturn: "#0a0908", Rahu: "#767a74" };

/* harmony and aspect are the same word — both divide twelve */
const HARMONY = [
  [0,"Identical","Conjunction","The disc very nearly disappears into its own field."],
  [1,"Analogous","Semi-sextile","Neighbours. The two colours share a component and sit quietly together."],
  [2,"Near-analogous","Sextile","Close enough to cooperate, far enough to be distinct."],
  [3,"Tetradic","Square","A quarter turn. The friction that will not resolve into comfort but reliably resolves into output."],
  [4,"Triadic","Trine","A third turn — the colourist's classical triad is the trikona."],
  [5,"Near-complementary","Quincunx","Almost opposite, and the almost is the problem: no shared component and no clean contrast."],
  [6,"Complementary","Opposition","Directly across. Maximum contrast — each colour makes the other more itself. Whether that reads as vividness or clash is not the wheel's decision."]
];

/* ============================================================
   THE DAŚĀ CLOCK · the full 120-year sequence, not just today
   ============================================================ */
const DASHA_SEQ = [["Ketu",7],["Venus",20],["Sun",6],["Moon",10],["Mars",7],
                   ["Rahu",18],["Jupiter",16],["Saturn",19],["Mercury",17]];
const YEAR = 365.2425;

/* ============================================================
   GATE → MANSION
   The Estates register reads a gate's own degrees directly
   against the nakshatra bounds. Verified against fourteen stated
   assignments in the register: fourteen exact matches.

   Method note, stated because it matters: the codex holds the
   gate wheel to be a fixed TROPICAL instrument, and nakshatra
   bounds are SIDEREAL. Reading one against the other treats the
   gate wheel as sidereal-anchored for this purpose alone. The
   register does it consistently and the seams land where it says
   they land, so it is implemented as specified — but it is a join
   between two frames and should be marked as a register decision
   rather than assumed.
   ============================================================ */
const NAK_ARC = 360 / 27;
const nakIndex = lon => Math.floor(norm(lon) / NAK_ARC);

function gateSpan(gate){
  const i = GATE_ORDER.indexOf(gate);
  if (i < 0) return null;
  const a = norm(302 + i * 5.625);
  return { start: a, end: norm(a + 5.625) };
}

/** Mansion for a specific line of a gate, plus whether it sits on a seam. */
function gateMansion(gate, line){
  const s = gateSpan(gate);
  if (!s) return null;
  const lineArc = 5.625 / 6;
  const lo = norm(s.start + (line - 1) * lineArc);
  const hi = norm(lo + lineArc);
  const a = nakIndex(lo), b = nakIndex(hi - 1e-9);
  return { primary: a, secondary: a === b ? null : b, seam: a !== b };
}

/* ============================================================
   THE COLOUR LAYER
   ============================================================ */
function harmonyBetween(a, b){
  const d = Math.min((a - b + 12) % 12, (b - a + 12) % 12);
  return HARMONY.find(h => h[0] === d) || HARMONY[HARMONY.length - 1];
}


/* ============================================================
   PANCHADHA MAITRI · the fivefold friendship
   Natural relationship is fixed and the same in every chart.
   Temporal relationship is read from where the two planets
   actually stand in THIS chart — which is what stops the
   resonance being identical for everyone in a Venus/Mercury
   period. The two compound into five states.
   ============================================================ */

/* Naisargika maitri, standard Parashari. Note that this table is
   deliberately NOT symmetric: the Moon holds no enemies, but
   Venus and Saturn both count the Moon an enemy. That asymmetry
   is in the tradition, not a typo, so the engine always reads it
   from the mahadasha lord's point of view. */
const NATURAL = {
  Sun:     { friend:["Moon","Mars","Jupiter"], neutral:["Mercury"], enemy:["Venus","Saturn"] },
  Moon:    { friend:["Sun","Mercury"], neutral:["Mars","Jupiter","Venus","Saturn"], enemy:[] },
  Mars:    { friend:["Sun","Moon","Jupiter"], neutral:["Venus","Saturn"], enemy:["Mercury"] },
  Mercury: { friend:["Sun","Venus"], neutral:["Mars","Jupiter","Saturn"], enemy:["Moon"] },
  Jupiter: { friend:["Sun","Moon","Mars"], neutral:["Saturn"], enemy:["Mercury","Venus"] },
  Venus:   { friend:["Mercury","Saturn"], neutral:["Mars","Jupiter"], enemy:["Sun","Moon"] },
  Saturn:  { friend:["Mercury","Venus"], neutral:["Jupiter"], enemy:["Sun","Moon","Mars"] },
  /* The nodes are contested across schools. This is the common set;
     mark it as a register decision, not a settled rule. */
  Rahu:    { friend:["Venus","Saturn","Mercury"], neutral:["Jupiter"], enemy:["Sun","Moon","Mars"] },
  Ketu:    { friend:["Venus","Saturn","Mercury"], neutral:["Jupiter"], enemy:["Sun","Moon","Mars"] }
};

function naturalRel(from, to){
  const n = NATURAL[from];
  if (!n || from === to) return "self";
  if (n.friend.includes(to)) return "friend";
  if (n.enemy.includes(to)) return "enemy";
  return "neutral";
}

/* Tatkalika maitri: counted in signs from the reference planet.
   The 2nd, 3rd, 4th, 10th, 11th and 12th are temporal friends;
   the 1st, 5th, 6th, 7th, 8th and 9th are temporal enemies. */
const TEMPORAL_FRIEND_HOUSES = [2,3,4,10,11,12];
function temporalRel(from, to){
  if (!CHART || from === to) return "self";
  const a = Math.floor(norm(CHART.sid[from]) / 30);
  const b = Math.floor(norm(CHART.sid[to]) / 30);
  const h = ((b - a + 12) % 12) + 1;
  return TEMPORAL_FRIEND_HOUSES.includes(h) ? "friend" : "enemy";
}
function housesBetween(from, to){
  if (!CHART) return null;
  const a = Math.floor(norm(CHART.sid[from]) / 30);
  const b = Math.floor(norm(CHART.sid[to]) / 30);
  return ((b - a + 12) % 12) + 1;
}

/* The compound table. */
const MAITRI = {
  "friend|friend":"great friend", "friend|enemy":"neutral",
  "neutral|friend":"friend",      "neutral|enemy":"enemy",
  "enemy|friend":"neutral",       "enemy|enemy":"great enemy"
};
function panchadhaMaitri(from, to){
  if (from === to) return "self";
  const nat = naturalRel(from, to), tmp = temporalRel(from, to);
  return MAITRI[nat + "|" + tmp] || "neutral";
}

/* ============================================================
   THE ACOUSTIC LADDER
   One correction from the matrix as drafted. It had Neutral on
   the major second (9:8) and Enemy on the minor third (6:5) —
   but 6:5 is the minor third, the basis of the minor triad, and
   it is a consonance. 9:8 is rougher. As drafted the ladder
   inverts in the middle: the "Enemy" interval sounds calmer than
   the "Neutral" one.

   Swapping those two makes tension rise monotonically all the
   way up, and it puts the major/minor distinction exactly on the
   friend/neutral line — which is the one boundary a listener can
   actually hear without being told.
   ============================================================ */
const RESONANCE = {
  "self":         { interval:"Unison",        ratio:[1,1],    state:"Genesis",
                    reads:"Foundation laying. The period sounds its own root and nothing else — raw initiation, no second term to argue with." },
  "great friend": { interval:"Perfect fifth", ratio:[3,2],    state:"Consonance",
                    reads:"Structural expansion. The two lords reinforce; what is built now tends to hold without being forced." },
  "friend":       { interval:"Major third",   ratio:[5,4],    state:"Harmony",
                    reads:"Stable growth. New material is absorbed rather than resisted — the good season for synthesis." },
  "neutral":      { interval:"Minor third",   ratio:[6,5],    state:"Transition",
                    reads:"Consonant but unsettled. Nothing is fighting, nothing is resolving. Gather, observe, hold the pattern." },
  "enemy":        { interval:"Major second",  ratio:[9,8],    state:"Tension",
                    reads:"Genuine roughness — the two tones beat against each other. Internal review, shadow work, the season to look rather than launch." },
  "great enemy":  { interval:"Tritone",       ratio:[45,32],  state:"Dissonance",
                    reads:"Heavy friction. The interval will not resolve where it stands. Shedding; the tearing down of a structure that has outlived its terms." }
};
const RESON_COL = { "self":"#c8f7ff", "great friend":"#74c3a4", "friend":"#5f9c86",
                    "neutral":"#a3e635", "enemy":"#ffcc33", "great enemy":"#b0574a" };

/** The full resonance state between the two active lords. */
function resonanceState(){
  if (!CHART) return null;
  const D = dashaTree();
  const root = D.cur.lord, iv = D.curA.lord;
  const rel = panchadhaMaitri(root, iv);
  const R = RESONANCE[rel];
  const rootHz = TONE[root] || (root === "Rahu" ? 63.11 : 47.33);
  return {
    root, lord2:iv, rel,
    natural: naturalRel(root, iv),
    temporal: temporalRel(root, iv),
    houses: housesBetween(root, iv),
    ...R,
    rootHz,
    ivHz: rootHz * R.ratio[0] / R.ratio[1],
    cents: 1200 * Math.log2(R.ratio[0] / R.ratio[1]),
    tree: D
  };
}

function soundResonance(){
  const r = resonanceState();
  if (!r) return;
  Sound.chord([r.rootHz / 2, r.rootHz, r.ivHz, r.rootHz * 2], { bloomMs:120, hold:3.4 });
}

/* ============================================================
   ORIENTATION · house 1 at one o'clock, running clockwise
   SVG angles here are the ordinary ones: 0° is due east, and
   because the y axis points down, increasing the angle turns
   clockwise. Twelve o'clock is therefore −90°, and one o'clock
   is −60°. Every wheel in this console reads from these two
   functions so they cannot fall out of step with each other.
   ============================================================ */
const HOUSE_ONE_ANGLE = -60;
/** Screen angle at which house h opens. */
const angleHouse = h => HOUSE_ONE_ANGLE + (h - 1) * 30;


/* ============================================================
   THE ARMILLARY
   Ezekiel's wheel is a wheel within a wheel, and the point of it
   is that the rings do not share a plane. So the five frames
   are given five different tilts, each ring is a real circle in
   three dimensions projected onto the screen, and the back half
   of every ring is drawn faintly so the crossing reads as depth
   rather than as overlap.

   The rotation is honest: the frames actually differ. The two
   zodiacs are offset by the ayanamsa. The gates and the runes
   run on different anchors. Tilting them apart lets you see all
   of that at once, which a flat wheel cannot do.

   The hub is a vajra — the thing that is both a weapon and a
   sceptre, and the only implement in the region whose whole
   meaning is that it is indestructible and double-ended. It
   sits on the nodal axis, which is the one line in the chart
   that has a top and a bottom and no middle.
   ============================================================ */
const ARM_RINGS = [
  { id:"trop",  r:250, tilt:  0, spin:0,   n:12, tag:"TROPICAL",  col:"#d9d4c4", op:.55 },
  { id:"sid",   r:214, tilt: 17, spin:0,   n:12, tag:"SIDEREAL",  col:"#ffcc33", op:.7  },
  { id:"gate",  r:180, tilt:-14, spin:0,   n:64, tag:"64 GATES",  col:"#5f9c86", op:.6  },
  { id:"nak",   r:146, tilt: 28, spin:0,   n:27, tag:"27 MANSIONS", col:"#7fb3c4", op:.6 },
  { id:"rune",  r:112, tilt:-25, spin:0,   n:24, tag:"24 RUNES",  col:"#c8f7ff", op:.5  }
];
/* Two states. Closed, every ring lies in one plane and the thing is an
   ordinary flat wheel — which is what you want ninety percent of the
   time. Open, the frames separate onto their own tilts and it becomes
   the armillary. Morph runs 0 to 1 between them and everything else is
   derived from it, so there is one source of truth for the pose. */
let armYaw = 24, armSpin = true, armSel = null, armRAF = null;
let armOpen = false, armMorph = 0, armMorphTo = 0;
const ARM_PITCH_OPEN = 52;
const armPitchNow = () => ARM_PITCH_OPEN * armMorph;
let armPitchUser = null;   /* set once the person drags */

/** Rotate a point on a tilted ring into view space. Returns depth too. */
function armPoint(r, deg, tiltDeg){
  const a = deg * Math.PI / 180, t = tiltDeg * armMorph * Math.PI / 180;
  /* the circle, in its own plane */
  let x = Math.cos(a) * r, y = 0, z = Math.sin(a) * r;
  /* tilt about the x axis */
  const ct = Math.cos(t), st = Math.sin(t);
  let y2 = y * ct - z * st, z2 = y * st + z * ct;
  /* yaw about the y axis */
  const cy = Math.cos(armYaw * Math.PI / 180), sy = Math.sin(armYaw * Math.PI / 180);
  const x3 = x * cy + z2 * sy, z3 = -x * sy + z2 * cy;
  /* pitch: how far the whole assembly is leaned toward the viewer */
  const p = (armPitchUser !== null ? armPitchUser : armPitchNow()) * Math.PI / 180;
  const y4 = y2 * Math.sin(p) + z3 * Math.cos(p);
  const z4 = y2 * Math.cos(p) - z3 * Math.sin(p);
  return { x:500 + x3, y:400 + y4, z:z4 };
}

function armRingPath(ring, front){
  const pts = [];
  for (let i = 0; i <= 180; i++){
    const d = i * 2 + ring.spin * armMorph;
    const p = armPoint(ring.r, d, ring.tilt);
    const isFront = p.z >= 0;
    if (isFront === front) pts.push(p);
    else if (pts.length){ pts.push(null); }
  }
  let d = "", pen = false;
  for (const p of pts){
    if (!p){ pen = false; continue; }
    d += (pen ? "L" : "M") + p.x.toFixed(1) + "," + p.y.toFixed(1) + " ";
    pen = true;
  }
  return d;
}

/** The vajra: a central sphere with five prongs at each end, on the nodal axis. */
function vajraSVG(){
  const up = armPoint(0, 0, 0);
  const reach = 22 + 74 * armMorph;
  const axT = armPoint(reach, 90, 90), axB = armPoint(reach, 270, 90);
  const cx = 500, cy = 400;
  let o = `<g class="vajra">`;
  /* the shaft along the nodal axis */
  o += `<line class="vaj" x1="${axT.x.toFixed(1)}" y1="${axT.y.toFixed(1)}"
      x2="${axB.x.toFixed(1)}" y2="${axB.y.toFixed(1)}"
      stroke="#ffcc33" stroke-width="2.4" opacity=".8"/>`;
  /* the two lotus knots */
  for (const e of [axT, axB]){
    const dx = (e.x - cx) * 0.42, dy = (e.y - cy) * 0.42;
    o += `<ellipse cx="${(cx + dx).toFixed(1)}" cy="${(cy + dy).toFixed(1)}" rx="7" ry="4.5"
      fill="none" stroke="#ffcc33" stroke-width="1.1" opacity=".7"
      transform="rotate(${(Math.atan2(e.y - cy, e.x - cx) * 180 / Math.PI + 90).toFixed(1)} ${
        (cx + dx).toFixed(1)} ${(cy + dy).toFixed(1)})"/>`;
  }
  /* five prongs at each end: one straight, four curving back to meet it */
  for (const [end, sign] of [[axT, 1], [axB, -1]]){
    const ux = (end.x - cx), uy = (end.y - cy);
    const len = Math.hypot(ux, uy) || 1;
    const nx = ux / len, ny = uy / len;
    const px = -ny, py = nx;
    const tipX = cx + nx * (len + 8 + 22 * armMorph), tipY = cy + ny * (len + 8 + 22 * armMorph);
    o += `<line class="vaj" x1="${(cx + nx * len * .78).toFixed(1)}"
        y1="${(cy + ny * len * .78).toFixed(1)}" x2="${tipX.toFixed(1)}" y2="${tipY.toFixed(1)}"
        stroke="#ffcc33" stroke-width="1.8" opacity=".85"/>`;
    for (const s of [-1, -0.45, 0.45, 1]){
      const sp = 5 + 8 * armMorph;
      const bx = cx + nx * len * .78 + px * s * sp;
      const by = cy + ny * len * .78 + py * s * sp;
      const mx = cx + nx * (len + 6) + px * s * (sp + 4);
      const my = cy + ny * (len + 6) + py * s * (sp + 4);
      o += `<path class="vaj" d="M${bx.toFixed(1)},${by.toFixed(1)}
        Q${mx.toFixed(1)},${my.toFixed(1)} ${(tipX - nx * 7).toFixed(1)},${(tipY - ny * 7).toFixed(1)}"
        stroke="#ffcc33" stroke-width="1.15" opacity="${0.42 + Math.abs(s) * 0.2}"/>`;
    }
  }
  /* the hub sphere */
  o += `<circle cx="${cx}" cy="${cy}" r="${(15 + 4 * (1 - armMorph)).toFixed(1)}"
      fill="#020405" stroke="#ffcc33" stroke-width="1.3" opacity=".9"/>
    <circle cx="${cx}" cy="${cy}" r="15" fill="url(#vajGlow)"/>
    <circle cx="${cx}" cy="${cy}" r="6.5" fill="none" stroke="#5f9c86" stroke-width=".9" opacity=".8"/>
    <circle cx="${cx}" cy="${cy}" r="2.2" fill="#d9d4c4"/>
    <defs><radialGradient id="vajGlow">
      <stop offset="0%" stop-color="#ffcc33" stop-opacity=".4"/>
      <stop offset="100%" stop-color="#ffcc33" stop-opacity="0"/></radialGradient></defs></g>`;
  return o;
}

function armillarySVG(){
  if (!CHART) return "";
  const ay = CHART.ay;
  const anchor = { trop:0, sid:ay, gate:302 + ay, nak:ay, rune:0 };
  let back = "", front = "", marks = "";

  for (const ring of ARM_RINGS){
    /* the band, split so the far half is faint */
    back  += `<path class="band band-back" d="${armRingPath(ring, false)}"
      stroke="${ring.col}" stroke-width="1" opacity="${(ring.op * .38).toFixed(2)}"
      stroke-dasharray="5 4"/>`;
    front += `<path class="band band-front" d="${armRingPath(ring, true)}"
      stroke="${ring.col}" stroke-width="1.3" opacity="${ring.op}"/>`;
    /* division ticks */
    for (let i = 0; i < ring.n; i++){
      const deg = anchor[ring.id] + (i * 360 / ring.n) + ring.spin * armMorph;
      const a = armPoint(ring.r, deg, ring.tilt);
      const b = armPoint(ring.r + 7, deg, ring.tilt);
      const tgt = a.z >= 0 ? "front" : "back";
      const line = `<line class="tickm" x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}"
        x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="${ring.col}"
        stroke-width=".7" opacity="${a.z >= 0 ? .5 : .16}"/>`;
      if (tgt === "front") front += line; else back += line;
      /* glyphs only where they fit */
      if (ring.n <= 12 || (ring.n === 27 && i % 3 === 0) || (ring.n === 24 && i % 2 === 0)){
        const g = armPoint(ring.r + 17, deg + (180 / ring.n), ring.tilt);
        const txt = ring.id === "trop" || ring.id === "sid" ? SIGN_GLYPH[i]
                  : ring.id === "nak" ? NAKSHATRA[i][0].slice(0,3).toUpperCase()
                  : ring.id === "rune" ? HOUSES[Math.floor(i/2)][i % 2 ? "egress" : "ingress"][0]
                  : "";
        if (txt){
          const el = `<text class="glyph" x="${g.x.toFixed(1)}" y="${g.y.toFixed(1)}"
            font-size="${ring.id === "nak" ? 6 : ring.id === "rune" ? 11 : 12}"
            fill="${ring.col}" opacity="${g.z >= 0 ? .8 : .2}">${txt}</text>`;
          if (g.z >= 0) front += el; else back += el;
        }
      }
    }
    const tp = armPoint(ring.r, 90 + ring.spin * armMorph, ring.tilt);
    front += `<text class="ring-tag" x="${tp.x.toFixed(1)}" y="${(tp.y - 9).toFixed(1)}"
      opacity="${tp.z >= 0 ? .5 : .12}">${ring.tag}</text>`;
  }

  /* the bodies, on the sidereal ring, with a spoke to the hub */
  for (const b of BODY_ORDER){
    const deg = ay + norm(CHART.sid[b]);
    const p = armPoint(ARM_RINGS[1].r, deg, ARM_RINGS[1].tilt);
    const near = p.z >= 0;
    const sel = armSel === b;
    const el = `<g class="pl ${sel ? "sel" : ""}" data-arm-body="${b}">
      <line class="spoke" x1="500" y1="400" x2="${p.x.toFixed(1)}" y2="${p.y.toFixed(1)}"
        opacity="${near ? .12 : .05}"/>
      <circle class="pl-dot" cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5.5"
        fill="#020405" stroke="${near ? "#c8f7ff" : "rgba(156,180,166,.3)"}" stroke-width="1"/>
      <circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="14" fill="transparent"/>
      <text class="pl-gl" x="${p.x.toFixed(1)}" y="${(p.y + 4).toFixed(1)}"
        opacity="${near ? 1 : .32}">${GLYPH[b]}</text></g>`;
    if (near) front += el; else back += el;
  }

  /* harmonic chords through the middle, drawn on the sidereal ring */
  let chords = "";
  for (let i = 0; i < CLASSICAL.length; i++)
    for (let j = i+1; j < CLASSICAL.length; j++){
      const A = aspectBetween(CHART.trop[CLASSICAL[i]], CHART.trop[CLASSICAL[j]]);
      if (!A) continue;
      const p1 = armPoint(ARM_RINGS[1].r - 8, ay + norm(CHART.sid[CLASSICAL[i]]), ARM_RINGS[1].tilt);
      const p2 = armPoint(ARM_RINGS[1].r - 8, ay + norm(CHART.sid[CLASSICAL[j]]), ARM_RINGS[1].tilt);
      const dim = armSel && armSel !== CLASSICAL[i] && armSel !== CLASSICAL[j];
      chords += `<path class="asp ${dim ? "dim" : ""}" stroke="${A.col}"
        d="M${p1.x.toFixed(1)},${p1.y.toFixed(1)} Q500,400 ${p2.x.toFixed(1)},${p2.y.toFixed(1)}"
        opacity="${(1 - A.orb / (A.orb + 6)) * .6 + .12}"/>`;
    }

  return `<svg class="armil" viewBox="120 60 760 690" id="armilSVG">
    ${back}${chords}${vajraSVG()}${front}</svg>`;
}

function armPaint(){
  const host = document.getElementById("armHost");
  if (!host) return;
  host.innerHTML = armillarySVG();
}

function armTick(){
  if (!window.__armVisible){
    armRAF = null; return;
  }
  let live = false;
  /* ease the morph toward its target */
  if (Math.abs(armMorph - armMorphTo) > 0.001){
    armMorph += (armMorphTo - armMorph) * 0.075;
    live = true;
  } else if (armMorph !== armMorphTo){
    armMorph = armMorphTo;
    live = true;
  }
  /* the rings only turn once they have separated */
  if (armSpin && armMorph > 0.05){
    ARM_RINGS.forEach((r, i) => { r.spin += 0.055 * (i % 2 ? -1 : 1) * (1 + i * 0.18); });
    live = true;
  }
  if (live) armPaint();
  armRAF = requestAnimationFrame(armTick);
}
function armStart(){ if (!armRAF) armRAF = requestAnimationFrame(armTick); }

function armToggle(){
  armOpen = !armOpen;
  armMorphTo = armOpen ? 1 : 0;
  armPitchUser = null;
  document.body.classList.toggle("arm-open", armOpen);
  if (armOpen){
    Sound.chord([63.11, 94.67, 126.22, 189.33], { bloomMs:140, hold:2.6 });
  } else {
    ARM_RINGS.forEach(r => { r.spin = 0; });
    bowl(126.22, .45);
  }
  const p = document.getElementById("armPitch");
  if (p) p.value = ARM_PITCH_OPEN;
  armStart();
}

function armillaryPanel(){
  if (!CHART) return `<div class="empty">Cast a chart to build the armillary</div>`;
  return `
    <div class="howto"><h5>Closed, then open</h5>
      <p>Closed, the five frames lie in one plane and this is an ordinary flat wheel — tropical
      signs outermost, then sidereal, the sixty-four gates, the twenty-seven mansions, the
      twenty-four runes. That is the reading pose and it is the right one most of the time.</p>
      <p>Touch it and it opens. The frames separate onto five different tilts, because
      <em>they genuinely do not share a plane</em> — the two zodiacs are offset by the ayanamsa,
      the gates run on their own anchor at 2° Aquarius, the mansions and runes on two more. A
      flat wheel has to pick one and hide the rest. Opened, you see all five disagreeing at once,
      which is the actual situation. Touch it again to close.</p>
      <p>Once open: drag to turn, and the far half of each ring goes dashed so you can tell which
      is in front. The hub unfolds into a vajra on the nodal axis — double-ended, indestructible,
      and the one line in a chart with a top and a bottom and no middle.</p></div>
    <div class="arm-wrap">
      <div>
        <div class="arm-stage">
          <div id="armHost">${armillarySVG()}</div>
          <div class="arm-cue">touch the wheel to open it</div>
        </div>
        <div class="arm-ctl">
          <button data-arm-spin class="${armSpin ? "on" : ""}">${armSpin ? "Turning" : "Still"}</button>
          <span>lean</span>
          <input type="range" id="armPitch" min="14" max="88" value="${ARM_PITCH_OPEN}">
          <span>turn</span>
          <input type="range" id="armYaw" min="0" max="359" value="${armYaw}">
          <button data-arm-close>Close it</button>
        </div>
      </div>
      <div id="armGloss">${armSel ? bodyGlossary(armSel) : `
        <div class="gloss" style="border-left-color:var(--jade)">
          <h3 style="font-size:20px">The five frames</h3>
          <div class="sub">touch a body to open it</div>
          ${ARM_RINGS.map(r => `<div class="gr"><dt>${r.tag}</dt>
            <dd>${r.n} divisions · opens to ${r.tilt}°</dd></div>`).join("")}
          <div class="gr"><dt>Ayanamsa</dt><dd>${CHART.ay.toFixed(4)}° — the offset between the
            outer two rings</dd></div>
          <div class="gr"><dt>Hub</dt><dd>Vajra on the Rahu–Ketu axis</dd></div>
        </div>`}</div>
    </div>`;
}

/* Harmonic divisions of the circle, with working orbs. */
const HARMONICS = [
  { n:1, deg:0,   name:"Conjunction", orb:8, col:"#d9d4c4" },
  { n:2, deg:180, name:"Opposition",  orb:8, col:"#b0574a" },
  { n:3, deg:120, name:"Trine",       orb:7, col:"#5f9c86" },
  { n:4, deg:90,  name:"Square",      orb:7, col:"#ffcc33" },
  { n:6, deg:60,  name:"Sextile",     orb:5, col:"#a3e635" }
];
function aspectBetween(a, b){
  let d = Math.abs(norm(a - b));
  if (d > 180) d = 360 - d;
  for (const h of HARMONICS)
    if (Math.abs(d - h.deg) <= h.orb) return { ...h, exact:d, orb:Math.abs(d - h.deg) };
  return null;
}

/* ---- the glossary ---- */
function bodyGlossary(b){
  if (!CHART) return "";
  const trop = CHART.trop[b], sid = CHART.sid[b];
  const h = houseOf(sid, CHART.ascS), hh = HOUSES[h-1];
  const nk = nakIndex(sid), pada = Math.floor((norm(sid) % NAK_ARC) / (NAK_ARC/4)) + 1;
  const gN = CHART.natal.personality[b], gD = CHART.natal.design[b];
  const half = degIn(sid) < 15 ? "ingress" : "egress";
  const rune = half === "ingress" ? hh.ingress : hh.egress;
  const kar = Object.keys(CHART.karakas || CHART.karaka || {}).find(k =>
    (CHART.karaka || {})[k] === b);
  const karT = Object.keys(CHART.karakaT || {}).find(k => CHART.karakaT[k] === b);
  const st = STATIONS.find(s => s.feeder === b);
  const seatNum = Object.keys(NUM_SEAT).find(n => NUM_SEAT[n].graha === b);
  const D = dashaTree();
  const isMaha = D && D.cur.lord === b, isAntar = D && D.curA.lord === b;

  const others = Object.keys(GLYPH).filter(x => x !== b).map(x => {
    const rel = panchadhaMaitri(b, x);
    const R = RESONANCE[rel];
    const A = aspectBetween(trop, CHART.trop[x]);
    return { x, rel, R, A };
  }).sort((p,q) => (p.R.ratio[0]*p.R.ratio[1]) - (q.R.ratio[0]*q.R.ratio[1]));

  return `
    <div class="gloss">
      <h3>${GLYPH[b]} ${b}</h3>
      <div class="sub">${signOf(sid)} ${degIn(sid).toFixed(2)}° sidereal ·
        ${signOf(trop)} ${degIn(trop).toFixed(2)}° tropical</div>
      <dl>
        <div class="gr"><dt>House</dt><dd><span class="swatch" style="background:${hh.hex}"></span>${
          h} · ${hh.color}<br><span style="font-size:11.5px;color:rgba(217,212,196,.5)">${
          hh.phase}</span></dd></div>
        <div class="gr"><dt>Mansion</dt><dd>${NAKSHATRA[nk][0]} · pada ${pada}<br>
          <span style="font-size:11.5px;color:rgba(217,212,196,.5)">${ENGINE[nk][1]} shakti —
          ${ENGINE[nk][2]}</span></dd></div>
        <div class="gr"><dt>Rune</dt><dd><span style="font-family:var(--rune);font-size:17px;
          color:var(--gold)">${rune[0]}</span> ${rune[1]} · ${half}</dd></div>
        <div class="gr"><dt>Rave gate</dt><dd>${gN ? gN.gate + "." + gN.line + " " +
          (GATE_NAME[gN.gate]||"") : "—"}${gD ? `<br><span style="font-size:11.5px;
          color:rgba(217,212,196,.5)">design ${gD.gate}.${gD.line}</span>` : ""}</dd></div>
        ${kar ? `<div class="gr"><dt>Karaka</dt><dd>${kar.replace("karaka","")}${karT && karT !== kar ? ` <small>· tropical ${karT.replace("karaka","")}</small>` : ""}</dd></div>` : ""}
        ${st ? `<div class="gr"><dt>Feeds</dt><dd>${st.station} · ${st.world} · ${
          st.bifrost}<br><span style="font-size:11.5px;color:rgba(217,212,196,.5)">${
          st.hz.toFixed(2)} Hz · ${st.operator}</span></dd></div>` : ""}
        ${seatNum ? `<div class="gr"><dt>Stavefall</dt><dd>number ${seatNum}</dd></div>` : ""}
        ${(isMaha || isAntar) ? `<div class="gr"><dt>Running</dt><dd style="color:var(--jade)">${
          isMaha ? "mahadasha" : ""}${isMaha && isAntar ? " and " : ""}${
          isAntar ? "antardasha" : ""} now</dd></div>` : ""}
      </dl>

      <h4>Harmony to the others</h4>
      <div class="nw-legend" style="margin:2px 0 4px">
        <span>compound · ratio · angle</span></div>
      ${others.map(({x, rel, R, A}) => `
        <div class="harm" data-harm="${b}|${x}">
          <span class="g">${GLYPH[x]}</span>
          <span class="rel" style="color:${RESON_COL[rel]}">${rel}</span>
          <span class="rt">${R.ratio[0]}:${R.ratio[1]}</span>
          <span class="ang">${A ? A.name.slice(0,4).toLowerCase() + " " + A.orb.toFixed(1) + "°" : "—"}</span>
        </div>`).join("")}
      <p class="kenning" style="font-size:12px;margin-top:14px">Ordered by consonance. The ratio
      is the compound relationship read from your own wheel; the angle is the actual geometry
      between the two bodies. They are different questions and they often disagree — a great
      friend can sit on a square, and that tension is real in both directions.</p>
      <button class="play" data-sound-body="${b}" style="margin-top:14px">Sound it</button>
    </div>`;
}

/* ============================================================
   THE RESONANCE BENCH · a thing to play, not a thing to read
   Three ways in, none of them a quiz:
     the bench  — put any two grahas together and hear them
     the scrub  — drag through your own life and hear it change
     the ladder — play the six states in order, low to high
   ============================================================ */
let benchRoot = null, benchIv = null, scrubJD = null;

/** resonanceState, but for an arbitrary pair rather than the live one. */
/* The outer three have no natural friendships in the Parashari scheme
   and no station on the ladder, so they are not offered as roots or
   intervals. Asked for one anyway, the engine says so rather than
   inventing a relationship. */
function pairResonance(root, iv){
  if (OUTER.includes(root) || OUTER.includes(iv)){
    const R = RESONANCE["neutral"];
    return { root, lord2:iv, rel:"neutral", ...R,
      natural:"—", temporal:"—", houses:null,
      outer:true,
      reads:"One of these is an outer planet. They have no natural friendships in " +
            "the Parashari scheme and no seat on the Planetary Ladder, so no compound " +
            "relationship exists to read. They are plotted, not related.",
      rootHz:TONE[root] || 63.11, ivHz:(TONE[root] || 63.11) * R.ratio[0] / R.ratio[1],
      cents:0, beat:0 };
  }
  const rel = panchadhaMaitri(root, iv);
  const R = RESONANCE[rel];
  const rootHz = TONE[root] || (root === "Rahu" ? 63.11 : 47.33);
  return { root, lord2:iv, rel, ...R,
    natural: naturalRel(root, iv), temporal: temporalRel(root, iv),
    houses: housesBetween(root, iv),
    rootHz, ivHz: rootHz * R.ratio[0] / R.ratio[1],
    cents: 1200 * Math.log2(R.ratio[0] / R.ratio[1]),
    beat: Math.abs(rootHz * R.ratio[0] / R.ratio[1] - rootHz) };
}

function soundPair(root, iv){
  const r = pairResonance(root, iv);
  Sound.chord([r.rootHz / 2, r.rootHz, r.ivHz, r.rootHz * 2], { bloomMs:0, hold:3.2 });
  return r;
}

/* ---- the beat meter ----
   Two sine traces and their sum. When the ratio is simple the sum
   repeats quickly and looks steady; as the integers grow the sum
   takes longer to close and the envelope visibly heaves. That
   heaving is what roughness is. */
function beatSVG(rootHz, ivHz){
  const W = 700, H = 74, mid = H/2, cyc = 4;
  const period = 1 / (rootHz / cyc);
  const pts = (f, amp, off) => {
    let d = "";
    for (let i = 0; i <= 340; i++){
      const t = (i / 340) * period;
      const y = mid + off - amp * Math.sin(2 * Math.PI * f * t);
      d += (i ? "L" : "M") + (i / 340 * W).toFixed(1) + "," + y.toFixed(1) + " ";
    }
    return d;
  };
  let sum = "";
  for (let i = 0; i <= 340; i++){
    const t = (i / 340) * period;
    const y = mid - 13 * (Math.sin(2*Math.PI*rootHz*t) + Math.sin(2*Math.PI*ivHz*t)) / 2;
    sum += (i ? "L" : "M") + (i / 340 * W).toFixed(1) + "," + y.toFixed(1) + " ";
  }
  return `<svg class="beat" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <path class="wA" d="${pts(rootHz, 8, -22)}"/>
    <path class="wB" d="${pts(ivHz, 8, 22)}"/>
    <path class="sum" d="${sum}"/></svg>`;
}

/* ---- the scrub ---- */
function dashaAt(jd){
  const D = dashaTree();
  const m = D.maha.find(x => jd >= x.from && jd < x.to) || D.maha[0];
  const a = subPeriods(m.lord, m.from, m.years).find(x => jd >= x.from && jd < x.to);
  return { maha:m, antar:a || subPeriods(m.lord, m.from, m.years)[0] };
}

function scrubRead(jd){
  const at = dashaAt(jd);
  const r = pairResonance(at.maha.lord, at.antar.lord);
  return { jd, ...at, r };
}

/* ---- the panel ---- */
function resonanceGame(){
  if (!CHART) return `<div class="empty">Cast a chart to open the bench</div>`;
  const live = resonanceState();
  if (benchRoot === null){ benchRoot = live.root; benchIv = live.lord2; }
  const r = pairResonance(benchRoot, benchIv);
  const G = CLASSICAL;
  const D = live.tree;
  const span = { from: Math.max(D.maha[0].from, CHART.jd || D.maha[0].from), to: D.maha[D.maha.length-1].to };   // the clock runs from before birth; the scrub starts at birth
  const s = scrubRead(scrubJD ?? jdNow());

  const pick = (side, sel) => `<div class="gpick">${G.map(g => {
    const hz = TONE[g];
    return `<button data-bench="${side}" data-g="${g}" class="${g === sel ? "on" : ""}">
      ${GLYPH[g]}<span class="hz">${hz ? hz.toFixed(0) : "—"}</span></button>`;
  }).join("")}</div>`;

  return `
    <div class="howto"><h5>The bench</h5>
      <p>Put any two grahas together and listen. The <em>root</em> sounds its own tone; the
      <em>interval</em> sounds above it at whatever ratio your chart's compound relationship
      dictates. Nothing is being tested — the point is to get the six states into your ear, so
      that when a period turns you recognise the change before you look it up.</p>
      <p>The trace below draws both tones and their sum. When the ratio is simple the sum closes
      quickly and sits steady. As the integers grow it takes longer to close and the envelope
      starts to heave — <em>that heaving is what roughness is</em>, and it is the same thing your
      body registers as friction in a hard period.</p></div>

    <div class="bench">
      <div class="side root"><h6>Root · the mahadasha lord</h6>${pick("root", benchRoot)}</div>
      <div class="side iv"><h6>Interval · the antardasha lord</h6>${pick("iv", benchIv)}</div>
    </div>

    <div class="beat-key">
      <span><i style="background:var(--celadon)"></i>root ${r.rootHz.toFixed(2)} Hz</span>
      <span><i style="background:var(--jade)"></i>interval ${r.ivHz.toFixed(2)} Hz</span>
      <span><i style="background:var(--gold)"></i>their sum</span>
      <span>beat ${r.beat.toFixed(2)} Hz</span>
    </div>
    ${beatSVG(r.rootHz, r.ivHz)}

    <div class="reson" style="border-left-color:${RESON_COL[r.rel]};margin-top:6px">
      <div class="state" style="color:${RESON_COL[r.rel]}">${r.state}</div>
      <div class="iv">${r.root} → ${r.lord2} · ${r.interval} · ${r.ratio[0]}:${r.ratio[1]} ·
        ${r.cents.toFixed(0)} cents</div>
      <p style="margin:13px 0 0;font-size:14px;color:rgba(217,212,196,.8)">${r.reads}</p>
      <dl>
        <div class="r"><dt>Natural</dt><dd>${r.natural}</dd></div>
        <div class="r"><dt>Temporal</dt><dd>${r.temporal}${r.houses
          ? ` — ${r.lord2} stands ${r.houses} from ${r.root} in your wheel` : ""}</dd></div>
        <div class="r"><dt>Compound</dt><dd style="color:${RESON_COL[r.rel]}">${r.rel}</dd></div>
      </dl>
      <button class="play" data-sound-pair>Sound it</button>
      ${(benchRoot !== live.root || benchIv !== live.lord2)
        ? `<button class="play" data-bench-live style="margin-left:18px">Back to now</button>` : ""}
    </div>

    <div class="hr" style="margin:28px 0 20px"></div>
    <div class="howto"><h5>The scrub</h5>
      <p>Drag through your own life. The reading follows the handle — which period you are in,
      which lords are sounding, and what the interval between them is. Move slowly through a
      boundary and you will hear the state change at the exact moment the sub-period turns.</p></div>
    <div class="scrub">
      <div class="scrub-head"><span>born ${fmtYM(span.from)}</span>
        <b>${fmtFull(s.jd)} · age ${ageAt(s.jd).toFixed(1)}</b>
        <span>${fmtYM(span.to)}</span></div>
      <input type="range" id="scrubber" min="0" max="1000"
        value="${(((scrubJD ?? jdNow()) - span.from) / (span.to - span.from) * 1000).toFixed(0)}">
      <div class="scrub-out">
        <div><div class="k">Mahadasha</div><div class="v">${s.maha.lord}</div></div>
        <div><div class="k">Antardasha</div><div class="v">${s.antar.lord}</div></div>
        <div><div class="k">Interval</div><div class="v">${s.r.ratio[0]}:${s.r.ratio[1]}</div></div>
        <div><div class="k">State</div>
          <div class="v" style="color:${RESON_COL[s.r.rel]}">${s.r.state}</div></div>
      </div>
    </div>

    <div class="hr" style="margin:28px 0 20px"></div>
    <div class="howto"><h5>The ladder</h5>
      <p>The six states in order, lowest tension to highest, all sounded on the same root so the
      only thing changing is the interval. Play them top to bottom once and the scale is in your
      ear. The jump you are listening for is between <em>Neutral</em> and <em>Enemy</em> — that is
      where consonance actually ends.</p></div>
    <div class="ladder">
      ${["self","great friend","friend","neutral","enemy","great enemy"].map(k => {
        const R = RESONANCE[k];
        return `<button data-ladder="${k}" style="border-left-color:${RESON_COL[k]}">
          <span class="nm">${R.state}</span>
          <span class="rt">${R.ratio[0]}:${R.ratio[1]}</span>
          <span class="rd">${R.interval} · ${(1200*Math.log2(R.ratio[0]/R.ratio[1])).toFixed(0)} cents ·
            complexity ${R.ratio[0]*R.ratio[1]}</span></button>`;
      }).join("")}
    </div>
    <button class="ladder-play" data-ladder-all>Play the whole ladder ↓</button>
    <p class="kenning" style="font-size:13px;margin-top:16px">Complexity is the product of the two
    numbers in the ratio, and it is a fair proxy for roughness: 1, 6, 20, 30, 72, 1440. It rises
    the whole way, which is the property the ladder needs and did not have before the minor third
    and the major second were swapped.</p>`;
}

/* ============================================================
   NUMBER TO GRAHA · derived, not imported
   The nine numbers are seated on the Planetary Ladder rather
   than borrowed from a numerology tradition. Crown down: the Sun
   feeds the crown and takes 1; the Moon the brow and takes 2;
   then the five in the order the ladder already climbs them —
   Saturn at the throat, Jupiter at the heart, Mars at the solar
   plexus, Venus at the sacrum, Mercury at the root.

   The ladder's own rule is checked and holds: root to throat is
   strictly increasing in sidereal period (Mercury 88 days, Venus
   225, Mars 687, Jupiter 4,333, Saturn 10,759), with the two
   luminaries set apart above it.

   That fills seven. The nodes are not stations — they are the
   pole the stations are threaded on — so they take the two
   numbers left. Rahu is 8, standing above the crown. Ketu is 9,
   standing below the feet, and 9 is the modulus itself: in
   mod-nine arithmetic nine is zero, which is the right seat for
   the tail, the vanishing point, the one that carries nothing.

   Consequence worth knowing: a Stavefall number is no longer a
   bare planet name. It is a full station address — realm, band,
   colour, tone, operator — because the ladder already carries
   all of that. Numbers 8 and 9 are silent by doctrine: the nodes
   feed nothing, so they have no tone.
   ============================================================ */
const NUM_SEAT = {
  1: { graha:"Sun",     station:"asgard",     name:"Crown",        realm:"Asgard" },
  2: { graha:"Moon",    station:"alfheim",    name:"Brow",         realm:"Alfheim" },
  3: { graha:"Saturn",  station:"vanaheim",   name:"Throat",       realm:"Vanaheim" },
  4: { graha:"Jupiter", station:"midgard",    name:"Heart",        realm:"Midgard" },
  5: { graha:"Mars",    station:"muspelheim", name:"Solar plexus", realm:"Muspelheim" },
  6: { graha:"Venus",   station:"nidavellir", name:"Sacrum",       realm:"Nidavellir" },
  7: { graha:"Mercury", station:"hel",        name:"Root",         realm:"Hel" },
  8: { graha:"Rahu",    station:null, name:"The pole above", realm:"north of the crown" },
  9: { graha:"Ketu",    station:null, name:"The pole below", realm:"south of the feet" }
};

const jdNow = () => Date.now() / 86400000 + 2440587.5;
const jdToDay = jd => new Date((jd - 2440587.5) * 86400000);
const fmtYM = jd => jdToDay(jd).toLocaleDateString(undefined, { year:"numeric", month:"short" });
const fmtFull = jd => jdToDay(jd).toLocaleDateString(undefined,
  { year:"numeric", month:"short", day:"numeric" });
const ageAt = jd => ((jd - CHART.jd) / YEAR);

/** Sub-periods of a period, in the same order, proportional to their own spans. */
function subPeriods(lord, from, years){
  const i = DASHA_SEQ.findIndex(d => d[0] === lord);
  const out = [];
  let c = from;
  for (let k = 0; k < 9; k++){
    const [l, y] = DASHA_SEQ[(i + k) % 9];
    const len = years * y / 120;
    out.push({ lord:l, from:c, to:c + len * YEAR, years:len });
    c += len * YEAR;
  }
  return out;
}

function dashaTree(){
  if (!CHART) return null;
  const span = NAK_ARC;
  const moonNak = Math.floor(norm(CHART.sid.Moon) / span);
  const through = (norm(CHART.sid.Moon) % span) / span;
  const first = DASHA_SEQ[moonNak % 9];
  const balance = first[1] * (1 - through);

  const maha = [];
  let c = CHART.jd + balance * YEAR;
  maha.push({ lord:first[0], years:first[1], from:CHART.jd - first[1] * through * YEAR,
              to:c, partial:true, elapsedAtBirth:first[1] * through });
  let i = DASHA_SEQ.findIndex(d => d[0] === first[0]);
  for (let k = 1; k <= 9; k++){
    const [l, y] = DASHA_SEQ[(i + k) % 9];
    maha.push({ lord:l, years:y, from:c, to:c + y * YEAR });
    c += y * YEAR;
  }
  const now = jdNow();
  maha.forEach(m => { m.now = now >= m.from && now < m.to; m.past = now >= m.to; });

  const cur = maha.find(m => m.now) || maha[0];
  const antars = subPeriods(cur.lord, cur.from, cur.years);
  antars.forEach(a => { a.now = now >= a.from && now < a.to; a.past = now >= a.to; });
  const curA = antars.find(a => a.now) || antars[0];
  const praty = subPeriods(curA.lord, curA.from, curA.years);
  praty.forEach(p => { p.now = now >= p.from && now < p.to; p.past = now >= p.to; });
  const curP = praty.find(p => p.now) || praty[0];

  return { moonNak, through, balance, maha, antars, praty, cur, curA, curP, now };
}

const SIGN_GLYPH = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];

/* ============================================================
   THE COLOUR ROOM · rebuilt as a wheel you can work
   ============================================================ */
let hueFocus = null;

function hueWheelSVG(){
  const C = 150, RO = 138, RI = 76;
  const P = (r, d) => [C + r * Math.cos(d * Math.PI/180),
                       C + r * Math.sin(d * Math.PI/180)];
  let o = `<svg class="hue-wheel" viewBox="0 0 300 300" id="hueWheel">`;
  for (let i = 0; i < 12; i++){
    const a0 = angleHouse(i + 1), a1 = a0 + 30, mid = a0 + 15;
    const [x1,y1] = P(RO, a0), [x2,y2] = P(RO, a1);
    const [x3,y3] = P(RI, a1), [x4,y4] = P(RI, a0);
    o += `<g class="sec" data-hue="${i+1}">
      <path d="M${x1},${y1} A${RO},${RO} 0 0 1 ${x2},${y2} L${x3},${y3}
        A${RI},${RI} 0 0 0 ${x4},${y4} Z" fill="${HOUSES[i].hex}"/>
      <text class="num" x="${P(RO-24, mid)[0]}" y="${P(RO-24, mid)[1]+4}">${i+1}</text>
      <text class="cls" x="${P(RO-40, mid)[0]}" y="${P(RO-40, mid)[1]+3}">${
        HUE_CLASS[i].slice(0,4).toUpperCase()}</text>
    </g>`;
  }
  /* relation chords, drawn from the focused house */
  o += `<g id="hueLinks">`;
  for (let i = 0; i < 12; i++){
    const [ax,ay] = P(RI-4, angleHouse(i + 1) + 15);
    for (const d of [3,4,6]){
      const j = (i + d) % 12;
      const [bx,by] = P(RI-4, angleHouse(j + 1) + 15);
      o += `<path class="lnk" data-from="${i+1}" data-d="${d}"
        d="M${ax},${ay} Q${C},${C} ${bx},${by}"
        stroke="${d===6?"#d9d4c4":d===4?"#5f9c86":"#ffcc33"}"/>`;
    }
  }
  o += `</g><circle cx="${C}" cy="${C}" r="${RI-6}" fill="var(--void)" opacity=".9"/>
    <text x="${C}" y="${C-6}" text-anchor="middle" style="font-family:var(--mono);font-size:8px;
      letter-spacing:.22em;fill:rgba(217,212,196,.3)">TWELVE HOUSES</text>
    <text x="${C}" y="${C+8}" text-anchor="middle" style="font-family:var(--mono);font-size:8px;
      letter-spacing:.22em;fill:rgba(217,212,196,.3)">TWELVE HUES</text>
    <text x="${C}" y="${C+24}" text-anchor="middle" id="hueCentre"
      style="font-family:var(--serif);font-size:13px;fill:var(--celadon)"></text></svg>`;
  return o;
}

function colourRoom(){
  return `
    <div class="howto"><h5>How to use this</h5>
      <p>The colour wheel and the chart are both circles divided into twelve, and both take their
      relationships from angular distance. Click any house on the wheel to isolate it — the
      chords show its <em>square</em> at a quarter turn, its <em>trine</em> at a third, and its
      <em>complementary opposition</em> straight across.</p>
      <p>Below, the lab: put a planet in a house and watch what happens between the disc and the
      field. Chromatic grahas carry a hue and meet the room's hue. Achromatic ones have none, so
      they change the room's <em>value</em> or <em>saturation</em> instead.</p></div>

    ${hueWheelSVG()}
    <div id="hueRead" style="margin:18px 0 8px;min-height:64px"></div>

    <div class="hue-grid">${HOUSES.map((h,i) =>
      `<div class="hue-cell" data-hue="${h.n}" style="background:${h.hex};color:${
        ["Yellow","Yellow-orange","Yellow-green"].includes(h.color) ? "#0b100e" : "#f2f6f1"}">
        <div class="n">HOUSE ${h.n}</div><div class="h">${h.color}</div>
        <div class="e">${HUE_CLASS[i]} · ${HUE_ELEMENT[i]}</div></div>`).join("")}</div>

    <div class="pair"><em>The elements sort themselves</em><span>nobody arranged it</span></div>
    <p class="kenning" style="font-size:14px">Three hues are primary and cannot be mixed from
    anything else. They land on <b style="color:var(--jade);font-weight:400">houses 1, 5 and 9 —
    the fire trine</b>. Three are secondary, each the meeting of two primaries, and they land on
    3, 7 and 11 — the air trine, where things combine. The six tertiaries fill earth and water:
    earth follows a primary and consolidates what fire began; water leads into one and dissolves
    toward the fire ahead.</p>

    <div class="hr" style="margin:26px 0 20px"></div>
    ${colourLab()}

    <div class="hr" style="margin:26px 0 20px"></div>
    <div class="pair"><em>The anchor</em><span>the one real choice</span></div>
    <p class="kenning" style="font-size:14px">Red at the first house comes from Aries as the
    natural first sign and Mars as its lord. Defensible, and still a choice. Move the anchor and
    every correspondence rotates with it, including the elemental finding — so it holds because of
    where it starts, and where it starts is stated every time.</p>`;
}

function paintHue(n){
  hueFocus = hueFocus === n ? null : n;
  const wheel = $("hueWheel");
  if (wheel){
    wheel.querySelectorAll(".sec").forEach(s =>
      s.classList.toggle("dim", hueFocus !== null && +s.dataset.hue !== hueFocus &&
        ![3,4,6].some(d => (hueFocus - 1 + d) % 12 === +s.dataset.hue - 1 ||
                           (+s.dataset.hue - 1 + d) % 12 === hueFocus - 1)));
    wheel.querySelectorAll(".lnk").forEach(l =>
      l.classList.toggle("on", hueFocus !== null && +l.dataset.from === hueFocus));
    const c = wheel.querySelector("#hueCentre");
    if (c) c.textContent = hueFocus ? HOUSES[hueFocus-1].color : "";
  }
  const read = $("hueRead");
  if (!read) return;
  if (!hueFocus){ read.innerHTML = ""; return; }
  const h = HOUSES[hueFocus-1], i = hueFocus-1;
  const rel = d => {
    const j = (i + d) % 12;
    const r = HARMONY.find(x => x[0] === Math.min(d, 12-d));
    return `<div class="pair"><em><span class="swatch" style="background:${HOUSES[j].hex}"></span>
      House ${j+1} · ${HOUSES[j].color}</em><span>${r[1]} · ${r[2]}</span></div>`;
  };
  const occ = CHART ? Object.keys(GLYPH).filter(b => houseOf(CHART.sid[b], CHART.ascS) === hueFocus) : [];
  read.innerHTML = `
    <div class="pair" style="border-bottom:2px solid ${h.hex}">
      <em style="font-size:17px;color:var(--celadon)">House ${h.n} · ${h.color}</em>
      <span>${HUE_CLASS[i]} · ${HUE_ELEMENT[i]}</span></div>
    <div class="pair"><em>${h.phase}</em><span>${occ.length ?
      occ.map(b => GLYPH[b] + " " + b).join(" · ") : "no graha standing here"}</span></div>
    ${rel(3)}${rel(4)}${rel(6)}
    <div class="pair"><em>Runes seated</em><span style="font-family:var(--rune);font-size:17px">${
      h.ingress[0]} ${h.egress[0]}</span></div>`;
}

/* ============================================================
   GONGS AND BOWLS
   A struck bowl is inharmonic: its partials are not integer
   multiples, which is why it shimmers instead of sounding a
   note. These ratios are measured from Himalayan bowls, and the
   slight detune on each partial produces the beating that makes
   the tone move while it decays.
   ============================================================ */
const BOWL_PARTIALS = [
  [1.00, 1.00, 0],  [2.72, 0.42, 6],  [5.05, 0.24, -9],
  [8.10, 0.14, 11], [11.8, 0.08, -7], [16.2, 0.05, 14]
];
const GONG_PARTIALS = [
  [1.00, 1.00, 0],  [1.52, 0.62, 8],  [2.14, 0.48, -11], [2.91, 0.36, 13],
  [3.77, 0.27, -6], [4.86, 0.19, 9],  [6.35, 0.13, -14], [8.20, 0.09, 5],
  [10.4, 0.06, -8]
];

function strike(fundamental, kind, level){
  if (!Sound.raw) return;
  const ctx = Sound.raw();
  if (!ctx) return;
  if (ctx.state === "suspended") ctx.resume();
  const t0 = ctx.currentTime + 0.02;
  const set = kind === "gong" ? GONG_PARTIALS : BOWL_PARTIALS;
  const decay = kind === "gong" ? 19 : 13;
  const amp = (level || 1) * (kind === "gong" ? 0.1 : 0.13);

  set.forEach(([mult, weight, cents], i) => {
    const o = ctx.createOscillator();
    o.type = "sine";
    o.frequency.value = fundamental * mult;
    o.detune.value = cents;
    const g = ctx.createGain();
    g.gain.value = 0;
    /* higher partials die first — that is what makes a strike
       brighten at the front and darken as it rings out */
    const life = decay * Math.pow(0.72, i);
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(amp * weight, t0 + 0.006 + i * 0.004);
    g.gain.exponentialRampToValueAtTime(0.00008, t0 + life);
    /* a second voice a few cents away gives the beat */
    const o2 = ctx.createOscillator();
    o2.type = "sine";
    o2.frequency.value = fundamental * mult;
    o2.detune.value = cents + (kind === "gong" ? 7 : 3.2);
    const g2 = ctx.createGain(); g2.gain.value = 0;
    g2.gain.setValueAtTime(0, t0);
    g2.gain.linearRampToValueAtTime(amp * weight * 0.7, t0 + 0.01 + i * 0.004);
    g2.gain.exponentialRampToValueAtTime(0.00008, t0 + life * 0.9);

    Sound.into(g); Sound.into(g2);
    o.connect(g); o2.connect(g2);
    o.start(t0); o2.start(t0);
    o.stop(t0 + life + 0.4); o2.stop(t0 + life + 0.4);
  });
}

const bowl = (f, l) => strike(f || 126.22, "bowl", l);

/* ============================================================
   THE COLOUR LAB
   The field is the house's colour. The disc is the planet
   standing in it. What you can see happening between them is
   the reading.
   ============================================================ */
let labGraha = "Mars", labHouse = 7;

function colourLab(){
  return `
    <p class="kenning">The field is the house's colour. The disc is the planet standing in it.
    What you can see happening between them is the reading. Try Mars in the seventh — red on
    green, the loudest vibration the wheel can make. Then Mars in the first, where the disc very
    nearly disappears into its own field.</p>
    <div class="lab">
      <div class="lab-stage">
        <div class="lab-field" id="labField"></div>
        <div class="lab-disc" id="labDisc"></div>
        <div class="lab-read" id="labRead"></div>
      </div>
      <div>
        <div class="lab-label">Graha</div>
        <div class="picker" id="labGrahas">${
          Object.keys(GLYPH).map(g => `<button data-graha="${g}" class="${g===labGraha?"on":""}">${
            CHROMATIC[g] ? `<span class="sw" style="background:${CHROMATIC[g].hex}"></span>` :
            ACHROMATIC[g] ? `<span class="sw" style="background:${
              g==="Moon"?"#e8ece6":g==="Saturn"?"#12100e":g==="Venus"?"radial-gradient(circle at 35% 30%,#fff 0,#efe6ff 30%,#9d86e8 100%)":"#6d716c"}"></span>` :
            `<span class="sw" style="background:linear-gradient(90deg,#ff3b4e,#22e07a,#6b6bff)"></span>`
          }${GLYPH[g]} ${g}</button>`).join("")}</div>
        <div class="lab-label">Standing in house</div>
        <div class="picker" id="labHouses">${
          HOUSES.map(h => `<button data-house="${h.n}" class="${h.n===labHouse?"on":""}">
            <span class="sw" style="background:${h.hex}"></span>${h.n}</button>`).join("")}</div>
        <div id="labNotes"></div>
      </div>
    </div>`;
}

function paintLab(){
  const h = HOUSES[labHouse - 1];
  const field = $("labField"), disc = $("labDisc"), read = $("labRead"), notes = $("labNotes");
  if (!field) return;
  field.style.background = h.hex;

  let discCol = h.hex, title = "", meta = "", body = "", extra = "";

  if (CHROMATIC[labGraha]){
    const c = CHROMATIC[labGraha];
    discCol = c.hex;
    const [, name, aspect, gloss] = harmonyBetween(c.seat, labHouse);
    title = name; meta = `${labGraha} in house ${labHouse} · ${h.color} field · ${aspect}`;
    body = gloss;
    extra = `<div class="pair"><em>Graha hue</em><span>${c.hue} · seats at house ${c.seat}</span></div>
      <div class="pair"><em>Angular distance</em><span>${
        Math.min((c.seat - labHouse + 12) % 12, (labHouse - c.seat + 12) % 12)} houses</span></div>
      <p class="kenning" style="font-size:13.5px">Colour theory names its relationships by how far
      apart two hues sit on the wheel. So does astrology. Same circle, same divisions, same
      answers — neither borrowed from the other.</p>`;
  } else if (ACHROMATIC[labGraha]){
    const a = ACHROMATIC[labGraha];
    discCol = labGraha === "Venus" ? glazeDisc(h.hex) : OP_DISC[labGraha];
    title = a.op; meta = `${labGraha} in house ${labHouse} · ${h.color} field · ${a.adds}`;
    body = a.note;
    /* show the operation done to the field itself */
    const shifted = opAfter(labGraha, h.hex);
    field.style.background = (labGraha === "Venus" ? SHEEN + "," : "") +
      `linear-gradient(90deg,${h.hex} 0%,${h.hex} 38%,${shifted} 62%,${shifted} 100%)`;
    extra = `<div class="pair"><em>Operation</em><span>${a.op.toLowerCase()} — ${a.does}</span></div>
      <p class="kenning" style="font-size:13.5px">The left half of the field is the house
      untouched; the right is the house with this graha standing in it. Four grahas carry no hue
      and work on the colour instead, on two scales: the Moon and Saturn on its value, how light or
      dark it is; Venus and Rahu on its saturation, how vivid. Tint, shade and tone are colour theory's own names for adding
      white, black and grey, and that match is exact and nobody arranged it.${a.constructed
        ? ` The glaze is the painter's way of raising saturation, which no mixture can do. Giving it
      to Venus is a construction, on the meaning of <em>śukra</em>: bright, clear, pure.` : ""}</p>`;
  } else if (OUTER.includes(labGraha)){
    /* the outer three are plotted, not coloured: no graha, no hue */
    discCol = "transparent";
    title = "No colour"; meta = `${labGraha} in house ${labHouse} · ${h.color} field`;
    body = `${labGraha} is not one of the nine grahas, so the colour scheme gives it no hue and no operation. It stands in the house without changing its colour.`;
    extra = "";
  } else {
    /* Ketu, the prism */
    discCol = "transparent";
    disc.style.background = `conic-gradient(${HOUSES.map(x => x.hex).join(",")},${HOUSES[0].hex})`;
    title = "Prism"; meta = `Ketu in house ${labHouse} · ${h.color} field · construction, flagged`;
    body = UNRESOLVED.Ketu;
    extra = `<div class="pair"><em>Status</em><span style="color:var(--gold)">your decision — the reasons cut both ways</span></div>`;
  }

  if (labGraha !== "Ketu") disc.style.background = discCol;
  disc.style.boxShadow = `0 0 0 1px rgba(217,212,196,.1), 0 0 42px rgba(0,0,0,.4)`;
  read.innerHTML = `<h4>${title}</h4><div class="m">${meta}</div><p>${body}</p>`;

  const live = CHART ? houseOf(CHART.sid[labGraha], CHART.ascS) : null;
  notes.innerHTML = extra + (live ? `<div class="pair" style="margin-top:16px">
    <em>In your chart</em><span>${labGraha} stands in house ${live} — ${HOUSES[live-1].color}</span></div>
    ${live !== labHouse ? `<button class="act" data-jump="${live}">Show that instead →</button>` : ""}` : "");
}

function mixHex(a, b, t){
  const p = h => [1,3,5].map(i => parseInt(h.slice(i, i+2), 16));
  const [r1,g1,b1] = p(a), [r2,g2,b2] = p(b);
  const m = (x,y) => Math.round(x + (y - x) * t).toString(16).padStart(2,"0");
  return `#${m(r1,r2)}${m(g1,g2)}${m(b1,b2)}`;
}
let mindTab = "chart";

/* ============================================================
   THE STATION CONSOLES
   Where a chart is read from decides how it reads. The technical
   charts live in the brow, the colour doctrine in the crown, the
   dharma rave in the heart. A dense grid is the right instrument
   for analysis — it just belongs inside the ajna, not draped over
   the whole console.
   ============================================================ */

const BODY_ORDER = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu",
                    "Uranus","Neptune","Pluto"];
const GATE_TITLE = {"1":"The Creative","2":"The Receptive","3":"Difficulty at the Beginning","4":"Youthful Folly","5":"Waiting","6":"Conflict","7":"The Army","8":"Holding Together","9":"The Taming Power of the Small","10":"Treading","11":"Peace","12":"Standstill","13":"The Fellowship of Man","14":"Possession in Great Measure","15":"Modesty","16":"Enthusiasm","17":"Following","18":"Work on What Has Been Spoilt","19":"Approach","20":"Contemplation","21":"Biting Through","22":"Grace","23":"Splitting Apart","24":"Return","25":"Innocence","26":"The Taming Power of the Great","27":"Nourishment","28":"The Preponderance of the Great","29":"The Abysmal","30":"The Clinging Fire","31":"Influence","32":"Duration","33":"Retreat","34":"The Power of the Great","35":"Progress","36":"The Darkening of the Light","37":"The Family","38":"Opposition","39":"Obstruction","40":"Deliverance","41":"Decrease","42":"Increase","43":"Breakthrough","44":"Coming to Meet","45":"Gathering Together","46":"Pushing Upward","47":"Oppression","48":"The Well","49":"Revolution","50":"The Cauldron","51":"The Arousing","52":"Keeping Still","53":"Development","54":"The Marrying Maiden","55":"Abundance","56":"The Wanderer","57":"The Gentle","58":"The Joyous","59":"Dispersion","60":"Limitation","61":"Inner Truth","62":"The Preponderance of the Small","63":"After Completion","64":"Before Completion"};

/* ---------- wiring for the kept panels (branches carried over from the console) ---------- */
function repaintBench(){
  const host = document.getElementById("benchHost");
  if (host) host.innerHTML = resonanceGame();
}
let armDrag = null, armDragMoved = false;
document.addEventListener("pointerdown", e => {
  if (e.target.closest("#armilSVG") && armOpen){
    armDrag = { x:e.clientX, y:e.clientY, yaw:armYaw,
                pitch:armPitchUser !== null ? armPitchUser : armPitchNow() };
    armDragMoved = false;
  }
});
document.addEventListener("pointermove", e => {
  if (!armDrag) return;
  const dx = e.clientX - armDrag.x, dy = e.clientY - armDrag.y;
  if (Math.hypot(dx, dy) > 4) armDragMoved = true;
  if (!armDragMoved) return;
  e.preventDefault();
  armYaw = (armDrag.yaw + dx * 0.45 + 360) % 360;
  armPitchUser = Math.max(14, Math.min(88, armDrag.pitch - dy * 0.3));
  const p = document.getElementById("armPitch"), y = document.getElementById("armYaw");
  if (p) p.value = armPitchUser; if (y) y.value = armYaw;
  armPaint();
}, { passive:false });
document.addEventListener("pointerup", () => {
  armDrag = null;
  setTimeout(() => { armDragMoved = false; }, 40);
});
document.addEventListener("input", e => {
  if (e.target && (e.target.id === "armPitch" || e.target.id === "armYaw")){
    if (e.target.id === "armPitch") armPitchUser = +e.target.value;
    else armYaw = +e.target.value;
    armPaint();
  }
});
document.addEventListener("click", e => {
  if (e.target.closest("[data-sound-reson]")){ e.stopPropagation(); soundResonance(); return; }
  if (e.target.closest("[data-sound-pair]")){
    e.stopPropagation(); soundPair(benchRoot, benchIv); return; }
  if (e.target.closest("[data-bench-live]")){
    e.stopPropagation();
    const l = resonanceState(); benchRoot = l.root; benchIv = l.lord2;
    soundPair(benchRoot, benchIv); repaintBench(); return; }
  const bp = e.target.closest("[data-bench]");
  if (bp){
    e.stopPropagation();
    if (bp.dataset.bench === "root") benchRoot = bp.dataset.g; else benchIv = bp.dataset.g;
    soundPair(benchRoot, benchIv);
    repaintBench();
    return;
  }
  const ab = e.target.closest("[data-arm-body]");
  if (ab){
    e.stopPropagation();
    const b = ab.dataset.armBody;
    armSel = armSel === b ? null : b;
    if (armSel) Sound.chord([(TONE[b]||63.11)/2, TONE[b]||63.11, (TONE[b]||63.11)*1.5],
      { bloomMs:60, hold:2.4 });
    const g = document.getElementById("armGloss");
    if (g) g.innerHTML = armSel ? bodyGlossary(armSel) : "";
    armPaint();
    return;
  }
  if (e.target.closest("[data-arm-spin]")){
    e.stopPropagation(); armSpin = !armSpin;
    e.target.closest("button").classList.toggle("on", armSpin);
    e.target.closest("button").textContent = armSpin ? "Turning" : "Still";
    if (armSpin) armStart();
    return;
  }
  if (e.target.closest("[data-arm-close]")){ e.stopPropagation(); armToggle(); return; }
  if (e.target.closest("#armilSVG") && !e.target.closest("[data-arm-body]")){
    e.stopPropagation();
    if (!armDragMoved) armToggle();
    return;
  }
  const hue = e.target.closest("[data-hue]");
  if (hue){ e.stopPropagation(); paintHue(+hue.dataset.hue);
    bowl(126.22 * Math.pow(2, (+hue.dataset.hue - 1)/12), .5); return; }
  const gr = e.target.closest("[data-graha]");
  if (gr){
    e.stopPropagation(); labGraha = gr.dataset.graha;
    gr.parentElement.querySelectorAll("button").forEach(x => x.classList.remove("on"));
    gr.classList.add("on"); paintLab(); return;
  }
  const hs = e.target.closest("[data-house]");
  if (hs){
    e.stopPropagation(); labHouse = +hs.dataset.house;
    hs.parentElement.querySelectorAll("button").forEach(x => x.classList.remove("on"));
    hs.classList.add("on"); paintLab(); return;
  }
  const jump = e.target.closest("[data-jump]");
  if (jump){
    e.stopPropagation(); labHouse = +jump.dataset.jump;
    document.querySelectorAll("[data-house]").forEach(x =>
      x.classList.toggle("on", +x.dataset.house === labHouse));
    paintLab(); return;
  }
});

/* the armillary animates only while it is actually on screen */
(() => {
  const io = new IntersectionObserver(es => {
    window.__armVisible = es.some(x => x.isIntersecting) && !document.hidden;
    if (window.__armVisible) armStart();
  }, { threshold: 0.05 });
  window.watchArmillary = el => io.observe(el);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) window.__armVisible = false;
  });
})();

/* the public surface app.js uses */
window.Wyrd = {
  setChart(c){ CHART = c; benchRoot = null; benchIv = null; armSel = null; },
  armillary: armillaryPanel, colour: colourRoom, bench: resonanceGame,
  afterColour(){ paintLab(); paintHue(hueFocus || 1); },
  sky: HighSky, sound: Sound,
  helpers: { signOf, degIn, nakIndex, houseOf, norm, GLYPH, BODY_ORDER, NAKSHATRA, GATE_NAME, GATE_TITLE, HOUSES }
};
