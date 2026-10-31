"""The drawing kit for the Wyrd deck's engraved plates.

Every plate is a 380 x 360 engraving in The Völva's style: her plate tone, a hatched sky that
glows from one point, everything under a slight etched wobble, ink line with a tint, a wash and a
deep tone. Shapes are written with classes (ink, ink thin, tint, wash, mid, light, fill-ink,
hatchfill, plate); build.py writes the colours of each suit onto them.

The parts here are the ones the cards share: the planets' seals, each sign's device around the
seal, the eight suit emblems, and grounds (flame, hills, terraces, sea, cloud, rain, the river
beneath the voids). Each card's own scene is drawn in its sign's file."""
import math, random

FAMS = {
    "fire":  dict(K="#1d1712", T="#c4523c", W="#f5e1da", M="#8a2a1a", L="#faf5ec", plate="#f6f1e8", op=".62", sky=".8", hd=".8"),
    "earth": dict(K="#1d1712", T="#3e9c84", W="#e3efe7", M="#1d5e4f", L="#faf7ef", plate="#f6f1e8", op=".62", sky=".8", hd=".8"),
    "air":   dict(K="#1d1712", T="#c2902a", W="#f5ecd8", M="#7a5312", L="#fbf7ec", plate="#f6f1e8", op=".62", sky=".8", hd=".8"),
    "water": dict(K="#1d1712", T="#3f72a8", W="#e2eaf4", M="#1d3d68", L="#f8f9fb", plate="#f6f1e8", op=".62", sky=".8", hd=".8"),
    "void":  dict(K="#ece2cf", T="#b583b1", W="#261d2a", M="#5e3459", L="#33283a", plate="#0e0b10", op="1", sky=".55", hd=".7"),
}
ELEMENT = ["fire", "earth", "air", "water"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RUNES = ["Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz", "Gebo", "Wunjo", "Hagalaz", "Nauthiz", "Isa", "Jera",
         "Eihwaz", "Perthro", "Algiz", "Sowilo", "Tiwaz", "Berkano", "Ehwaz", "Mannaz", "Laguz", "Ingwaz", "Dagaz", "Othala"]
RUNE_PATH = {
    "Fehu": "M20 2L20 78M20 28.6L34.4 11.5M20 43.8L34.4 26.7", "Uruz": "M10.4 2L10.4 78M10.4 2L29.6 22.9M29.6 22.9L29.6 78",
    "Thurisaz": "M20 2L20 78M20 24.8L34.4 40M34.4 40L20 55.2", "Ansuz": "M20 2L20 78M20 7.7L34.4 24.8M20 24.8L34.4 41.9",
    "Raidho": "M20 2L20 78M20 2L34.4 19.1M34.4 19.1L20 36.2M20 36.2L34.4 78", "Kenaz": "M31.2 19.1L12 40M12 40L31.2 60.9",
    "Gebo": "M7.8 15.3L32.2 64.7M32.2 15.3L7.8 64.7", "Wunjo": "M20 2L20 78M20 2L34.4 19.1M34.4 19.1L20 36.2",
    "Hagalaz": "M10.4 2L10.4 78M29.6 2L29.6 78M10.4 32.4L29.6 47.6", "Nauthiz": "M20 2L20 78M8.8 30.5L31.2 49.5", "Isa": "M20 2L20 78",
    "Jera": "M18.4 15.3L7.8 30.5M7.8 30.5L18.4 45.7M21.6 34.3L32.2 49.5M32.2 49.5L21.6 64.7", "Eihwaz": "M20 2L20 78M20 2L32.8 15.3M20 78L7.2 64.7",
    "Perthro": "M20 2L20 78M20 5.8L32.8 19.1M32.8 19.1L32.8 5.8M20 74.2L32.8 60.9M32.8 60.9L32.8 74.2", "Algiz": "M20 2L20 78M20 34.3L7.2 11.5M20 34.3L32.8 11.5",
    "Sowilo": "M29 5.8L11 34.3M11 34.3L29 45.7M29 45.7L11 74.2", "Tiwaz": "M20 2L20 78M20 2L7.2 21M20 2L32.8 21",
    "Berkano": "M20 2L20 78M20 2L33.4 21M33.4 21L20 40M20 40L33.4 59M33.4 59L20 78", "Ehwaz": "M8.8 2L8.8 78M31.2 2L31.2 78M8.8 2L20 19.1M20 19.1L31.2 2",
    "Mannaz": "M8.8 2L8.8 78M31.2 2L31.2 78M8.8 2L31.2 32.4M31.2 2L8.8 32.4", "Laguz": "M20 2L20 78M20 2L33.4 21",
    "Ingwaz": "M20 24.8L31.2 40M31.2 40L20 55.2M20 55.2L8.8 40M8.8 40L20 24.8", "Dagaz": "M7.2 17.2L32.8 62.8M32.8 17.2L7.2 62.8M7.2 17.2L7.2 62.8M32.8 17.2L32.8 62.8",
    "Othala": "M20 7.7L32.2 28.6M20 7.7L7.8 28.6M32.2 28.6L8.8 68.5M7.8 28.6L31.2 68.5"}


def css(fam):
    p = FAMS[fam]
    return (f"svg .ink{{stroke:{p['K']};fill:none;stroke-width:2.2;stroke-linejoin:round;stroke-linecap:round}}"
            "svg .ink.heavy{stroke-width:3.2}svg .ink.thin{stroke-width:1.5}svg .ink.hair{stroke-width:.8}"
            f"svg .tint{{fill:{p['T']}}}svg .wash{{fill:{p['W']}}}svg .mid{{fill:{p['M']}}}svg .fill-ink{{fill:{p['K']}}}"
            f"svg .hatchfill{{fill:url(#hd)}}svg .plate{{fill:{p['plate']};fill-opacity:{p['op']}}}svg .light{{fill:{p['L']}}}")


def f(x):
    """A number as the plates write it: short, no trailing zeros."""
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def smooth(pts, closed=False, t=.5):
    """A Catmull-Rom curve through the points, as cubic Béziers."""
    if closed: pts = pts[-1:] + pts + pts[:2]
    else: pts = pts[:1] + pts + pts[-1:]
    d = f"M{f(pts[1][0])} {f(pts[1][1])}"
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d + ("Z" if closed else "")


def pol(cx, cy, r, a):
    a = math.radians(a)
    return cx + r * math.cos(a), cy + r * math.sin(a)


class Plate:
    """One engraving: its defs, and everything drawn inside the etched group."""
    def __init__(self, fam, seed, label, glow=(190, 170, 225), sky=360):
        self.fam, self.p, self.seed, self.label, self.glow, self.sky = fam, FAMS[fam], seed, label, glow, sky
        self.defs, self.body, self.under, self.have = [], [], [], set()
        self.rng = random.Random(seed)

    def __call__(self, *s):
        self.body.extend(s); return self

    def d(self, key, markup):
        if key not in self.have: self.have.add(key); self.defs.append(markup)
        return self

    def svg(self):
        p, (gx, gy, gr) = self.p, self.glow
        base = (f'<pattern id="sky" width="8" height="3.6" patternUnits="userSpaceOnUse"><line x1="0" y1="1.8" x2="8" y2="1.8" stroke="{p["K"]}" stroke-width="{p["sky"]}"/></pattern>'
                f'<pattern id="hd" width="3.6" height="3.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><line x1="0" y1="0" x2="0" y2="3.6" stroke="{p["K"]}" stroke-width="{p["hd"]}"/></pattern>'
                f'<pattern id="hx" width="3.6" height="3.6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="3.6" stroke="{p["K"]}" stroke-width="{p["hd"]}"/></pattern>'
                f'<radialGradient id="glowg" cx="{gx}" cy="{gy}" r="{gr}" gradientUnits="userSpaceOnUse"><stop offset="0.28" stop-color="#000"/><stop offset="0.82" stop-color="#fff"/></radialGradient>'
                f'<mask id="glow"><rect width="380" height="{self.sky}" fill="url(#glowg)"/></mask>'
                f'<filter id="etch" x="-4%" y="-4%" width="108%" height="108%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{self.seed}"/><feDisplacementMap in="SourceGraphic" scale="1.4"/></filter>')
        return (f'<defs>{base}{"".join(self.defs)}</defs><rect width="380" height="360" class="plate"/>'
                f'<rect width="380" height="{self.sky}" fill="url(#sky)" mask="url(#glow)"/>{"".join(self.under)}'
                f'<g filter="url(#etch)">{"".join(self.body)}</g>')


# ------------------------------------------------------------------ the three-stroke line (horns, ropes, garlands)
def rope(d, p, w=9, inner=6, dash=".8 3.2", fill=None, cap="round"):
    """A thick engraved band: an ink edge, a pale core, and the core's dotted grain."""
    fill = fill or p["W"]
    return (f'<path d="{d}" fill="none" stroke="{p["K"]}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{inner}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{p["K"]}" stroke-width="{inner}" stroke-dasharray="{dash}"/>')


# ------------------------------------------------------------------ the planets' seals
GLYPH = {
    "Mars": '<circle cx="186" cy="50" r="9" class="ink heavy"/><path class="ink heavy" d="M192.5 43.5L201 35M193.5 35H201V42.5"/>',
    "Sun": '<circle cx="190" cy="46" r="11" class="ink heavy"/><circle cx="190" cy="46" r="3" class="fill-ink"/>',
    "Venus": '<circle cx="190" cy="40" r="9" class="ink heavy"/><path class="ink heavy" d="M190 49V62M183.5 56H196.5"/>',
    "Mercury": '<circle cx="190" cy="45" r="6.5" class="ink heavy"/><path class="ink heavy" d="M183 32A7.5 7.5 0 0 0 197 32M190 51.5V63M184.5 57.5H195.5"/>',
    "Moon": '<path class="fill-ink" d="M197 31A15 15 0 1 0 197 61A19 19 0 0 1 197 31Z"/>',
    "Saturn": '<path class="ink heavy" d="M182 31H196M188 25V52C188 43 202 41 202 50C202 57 195 59 198 66"/>',
    "Jupiter": '<path class="ink heavy" d="M181 37C180 30 186 27 190 29C195 32 193 40 188 45C185 48 182 51 180 53H203M196 40V65"/>',
}


def seal(c, planet, cx=190, cy=46):
    p = c.p
    g = GLYPH[planet] if (cx, cy) == (190, 46) else f'<g transform="translate({f(cx - 190)} {f(cy - 46)})">{GLYPH[planet]}</g>'
    return (f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{p["T"]}" stroke-width="5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="26" class="light ink heavy"/><circle cx="{cx}" cy="{cy}" r="33" class="ink hair"/>{g}')


def sigil(planet, x, y, s=.5):
    """A planet's glyph alone, small, centred at x, y."""
    return f'<g transform="translate({f(x)} {f(y)}) scale({s}) translate(-190 -46)">{GLYPH[planet]}</g>'


def star_mark(c, planet, x, y, r=17):
    """An exaltation: the planet's glyph in a small rayed star."""
    rays = "".join(f'M{f(pol(x, y, r + 2, a)[0])} {f(pol(x, y, r + 2, a)[1])}L{f(pol(x, y, r + 9, a)[0])} {f(pol(x, y, r + 9, a)[1])}' for a in range(0, 360, 30))
    return (f'<path class="ink hair" d="{rays}"/><circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="light ink thin"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{r - 3}" fill="none" stroke="{c.p["T"]}" stroke-width="2"/>{sigil(planet, x, y, r / 30)}')


# ------------------------------------------------------------------ each sign's device, either side of the seal
def mirror(markup):
    return markup + f'<g transform="translate(380 0) scale(-1 1)">{markup}</g>'


def device(c, sign):
    p = c.p
    if sign == "Gemini":            # the twin pillars
        col = (f'<path class="wash ink thin" d="M128 22H144V72H128Z"/><path class="hatchfill" d="M138 22H144V72H138Z"/>'
               f'<path class="ink hair" d="M132 24V70M136 24V70M140 24V70"/>'
               f'<path class="light ink thin" d="M122 14H150V22H122Z"/><path class="ink thin" d="M122 14C119 10 117 6 121 4M150 14C153 10 155 6 151 4"/>'
               f'<path class="tint ink thin" d="M124 72H148V80H124Z"/><path class="light ink thin" d="M120 80H152V85H120Z"/>')
        return mirror(col) + f'<path class="ink hair" d="M121 6C150 13 230 13 259 6M120 88C150 81 230 81 260 88"/>'
    if sign == "Cancer":            # the crab's claws, reaching in
        arm = rope("M100 88C100 68 110 56 126 52", p, 10, 7)
        claw = (f'<path class="wash ink thin" d="M124 54C120 40 128 26 142 22C152 20 158 24 158 30C150 28 142 30 138 38C146 36 152 40 154 46C146 50 134 56 124 54Z"/>'
                f'<path class="hatchfill" d="M124 54C120 40 128 26 142 22C134 30 130 40 132 50Z"/>'
                f'<path class="ink hair" d="M136 26C132 32 130 40 130 48M146 24C141 28 138 34 137 40"/>'
                f'<path class="tint ink hair" d="M154 30l4 -2l-1 4ZM154 46l4 1l-3 3Z"/>')
        legs = '<path class="ink thin" d="M104 86C96 84 90 88 86 94M108 80C98 76 90 78 84 84M112 74C104 66 96 66 90 70"/>'
        return mirror(arm + f'<g transform="translate(140 38) scale(1.28) translate(-140 -38)">{claw}</g>' + legs)
    if sign == "Leo":               # two lion's heads in profile, roaring toward the seal
        return lion_face(c, 124, 46, .95) + lion_face(c, 256, 46, .95)
    if sign == "Virgo":             # two ears of wheat
        grains = "".join(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="3.2" ry="6.4" transform="rotate({r} {f(x)} {f(y)})" class="{cl} ink hair"/>'
                         for k, (x, y) in enumerate([(141, 18), (146, 26), (138, 30), (143, 38), (135, 42), (140, 50), (132, 54), (137, 62)])
                         for r, cl in [(-28 if k % 2 == 0 else 28, "tint" if k % 2 else "wash")])
        awns = '<path class="ink hair" d="M141 12L144 2M146 20L152 12M138 24L132 16M143 32L150 26M135 36L128 30M140 44L147 38M132 48L125 43"/>'
        stalk = '<path class="ink thin" d="M128 86C130 72 134 52 142 14"/><path class="ink hair" d="M130 78C122 72 116 72 110 76"/>'
        return mirror(stalk + grains + awns)
    if sign == "Libra":             # the balance: a beam behind the seal, a pan each side
        pan = lambda x: (f'<path class="ink hair" d="M{x} 40L{x - 16} 70M{x} 40L{x + 16} 70M{x} 40V70"/>'
                         f'<path class="tint ink thin" d="M{x - 20} 70H{x + 20}C{x + 18} 80 {x - 18} 80 {x - 20} 70Z"/>'
                         f'<circle cx="{x}" cy="40" r="3" class="light ink thin"/>')
        return (rope("M114 40H266", p, 8, 5) + pan(122) + pan(258) +
                '<path class="tint ink thin" d="M110 40l-6 -4v8ZM270 40l6 -4v8Z"/>')
    if sign == "Scorpio":           # two tails, arched, their stings turned to the seal
        segs = [(108, 86), (102, 72), (103, 58), (109, 44), (119, 32), (131, 23), (144, 19)]
        spine = rope(smooth(segs), p, 9, 6, ".8 3.2")
        tail = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{8.4 - k * .6:.1f}" ry="{7 - k * .5:.1f}" class="{"wash" if k % 2 else "light"} ink thin"/><path class="ink hair" d="M{x - 5 + k * .3:.1f} {y}h{10 - k * .6:.1f}"/>' for k, (x, y) in enumerate(segs))
        sting = f'<path class="tint ink thin" d="M150 12C161 12 166 20 163 28C160 23 155 22 150 24Z"/><path class="ink thin" d="M163 28L167 35"/>'
        return mirror(spine + tail + sting)
    if sign == "Sagittarius":       # the drawn bow, its arrow through the seal
        bow = rope("M108 74C110 46 140 24 190 22C240 24 270 46 272 74", p, 8, 5)
        string = '<path class="ink thin" d="M108 74L190 84L272 74"/>'
        arrow = (f'<path class="ink heavy" d="M190 84V4"/><path class="tint ink thin" d="M190 0L184 12H196Z"/>'
                 f'<path class="wash ink thin" d="M190 76L182 88L184 92L190 84L196 92L198 88Z"/>')
        return string + bow + arrow + '<path class="tint ink thin" d="M104 74l4 8l4 -6ZM276 74l-4 8l-4 -6Z"/>'
    if sign == "Capricorn":         # the goat's horns, swept back and ridged
        d = "M164 30C150 20 136 8 116 6C104 6 96 12 94 22C98 16 106 14 114 16C128 20 142 34 158 46"
        horn = (f'<path class="wash ink thin" d="{d}Z"/>'
                f'<path class="hatchfill" d="M94 22C98 16 106 14 114 16C128 20 142 34 158 46L164 40C146 26 128 16 112 14C104 14 98 18 94 22Z"/>'
                + "".join(f'<path class="ink hair" d="M{f(x)} {f(y)}l{f(dx)} {f(dy)}"/>' for x, y, dx, dy in
                          [(152, 22, -4, 14), (142, 15, -5, 13), (132, 10, -5, 11), (122, 7, -4, 10), (112, 7, -2, 9), (104, 10, 0, 7)]))
        beard = '<path class="ink thin" d="M176 76C178 84 182 88 186 92M184 78C186 86 188 90 190 94"/>'
        return mirror(horn) + beard
    if sign == "Aquarius":          # two urns, tipped to pour
        urn = (f'<g transform="rotate(28 128 44)"><path class="wash ink thin" d="M116 22H140L138 28C150 36 150 58 138 66H118C106 58 106 36 118 28Z"/>'
               f'<path class="hatchfill" d="M134 28C146 36 146 58 136 66H138C150 58 150 36 138 28Z"/>'
               f'<path class="tint ink hair" d="M110 40H146V48H110Z" clip-path="url(#urnclip)"/>'
               f'<path class="ink thin" d="M118 30C108 30 104 38 110 44M138 30C148 30 152 38 146 44"/></g>')
        stream = '<path class="ink thin" d="M146 30C154 40 150 52 158 62C162 68 160 76 164 82"/><path class="ink hair" d="M150 32C158 42 154 54 162 62"/>'
        waves = (f'<path fill="none" stroke="{p["T"]}" stroke-width="2.4" d="M120 84L132 78L144 84L156 78L168 84L180 78L192 84L204 78L216 84L228 78L240 84L252 78L264 84"/>'
                 '<path class="ink hair" d="M120 90L132 84L144 90L156 84L168 90L180 84L192 90L204 84L216 90L228 84L240 90L252 84L264 90"/>')
        c.d("urnclip", '<clipPath id="urnclip"><path d="M116 22H140L138 28C150 36 150 58 138 66H118C106 58 106 36 118 28Z"/></clipPath>')
        return mirror(urn + stream) + waves
    if sign == "Pisces":            # two fishes, nose to tail about the seal, bound by a cord
        fish = (f'<path class="wash ink thin" d="M146 18C132 22 120 34 118 48C116 58 122 66 130 70C124 60 126 48 134 38C140 30 148 24 158 22C156 18 152 16 146 18Z"/>'
                f'<path class="hatchfill" d="M118 48C116 58 122 66 130 70C126 62 126 54 128 46Z"/>'
                f'<path class="tint ink thin" d="M130 70L122 82L136 78Z"/><circle cx="150" cy="21" r="1.6" class="fill-ink"/>'
                f'<path class="ink hair" d="M128 40C132 44 132 50 128 54M136 32C140 36 140 42 136 46"/>')
        cord = f'<path class="ink hair" stroke-dasharray="3 2" d="M132 80C160 92 220 92 248 80"/>'
        fish = f'<g transform="translate(138 44) scale(1.22) translate(-138 -44)">{fish}</g>'
        return fish + f'<g transform="rotate(180 190 46)">{fish}</g>' + cord
    if sign in ("Aries", "Taurus"):
        return canvas_horns(c, sign)
    return ""


def canvas_horns(c, sign):
    """Aries's ram's horns and Taurus's bull's horns, lifted from the plates approved on the design canvas."""
    import json, os, re
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "deck", "plates")
    if sign == "Aries":
        src = json.load(open(os.path.join(here, "b00.json"), encoding="utf-8"))["svg"]
        return "".join(re.findall(r'<path d="M(?:140|240) 46L[^"]*"[^>]*/>', src))
    src = json.load(open(os.path.join(here, "b03.json"), encoding="utf-8"))["svg"]
    horn = re.search(r'<g id="@@horn".*?</g>', src)[0].replace('id="@@horn"', 'id="horn"')
    c.d("horn", horn)
    return '<use href="#horn"/><use href="#horn" transform="translate(380 0) scale(-1 1)"/>'


def lion_head(c, x, y, s=1):
    """A lion's head in profile facing right: the mane in layered locks swept back from the face, a heavy
    brow over the eye, the broad blunt muzzle with its whisker-pads, and the jaws open in the roar."""
    q = lambda dx, dy: f"{f(x + dx * s)} {f(y + dy * s)}"
    mx, my = x - 4 * s, y + 1 * s
    out = []
    for ring, (r0, r1, cls, step) in enumerate([(22, 39, "wash ink thin", 19), (19, 32, "tint ink thin", 17), (16, 25, "mid ink thin", 15)]):
        for a in range(70 + ring * 5, 296 - ring * 3, step):
            back = 22 if a < 180 else -22
            b0, b1 = pol(mx, my, r0 * s, a - 10), pol(mx, my, r0 * s, a + 10)
            tip = pol(mx, my, r1 * s, a + back)
            c1 = pol(mx, my, (r0 + r1) / 2 * s * 1.06, a - 10 + back * .35); c2 = pol(mx, my, (r0 + r1) / 2 * s * .98, a + 12 + back * .85)
            out.append(f'<path class="{cls}" d="M{f(b0[0])} {f(b0[1])}Q{f(c1[0])} {f(c1[1])} {f(tip[0])} {f(tip[1])}Q{f(c2[0])} {f(c2[1])} {f(b1[0])} {f(b1[1])}Z"/>')
            if ring < 2:
                h0 = pol(mx, my, (r0 + 3) * s, a + 2); h1 = pol(mx, my, (r1 - 6) * s, a + back * .8)
                out.append(f'<path class="ink hair" d="M{f(h0[0])} {f(h0[1])}Q{f(pol(mx, my, (r0 + r1) / 2 * s, a + back * .2)[0])} {f(pol(mx, my, (r0 + r1) / 2 * s, a + back * .2)[1])} {f(h1[0])} {f(h1[1])}"/>')
    face = (f"M{q(-6, -21)}C{q(2, -24)} {q(10, -21)} {q(14, -17)}C{q(20, -12)} {q(26, -8)} {q(30, -4)}C{q(34, -1)} {q(34, 4)} {q(32, 7)}"
            f"C{q(32, 10)} {q(31, 12)} {q(30, 13)}L{q(16, 14)}L{q(27, 21)}C{q(27, 25)} {q(24, 29)} {q(18, 29)}"
            f"C{q(10, 30)} {q(2, 27)} {q(-4, 22)}C{q(-12, 16)} {q(-15, 4)} {q(-13, -8)}C{q(-12, -15)} {q(-10, -19)} {q(-6, -21)}Z")
    out.append(f'<path class="wash ink thin" d="{face}"/>')
    out.append(f'<path fill="url(#hd)" d="M{q(-4, 22)}C{q(-12, 16)} {q(-15, 4)} {q(-13, -8)}C{q(-8, 0)} {q(-2, 12)} {q(8, 20)}C{q(14, 24)} {q(20, 26)} {q(26, 24)}C{q(24, 28)} {q(20, 29)} {q(18, 29)}C{q(10, 30)} {q(2, 27)} {q(-4, 22)}Z" opacity=".9"/>')
    out.append(f'<path class="mid ink thin" d="M{q(30, 13)}C{q(26, 13)} {q(20, 13)} {q(16, 14)}L{q(27, 21)}C{q(28, 18)} {q(30, 15)} {q(30, 13)}Z"/>'
               f'<path class="tint ink hair" d="M{q(19, 15.5)}C{q(22, 16)} {q(25, 17)} {q(27, 19)}"/>'
               f'<path class="light ink hair" d="M{q(28, 13)}L{q(27, 18)}L{q(25.5, 13)}ZM{q(22, 18.4)}L{q(23.4, 14.6)}L{q(24.6, 19.4)}Z"/>')
    out.append(f'<path class="fill-ink" d="M{q(28, -4)}C{q(32, -5)} {q(35, -1)} {q(34, 3)}C{q(32, 4)} {q(29, 2)} {q(28, -4)}Z"/>'
               f'<path class="ink thin" d="M{q(33, 4)}C{q(31, 6)} {q(28, 6)} {q(26, 5)}"/>'
               f'<ellipse cx="{f(x + 23 * s)}" cy="{f(y + 6 * s)}" rx="{f(6 * s)}" ry="{f(4.4 * s)}" class="ink hair"/>'
               + "".join(f'<circle cx="{f(x + dx * s)}" cy="{f(y + dy * s)}" r="{f(.75 * s)}" class="fill-ink"/>' for dx, dy in [(20, 5), (23, 4), (26, 5), (21, 8), (24, 8)]))
    out.append(f'<path class="ink heavy" d="M{q(1, -14)}C{q(6, -17)} {q(13, -16)} {q(18, -12)}"/>'
               f'<path class="light ink thin" d="M{q(5, -10)}C{q(8, -13)} {q(13, -13)} {q(16, -10)}C{q(13, -8)} {q(8, -8)} {q(5, -10)}Z"/>'
               f'<circle cx="{f(x + 11 * s)}" cy="{f(y - 10.3 * s)}" r="{f(1.7 * s)}" class="fill-ink"/>'
               f'<path class="ink hair" d="M{q(14, -16)}C{q(20, -12)} {q(25, -8)} {q(29, -5)}M{q(-2, -6)}C{q(2, 2)} {q(6, 8)} {q(14, 12)}M{q(-8, 0)}C{q(-6, 8)} {q(-2, 14)} {q(4, 19)}M{q(10, 23)}C{q(14, 25)} {q(18, 26)} {q(22, 25)}"/>')
    out.append(f'<path class="wash ink thin" d="M{q(-14, -16)}C{q(-18, -26)} {q(-8, -31)} {q(-2, -24)}C{q(-6, -21)} {q(-10, -18)} {q(-14, -16)}Z"/><path class="mid" d="M{q(-11, -19)}C{q(-12, -24)} {q(-7, -26)} {q(-5, -23)}Z"/>')
    return "".join(out)


def lion_face(c, x, y, s=1, roar=True):
    """A lion's face seen from the front (see _lion_face), cut once and set wherever it's wanted."""
    key = "lionface" if roar else "lionface0"
    c.d(key, f'<g id="{key}">{_lion_face(c, 0, 0, 1, roar)}</g>')
    return use(key, x, y, s)


def _lion_face(c, x, y, s=1, roar=True):
    q = lambda dx, dy: f"{f(x + dx * s)} {f(y + dy * s)}"
    out = []
    for ring, (r0, r1, cls, n, sw) in enumerate([(19, 37, "wash ink thin", 19, 18), (17, 30, "tint ink thin", 16, 15), (15, 24, "mid ink thin", 13, 11)]):
        for k in range(n):
            a = -90 + (k + ring * .5) * 360 / n
            b0, b1 = pol(x, y + 2 * s, r0 * s, a - 180 / n * 1.1), pol(x, y + 2 * s, r0 * s, a + 180 / n * 1.1)
            tip = pol(x, y + 2 * s, r1 * s, a + sw)
            c1 = pol(x, y + 2 * s, (r0 + r1) / 2 * s * 1.08, a - 4); c2 = pol(x, y + 2 * s, (r0 + r1) / 2 * s, a + sw + 10)
            out.append(f'<path class="{cls}" d="M{f(b0[0])} {f(b0[1])}Q{f(c1[0])} {f(c1[1])} {f(tip[0])} {f(tip[1])}Q{f(c2[0])} {f(c2[1])} {f(b1[0])} {f(b1[1])}Z"/>')
            if ring == 0:
                h0 = pol(x, y + 2 * s, (r0 + 3) * s, a); h1 = pol(x, y + 2 * s, (r1 - 5) * s, a + sw * .8)
                out.append(f'<path class="ink hair" d="M{f(h0[0])} {f(h0[1])}L{f(h1[0])} {f(h1[1])}"/>')
    for side in (-1, 1):
        out.append(f'<path class="wash ink thin" d="M{q(side * 9, -16)}C{q(side * 10, -26)} {q(side * 22, -26)} {q(side * 19, -13)}Z"/><path class="mid" d="M{q(side * 11, -16)}C{q(side * 12, -22)} {q(side * 18, -22)} {q(side * 17, -15)}Z"/>')
    out.append(f'<path class="wash ink thin" d="M{q(0, -19)}C{q(8, -19)} {q(15, -17)} {q(17, -11)}C{q(20, -4)} {q(20, 4)} {q(17, 10)}C{q(14, 17)} {q(8, 22)} {q(0, 23)}C{q(-8, 22)} {q(-14, 17)} {q(-17, 10)}C{q(-20, 4)} {q(-20, -4)} {q(-17, -11)}C{q(-15, -17)} {q(-8, -19)} {q(0, -19)}Z"/>')
    out.append(f'<path fill="url(#hd)" d="M{q(8, -18)}C{q(14, -16)} {q(17, -12)} {q(18, -8)}C{q(21, 0)} {q(19, 8)} {q(16, 12)}C{q(13, 17)} {q(8, 21)} {q(3, 22)}C{q(10, 14)} {q(14, 2)} {q(8, -18)}Z" opacity=".8"/>')
    for side in (-1, 1):
        out.append(f'<path class="ink heavy" d="M{q(side * 2, -8)}C{q(side * 5, -11)} {q(side * 10, -11)} {q(side * 15, -8)}"/>'
                   f'<path class="light ink thin" d="M{q(side * 3, -4)}C{q(side * 6, -8)} {q(side * 10, -9)} {q(side * 13.5, -7.5)}C{q(side * 11, -4)} {q(side * 6, -2.6)} {q(side * 3, -4)}Z"/>'
                   f'<circle cx="{f(x + side * 8.4 * s)}" cy="{f(y - 5.8 * s)}" r="{f(1.3 * s)}" class="fill-ink"/>'
                   f'<path class="ink thin" d="M{q(side * 3, -4)}C{q(side * 3.4, -1)} {q(side * 4.4, 2)} {q(side * 5.4, 4)}"/>'
                   f'<path class="ink hair" d="M{q(side * 2, -6)}C{q(side * 3, -1)} {q(side * 4, 3)} {q(side * 5, 5)}M{q(side * 4, -13)}C{q(side * 6, -15)} {q(side * 9, -15)} {q(side * 12, -13)}M{q(side * 15, -2)}C{q(side * 15, 4)} {q(side * 13, 9)} {q(side * 10, 12)}"/>'
                   f'<path class="wash ink hair" d="M{q(0, 9)}C{q(side * 2, 7)} {q(side * 9, 7)} {q(side * 10, 11)}C{q(side * 10, 14)} {q(side * 4, 15)} {q(0, 13)}Z"/>'
                   + "".join(f'<circle cx="{f(x + side * dx * s)}" cy="{f(y + dy * s)}" r="{f(.7 * s)}" class="fill-ink"/>' for dx, dy in [(4, 10), (7, 10), (5.5, 12.4)]))
    out.append(f'<path class="mid ink thin" d="M{q(-5, 2)}C{q(-3, 0)} {q(3, 0)} {q(5, 2)}C{q(4, 6)} {q(2, 8)} {q(0, 9)}C{q(-2, 8)} {q(-4, 6)} {q(-5, 2)}Z"/>')
    if roar:
        out.append(f'<path class="mid ink thin" d="M{q(-7, 14)}C{q(-6, 21)} {q(6, 21)} {q(7, 14)}C{q(3, 15)} {q(-3, 15)} {q(-7, 14)}Z"/>'
                   f'<path class="tint ink hair" d="M{q(-3, 18)}C{q(-1, 19)} {q(1, 19)} {q(3, 18)}"/>'
                   f'<path class="light ink hair" d="M{q(-5.4, 14.4)}L{q(-4.4, 18.4)}L{q(-3.4, 14.8)}ZM{q(5.4, 14.4)}L{q(4.4, 18.4)}L{q(3.4, 14.8)}Z"/>')
    out.append(f'<path class="ink thin" d="M{q(-3, 23)}C{q(-1, 26)} {q(1, 26)} {q(3, 23)}"/>')
    return "".join(out)


def crown(c, sign, planet):
    """The head of every minor card: the seal of the decan's ruler within its sign's device."""
    if sign == "Leo": c.d("maneclip", '<clipPath id="maneclip"><rect x="80" y="0" width="220" height="96"/></clipPath>')
    return device(c, sign) + seal(c, planet)


# ------------------------------------------------------------------ the suit emblems, as defs placed with <use>
def emblems(c, *names, runes=("Fehu", "Uruz")):
    p = c.p
    for n in names:
        if n == "vv":
            c.d("arm", f'<g id="arm" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["W"]}" stroke-width="1.3" d="M-5 -23C-14 -28 -12 -37 -2 -39.5L0 -26L2 -39.5C12 -37 14 -28 5 -23Z"/>'
                f'<path fill="none" stroke-width=".6" d="M-4 -25C-10 -29 -9 -35 -3 -37M4 -25C10 -29 9 -35 3 -37"/>'
                f'<path fill="none" stroke-width="1.3" d="M0 -24V-41M-2.6 -34L0 -42L2.6 -34"/>'
                f'<path fill="{p["T"]}" stroke-width="1.3" d="M-7 -15C-8 -21 -4 -24 0 -24C4 -24 8 -21 7 -15Z"/>'
                f'<path fill="none" stroke-width=".6" d="M-4 -16C-4 -20 -2 -22 0 -22M4 -16C4 -20 2 -22 0 -22"/>'
                f'<path fill="{p["L"]}" stroke-width="1.3" d="M-3.4 -10V-15H3.4V-10Z"/></g>')
            c.d("vv", f'<g id="vv"><use href="#arm"/><use href="#arm" transform="rotate(90)"/><use href="#arm" transform="rotate(180)"/><use href="#arm" transform="rotate(270)"/>'
                f'<circle r="10.5" fill="{p["L"]}" stroke="{p["K"]}" stroke-width="1.3"/><circle r="7" fill="{p["T"]}" stroke="{p["K"]}" stroke-width="1.3"/>'
                f'<path fill="none" stroke="{p["K"]}" stroke-width=".6" d="M-4.6 0A4.6 4.6 0 0 1 4.6 0M-2.4 1.8A2.6 2.6 0 0 0 2.4 1.8"/></g>')
            c.d("vvh", f'<g id="vvh"><circle r="47" fill="none" stroke="{p["T"]}" stroke-width="4"/><circle r="50" fill="none" stroke="{p["K"]}" stroke-width=".8"/>'
                f'<circle r="44" fill="none" stroke="{p["K"]}" stroke-width=".8"/><circle r="38" fill="none" stroke="{p["K"]}" stroke-width="7" stroke-dasharray=".7 3.2"/>'
                f'<use href="#vv" transform="scale(1.05)"/></g>')
        elif n == "jewel":
            c.d("jewel", f'<g id="jewel" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["T"]}" stroke-width="1.3" d="M0 -24C8 -14 16 -6 14 6C12 16 6 20 0 20C-6 20 -12 16 -14 6C-16 -6 -8 -14 0 -24Z"/>'
                f'<path fill="none" stroke-width=".6" d="M0 -18C5 -10 10 -4 9 5M0 -18C-5 -10 -10 -4 -9 5M0 -24V-15"/>'
                f'<path fill="{p["W"]}" stroke-width="1.3" d="M9.2 3.8L3.8 9.2L-3.8 9.2L-9.2 3.8L-9.2 -3.8L-3.8 -9.2L3.8 -9.2L9.2 -3.8Z"/>'
                f'<path fill="{p["M"]}" stroke="none" d="M4.2 1.8L9.2 3.8L3.8 9.2L1.8 4.2ZM1.8 4.2L3.8 9.2L-3.8 9.2L-1.8 4.2ZM4.2 -1.8L9.2 -3.8L9.2 3.8L4.2 1.8Z"/>'
                f'<path fill="none" stroke-width=".6" d="M4.2 1.8L9.2 3.8M1.8 4.2L3.8 9.2M-1.8 4.2L-3.8 9.2M-4.2 1.8L-9.2 3.8M-4.2 -1.8L-9.2 -3.8M-1.8 -4.2L-3.8 -9.2M1.8 -4.2L3.8 -9.2M4.2 -1.8L9.2 -3.8"/>'
                f'<path fill="{p["L"]}" stroke-width=".9" d="M4.2 1.8L1.8 4.2L-1.8 4.2L-4.2 1.8L-4.2 -1.8L-1.8 -4.2L1.8 -4.2L4.2 -1.8Z"/></g>')
        elif n == "vaj":          # the single vajra, upright, about 64 tall
            half = (f'<path fill="{p["W"]}" stroke-width="1.3" d="M-2 -9C-14 -13 -14 -27 -1.4 -31.5L0 -26L1.4 -31.5C14 -27 14 -13 2 -9Z"/>'
                    f'<path fill="none" stroke-width=".6" d="M-1.6 -11C-8 -15 -8 -24 -1 -28M1.6 -11C8 -15 8 -24 1 -28"/>'
                    f'<path fill="none" stroke-width="1.3" d="M0 -9V-33M-2.2 -28L0 -34.5L2.2 -28"/>'
                    f'<path fill="{p["T"]}" stroke-width="1.2" d="M-6.4 -5.6C-7 -9 -4 -10.6 0 -10.6C4 -10.6 7 -9 6.4 -5.6Z"/>')
            c.d("vaj", f'<g id="vaj" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">{half}<g transform="scale(1 -1)">{half}</g>'
                f'<circle r="5.4" fill="{p["L"]}" stroke-width="1.3"/><circle r="2.6" fill="{p["T"]}" stroke-width=".8"/></g>')
        elif n == "lotus":        # a lotus in flower, about 48 across
            petal = 'M0 2C-7 -4 -8 -16 0 -27C8 -16 7 -4 0 2Z'
            c.d("lotus", f'<g id="lotus" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["W"]}" stroke-width="1.1" d="{petal}" transform="rotate(-62) scale(.86)"/><path fill="{p["W"]}" stroke-width="1.1" d="{petal}" transform="rotate(62) scale(.86)"/>'
                f'<path fill="{p["T"]}" stroke-width="1.2" d="{petal}" transform="rotate(-32) scale(.95)"/><path fill="{p["T"]}" stroke-width="1.2" d="{petal}" transform="rotate(32) scale(.95)"/>'
                f'<path fill="{p["L"]}" stroke-width="1.3" d="{petal}"/><path fill="none" stroke-width=".6" d="M0 -2V-22M-3 -4C-4 -10 -3 -16 0 -21M3 -4C4 -10 3 -16 0 -21"/>'
                f'<path fill="{p["W"]}" stroke-width="1.2" d="M-14 2C-8 7 8 7 14 2C8 9 -8 9 -14 2Z"/><path fill="{p["T"]}" stroke-width="1" d="M-9 4C-4 8 4 8 9 4C4 6 -4 6 -9 4Z"/></g>')
        elif n == "stave":        # a runestave, carved with its sign's two runes, 222 tall at scale 1
            a, b = RUNE_PATH[runes[0]], RUNE_PATH[runes[1]]
            c.d("stave", f'<g id="stave" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["W"]}" stroke-width="1.7" d="M-7 -98L-6 106H6L7 -98Z"/><path fill="url(#hd)" stroke="none" d="M2.4 -98L2.2 106H6L7 -98Z"/>'
                f'<path fill="{p["T"]}" stroke-width="1.5" d="M-6.6 106H6.6V115H-6.6Z"/><path fill="none" stroke-width=".8" d="M-6.6 110H6.6"/>'
                f'<circle cy="-107" r="10" fill="{p["T"]}" stroke-width="1.7"/><path fill="none" stroke-width=".7" d="M-5 -110C-2 -114 2 -114 5 -110"/>'
                f'<path fill="none" stroke-width="1.1" d="M-7 -95H7M-7 -91.5H7M-6.5 -32H6.5M-6.5 -28.5H6.5M-6.2 48H6.2M-6.2 51.5H6.2"/>'
                f'<g fill="none" stroke-width="7.5" stroke-linecap="square">'
                + "".join(f'<path transform="translate(-2.8 {y}) scale(.14)" d="{r}"/>' for y, r in [(-86, a), (-66, b), (-20, a), (0, b), (62, a), (82, b)]) + '</g></g>')
        elif n == "shield":
            c.d("shield", f'<g id="shield" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<circle r="20" fill="{p["W"]}" stroke-width="1.6"/><path fill="{p["T"]}" stroke="none" d="M0 0L0 -18A18 18 0 0 1 18 0ZM0 0L0 18A18 18 0 0 1 -18 0Z"/>'
                f'<path fill="none" stroke-width=".6" d="M-12 -14.6V14.6M-6 -18V18M6 -18V18M12 -14.6V14.6"/><circle r="18" fill="none" stroke-width=".6"/>'
                f'<circle r="20" fill="none" stroke-width="2.6"/><circle r="5.6" fill="{p["L"]}" stroke-width="1.4"/><circle r="2.4" fill="{p["M"]}" stroke="none"/></g>')
        elif n == "sword":        # a sword, point up, about 110 tall: blade, fuller, guard, wrapped grip, lobed pommel
            c.d("sword", f'<g id="sword" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["L"]}" stroke-width="1.4" d="M-5.4 18L-5 -54L0 -66L5 -54L5.4 18Z"/><path fill="url(#hd)" stroke="none" d="M0 18V-66L5 -54L5.4 18Z"/>'
                f'<path fill="none" stroke-width=".7" d="M0 12V-52"/>'
                f'<path fill="{p["T"]}" stroke-width="1.3" d="M-18 17C-10 14 10 14 18 17L17 22C10 19.6 -10 19.6 -17 22Z"/>'
                f'<path fill="{p["W"]}" stroke-width="1.2" d="M-3.2 21H3.2V37H-3.2Z"/><path fill="none" stroke-width=".7" d="M-3.2 24L3.2 26M-3.2 28L3.2 30M-3.2 32L3.2 34"/>'
                f'<path fill="{p["T"]}" stroke-width="1.3" d="M-11 41C-11 35 11 35 11 41C11 45 6 47 0 46C-6 47 -11 45 -11 41Z"/><path fill="none" stroke-width=".7" d="M-4 37V45M4 37V45"/></g>')
        elif n == "cup":          # a cup, about 58 tall
            c.d("cup", f'<g id="cup" stroke="{p["K"]}" stroke-linejoin="round" stroke-linecap="round">'
                f'<path fill="{p["W"]}" stroke-width="1.5" d="M-17 -26H17C17 -7 9 4 0 5C-9 4 -17 -7 -17 -26Z"/><path fill="url(#hd)" stroke="none" d="M7 -26H17C17 -7 9 4 0 5C6 0 8 -12 7 -26Z"/>'
                f'<path fill="{p["T"]}" stroke-width="1" d="M-16.6 -20H16.6L16.2 -15H-16.2Z"/><path fill="none" stroke-width=".6" d="M-14 -19.5L-11 -15.5L-8 -19.5L-5 -15.5L-2 -19.5L1 -15.5L4 -19.5L7 -15.5L10 -19.5L13 -15.5"/>'
                f'<ellipse cy="-26" rx="17" ry="4" fill="{p["L"]}" stroke-width="1.3"/><ellipse cy="-25.6" rx="13" ry="2.4" fill="{p["T"]}" stroke="none"/>'
                f'<path fill="none" stroke-width="1.3" d="M-2.6 5V17M2.6 5V17"/><ellipse cy="11" rx="5.4" ry="2.8" fill="{p["T"]}" stroke-width="1.2"/>'
                f'<path fill="{p["W"]}" stroke-width="1.3" d="M-13 25C-10 18 10 18 13 25Z"/><ellipse cy="25" rx="13" ry="2.6" fill="{p["L"]}" stroke-width="1.2"/></g>')
    return c


def use(name, x, y, s=1, r=0, extra=""):
    t = f"translate({f(x)} {f(y)})" + (f" rotate({f(r)})" if r else "") + (f" scale({s})" if s != 1 else "")
    return f'<use href="#{name}" transform="{t}"{extra}/>'


# ------------------------------------------------------------------ grounds and weather
def flames(c, y=360, x0=-8, x1=388, n=10, hmin=40, hmax=100, wide=40):
    """A field of flame, as on the 2 of Double Vajras."""
    out, step, cores = [], (x1 - x0) / n, []
    for i in range(n):
        x = x0 + i * step; h = c.rng.uniform(hmin, hmax); w = wide
        tip = (x + w * .45 + c.rng.uniform(-6, 6), y - h)
        out.append(f'<path class="wash ink thin" d="M{f(x - 6)} {f(y)}C{f(x - 10)} {f(y - h * .25)} {f(x + 6)} {f(y - h * .45)} {f(x + 5)} {f(y - h * .62)}'
                   f'C{f(x + 4)} {f(y - h * .8)} {f(tip[0] - 4)} {f(y - h * .86)} {f(tip[0])} {f(tip[1])}C{f(tip[0] + 10)} {f(y - h * .78)} {f(x + w * .8)} {f(y - h * .5)} {f(x + w * .72)} {f(y - h * .22)}'
                   f'C{f(x + w * .9)} {f(y - h * .1)} {f(x + w * .85)} {f(y - 4)} {f(x + w * .9)} {f(y)}Z"/>')
        cores.append(f'M{f(x + 8)} {f(y)}C{f(x + 5)} {f(y - h * .35)} {f(x + 18)} {f(y - h * .5)} {f(x + 14)} {f(y - h * .78)}M{f(x + 21)} {f(y)}C{f(x + 22)} {f(y - h * .2)} {f(x + 25)} {f(y - h * .3)} {f(x + 22)} {f(y - h * .42)}')
    out.append(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" stroke-linecap="round" d="{"".join(cores)}"/>')
    return "".join(out)


def flame(c, x, y, h=40, w=22):
    """One flame, rising from x, y."""
    return (f'<path class="wash ink thin" d="M{f(x - w / 2)} {f(y)}C{f(x - w / 2 - 4)} {f(y - h * .4)} {f(x - 2)} {f(y - h * .6)} {f(x)} {f(y - h)}C{f(x + 4)} {f(y - h * .6)} {f(x + w / 2 + 4)} {f(y - h * .4)} {f(x + w / 2)} {f(y)}Z"/>'
            f'<path class="tint ink hair" d="M{f(x - w / 4)} {f(y)}C{f(x - w / 4 - 2)} {f(y - h * .3)} {f(x - 1)} {f(y - h * .4)} {f(x)} {f(y - h * .66)}C{f(x + 2)} {f(y - h * .4)} {f(x + w / 4 + 2)} {f(y - h * .3)} {f(x + w / 4)} {f(y)}Z"/>')


def ground(c, y=300, wob=6, hatch=True, cls="wash ink thin"):
    """Level ground across the plate with a hatched foreground."""
    r = c.rng
    pts = [(x, y + r.uniform(-wob, wob)) for x in range(-20, 401, 50)]
    d = smooth(pts)
    out = f'<path class="{cls}" d="{d}V380H-20Z"/>'
    if hatch:
        pts2 = [(x, y + 18 + r.uniform(-wob, wob)) for x in range(-20, 401, 50)]
        out += f'<path class="hatchfill" d="{smooth(pts2)}V380H-20Z"/>'
        out += f'<path class="ink hair" d="{smooth([(x, y + 34 + r.uniform(-4, 4)) for x in range(-20, 401, 60)])}"/>'
    return out


def hills(c, base, peaks, cls="wash ink thin", shade=True):
    """A line of hills: peaks are (x, height) pairs."""
    pts = [(-20, base)] + [(x, base - h) for x, h in peaks] + [(400, base)]
    d = smooth(pts)
    out = f'<path class="{cls}" d="{d}V380H-20Z"/>'
    if shade:
        for x, h in peaks:
            out += f'<path class="hatchfill" d="M{f(x)} {f(base - h)}C{f(x + 18)} {f(base - h * .6)} {f(x + 30)} {f(base - h * .3)} {f(x + 46)} {f(base)}H{f(x + 10)}C{f(x + 12)} {f(base - h * .4)} {f(x + 6)} {f(base - h * .8)} {f(x)} {f(base - h)}Z" opacity=".8"/>'
    return out


def sea(c, top=236, bottom=360, x0=0, x1=380, rows=8, tint_rows=()):
    """A calm sea: a pale field ruled with broken lines."""
    out = f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" class="wash"/><path class="ink thin" d="M{x0} {top}H{x1}"/>'
    lines = "".join(f'M{f(x0 + c.rng.uniform(0, 30))} {f(top + (k + 1) * (bottom - top) / (rows + 1))}H{x1}' for k in range(rows))
    out += f'<path class="ink hair" stroke-dasharray="12 5 3 5" d="{lines}"/>'
    for y, xa, xb in tint_rows:
        out += f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" stroke-linecap="round" d="M{xa} {y}H{xb}"/>'
    return out


def chop(c, y, x0=0, x1=380, length=30, amp=6):
    """Choppy water drawn as crests only, over a sea already laid."""
    d = "".join(f"M{f(x)} {f(y + (k % 2) * 8)}c{f(length * .3)} {f(-amp)} {f(length * .6)} {f(-amp)} {f(length * .8)} 0c-4 -2 -6 -4 -4 -6" for k, x in enumerate(range(int(x0), int(x1), int(length))))
    return f'<path class="ink thin" d="{d}"/>'


def waves(c, y, x0=-10, x1=390, amp=10, length=48, cls="wash ink thin", crest=True, hatch=True):
    """A row of curling waves."""
    d = f"M{x0} {y}"
    x = x0
    while x < x1:
        d += f"C{f(x + length * .25)} {f(y - amp)} {f(x + length * .55)} {f(y - amp * 1.1)} {f(x + length * .7)} {f(y - amp * .4)}C{f(x + length * .8)} {f(y + amp * .1)} {f(x + length * .9)} {f(y)} {f(x + length)} {f(y)}"
        x += length
    out = f'<path class="{cls}" d="{d}V380H{x0}Z"/>'
    if crest:
        foam = "".join(f'M{f(xx + length * .62)} {f(y - amp * .7)}c3 -2 6 -1 6 2' for xx in range(int(x0), int(x1), int(length)))
        out += f'<path class="ink hair" d="{foam}"/>'
    if hatch:
        out += f'<path class="hatchfill" d="M{x0} {f(y + amp * 1.4)}H{x1}V{f(y + amp * 2.6)}H{x0}Z" opacity=".6"/>'
    return out


def cloud(c, cx, cy, w=120, h=34, cls="light ink thin", shade=True):
    """A cloud as an engraver cuts one: rounded billows, the larger behind and the smaller before,
    each shaded on its underside, all resting on one flat base."""
    r = c.rng
    key = f"cl{int(cx)}_{int(cy)}_{int(w)}"
    c.d(key, f'<clipPath id="{key}"><rect x="{f(cx - w)}" y="{f(cy - h * 4)}" width="{f(w * 2)}" height="{f(h * 4)}"/></clipPath>')
    n = max(3, int(w / 26))
    back, front = [], []
    for k in range(n):
        t = (k + .5) / n; bump = math.sin(math.pi * t)
        pr = h * (.5 + .5 * bump) * r.uniform(.88, 1.08)
        back.append((cx - w / 2 + t * w + r.uniform(-3, 3), cy - h * .32 * bump - pr * .25, pr))
    for k in range(n - 1):
        t = (k + 1) / n; bump = math.sin(math.pi * t)
        pr = h * (.36 + .3 * bump) * r.uniform(.85, 1.05)
        front.append((cx - w / 2 + t * w + r.uniform(-3, 3), cy - pr * .1, pr))
    out = [f'<g clip-path="url(#{key})">']
    for px, py, pr in back + front:
        out.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(pr)}" class="{cls}"/>')
        if shade:
            a0, a1 = pol(px, py, pr * .92, 10), pol(px, py, pr * .92, 170)
            out.append(f'<path fill="url(#hd)" d="M{f(a0[0])} {f(a0[1])}A{f(pr * .92)} {f(pr * .92)} 0 0 1 {f(a1[0])} {f(a1[1])}A{f(pr * 1.1)} {f(pr * .7)} 0 0 0 {f(a0[0])} {f(a0[1])}Z" opacity=".75"/>')
        out.append(f'<path class="ink hair" d="M{f(px - pr * .5)} {f(py - pr * .2)}A{f(pr * .6)} {f(pr * .6)} 0 0 1 {f(px + pr * .1)} {f(py - pr * .62)}"/>')
    out.append('</g>')
    ends = [(px - math.sqrt(max(pr * pr - (cy - py) ** 2, 0)), px + math.sqrt(max(pr * pr - (cy - py) ** 2, 0))) for px, py, pr in back + front if pr > cy - py]
    if ends:
        out.append(f'<path class="ink thin" d="M{f(min(e[0] for e in ends))} {f(cy)}H{f(max(e[1] for e in ends))}"/>')
    return "".join(out)


def rain(c, x0, x1, y0, y1, n=40, slant=-6, length=12):
    r = c.rng
    d = "".join(f"M{f(x)} {f(y)}l{slant} {length}" for x, y in ((r.uniform(x0, x1), r.uniform(y0, y1 - length)) for _ in range(n)))
    return f'<path class="ink hair" d="{d}"/>'


def stars(c, n, x0=10, x1=370, y0=10, y1=200, avoid=None, cls="fill-ink"):
    r, out = c.rng, []
    while len(out) < n:
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        if avoid and avoid(x, y): continue
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r.choice([1, 1.2, 1.4, 1.6])}"/>')
    return f'<g class="{cls}">{"".join(out)}</g>'


def sparkle(x, y, r=6, cls="tint ink hair"):
    return f'<path class="{cls}" d="M{f(x)} {f(y - r)}L{f(x + r * .25)} {f(y - r * .25)}L{f(x + r)} {f(y)}L{f(x + r * .25)} {f(y + r * .25)}L{f(x)} {f(y + r)}L{f(x - r * .25)} {f(y + r * .25)}L{f(x - r)} {f(y)}L{f(x - r * .25)} {f(y - r * .25)}Z"/>'


def crescent(x, y, r=17, cls="tint ink thin", flip=False):
    """A waxing crescent (or waning, flipped), its points up and down."""
    s = -1 if flip else 1
    return f'<path class="{cls}" d="M{f(x)} {f(y - r)}A{r} {r} 0 1 {0 if s > 0 else 1} {f(x)} {f(y + r)}A{f(r * 1.24)} {f(r * 1.24)} 0 0 {1 if s > 0 else 0} {f(x)} {f(y - r)}Z"/>'


def full_moon(c, x, y, r=34):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="light ink thin"/><circle cx="{f(x)}" cy="{f(y)}" r="{r - 4}" class="ink hair"/>'
            f'<path class="hatchfill" d="M{f(x + r * .2)} {f(y - r * .9)}A{r} {r} 0 0 1 {f(x + r * .2)} {f(y + r * .9)}A{f(r * .9)} {f(r * .9)} 0 0 0 {f(x + r * .2)} {f(y - r * .9)}Z" opacity=".7"/>')


def sun_rays(c, x, y, r0, r1, a0=180, a1=360, step=12, width=4):
    """A rayed sun's long rays, tinted, as on the 3 of Wands."""
    out = []
    a = a0
    while a <= a1 + .01:
        p0, p1, p2 = pol(x, y, r0, a - width / 4), pol(x, y, r1, a), pol(x, y, r0, a + width / 4)
        out.append(f'<path class="tint ink hair" d="M{f(p0[0])} {f(p0[1])}L{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}Z"/>')
        a += step
    return "".join(out)


def river_beneath(c, top=304):
    """The river under every void."""
    p = c.p
    return (f'<path class="ink thin" d="M0 {top}H380"/><rect x="0" y="{top + 8}" width="380" height="40" fill="{p["W"]}"/>'
            f'<path class="ink thin" d="M0 {top + 8}C60 {top + 12} 120 {top + 6} 190 {top + 10}S320 {top + 14} 380 {top + 8}M0 {top + 48}C60 {top + 44} 120 {top + 50} 190 {top + 46}S320 {top + 42} 380 {top + 48}"/>'
            f'<path fill="none" stroke="{p["T"]}" stroke-width="1.6" stroke-dasharray="16 7 4 7" d="M8 {top + 20}C60 {top + 16} 120 {top + 24} 190 {top + 20}S320 {top + 16} 372 {top + 22}M20 {top + 34}C80 {top + 30} 140 {top + 38} 210 {top + 34}S330 {top + 30} 380 {top + 36}"/>'
            f'<path class="ink hair" stroke-dasharray="6 6" d="M0 {top + 27}H380M0 {top + 41}H380"/>')


def mountain(c, x0, x1, peak, y_base, cls="wash ink heavy", snow=False):
    """A steep mountain with a hatched shadow side."""
    px, py = peak
    d = f"M{f(x0)} {f(y_base)}L{f(px - 14)} {f(py + 14)}C{f(px - 8)} {f(py + 2)} {f(px - 3)} {f(py)} {f(px)} {f(py)}C{f(px + 3)} {f(py)} {f(px + 8)} {f(py + 2)} {f(px + 14)} {f(py + 14)}L{f(x1)} {f(y_base)}Z"
    out = f'<path class="{cls}" d="{d}"/><path class="hatchfill" d="M{f(px)} {f(py)}C{f(px + 3)} {f(py)} {f(px + 8)} {f(py + 2)} {f(px + 14)} {f(py + 14)}L{f(x1)} {f(y_base)}H{f(px + (x1 - px) * .3)}C{f(px + 10)} {f(py + (y_base - py) * .5)} {f(px + 4)} {f(py + 30)} {f(px)} {f(py)}Z"/>'
    if snow:
        out += f'<path class="light ink thin" d="M{f(px - 14)} {f(py + 14)}C{f(px - 8)} {f(py + 2)} {f(px - 3)} {f(py)} {f(px)} {f(py)}C{f(px + 3)} {f(py)} {f(px + 8)} {f(py + 2)} {f(px + 14)} {f(py + 14)}L{f(px + 6)} {f(py + 22)}L{f(px)} {f(py + 14)}L{f(px - 6)} {f(py + 24)}Z"/>'
    return out


def clump(c, cx, cy, r, n=None, cls="wash ink thin"):
    """One mass of foliage, as an engraver cuts it: a scalloped edge, a hatched shadow on the side away
    from the light, and a few leaf-marks inside."""
    rng = c.rng
    n = n or max(9, int(r / 3.2))
    pts = []
    for k in range(n):
        a = -90 + k * 360 / n + rng.uniform(-6, 6)
        pts.append(pol(cx, cy, r * rng.uniform(.9, 1.04), a))
    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for k in range(n):
        x1, y1 = pts[(k + 1) % n]; x0, y0 = pts[k]
        rr = math.hypot(x1 - x0, y1 - y0) * .62
        d += f"A{f(rr)} {f(rr)} 0 0 1 {f(x1)} {f(y1)}"
    d += "Z"
    sh_o = [pol(cx, cy, r * .9, a) for a in (-30, 150)]
    sh = (f"M{f(sh_o[0][0])} {f(sh_o[0][1])}A{f(r * .9)} {f(r * .9)} 0 0 1 {f(sh_o[1][0])} {f(sh_o[1][1])}"
          f"A{f(r * .82)} {f(r * .82)} 0 0 0 {f(sh_o[0][0])} {f(sh_o[0][1])}Z")
    marks = "".join(f"M{f(cx + dx)} {f(cy + dy)}q{f(r * .09)} {f(r * .08)} {f(r * .18)} 0"
                    for dx, dy in ((rng.uniform(-.6, .4) * r, rng.uniform(-.55, .3) * r) for _ in range(max(3, int(r / 6)))))
    return f'<path class="{cls}" d="{d}"/><path fill="url(#hd)" d="{sh}" opacity=".85"/><path class="ink hair" d="{marks}"/>'


def tree(c, x, y, h=150, spread=90, leaves=True, cls="wash ink heavy", lean=0):
    """A broad tree as an engraver cuts it: a flared trunk with its bark, boughs tapering out of the
    fork, and the crown built of scalloped masses of foliage, shaded away from the light. The crown's
    masses are kept on c.canopy, (x, y, r) each, for fruit, jewels or leaves to be hung in."""
    rng = c.rng
    tw = max(6.0, spread * .12)
    fx, fy = x + lean, y - h * .42
    out = []
    out.append(f'<path class="{cls}" d="{taper([(x, y + 2), (x + lean * .35, y - h * .26), (fx, fy)], tw * 2.3, tw * 1.2)}"/>')
    out.append(f'<path class="{cls.replace("heavy", "thin")}" d="M{f(x - tw * 3)} {f(y + 2)}C{f(x - tw * 1.4)} {f(y)} {f(x - tw * 1.2)} {f(y - 10)} {f(x - tw * 1.1)} {f(y - 22)}'
               f'L{f(x + tw * 1.1)} {f(y - 22)}C{f(x + tw * 1.2)} {f(y - 10)} {f(x + tw * 1.4)} {f(y)} {f(x + tw * 3)} {f(y + 2)}Z"/>')
    out.append(f'<path fill="url(#hd)" d="{taper([(x + tw * .5, y + 2), (x + tw * .5 + lean * .35, y - h * .26), (fx + tw * .4, fy)], tw * 1.1, tw * .5)}" opacity=".9"/>')
    bark = "".join(f"M{f(x + dx)} {f(y - 4)}C{f(x + dx + lean * .1 + rng.uniform(-2, 2))} {f(y - h * .18)} {f(x + dx * .7 + lean * .25)} {f(y - h * .3)} {f(x + dx * .6 + lean * .4)} {f(y - h * .42)}"
                   for dx in (-tw * .9, -tw * .3, tw * .3))
    out.append(f'<path class="ink hair" d="{bark}"/>')
    # the crown's masses: a broad dome over the fork
    cy0 = y - h * .76
    spots = [(-.66, .12, .4), (.66, .1, .4), (-.36, -.32, .46), (.38, -.34, .46), (0, -.56, .44), (-.26, .14, .38), (.28, .14, .38), (0, -.08, .42)]
    canopy = [(fx + dx * spread, cy0 + dy * h * .42, rr * spread * rng.uniform(.88, 1.06)) for dx, dy, rr in spots]
    boughs = []
    for cx, cy, r in canopy[:5]:
        mx, my = (fx + cx) / 2, (fy + cy) / 2 - 8
        boughs.append(taper([(fx, fy + 8), (mx, my), (cx * .75 + fx * .25, cy * .75 + fy * .25 + 8)], tw * 1.15, tw * .4))
    out.append("".join(f'<path class="{cls.replace("heavy", "thin")}" d="{d}"/>' for d in boughs))
    if leaves:
        for cx, cy, r in sorted(canopy, key=lambda t: t[1]):
            out.append(clump(c, cx, cy, r))
    else:
        twigs = "".join(f"M{f(cx * .8 + fx * .2)} {f(cy * .8 + fy * .2)}l{f((cx - fx) * .25)} {f((cy - fy) * .25 - 6)}" for cx, cy, r in canopy[:5])
        out.append(f'<path class="ink thin" d="{twigs}"/>')
    c.canopy = canopy
    return "".join(out)


def longship(c, x, y, s=1, stripes=True):
    """The longship from the 3 of Wands, its keel at x, y."""
    p = c.p
    c.d(f"sail{x}{y}", f'<clipPath id="sail{x}_{y}"><path d="M272 208H332L336 268H268Z"/></clipPath>')
    body = (f'<path class="ink heavy" d="M302 300V198"/><path class="ink thin" d="M268 205H336"/><path class="ink hair" d="M302 200L244 288M302 200L370 266"/>'
            f'<path class="wash ink thin" d="M272 208H332L336 268H268Z"/>'
            + (f'<g clip-path="url(#sail{x}_{y})"><path class="tint" d="M282 200H293V276H280ZM303 200H314V276H303ZM324 200H335V276H326Z"/></g>' if stripes else "")
            + f'<path class="ink thin" d="M272 208H332L336 268H268Z"/><path class="ink hair" d="M270 228H334M269 248H335"/>'
            f'<path class="light ink thin" d="M246 292C268 306 336 308 360 292C366 286 368 276 368 268C370 262 377 263 375 270C373 278 372 288 366 296C346 318 262 318 240 298C236 292 238 284 236 278C234 272 240 271 242 277C244 283 244 288 246 292Z"/>'
            f'<path class="hatchfill" d="M246 300C270 314 334 314 362 298C356 306 346 316 300 316C270 316 252 310 246 300Z"/><path class="ink hair" d="M244 296C270 310 336 312 362 296"/>'
            f'<path class="tint ink thin" d="M372 264C376 258 384 258 382 266C380 270 376 270 374 268Z"/><circle cx="377" cy="263" r="1" class="fill-ink"/>'
            f'<path class="ink thin" d="M258 308l-8 16M272 311l-7 17M286 313l-6 17M300 314l-5 17M314 313l-4 17M328 311l-3 16M342 307l-2 15"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s}) translate(-302 -316)">{body}</g>'


def ring_of(n, cx, cy, r, a0=-90):
    return [pol(cx, cy, r, a0 + k * 360 / n) for k in range(n)]


# ------------------------------------------------------------------ bodies and weather drawn as shapes
def densify(pts, n=8):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for k in range(n):
            t = k / n; out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out + [pts[-1]]


def taper(pts, w0, w1, closed_head=True):
    """A body along the points, w0 wide at the first and w1 at the last (a serpent, a stream, a tail)."""
    P = densify(pts, 6)
    L, R = [], []
    n = len(P)
    for i, (x, y) in enumerate(P):
        x0, y0 = P[max(i - 1, 0)]; x1, y1 = P[min(i + 1, n - 1)]
        dx, dy = x1 - x0, y1 - y0; m = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        L.append((x - dy / m * w, y + dx / m * w)); R.append((x + dy / m * w, y - dx / m * w))
    sl = smooth(L[::3] + [L[-1]]); sr = smooth((R[::3] + [R[-1]])[::-1])
    return sl + "L" + sr[1:] + "Z"


def storm(c, y, x0=-10, x1=390, depth=40, cls="mid ink thin"):
    """A storm cloud's underside: dark billows hanging over the plate."""
    r = c.rng
    d = f"M{x0} -10H{x1}V{y}"
    x = x1
    while x > x0:
        w = r.uniform(34, 56)
        d += f"C{f(x - w * .2)} {f(y + r.uniform(10, 22))} {f(x - w * .8)} {f(y + r.uniform(10, 22))} {f(x - w)} {f(y + r.uniform(-4, 4))}"
        x -= w
    d += "Z"
    return f'<path class="{cls}" d="{d}"/><path fill="url(#hx)" d="{d}" opacity=".55"/>'


def raven(c, x, y, s=1, flip=False):
    """A raven perched in profile, facing left: heavy beak, the shaggy throat, wing folded, wedge tail."""
    p = c.p
    body = ('<path class="fill-ink" d="M-20 -36C-14 -40 -6 -38 -2 -32C8 -28 18 -20 24 -10L38 2L34 8L22 4C14 6 6 6 -2 2C-10 -2 -14 -10 -16 -18'
            'C-18 -22 -21 -24 -24 -26L-24 -31C-24 -34 -22 -36 -20 -36Z"/>'
            '<path class="fill-ink" d="M-23 -32L-38 -28L-23 -25Z"/>'
            f'<path fill="none" stroke="{p["L"]}" stroke-width=".9" d="M-4 -24C6 -22 14 -16 20 -8M-2 -18C8 -16 16 -10 22 -4M2 -12C10 -10 16 -6 24 0M28 0L36 4M-16 -20l-4 4M-14 -16l-4 4"/>'
            f'<circle cx="-18" cy="-31" r="1.5" fill="{p["L"]}"/>'
            '<path class="ink thin" d="M0 2L-2 12M-6 12H2M6 2L6 12M2 12H10"/>')
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{body}</g>'


def leafdef(c):
    p = c.p
    c.d("leaf", f'<g id="leaf" stroke="{p["K"]}" stroke-linejoin="round"><path fill="{p["W"]}" stroke-width="1.1" d="M0 0C-8 -6 -8 -16 0 -22C8 -16 8 -6 0 0Z"/>'
        f'<path fill="none" stroke-width=".5" d="M0 -2V-20"/></g>')


def leaves(c, cx, cy, n, spread, a0=-170, a1=-10, s=(.6, .95)):
    """A cluster of leaves about a point (a bough's crown, a bower, a garland)."""
    leafdef(c)
    out = []
    for _ in range(n):
        a = c.rng.uniform(a0, a1); rr = c.rng.uniform(.3, 1.0) * spread
        lx, ly = pol(cx, cy, rr, a)
        out.append(use("leaf", lx, ly, round(c.rng.uniform(*s), 2), a + 90))
    return "".join(out)


def rune(name, x, y, h=30, w=2.4, color=None, cls="ink"):
    """A rune carved at x, y (its centre), h tall."""
    s = h / 80
    st = f' stroke="{color}"' if color else ""
    return f'<path class="{cls}"{st} stroke-width="{f(w / s)}" transform="translate({f(x - 20 * s)} {f(y - 40 * s)}) scale({s:.3f})" d="{RUNE_PATH[name]}"/>'


def bud(x, y, s=1, r=0, cls="tint ink thin"):
    """A closed lotus bud on the top of its stalk at x, y."""
    t = f"translate({f(x)} {f(y)})" + (f" rotate({r})" if r else "") + (f" scale({s})" if s != 1 else "")
    return (f'<g transform="{t}"><path class="{cls}" d="M0 0C-9 -8 -9 -22 0 -34C9 -22 9 -8 0 0Z"/>'
            f'<path class="wash ink thin" d="M0 0C-12 -4 -14 -14 -10 -20C-6 -12 -4 -6 0 0ZM0 0C12 -4 14 -14 10 -20C6 -12 4 -6 0 0Z"/>'
            f'<path class="ink hair" d="M0 -4V-30M-3 -6C-5 -14 -4 -22 0 -28"/></g>')


def pad(x, y, rx=22, ry=6, cls="wash ink thin"):
    """A lotus leaf floating on still water, its notch toward the viewer."""
    return (f'<path class="{cls}" d="M{f(x)} {f(y + ry)}L{f(x - 4)} {f(y)}A{rx} {ry} 0 1 1 {f(x + 4)} {f(y)}Z"/>'
            f'<path class="ink hair" d="M{f(x - rx * .7)} {f(y - ry * .2)}L{f(x)} {f(y)}L{f(x + rx * .7)} {f(y - ry * .3)}M{f(x)} {f(y)}L{f(x - rx * .2)} {f(y - ry * .9)}M{f(x)} {f(y)}L{f(x + rx * .3)} {f(y - ry * .9)}"/>')


def ripples(x, y, w=40, n=3):
    return "".join(f'<ellipse cx="{f(x)}" cy="{f(y + k * 3)}" rx="{f(w * (1 + k * .5) / 2)}" ry="{f(2.4 + k * 1.4)}" class="ink hair"/>' for k in range(n))


def sun_wheel(c, x, y, r=40, spokes=8):
    """The sun-wheel: rim, spokes and hub."""
    p = c.p
    sp = "".join(f"M{f(pol(x, y, 8, a)[0])} {f(pol(x, y, 8, a)[1])}L{f(pol(x, y, r - 5, a)[0])} {f(pol(x, y, r - 5, a)[1])}" for a in range(0, 360, 360 // spokes))
    wedges = "".join(f'<path class="tint" d="M{f(x)} {f(y)}L{f(pol(x, y, r - 5, a)[0])} {f(pol(x, y, r - 5, a)[1])}A{r - 5} {r - 5} 0 0 1 {f(pol(x, y, r - 5, a + 360 / spokes)[0])} {f(pol(x, y, r - 5, a + 360 / spokes)[1])}Z" opacity=".55"/>'
                     for a in range(0, 360, 720 // spokes))
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="light ink heavy"/>{wedges}' + rope(f"M{f(x - r + 2.5)} {f(y)}a{r - 2.5} {r - 2.5} 0 1 0 {f(2 * r - 5)} 0a{r - 2.5} {r - 2.5} 0 1 0 {f(-2 * r + 5)} 0", p, 7, 4, ".7 2.6")
            + f'<path class="ink thin" d="{sp}"/><circle cx="{f(x)}" cy="{f(y)}" r="9" class="wash ink thin"/><circle cx="{f(x)}" cy="{f(y)}" r="3.4" class="fill-ink"/>')


def claw(c, x, y, h=100, lean=0, talons=4, span=34, cls="wash ink thin", reach=24):
    """A great clawed hand rising from below, its talons hooked over y."""
    out = []
    bx = x + lean
    arm = f"M{f(x - span * .45)} {f(y + h)}C{f(x - span * .5)} {f(y + h * .5)} {f(bx - span * .6)} {f(y + 20)} {f(bx - span * .5)} {f(y + 6)}L{f(bx + span * .5)} {f(y + 6)}C{f(bx + span * .6)} {f(y + 20)} {f(x + span * .5)} {f(y + h * .5)} {f(x + span * .45)} {f(y + h)}Z"
    out.append(f'<path class="{cls}" d="{arm}"/><path fill="url(#hd)" d="M{f(x + span * .1)} {f(y + h)}C{f(x + span * .2)} {f(y + h * .5)} {f(bx + span * .3)} {f(y + 20)} {f(bx + span * .5)} {f(y + 6)}C{f(bx + span * .6)} {f(y + 20)} {f(x + span * .5)} {f(y + h * .5)} {f(x + span * .45)} {f(y + h)}Z" opacity=".8"/>')
    scales = "".join(f"M{f(x - span * .3 + (k % 3) * span * .3)} {f(y + 24 + (k // 3) * 16)}q{f(span * .15)} 6 {f(span * .3)} 0" for k in range(int(h / 16) * 3))
    out.append(f'<path class="ink hair" d="{scales}"/>')
    for k in range(talons):
        t = k / (talons - 1) - .5
        x0 = bx + t * span; tip = (bx + t * span * 1.7, y - reach + abs(t) * 10)
        out.append(f'<path class="light ink thin" d="M{f(x0 - 5)} {f(y + 8)}C{f(x0 - 6)} {f(y - 6)} {f(tip[0] - 4)} {f(tip[1] - 4)} {f(tip[0] + (6 if t <= 0 else -6))} {f(tip[1])}C{f(tip[0])} {f(tip[1] + 6)} {f(x0 + 3)} {f(y - 2)} {f(x0 + 5)} {f(y + 8)}Z"/>')
    return "".join(out)


def crown_shape(x, y, w=60, h=34, cls="tint ink thin"):
    """A five-pointed king's crown sitting on y, centred on x."""
    pts = [(x - w / 2, y), (x - w / 2, y - h * .5), (x - w / 4, y - h * .2), (x - w / 8, y - h), (x, y - h * .3), (x + w / 8, y - h), (x + w / 4, y - h * .2), (x + w / 2, y - h * .5), (x + w / 2, y)]
    d = "M" + "L".join(f"{f(a)} {f(b)}" for a, b in pts) + "Z"
    gems = "".join(f'<circle cx="{f(x + k * w / 5)}" cy="{f(y - h * .14)}" r="2.6" class="light ink hair"/>' for k in (-2, -1, 0, 1, 2))
    tips = "".join(f'<circle cx="{f(a)}" cy="{f(b - 3)}" r="3" class="light ink thin"/>' for a, b in [pts[1], pts[3], pts[5], pts[7]])
    return f'<path class="{cls}" d="{d}"/><path class="ink thin" d="M{f(x - w / 2)} {f(y - h * .28)}H{f(x + w / 2)}"/>{gems}{tips}'


def trident(x, y, h=150, r=0, cls="light ink thin"):
    """Shiva's or the Goddess's trident, its point at x, y, h long, turned r degrees."""
    body = (f'<path class="{cls}" d="M-3 22V{h}H3V22Z"/><path class="ink hair" d="M0 26V{h - 4}"/>'
            f'<path class="{cls}" d="M0 -2L-5 10V22H5V10Z"/>'
            f'<path class="{cls}" d="M-5 22C-22 22 -28 10 -26 -14L-22 -6C-21 8 -16 14 -5 14ZM5 22C22 22 28 10 26 -14L22 -6C21 8 16 14 5 14Z"/>'
            f'<path class="tint ink thin" d="M-7 26H7V34H-7Z"/><path class="ink thin" d="M-5 48H5M-5 54H5"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r})">{body}</g>'


def dragon_head(x, y, s=1, flip=False, cls="wash ink thin"):
    """A carved dragon's head, as on a prow or a pole's top, facing left."""
    body = (f'<path class="{cls}" d="M0 40C-2 22 2 6 12 -4C2 -8 -10 -6 -22 -2C-30 0 -36 -4 -38 -10C-28 -10 -22 -14 -18 -18C-26 -22 -32 -28 -32 -34C-20 -30 -8 -30 4 -26C14 -34 26 -34 34 -26C40 -18 40 -4 34 8C30 18 28 30 30 40Z"/>'
            f'<path class="tint ink thin" d="M10 -28C18 -42 30 -46 40 -40C34 -38 30 -34 30 -28M22 -32C30 -46 44 -50 52 -42C46 -40 40 -36 38 -30"/>'
            f'<circle cx="14" cy="-18" r="3.6" class="light ink thin"/><circle cx="14" cy="-18" r="1.4" class="fill-ink"/>'
            f'<path class="ink hair" d="M-30 -32L-26 -22M-22 -30L-18 -20M-14 -29L-11 -20M-36 -10L-32 -4M-28 -8L-26 -2M6 8C14 14 20 24 20 36M12 0C22 8 28 22 26 36"/>')
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{body}</g>'


def wreath(c, x, y, r=22, n=18):
    """A victor's wreath of leaves, tied below."""
    leafdef(c)
    out = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="ink thin"/>']
    for k in range(n):
        a = -80 + k * 340 / n
        lx, ly = pol(x, y, r, a)
        out.append(use("leaf", lx, ly, .52, a + 90 + 40))
    out.append(rope(f"M{f(x - 5)} {f(y + r)}C{f(x - 10)} {f(y + r + 12)} {f(x - 14)} {f(y + r + 18)} {f(x - 12)} {f(y + r + 28)}M{f(x + 5)} {f(y + r)}C{f(x + 10)} {f(y + r + 12)} {f(x + 12)} {f(y + r + 20)} {f(x + 16)} {f(y + r + 26)}", c.p, 4.6, 2.6, ".6 2", fill=c.p["T"]))
    return "".join(out)


def smoke(c, x, y, h=60, n=3, spread=14):
    return "".join(f'<path class="ink hair" d="M{f(x + (k - n / 2) * spread)} {f(y)}c-8 {f(-h * .25)} 8 {f(-h * .4)} 0 {f(-h * .6)}s8 {f(-h * .25)} 0 {f(-h * .4)}"/>' for k in range(n))


def vase(c, x=190, y=300, s=1):
    """The treasure vase, its foot at x, y."""
    body = ('<path class="light ink heavy" d="M160 300C138 290 134 254 158 238C168 232 176 230 180 224L176 214H204L200 224C204 230 212 232 222 238C246 254 242 290 220 300Z"/>'
            '<path class="hatchfill" d="M214 236C238 252 240 288 220 300H204C222 284 224 254 214 236Z"/>'
            '<path class="tint ink thin" d="M141 262C160 270 220 270 239 262L240 274C220 282 160 282 140 274Z"/>'
            '<path class="ink hair" d="M146 268C150 272 154 272 158 268S166 272 170 268S178 272 182 268S190 272 194 268S202 272 206 268S214 272 218 268S226 272 230 268S238 272 236 268"/>'
            '<path class="wash ink thin" d="M168 214C174 204 206 204 212 214Z"/><path class="ink thin" d="M166 214H214"/>'
            '<path class="tint ink thin" d="M168 300H212L218 312H162Z"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s}) translate(-190 -312)">{body}</g>'


def hammer(x, y, r=0, s=1):
    body = ('<path class="wash ink thin" d="M-3 0V-56H3V0Z"/><path class="ink hair" d="M0 -6V-50"/>'
            '<path class="mid ink thin" d="M-16 -70H14L18 -66V-58L14 -54H-16Z"/><path class="ink hair" d="M-10 -70V-54M8 -70V-54"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})">{body}</g>'


def anvil(x, y, s=1):
    body = ('<path class="mid ink heavy" d="M-46 -40H30C40 -40 52 -36 62 -28C50 -28 40 -26 34 -22H24V-8C24 -2 30 2 36 4V12H-36V4C-30 2 -24 -2 -24 -8V-22H-38C-44 -22 -48 -28 -46 -40Z"/>'
            '<path class="light ink thin" d="M-46 -40H30C40 -40 52 -36 62 -28H-44Z"/><path fill="url(#hx)" d="M-24 -22H24V-8C24 -2 30 2 36 4V12H-36V4C-30 2 -24 -2 -24 -8Z" opacity=".6"/>'
            '<path class="wash ink heavy" d="M-46 12H46V24H-46Z"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s})">{body}</g>'


def falcon(x, y, s=1, flip=False):
    """A falcon perched upright, facing left."""
    body = ('<path class="wash ink thin" d="M0 0C-10 -6 -14 -22 -10 -36C-8 -46 -2 -52 6 -52C12 -52 16 -46 16 -40C22 -30 22 -14 16 -2L20 20H10L6 4Z"/>'
            '<path class="mid ink thin" d="M6 -48C14 -44 20 -32 20 -18C20 -6 16 4 10 12L18 26H10L4 8C12 -6 14 -26 6 -48Z"/>'
            '<path class="tint ink thin" d="M-6 -48C-2 -54 8 -54 12 -46C6 -46 0 -44 -6 -42Z"/>'
            '<path class="fill-ink" d="M-6 -46L-14 -42L-8 -38Z"/><circle cx="2" cy="-46" r="1.6" class="fill-ink"/>'
            '<path class="ink hair" d="M-6 -30l2 2M-2 -24l2 2M-6 -18l2 2M-2 -12l2 2M2 -30l2 2M2 -18l2 2"/>'
            '<path class="ink thin" d="M-2 0L-6 8M4 2L2 10"/>')
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{body}</g>'


def hound(x, y, s=1, flip=False):
    """A long hound lying watchful, its head raised, facing left."""
    body = ('<path class="wash ink thin" d="M-40 0C-44 -8 -40 -16 -30 -18C-22 -30 -12 -36 -2 -34C4 -40 14 -40 20 -34L20 -24C30 -22 42 -18 54 -14C66 -12 76 -6 80 0Z"/>'
            '<path class="wash ink thin" d="M-44 -22C-48 -30 -46 -42 -34 -46C-26 -50 -18 -46 -14 -40C-12 -34 -16 -28 -24 -26C-30 -24 -38 -22 -44 -22Z"/>'
            '<path class="tint ink thin" d="M-26 -48C-22 -56 -14 -56 -12 -48C-14 -42 -18 -38 -22 -38Z"/>'
            '<path class="fill-ink" d="M-48 -26L-52 -28L-50 -22Z"/><circle cx="-36" cy="-38" r="1.6" class="fill-ink"/>'
            '<path class="ink thin" d="M-40 0H-12M-6 0H12M80 0C90 -4 98 -12 102 -22"/>'
            '<path class="ink hair" d="M0 -26C10 -20 24 -16 40 -12M10 -32C16 -28 22 -26 30 -24M-30 -16C-20 -10 -6 -8 8 -8"/>'
            '<path class="hatchfill" d="M20 -24C30 -22 42 -18 54 -14C66 -12 76 -6 80 0H26C24 -10 22 -18 20 -24Z" opacity=".8"/>')
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{body}</g>'


def lemniscate(c, x, y, w=40, h=14, cls="ink heavy"):
    """The Magician's sign: the figure of eight lying on its side."""
    return (f'<path fill="none" stroke="{c.p["T"]}" stroke-width="6" d="M{f(x)} {f(y)}C{f(x + w * .3)} {f(y - h)} {f(x + w * .6)} {f(y - h)} {f(x + w * .6)} {f(y)}S{f(x + w * .3)} {f(y + h)} {f(x)} {f(y)}S{f(x - w * .6)} {f(y + h)} {f(x - w * .6)} {f(y)}S{f(x - w * .3)} {f(y - h)} {f(x)} {f(y)}Z"/>'
            f'<path class="{cls}" d="M{f(x)} {f(y)}C{f(x + w * .3)} {f(y - h)} {f(x + w * .6)} {f(y - h)} {f(x + w * .6)} {f(y)}S{f(x + w * .3)} {f(y + h)} {f(x)} {f(y)}S{f(x - w * .6)} {f(y + h)} {f(x - w * .6)} {f(y)}S{f(x - w * .3)} {f(y - h)} {f(x)} {f(y)}Z"/>')


def apple_tree(c, x, y, h=130, spread=70, n=7):
    out = tree(c, x, y, h, spread)
    for k in range(n):
        cx, cy, r = c.canopy[k % len(c.canopy)]
        ax, ay = pol(cx, cy, r * c.rng.uniform(.2, .7), c.rng.uniform(0, 360))
        out += f'<circle cx="{f(ax)}" cy="{f(ay)}" r="5" class="tint ink thin"/><path class="light ink hair" d="M{f(ax - 2.4)} {f(ay - 1.6)}a2.6 2.6 0 0 1 2.4 -1.8"/><path class="ink hair" d="M{f(ax)} {f(ay - 5)}l1 -3"/>'
    return out


def discus(c, x, y, r=34):
    """The Sudarshana discus: a toothed wheel of fire."""
    teeth = "".join(f"{'M' if k == 0 else 'L'}{f(pol(x, y, r + (9 if k % 2 == 0 else 0), k * 10)[0])} {f(pol(x, y, r + (9 if k % 2 == 0 else 0), k * 10)[1])}" for k in range(36)) + "Z"
    sp = "".join(f"M{f(pol(x, y, 8, a)[0])} {f(pol(x, y, 8, a)[1])}L{f(pol(x, y, r - 8, a)[0])} {f(pol(x, y, r - 8, a)[1])}" for a in range(0, 360, 30))
    return (f'<path class="tint ink thin" d="{teeth}"/><circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="light ink heavy"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{r - 6}" class="ink hair"/><path class="ink hair" d="{sp}"/><circle cx="{f(x)}" cy="{f(y)}" r="8" class="tint ink thin"/>')


def honeycomb(x, y, s=1, rows=4, cols=4):
    out = []
    w = 10 * s; h = w * math.sqrt(3)
    for r in range(rows):
        for q in range(cols - (r % 2)):
            cx = x + q * 2 * w * .88 + (r % 2) * w * .88; cy = y + r * h * .86
            pts = [pol(cx, cy, w, a) for a in range(30, 390, 60)]
            out.append('<path class="tint ink thin" d="M' + "L".join(f"{f(a)} {f(b)}" for a, b in pts) + 'Z"/>')
    return "".join(out)


def palm_books(x, y, s=1, r=0):
    """A bundle of palm-leaf manuscripts between wooden boards, tied with cord."""
    body = ('<path class="mid ink thin" d="M-40 -14H40V-8H-40Z"/><path class="light ink thin" d="M-38 -8H38V8H-38Z"/><path class="mid ink thin" d="M-40 8H40V14H-40Z"/>'
            '<path class="ink hair" d="M-38 -4H38M-38 0H38M-38 4H38"/><circle cx="-20" cy="0" r="2" class="fill-ink"/><circle cx="20" cy="0" r="2" class="fill-ink"/>'
            '<path class="ink thin" d="M-20 -14V14M20 -14V14M20 14C24 22 30 24 36 22"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})">{body}</g>'


def feather(x, y, s=1, r=0):
    """A peacock's eye feather."""
    barbs = "".join(f"M0 {-k * 8}C{-10 - k} {-k * 8 - 6} {-14} {-k * 8 - 14} {-12} {-k * 8 - 20}M0 {-k * 8}C{10 + k} {-k * 8 - 6} {14} {-k * 8 - 14} {12} {-k * 8 - 20}" for k in range(9))
    body = (f'<path class="ink hair" d="{barbs}"/><path class="ink thin" d="M0 20V-92"/>'
            '<ellipse cx="0" cy="-86" rx="14" ry="18" class="wash ink thin"/><ellipse cx="0" cy="-84" rx="9" ry="12" class="tint ink thin"/><ellipse cx="0" cy="-82" rx="4.4" ry="6" class="mid ink thin"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})">{body}</g>'


def vel(x, y, h=200, r=0, cls="light ink thin"):
    """Murugan's spear: a broad leaf-shaped blade on a long shaft, its point at x, y."""
    body = (f'<path class="{cls}" d="M0 0C-14 20 -18 44 -6 62H6C18 44 14 20 0 0Z"/><path class="ink hair" d="M0 6V58"/>'
            f'<path class="tint ink thin" d="M-8 62H8V70H-8Z"/><path class="{cls}" d="M-3 70V{h}H3V70Z"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r})">{body}</g>'


def serpent_ring(c, x, y, r, w=12):
    """The serpent that circles the world, biting its tail at the bottom."""
    p = c.p
    a0, a1 = 100, 430
    pts = [pol(x, y, r, a) for a in range(a0, a1 + 1, 10)]
    d = smooth(pts)
    scales = "".join(f"M{f(pol(x, y, r - w * .3, a)[0])} {f(pol(x, y, r - w * .3, a)[1])}L{f(pol(x, y, r + w * .3, a + 4)[0])} {f(pol(x, y, r + w * .3, a + 4)[1])}" for a in range(a0 + 6, a1, 8))
    hx, hy = pol(x, y, r, a1)
    return (rope(d, p, w, w - 4, "1 3", fill=p["T"]) + f'<path class="ink hair" d="{scales}"/>'
            f'<path class="wash ink thin" d="M{f(hx - 4)} {f(hy - 9)}C{f(hx - 18)} {f(hy - 12)} {f(hx - 28)} {f(hy - 6)} {f(hx - 30)} {f(hy + 2)}L{f(hx - 18)} {f(hy + 2)}C{f(hx - 12)} {f(hy + 8)} {f(hx - 2)} {f(hy + 10)} {f(hx + 4)} {f(hy + 6)}Z"/>'
            f'<circle cx="{f(hx - 12)}" cy="{f(hy - 4)}" r="1.8" class="fill-ink"/>')


def knot_heart(c, x, y, s=1):
    """A heart drawn as a single interlaced cord."""
    p = c.p
    d = (f"M{f(x)} {f(y + 64 * s)}C{f(x - 30 * s)} {f(y + 34 * s)} {f(x - 70 * s)} {f(y + 10 * s)} {f(x - 70 * s)} {f(y - 24 * s)}C{f(x - 70 * s)} {f(y - 52 * s)} {f(x - 40 * s)} {f(y - 66 * s)} {f(x - 18 * s)} {f(y - 54 * s)}"
         f"C{f(x - 4 * s)} {f(y - 46 * s)} {f(x + 6 * s)} {f(y - 30 * s)} {f(x + 18 * s)} {f(y - 10 * s)}"
         f"M{f(x)} {f(y + 64 * s)}C{f(x + 30 * s)} {f(y + 34 * s)} {f(x + 70 * s)} {f(y + 10 * s)} {f(x + 70 * s)} {f(y - 24 * s)}C{f(x + 70 * s)} {f(y - 52 * s)} {f(x + 40 * s)} {f(y - 66 * s)} {f(x + 18 * s)} {f(y - 54 * s)}"
         f"C{f(x + 4 * s)} {f(y - 46 * s)} {f(x - 6 * s)} {f(y - 30 * s)} {f(x - 18 * s)} {f(y - 10 * s)}")
    inner = (f"M{f(x)} {f(y + 40 * s)}C{f(x - 24 * s)} {f(y + 20 * s)} {f(x - 50 * s)} {f(y)} {f(x - 48 * s)} {f(y - 24 * s)}M{f(x)} {f(y + 40 * s)}C{f(x + 24 * s)} {f(y + 20 * s)} {f(x + 50 * s)} {f(y)} {f(x + 48 * s)} {f(y - 24 * s)}")
    fillp = (f"M{f(x)} {f(y + 64 * s)}C{f(x - 30 * s)} {f(y + 34 * s)} {f(x - 70 * s)} {f(y + 10 * s)} {f(x - 70 * s)} {f(y - 24 * s)}C{f(x - 70 * s)} {f(y - 52 * s)} {f(x - 40 * s)} {f(y - 66 * s)} {f(x - 18 * s)} {f(y - 54 * s)}"
             f"C{f(x - 8 * s)} {f(y - 48 * s)} {f(x - 2 * s)} {f(y - 40 * s)} {f(x)} {f(y - 34 * s)}C{f(x + 2 * s)} {f(y - 40 * s)} {f(x + 8 * s)} {f(y - 48 * s)} {f(x + 18 * s)} {f(y - 54 * s)}"
             f"C{f(x + 40 * s)} {f(y - 66 * s)} {f(x + 70 * s)} {f(y - 52 * s)} {f(x + 70 * s)} {f(y - 24 * s)}C{f(x + 70 * s)} {f(y + 10 * s)} {f(x + 30 * s)} {f(y + 34 * s)} {f(x)} {f(y + 64 * s)}Z")
    return f'<path class="tint" d="{fillp}" opacity=".85"/>' + rope(d, p, 9, 6, ".8 3") + rope(inner, p, 6, 3.6, ".6 2.4")


def endless_knot(c, x, y, s=1):
    """The endless knot: an interlaced diamond with a loop at each corner."""
    p = c.p
    r = 34 * s
    sq = f"M{f(x)} {f(y - r)}L{f(x + r)} {f(y)}L{f(x)} {f(y + r)}L{f(x - r)} {f(y)}Z"
    # the inner lattice: two lines each way, parallel to the diamond's sides
    lat = ""
    for t in (1 / 3, 2 / 3):
        lat += f"M{f(x - r + t * r)} {f(y - t * r)}L{f(x + t * r)} {f(y + r - t * r)}M{f(x - r + t * r)} {f(y + t * r)}L{f(x + t * r)} {f(y - r + t * r)}"
    loops = ""
    for a in (0, 90, 180, 270):
        cx, cy = pol(x, y, r * 1.12, a)
        loops += f"M{f(cx)} {f(cy)}m{f(-r * .26)} 0a{f(r * .26)} {f(r * .26)} 0 1 0 {f(r * .52)} 0a{f(r * .26)} {f(r * .26)} 0 1 0 {f(-r * .52)} 0"
    return rope(loops, p, 7 * s, 4.4 * s, ".7 2.6", fill=p["T"]) + f'<path class="wash" d="{sq}"/>' + rope(sq + lat, p, 7 * s, 4.4 * s, ".7 2.6", fill=p["T"])


def footprint(x, y, s=1, r=0, cls="light ink thin"):
    """A bare footprint, its toes forward (up): the sole, narrow at the heel, and five toes."""
    body = (f'<path class="{cls}" d="M-2 -30C8 -32 14 -24 13 -12C12 -2 11 8 9 18C7 28 2 33 -3 32C-9 31 -12 24 -11 14C-10 4 -12 -6 -12 -14C-12 -24 -8 -29 -2 -30Z"/>'
            + "".join(f'<ellipse cx="{f(dx)}" cy="{f(dy)}" rx="{f(rr)}" ry="{f(rr * 1.25)}" class="{cls}"/>' for dx, dy, rr in [(-7, -36, 4.2), (0, -39, 3.2), (6, -38, 2.8), (11, -35, 2.5), (14.5, -30, 2.2)])
            + '<path class="ink hair" d="M-6 -18C-4 -8 -4 4 -2 14"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})">{body}</g>'


def parasol(x, y, s=1, cls="tint ink thin"):
    """The parasol of honour, its handle's foot at x, y."""
    body = (f'<path class="ink heavy" d="M0 0V-104"/><path class="{cls}" d="M-40 -90C-30 -112 30 -112 40 -90' + "".join(f"Q{f(40 - (j + .5) * 80 / 6)} -82 {f(40 - (j + 1) * 80 / 6)} -90" for j in range(6)) + 'Z"/>'
            '<path class="ink hair" d="M0 -108L-30 -92M0 -108L30 -92M0 -108L-12 -90M0 -108L12 -90"/><circle cx="0" cy="-110" r="4" class="light ink thin"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s})">{body}</g>'


def water_pot(x, y, s=1, cls="wash ink thin"):
    """The ascetic's water pot with its spout and handle, its foot at x, y."""
    body = (f'<path class="{cls}" d="M-16 0C-26 -6 -26 -26 -12 -32L-10 -40H10L12 -32C26 -26 26 -6 16 0Z"/>'
            f'<path class="ink thin" d="M18 -22C28 -24 34 -30 36 -38M-10 -40C-14 -56 14 -56 10 -40"/><path class="tint ink thin" d="M-22 -16H22V-10H-22Z"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s})">{body}</g>'


def diya(x, y, s=1):
    """A clay oil lamp with its flame."""
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s})"><path class="tint ink thin" d="M-14 -4C-10 4 10 4 14 -4L18 -8C8 -6 -8 -6 -18 -8Z"/>'
            f'<path class="light ink thin" d="M14 -8C14 -18 10 -24 14 -30C20 -24 22 -16 18 -8Z"/></g>')


def tower(c, x, y, w=44, h=130, struck=True):
    """A stone tower on y, its top crowned; struck by lightning when struck."""
    out = (f'<path class="wash ink heavy" d="M{f(x - w / 2)} {f(y)}L{f(x - w / 2 + 4)} {f(y - h)}H{f(x + w / 2 - 4)}L{f(x + w / 2)} {f(y)}Z"/>'
           f'<path class="hatchfill" d="M{f(x + w / 6)} {f(y)}L{f(x + w / 6 + 2)} {f(y - h)}H{f(x + w / 2 - 4)}L{f(x + w / 2)} {f(y)}Z"/>'
           + "".join(f'<path class="ink hair" d="M{f(x - w / 2 + 4)} {f(y - k * 14)}H{f(x + w / 2 - 4)}"/>' for k in range(1, int(h / 14)))
           + f'<path class="plate ink thin" d="M{f(x - 6)} {f(y - h * .6)}V{f(y - h * .6 - 16)}C{f(x - 6)} {f(y - h * .6 - 22)} {f(x + 6)} {f(y - h * .6 - 22)} {f(x + 6)} {f(y - h * .6 - 16)}V{f(y - h * .6)}Z"/>'
           f'<path class="wash ink heavy" d="M{f(x - w / 2 - 4)} {f(y - h)}V{f(y - h - 12)}H{f(x - w / 4)}V{f(y - h - 4)}H{f(x - 4)}V{f(y - h - 12)}H{f(x + 4)}V{f(y - h - 4)}H{f(x + w / 4)}V{f(y - h - 12)}H{f(x + w / 2 + 4)}V{f(y - h)}Z"/>')
    if struck:
        out += (f'<path class="tint ink thin" d="M{f(x + 60)} {f(y - h - 70)}L{f(x + 14)} {f(y - h - 20)}L{f(x + 28)} {f(y - h - 22)}L{f(x + 2)} {f(y - h + 6)}L{f(x + 34)} {f(y - h - 32)}L{f(x + 20)} {f(y - h - 30)}L{f(x + 70)} {f(y - h - 70)}Z"/>'
                + flame(c, x - 2, y - h * .6 - 8, 26, 14) + flame(c, x + 6, y - h - 6, 30, 16))
    return out


def eclipse(c, x, y, r=26):
    """The moon in eclipse: a dark disc, its edge burning, a thin crescent left."""
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{r + 5}" fill="none" stroke="{c.p["T"]}" stroke-width="2"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="light ink thin"/><circle cx="{f(x + r * .26)}" cy="{f(y - r * .1)}" r="{f(r * .94)}" class="mid ink thin"/>'
            f'<circle cx="{f(x + r * .26)}" cy="{f(y - r * .1)}" r="{f(r * .94)}" fill="url(#hx)" opacity=".6"/>')


def rainbow(c, x, y, r, bands=("tint", "wash", "light", "mid"), w=9):
    out = []
    for k, cls in enumerate(bands):
        rr = r - k * w
        out.append(f'<path class="{cls} ink thin" d="M{f(x - rr)} {f(y)}A{f(rr)} {f(rr)} 0 0 1 {f(x + rr)} {f(y)}H{f(x + rr - w)}A{f(rr - w)} {f(rr - w)} 0 0 0 {f(x - rr + w)} {f(y)}Z"/>')
    return "".join(out)


def conch(x, y, s=1, r=0, cls="light ink heavy"):
    """The great conch, its mouth to the left."""
    body = (f'<path class="{cls}" d="M-46 6C-50 -10 -36 -26 -10 -30C14 -34 36 -26 50 -12C56 -6 60 0 58 6C50 4 44 8 40 14C30 24 10 30 -10 28C-30 26 -42 18 -46 6Z"/>'
            '<path class="tint ink thin" d="M-46 6C-40 -4 -28 -10 -14 -10C-4 -10 2 -4 0 4C-2 12 -14 16 -26 16C-36 16 -44 12 -46 6Z"/>'
            '<path class="ink thin" d="M58 6C64 4 70 6 74 2C70 10 64 14 56 12"/>'
            '<path class="ink hair" d="M6 -30C10 -20 10 -6 4 6M22 -28C26 -18 26 -4 20 8M36 -22C40 -14 40 -2 34 10M-20 -26C-12 -22 -4 -16 0 -8"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})">{body}</g>'


def serpent_coil(c, x, y, s=1):
    """A great serpent coiled on the ground, its head raised to the left."""
    p = c.p
    coils = "".join(f'<ellipse cx="{f(x)}" cy="{f(y - k * 12 * s)}" rx="{f((70 - k * 16) * s)}" ry="{f((14 - k * 2) * s)}" class="tint ink thin"/>'
                    f'<path class="ink hair" d="M{f(x - (60 - k * 16) * s)} {f(y - k * 12 * s)}q{f(8 * s)} {f(6 * s)} {f(16 * s)} 0m{f(20 * s)} {f(4 * s)}q{f(8 * s)} {f(6 * s)} {f(16 * s)} 0m{f(20 * s)} {f(-2 * s)}q{f(8 * s)} {f(6 * s)} {f(16 * s)} 0"/>' for k in range(3))
    neck = [(x - 10 * s, y - 34 * s), (x - 30 * s, y - 64 * s), (x - 20 * s, y - 100 * s), (x - 44 * s, y - 122 * s)]
    head = (f'<path class="tint ink thin" d="M{f(x - 44 * s)} {f(y - 136 * s)}C{f(x - 60 * s)} {f(y - 138 * s)} {f(x - 78 * s)} {f(y - 130 * s)} {f(x - 82 * s)} {f(y - 124 * s)}'
            f'C{f(x - 74 * s)} {f(y - 114 * s)} {f(x - 56 * s)} {f(y - 112 * s)} {f(x - 40 * s)} {f(y - 116 * s)}Z"/>'
            f'<circle cx="{f(x - 58 * s)}" cy="{f(y - 128 * s)}" r="{f(2.2 * s)}" class="light ink hair"/>'
            f'<path class="ink thin" d="M{f(x - 82 * s)} {f(y - 124 * s)}l{f(-10 * s)} {f(-2 * s)}m{f(10 * s)} {f(2 * s)}l{f(-10 * s)} {f(4 * s)}"/>')
    return coils + rope(smooth(neck), p, 14 * s, 10 * s, "1 3.4", fill=p["T"]) + head


def wolf(c, x, y, s=1, pose="lying", flip=False, cls="wash ink thin"):
    """A wolf in profile, facing left: lying with its head up ("lying", its jaws held open) or at full
    stretch ("running"). Grey-washed, its shadow side hatched, its fur cut in short strokes."""
    if pose == "lying":
        body = ("M-60 -46C-50 -54 -36 -54 -26 -46C-14 -42 6 -40 30 -36C46 -34 58 -28 62 -18C66 -8 62 2 54 4"
                "L-36 4C-46 4 -50 -2 -52 -8C-56 -14 -60 -24 -62 -34Z")
        head = ("M-60 -46C-66 -50 -74 -50 -82 -46L-100 -38C-104 -36 -104 -32 -100 -31L-82 -32L-98 -18C-100 -15 -97 -12 -94 -13"
                "L-74 -22C-66 -24 -58 -26 -54 -32C-52 -38 -55 -44 -60 -46Z")
        ear = "M-62 -48L-60 -66L-50 -50Z M-54 -48L-48 -64L-42 -48Z"
        legs = [taper([(-44, -2), (-70, 2), (-94, 4)], 14, 9), taper([(-36, 0), (-62, 6), (-84, 8)], 12, 8)]
        tail = taper([(60, -14), (76, 0), (62, 12), (30, 12)], 18, 6)
        shade = "M-36 4C-20 -6 30 -8 54 4Z"
        fur = "".join(f"M{x0} {y0}l-6 4" for x0, y0 in [(-40, -44), (-28, -42), (-14, -40), (0, -38), (14, -37), (28, -35), (42, -32), (54, -26)])
        extra = ('<path class="mid ink hair" d="M-82 -32L-94 -18L-74 -24Z"/><circle cx="-70" cy="-40" r="2" class="fill-ink"/><path class="fill-ink" d="M-104 -36l-3 1l3 3Z"/>'
                 '<path class="ink hair" d="M-76 -42C-72 -44 -66 -44 -62 -42M-56 -34C-50 -30 -46 -24 -44 -14"/>'
                 '<path class="ink thin" d="M18 -4C22 -22 50 -28 58 -12C60 -2 52 4 42 4"/><path class="ink hair" d="M24 -8C30 -18 46 -20 52 -12"/>')
    else:
        body = ("M-50 -30C-40 -38 -10 -40 16 -36C32 -34 42 -38 52 -42C60 -36 62 -26 58 -18C52 -8 40 -4 26 -4"
                "C10 -4 -8 -8 -24 -6C-38 -4 -48 -10 -52 -18C-54 -24 -54 -28 -50 -30Z")
        head = ("M52 -42C60 -50 72 -52 80 -48L100 -42C104 -40 104 -36 100 -35L82 -32L96 -26C96 -22 92 -20 88 -22L72 -24C64 -24 58 -22 56 -18Z")
        ear = "M58 -46L62 -62L68 -48Z M64 -48L72 -60L74 -46Z"
        legs = [taper([(40, -8), (60, 6), (84, 10)], 12, 7), taper([(30, -6), (46, 12), (70, 20)], 11, 7),
                taper([(-40, -14), (-62, 2), (-90, 4)], 16, 7), taper([(-32, -10), (-50, 10), (-78, 16)], 14, 7)]
        tail = taper([(-50, -26), (-76, -28), (-104, -20)], 16, 6)
        shade = "M-24 -6C-8 -12 20 -12 26 -4C10 -4 -8 -8 -24 -6Z"
        fur = "".join(f"M{x0} {y0}l-7 3" for x0, y0 in [(-36, -34), (-22, -36), (-8, -37), (6, -36), (20, -35), (34, -37), (46, -40)])
        extra = ('<circle cx="72" cy="-42" r="2" class="fill-ink"/><path class="fill-ink" d="M104 -40l3 1l-3 3Z"/>'
                 '<path class="ink hair" d="M66 -46C70 -48 76 -48 80 -46M58 -26C54 -20 48 -14 40 -10"/>')
    sx = -s if flip else s
    parts = "".join(f'<path class="{cls}" d="{d}"/>' for d in legs[:len(legs) // 2])
    tl = [(60, -14), (76, 0), (62, 12)] if pose == "lying" else [(-50, -26), (-76, -28), (-104, -20)]
    parts += f'<path class="{cls}" d="{tail}"/><path class="ink hair" d="' + "".join(f"M{f(tx)} {f(ty)}l-6 -3" for tx, ty in densify(tl, 3)[1:-1]) + '"/>'
    parts += f'<path class="{cls}" d="{body}"/><path fill="url(#hd)" d="{shade}" opacity=".9"/>'
    parts += "".join(f'<path class="{cls}" d="{d}"/>' for d in legs[len(legs) // 2:])
    parts += f'<path class="{cls}" d="{head}"/><path class="mid ink thin" d="{ear}"/><path class="ink hair" d="{fur}"/>{extra}'
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{parts}</g>'


def horse(c, x, y, s=1, cls="wash ink thin"):
    """A horse standing in profile, facing right, its hooves on y: a deep chest and arched neck, the long
    head with its large eye, ears pricked, mane and tail in strands, legs with knee, hock and hoof."""
    body = ("M20 -70C8 -66 -6 -64 -20 -66C-30 -67 -38 -67 -44 -63C-50 -58 -52 -50 -50 -42C-48 -36 -42 -34 -36 -33"
            "C-24 -30 -4 -29 14 -31C24 -32 32 -36 38 -44C42 -50 44 -58 50 -70C55 -78 58 -84 64 -88"
            "L78 -72C82 -68 86 -66 86 -62C86 -58 82 -56 78 -58C72 -60 66 -66 60 -70C56 -66 52 -60 48 -50"
            "C44 -40 38 -34 30 -34Z")
    head = ("M50 -96C54 -102 60 -102 64 -98C70 -92 80 -80 88 -70C92 -66 92 -61 88 -59C84 -57 80 -59 76 -61"
            "C70 -64 64 -70 58 -74C54 -78 50 -84 48 -90C47 -93 48 -95 50 -96Z")
    neck = ("M22 -70C30 -80 38 -92 50 -96C52 -88 56 -80 60 -74C54 -64 48 -52 44 -44C38 -38 30 -36 22 -40Z")
    legs = [taper([(34, -40), (35, -22), (37, -8), (38, -1)], 11, 6), taper([(24, -38), (22, -20), (21, -8), (20, -1)], 10, 6),
            taper([(-38, -46), (-46, -24), (-41, -8), (-40, -1)], 17, 6), taper([(-28, -40), (-34, -22), (-29, -8), (-28, -1)], 13, 6)]
    out = "".join(f'<path class="{cls}" d="{d}"/><path fill="url(#hd)" d="{d}" opacity=".7"/>' for d in legs[1::2])
    out += f'<path class="{cls}" d="{taper([(-48, -60), (-58, -44), (-60, -24), (-56, -10)], 13, 4)}"/>'
    out += '<path class="ink hair" d="M-50 -56C-56 -44 -58 -30 -56 -16M-54 -52C-58 -40 -60 -28 -60 -18"/>'
    out += f'<path class="{cls}" d="{body}"/><path class="{cls}" d="{neck}"/><path class="{cls}" d="{head}"/>'
    out += ('<path fill="url(#hd)" d="M-36 -33C-24 -30 -4 -29 14 -31C24 -32 30 -35 34 -40C20 -38 0 -38 -20 -40C-30 -41 -38 -40 -44 -38Z" opacity=".9"/>'
            '<path class="mid ink thin" d="M50 -96C42 -94 34 -86 28 -78C24 -74 22 -72 20 -70C26 -72 30 -76 34 -80C36 -76 38 -74 40 -74C42 -80 46 -88 50 -96Z"/>'
            '<path class="ink hair" d="M46 -92l-6 6M42 -88l-6 6M38 -84l-6 6M34 -80l-6 5"/>'
            '<path class="mid ink thin" d="M52 -98L50 -110L57 -100ZM57 -99L58 -111L62 -100Z"/>'
            '<circle cx="64" cy="-88" r="3.6" class="light ink thin"/><circle cx="64.6" cy="-88" r="1.8" class="fill-ink"/>'
            '<path class="ink hair" d="M58 -92C62 -94 66 -94 70 -91M84 -64C86 -63 88 -63 89 -64M76 -62C80 -66 82 -70 84 -72M-10 -60C-2 -58 6 -58 14 -60M34 -58C38 -52 40 -46 40 -40"/>'
            '<circle cx="86" cy="-64" r="1" class="fill-ink"/>')
    out += "".join(f'<path class="{cls}" d="{d}"/><path fill="url(#hd)" d="{d}" opacity=".5"/>' for d in legs[0::2])
    out += "".join(f'<path class="mid ink thin" d="M{hx - 4.5} -3H{hx + 4.5}L{hx + 5.5} 1H{hx - 5.5}Z"/>' for hx in (38, 20, -40, -28))
    return f'<g transform="translate({f(x)} {f(y)}) scale({s})">{out}</g>'


def root(c, pts, w0, w1, cls="wash ink heavy"):
    """A great gnarled root or bough: thick at its start, tapering, with its bark cut in."""
    d = taper(pts, w0, w1)
    P = densify(pts, 6)
    bark = "".join(f"M{f(px)} {f(py)}l{f(rr)} {f(-rr * .6)}" for px, py, rr in ((px, py, 3 + (k % 3)) for k, (px, py) in enumerate(P[1:-2:2])))
    side = taper([(px + 2, py + w0 * .18) for px, py in pts], w0 * .45, w1 * .3)
    return f'<path class="{cls}" d="{d}"/><path fill="url(#hd)" d="{side}" opacity=".85"/><path class="ink hair" d="{bark}"/>'



def root_arch(c, pts, w0, w1, rootlets=(), cls="wash ink heavy"):
    """A great root as an engraver cuts it: its bark running along its length in broken lines, knots
    swelling on it, one side in shadow, and fine rootlets hanging from beneath."""
    P = densify(pts, 10)
    n = len(P)
    outline = taper(pts, w0, w1)
    out = [f'<path class="{cls}" d="{outline}"/>']
    def offset(k_off, a=0, b=1):
        Q = []
        for i in range(int(a * (n - 1)), int(b * (n - 1)) + 1):
            x, y = P[i]; x0, y0 = P[max(i - 1, 0)]; x1, y1 = P[min(i + 1, n - 1)]
            dx, dy = x1 - x0, y1 - y0; m = math.hypot(dx, dy) or 1
            w = (w0 + (w1 - w0) * i / (n - 1)) / 2
            Q.append((x - dy / m * w * k_off, y + dx / m * w * k_off))
        return Q
    shade = offset(.25) + offset(.95)[::-1]
    out.append(f'<path fill="url(#hd)" d="M' + "L".join(f"{f(a)} {f(b)}" for a, b in shade) + 'Z" opacity=".85"/>')
    rng = c.rng
    for k_off in (-.7, -.4, -.1, .2, .5):
        a = rng.uniform(0, .25); b = rng.uniform(.55, 1)
        Q = offset(k_off, a, b)
        if len(Q) > 3: out.append(f'<path class="ink hair" d="{smooth(Q[::2])}"/>')
    for t in (.22, .48, .74):
        x, y = P[int(t * (n - 1))]; w = (w0 + (w1 - w0) * t) / 2
        out.append(f'<ellipse cx="{f(x)}" cy="{f(y - w * .2)}" rx="{f(w * .42)}" ry="{f(w * .26)}" class="{cls.replace("heavy", "thin")}"/><ellipse cx="{f(x)}" cy="{f(y - w * .2)}" rx="{f(w * .18)}" ry="{f(w * .1)}" class="ink hair"/>')
    for t, length in rootlets:
        Q = offset(.9); x, y = Q[int(t * (len(Q) - 1))]
        d = f"M{f(x)} {f(y)}C{f(x + rng.uniform(-8, 8))} {f(y + length * .4)} {f(x + rng.uniform(-10, 10))} {f(y + length * .7)} {f(x + rng.uniform(-6, 6))} {f(y + length)}"
        out.append(f'<path class="ink thin" d="{d}"/><path class="ink hair" d="M{f(x)} {f(y + length * .3)}l{f(rng.uniform(-8, 8))} {f(length * .25)}"/>')
    return "".join(out)
