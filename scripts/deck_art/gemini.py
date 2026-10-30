"""Gemini: the 8, 9 and 10 of Vajras and of Swords (Jupiter, Mars and the Sun), and the voids at
stations XXII (Hiranyaksha), XXV (Prahlada) and XXVII (Ketu-Asura)."""
import math
from lib import *

S, RUNE2 = "Gemini", ("Raidho", "Kenaz")


def b06():
    c = Plate("air", 81, "8 of Vajras, engraved: eight vajras laid as a lattice fence across the mountain path, clouds gathering at the pass, under the seal of Jupiter between the twin pillars",
              glow=(190, 150, 220))
    emblems(c, "vaj")
    c(mountain(c, -30, 210, (84, 120), 300, snow=True), mountain(c, 170, 410, (300, 128), 300, snow=True))
    c('<path class="ink hair" d="M70 150L40 220M84 140L70 200M96 150L120 230M286 160L256 230M300 150L292 210M312 160L340 240"/>')
    c(cloud(c, 190, 152, 120, 26), cloud(c, 96, 176, 90, 18, shade=False), cloud(c, 286, 180, 96, 20, shade=False))
    c(ground(c, 296))
    c('<path class="light ink thin" d="M150 360C168 330 180 300 184 268C186 240 188 214 190 190C192 214 194 240 196 268C200 300 212 330 230 360Z"/>',
      '<path class="ink hair" d="M176 330h10M186 304h8M182 284h6M192 262h5M188 240h4"/>')
    rail = '<path class="ink thin" d="M78 268C140 262 240 262 302 268M78 222C140 216 240 216 302 222"/>'
    c(rail)
    for x in (116, 166, 216, 266):
        c(use("vaj", x, 245, .8, -34), use("vaj", x, 245, .8, 34), f'<circle cx="{x}" cy="245" r="3" class="tint ink thin"/>')
    c('<path class="ink thin" d="M78 214V280M302 214V280"/><circle cx="78" cy="212" r="3.6" class="tint ink thin"/><circle cx="302" cy="212" r="3.6" class="tint ink thin"/>')
    c(crown(c, S, "Jupiter"))
    return c


def b07():
    c = Plate("air", 82, "9 of Vajras, engraved: nine vajras falling as thunderbolts from the storm-cloud onto a lone peak, rain driving, the teardrop of Ardra shining below, under the seal of Mars between the twin pillars",
              glow=(190, 230, 200))
    emblems(c, "vaj")
    c(storm(c, 104, depth=20, cls="light ink thin"), storm(c, 122, depth=20, cls="wash ink thin"))
    c(rain(c, 0, 380, 120, 300, 70, -8, 16))
    c(mountain(c, 110, 270, (190, 236), 304), ground(c, 300))
    spots = [(70, 150), (190, 146), (310, 150), (110, 196), (232, 192), (330, 210), (52, 232), (150, 246), (286, 256)]
    for k, (x, y) in enumerate(spots):
        c(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2" stroke-linejoin="round" d="M{x - 16} {y - 44}L{x - 6} {y - 30}L{x - 14} {y - 26}L{x - 2} {y - 14}"/>')
        c(use("vaj", x, y, .78, 24 + (k % 3) * 6))
    c('<path class="tint ink thin" d="M318 290C324 300 330 306 330 314C330 322 324 326 318 326C312 326 306 322 306 314C306 306 312 300 318 290Z"/><path class="light" d="M312 312C312 306 314 304 316 302C314 308 314 312 314 316Z"/>')
    c(crown(c, S, "Mars"))
    return c


def b08():
    c = Plate("air", 83, "10 of Vajras, engraved: a broken stupa on the plain, ten vajras standing upright in its rubble, the sun rising behind it, under the seal of the Sun between the twin pillars",
              glow=(190, 236, 210), sky=300)
    emblems(c, "vaj")
    c(sun_rays(c, 190, 250, 64, 230, 186, 354, 12), '<path class="wash ink heavy" d="M130 250A60 60 0 0 1 250 250Z"/><path class="ink hair" d="M138 250A52 52 0 0 1 242 250"/>')
    c(ground(c, 262))
    c('<path class="wash ink heavy" d="M112 262V242H268V262Z"/><path class="hatchfill" d="M232 242H268V262H232Z"/><path class="ink hair" d="M112 252H268M140 242V252M180 242V252M220 242V252M160 252V262M200 252V262M240 252V262"/>',
      '<path class="wash ink heavy" d="M132 242C132 196 150 170 172 162L184 176L196 158C222 166 248 196 248 242Z"/>',
      '<path class="hatchfill" d="M214 168C236 180 248 206 248 242H220C222 214 220 190 214 168Z"/>',
      '<path class="ink thin" d="M184 176L176 202L190 214L182 242M196 158L204 186"/>',
      '<path class="light ink thin" d="M284 254L310 238L318 244L292 262Z"/><path class="ink hair" d="M290 252L314 240"/>',
      '<ellipse cx="322" cy="246" rx="10" ry="3" transform="rotate(-30 322 246)" class="tint ink thin"/><ellipse cx="333" cy="240" rx="8" ry="2.6" transform="rotate(-30 333 240)" class="wash ink thin"/>',
      '<path class="wash ink thin" d="M96 262l8 -8l10 4l2 6ZM256 262l6 -10l12 2l4 8ZM60 286l10 -8l12 4l2 8ZM302 290l8 -10l12 4l2 8ZM150 282l6 -6l8 2l2 6Z"/>')
    for k, (x, y, s) in enumerate([(40, 318, .9), (78, 304, .82), (116, 296, .76), (156, 300, .8), (190, 318, .94), (224, 300, .8), (264, 296, .76), (302, 304, .82), (340, 318, .9), (190, 278, .66)]):
        c(f'<path class="ink thin" d="M{x - 8} {y + 26}C{x - 3} {y + 22} {x + 3} {y + 22} {x + 8} {y + 26}"/>', use("vaj", x, y, s))
    c(crown(c, S, "Sun"))
    return c


def n06():
    c = Plate("air", 84, "8 of Swords, engraved: eight swords planted in a ring about a runestone bound with rope, mist lying in the hollow, under the seal of Jupiter between the twin pillars",
              glow=(190, 200, 220))
    emblems(c, "sword")
    c(hills(c, 236, [(60, 40), (180, 26), (320, 46)]))
    c(ground(c, 300))
    c('<path class="wash ink heavy" d="M154 306C150 244 158 176 178 146C186 134 198 134 204 146C222 178 230 244 226 306Z"/>',
      '<path class="hatchfill" d="M202 144C222 178 230 244 226 306H210C214 250 212 190 202 144Z"/>')
    c(rope("M152 186C176 196 204 196 228 186M150 222C176 232 206 232 230 222M152 258C176 268 206 268 228 258M156 170L224 274M226 170L156 274", c.p, 6, 3.8, ".8 2.6"))
    for y in (212, 250):
        c(f'<path class="ink hair" stroke-dasharray="14 6" d="M0 {y + 40}C60 {y + 34} 120 {y + 44} 190 {y + 38}S320 {y + 32} 380 {y + 40}"/>')
    for k, (x, y, r, s) in enumerate([(70, 268, -10, .9), (104, 248, -6, .82), (134, 236, -3, .76), (60, 318, -12, 1), (246, 236, 3, .76), (276, 248, 6, .82), (310, 268, 10, .9), (320, 318, 12, 1)]):
        c(f'<path class="ink thin" d="M{x - 9} {y + 6}C{x - 3} {y + 2} {x + 3} {y + 2} {x + 9} {y + 6}"/>', use("sword", x, y - 30 * s, s, 180 + r))
    c('<path class="ink hair" stroke-dasharray="14 6" d="M0 330C60 324 120 334 190 328S320 322 380 330M0 346C70 342 140 350 210 346S330 342 380 346"/>')
    c(crown(c, S, "Jupiter"))
    return c


def n07():
    c = Plate("air", 85, "9 of Swords, engraved: nine swords falling point-first into a dark field by night, two already standing in it, a raven on the near stone, under the seal of Mars between the twin pillars",
              glow=(190, 160, 260))
    emblems(c, "sword")
    c('<rect x="0" y="92" width="380" height="200" fill="url(#hx)" opacity=".45"/>')
    c(ground(c, 290, cls="wash ink thin"), '<rect x="0" y="292" width="380" height="68" fill="url(#hx)" opacity=".8"/>')
    for k, (x, y, r) in enumerate([(66, 132, 8), (128, 124, 4), (190, 120, 0), (252, 124, -4), (314, 132, -8), (96, 196, 6), (190, 190, 0), (284, 196, -6), (150, 248, 3)]):
        c(f'<path class="ink hair" d="M{x} {y - 58}V{y - 76}M{x - 6} {y - 54}V{y - 66}M{x + 6} {y - 54}V{y - 66}"/>' if k < 5 else "")
        c(use("sword", x, y, .62, 180 + r))
    c(use("sword", 238, 282, .74, 186), f'<path class="ink thin" d="M228 300C234 296 242 296 248 300"/>')
    c('<path class="wash ink heavy" d="M20 360C18 320 24 290 40 276C52 266 66 268 74 280C86 298 90 330 88 360Z"/><path class="hatchfill" d="M66 270C80 286 90 320 88 360H74C78 330 76 296 66 270Z"/>')
    c(raven(c, 72, 272, 1.15))
    c(crown(c, S, "Mars"))
    return c


def n08():
    c = Plate("air", 86, "10 of Swords, engraved: ten swords driven into the ground before the charred frame of a hall, the sun rising behind the far hills, under the seal of the Sun between the twin pillars",
              glow=(190, 230, 210), sky=300)
    emblems(c, "sword")
    c(sun_rays(c, 190, 232, 50, 220, 188, 352, 11), '<path class="wash ink heavy" d="M144 232A46 46 0 0 1 236 232Z"/>')
    c(hills(c, 236, [(40, 16), (150, 10), (250, 14), (350, 18)]))
    c(rope("M96 258V198M120 258V186M150 258V172M230 258V172M260 258V186M284 258V198", c.p, 7, 4, ".7 2.4", fill=c.p["M"], cap="butt"),
      rope("M90 200L190 150L262 186M120 186L150 172M300 206L248 180", c.p, 6, 3.4, ".7 2.4", fill=c.p["M"]),
      '<path class="ink thin" d="M120 186L150 210M260 186L232 212M150 172L190 196L212 182"/><path class="fill-ink" d="M186 152L194 152L190 140Z"/>',
      '<path class="ink hair" d="M160 140C156 128 164 120 160 108M196 136C200 122 192 114 198 100M228 150C224 138 232 132 228 122"/>')
    c(ground(c, 262))
    xs = [36, 70, 104, 138, 172, 208, 242, 276, 310, 344]
    for k, x in enumerate(xs):
        y = 300 + (12 if k % 2 else 0)
        c(f'<path class="ink thin" d="M{x - 9} {y + 6}C{x - 3} {y + 2} {x + 3} {y + 2} {x + 9} {y + 6}"/>', use("sword", x, y - 34, .62, 180 + (k - 4.5) * 2.4))
    c(crown(c, S, "Sun"))
    return c


# ---------------------------------------------------------------- the voids
def v022():
    c = Plate("void", 122, "Hiranyaksha, engraved white on black: the earth dragged down into the black ocean, the great boar rising out of the deep to lift her on his tusk, the river running beneath",
              glow=(220, 150, 220), sky=304)
    c(stars(c, 9, y1=84))
    c(waves(c, 96, amp=8, length=40, cls="wash ink thin", hatch=False))
    c('<rect x="0" y="106" width="380" height="198" fill="url(#hx)" opacity=".4"/>')
    for x, y, r in [(300, 210, 3), (312, 180, 2.2), (292, 150, 1.6), (70, 160, 2.4), (58, 130, 1.6), (320, 250, 2)]:
        c(f'<circle cx="{x}" cy="{y}" r="{r}" class="ink hair"/>')
    # the earth, sunk to the deep, balanced on the tusk
    c('<circle cx="238" cy="140" r="34" class="tint ink heavy"/><circle cx="238" cy="140" r="28" class="ink hair"/>',
      '<path class="wash ink thin" d="M216 128C224 116 240 118 246 128C254 122 266 130 262 140C270 150 258 162 248 158C240 170 222 164 222 152C210 150 208 136 216 128Z"/>',
      '<path class="ink hair" d="M204 140H272M210 122C226 130 250 130 266 122M210 158C226 150 250 150 266 158"/>',
      '<path class="ink hair" d="M216 104C212 92 220 86 216 74M240 104C244 92 236 84 242 72M262 108C258 98 264 92 262 82"/>')
    # the boar, rising in profile from the bottom of the sea, snout up
    head = "M64 304C60 268 76 236 110 214C132 200 160 194 186 196L226 196C236 196 244 202 246 210C248 218 244 226 236 228L212 232C196 244 188 262 192 304Z"
    c(f'<path class="wash ink heavy" d="{head}"/>', f'<path fill="url(#hd)" d="M192 304C188 262 196 244 212 232L236 228C222 250 214 276 216 304Z" opacity=".9"/>',
      '<path class="ink hair" d="M84 276C104 260 128 250 156 246M80 292C102 278 128 270 160 268M100 236C120 226 144 222 170 222"/>')
    for k in range(16):
        t = k / 15; x = 64 + (148 - 64) * t + 6 * math.sin(t * 3); y = 300 - (300 - 204) * (t ** .8)
        c(f'<path class="ink thin" d="M{f(x)} {f(y)}l{f(-10 + t * 4)} {f(-12 + t * 2)}"/>')
    c('<path class="mid ink thin" d="M128 208L112 170L150 198Z"/><path class="ink hair" d="M120 190L134 202"/>',
      '<path class="light ink thin" d="M168 212C174 206 184 206 188 212C182 216 174 216 168 212Z"/><circle cx="179" cy="211" r="2.2" class="fill-ink"/>',
      '<ellipse cx="243" cy="212" rx="5" ry="10" transform="rotate(-14 243 212)" class="mid ink thin"/><circle cx="242" cy="208" r="1.4" class="fill-ink"/><circle cx="244" cy="216" r="1.4" class="fill-ink"/>',
      '<path class="ink thin" d="M212 232C204 236 198 236 192 232"/>')
    c('<path class="light ink heavy" d="M214 228C232 226 246 214 248 196C250 186 246 178 240 174C238 186 232 200 220 208C214 212 210 220 214 228Z"/><path class="ink hair" d="M220 220C232 214 240 202 242 188"/>')
    c(river_beneath(c))
    return c


def v025():
    c = Plate("void", 125, "Prahlada, engraved white on black: a ring of fire burning about a lotus that sits in its heart untouched, the pillar beside it split open, the river running beneath",
              glow=(190, 220, 220), sky=304)
    emblems(c, "lotus")
    c(stars(c, 10, y1=110))
    c(ground(c, 290, hatch=False, cls="wash ink thin"))
    for k in range(13):
        a = 180 + k * 15
        x, y = pol(190, 250, 104, a)
        c(flame(c, x, y + 30 - (0 if k in (0, 12) else 0), 46 + (k % 3) * 10, 22))
    c(use("lotus", 190, 250, 1.5), '<ellipse cx="190" cy="262" rx="40" ry="6" class="ink hair"/>')
    c('<path class="wash ink heavy" d="M312 296V120H340V296Z"/><path class="hatchfill" d="M330 120H340V296H330Z"/><path class="light ink thin" d="M306 110H346V120H306ZM306 296H346V304H306Z"/>',
      '<path class="fill-ink" d="M320 120L330 160L318 196L332 236L322 296H326L338 236L324 196L336 160L326 120Z"/>',
      f'<path fill="none" stroke="{c.p["T"]}" stroke-width="1.4" d="M324 140L304 132M330 190L352 182M324 226L302 232"/>')
    c(river_beneath(c))
    return c


def v027():
    c = Plate("void", 127, "Ketu-Asura, engraved white on black: the asura's headless body streaming across the night as a comet, its tail ending in a serpent's tip, his pennant flying from a staff on the bank, the river running beneath",
              glow=(110, 110, 230), sky=304)
    hx, hy = 104, 104
    c(stars(c, 22, y1=290, avoid=lambda x, y: math.hypot(x - hx, y - hy) < 40 or (x > hx and abs((y - hy) - (x - hx) * .62) < 50)))
    # the tail, fanning out from where the head should be
    edge_a = [(hx + 8, hy - 6), (170, 120), (240, 150), (300, 186), (340, 214)]
    edge_b = [(hx + 4, hy + 8), (160, 152), (220, 200), (270, 236), (300, 258)]
    tail = smooth(edge_a) + "L" + smooth(edge_b[::-1])[1:] + "Z"
    c(f'<path class="tint" d="{tail}" opacity=".35"/>')
    for k in range(13):
        t = k / 12
        e = [(ax + (bx - ax) * t, ay + (by - ay) * t) for (ax, ay), (bx, by) in zip(edge_a, edge_b)]
        c(f'<path class="{"ink thin" if k in (0, 12) else "ink hair"}" d="{smooth(e)}"/>')
    c('<path class="tint ink thin" d="M340 214C352 220 362 232 358 244C354 254 340 254 336 246C334 240 340 236 344 240"/><path class="tint ink thin" d="M300 258C306 270 304 282 294 286"/>')
    # where the head should be: a ring of light round nothing
    c(sun_rays(c, hx, hy, 18, 34, 0, 360, 22, 2.4))
    c(f'<circle cx="{hx}" cy="{hy}" r="15" class="light ink heavy"/><circle cx="{hx}" cy="{hy}" r="9" class="plate ink thin"/>')
    # his pennant on the bank
    c('<path class="ink heavy" d="M58 304V190"/><circle cx="58" cy="187" r="3.4" class="tint ink thin"/>',
      '<path class="tint ink thin" d="M60 194C84 190 104 200 132 196L114 210L134 224C106 228 86 218 60 222Z"/><path class="ink hair" d="M62 202C84 200 100 206 118 204M62 212C84 210 100 216 120 216"/>')
    c(river_beneath(c))
    return c


CARDS = {"b06": b06, "b07": b07, "b08": b08, "n06": n06, "n07": n07, "n08": n08, "v022": v022, "v025": v025, "v027": v027}
