"""Scorpio: the 5, 6 and 7 of Lotuses and of Cups (Mars, the Sun and Venus), and the voids at
stations LXVII (Andhakasura), LXX (Jalandhara) and LXXII (Maricha)."""
import math
from lib import *

S = "Scorpio"


def wilted(x, y, s=1, lean=1):
    """A lotus gone over: its stalk bowed, its head hanging toward the water."""
    stalk = f"M{f(x)} {f(y + 70 * s)}C{f(x)} {f(y + 30 * s)} {f(x + lean * 10 * s)} {f(y)} {f(x + lean * 34 * s)} {f(y + 10 * s)}"
    return stalk, (x + lean * 36 * s, y + 18 * s, 180 - lean * 36)


def b21():
    c = Plate("water", 131, "5 of Lotuses, engraved: three lotuses bowed and dropping their petals into the pond, two still standing in flower behind them, under the seal of Mars between the scorpion's tails",
              glow=(190, 190, 200))
    emblems(c, "lotus")
    c(hills(c, 250, [(80, 18), (300, 24)]))
    c(sea(c, top=250, rows=7))
    for x, h in [(262, 150), (318, 170)]:
        c(rope(f"M{x} 330C{x - 4} 280 {x + 4} 220 {x} {h + 20}", c.p, 5, 3, ".6 2.2"), use("lotus", x, h + 18, 1.05), ripples(x, 332, 26, 1))
    for x, y, lean in [(70, 232, 1), (128, 246, -1), (180, 236, 1)]:
        st, (hx, hy, r) = wilted(x, y, 1, lean)
        c(rope(st, c.p, 5, 3, ".6 2.2"), use("lotus", hx, hy, .95, r), ripples(x, y + 72, 26, 1))
    for x, y, r in [(96, 300, 30), (150, 316, -50), (206, 306, 70), (60, 330, -20), (226, 336, 40)]:
        c(f'<path class="tint ink thin" transform="translate({x} {y}) rotate({r})" d="M0 2C-5 -3 -6 -11 0 -18C6 -11 5 -3 0 2Z"/>')
    c(crown(c, S, "Mars"))
    return c


def b22():
    c = Plate("water", 132, "6 of Lotuses, engraved: six lotuses set round the rim of a stone fountain playing in the sun, under the seal of the Sun between the scorpion's tails",
              glow=(190, 160, 220))
    emblems(c, "lotus")
    c(sun_rays(c, 190, 196, 40, 120, 196, 344, 12))
    c(ground(c, 300))
    c('<path class="wash ink heavy" d="M84 260C84 290 130 304 190 304C250 304 296 290 296 260Z"/><path class="hatchfill" d="M250 300C276 294 296 280 296 260H262C262 278 258 292 250 300Z"/>',
      '<ellipse cx="190" cy="260" rx="106" ry="18" class="light ink heavy"/><ellipse cx="190" cy="260" rx="92" ry="12" class="wash ink thin"/>',
      '<path class="ink hair" d="M110 262C140 266 240 266 270 262"/>',
      '<path class="wash ink heavy" d="M180 260V196H200V260Z"/><path class="hatchfill" d="M194 196H200V260H194Z"/><ellipse cx="190" cy="196" rx="24" ry="6" class="light ink thin"/>')
    c('<path class="ink thin" d="M186 192C170 160 140 160 120 196M194 192C210 160 240 160 260 196M188 190C184 170 178 152 172 140M192 190C196 170 202 152 208 140"/>',
      '<path class="ink hair" d="M120 196l-4 10M124 200l-2 12M260 196l4 10M256 200l2 12" stroke-dasharray="2 3"/>')
    for x, y in [(104, 256), (146, 270), (190, 274), (234, 270), (276, 256), (190, 142)]:
        c(use("lotus", x, y, .9 if y != 142 else .8))
    c(crown(c, S, "Sun"))
    return c


def b23():
    c = Plate("water", 133, "7 of Lotuses, engraved: seven lotuses floating on clouds, each bearing a vision, a jewel, a crown, a palace, a serpent, a flame, a moon and an eye, under the seal of Venus between the scorpion's tails",
              glow=(190, 200, 230))
    emblems(c, "lotus", "jewel")
    spots = [(76, 166), (152, 150), (228, 150), (304, 166), (112, 264), (190, 252), (268, 264)]
    for x, y in spots:
        c(cloud(c, x, y + 26, 74, 16, "light ink thin", False), use("lotus", x, y + 18, .9))
    x, y = spots[0]; c(use("jewel", x, y - 10, .45))
    x, y = spots[1]; c(crown_shape(x, y + 2, 30, 18, "tint ink thin"))
    x, y = spots[2]; c(pagoda(c, x, y + 6, 18, 2, finial=True, door=False))
    x, y = spots[3]; c(f'<path class="tint ink thin" d="M{x - 12} {y + 4}C{x - 16} {y - 8} {x + 8} {y - 8} {x + 4} {y - 14}C{x} {y - 20} {x - 10} {y - 18} {x - 8} {y - 24}"/><circle cx="{x - 8}" cy="{y - 25}" r="3" class="tint ink thin"/>')
    x, y = spots[4]; c(flame(c, x, y + 4, 26, 14))
    x, y = spots[5]; c(crescent(x, y - 8, 12, "light ink thin"))
    x, y = spots[6]; c(f'<path class="light ink thin" d="M{x - 16} {y - 6}C{x - 6} {y - 16} {x + 6} {y - 16} {x + 16} {y - 6}C{x + 6} {y + 4} {x - 6} {y + 4} {x - 16} {y - 6}Z"/><circle cx="{x}" cy="{y - 6}" r="4.6" class="tint ink thin"/><circle cx="{x}" cy="{y - 6}" r="1.6" class="fill-ink"/>')
    c(sparkle(40, 220, 5), sparkle(340, 224, 5), sparkle(190, 200, 4))
    c(sea(c, top=318, rows=3))
    c(crown(c, S, "Venus"))
    return c


def n21():
    c = Plate("water", 134, "5 of Cups, engraved: three cups knocked over and spilled on the bank, two still standing behind, the bridge over the river leading on to the hall, under the seal of Mars between the scorpion's tails",
              glow=(190, 190, 200))
    emblems(c, "cup")
    c(hills(c, 214, [(40, 16), (300, 22)]))
    c(longhouse(c, 86, 208, 70, 30))
    c('')
    c(sea(c, top=228, bottom=272, rows=3))
    c('<path class="wash ink heavy" d="M210 272C214 236 238 222 262 222C286 222 310 236 314 272H298C294 248 280 238 262 238C244 238 230 248 226 272Z"/><path class="ink hair" d="M212 252H312M216 240L226 248M236 228V238M262 222V238M288 228V238M308 240L298 248"/>')
    c(ground(c, 272))
    for x, y, r in [(54, 300, 96), (112, 318, 84), (166, 304, 100)]:
        c(f'<path class="tint" d="M{x + 18} {y + 4}C{x + 40} {y + 14} {x + 60} {y + 12} {x + 74} {y + 20}C{x + 50} {y + 22} {x + 30} {y + 18} {x + 16} {y + 10}Z" opacity=".75"/>', use("cup", x, y, .78, r))
    c(use("cup", 300, 300, .8), use("cup", 346, 312, .8))
    c(crown(c, S, "Mars"))
    return c


def n22():
    c = Plate("water", 135, "6 of Cups, engraved: six cups brimming with flowers set out before the turf house in the sun, smoke rising from its roof, under the seal of the Sun between the scorpion's tails",
              glow=(190, 160, 220))
    emblems(c, "cup")
    c(sun_rays(c, 300, 150, 30, 120, 150, 330, 15))
    c('<circle cx="300" cy="150" r="26" class="light ink thin"/>')
    c(longhouse(c, 150, 272, 200, 96, turf=True, smoke=True))
    c(ground(c, 270))
    for k, (x, y) in enumerate([(56, 300), (104, 312), (152, 318), (208, 318), (256, 312), (304, 300)]):
        c(use("cup", x, y, .74))
        for j in range(3):
            fx, fy = x - 8 + j * 8, y - 32 - (j % 2) * 6
            c(f'<circle cx="{fx}" cy="{fy}" r="4.4" class="light ink thin"/><circle cx="{fx}" cy="{fy}" r="1.8" class="tint"/>')
    c(crown(c, S, "Sun"))
    return c


def n23():
    c = Plate("water", 136, "7 of Cups, engraved: seven cups floating on clouds, each holding a vision, the serpent, the ring Draupnir, a dragon, a hall, a wreath, an apple and a veil, under the seal of Venus between the scorpion's tails",
              glow=(190, 200, 230))
    emblems(c, "cup")
    spots = [(76, 176), (152, 160), (228, 160), (304, 176), (112, 282), (190, 270), (268, 282)]
    for x, y in spots:
        c(cloud(c, x, y + 30, 78, 16, "light ink thin", False), use("cup", x, y + 6, .78))
    x, y = spots[0]; c(f'<path class="tint ink thin" d="M{x - 12} {y - 22}C{x - 16} {y - 34} {x + 8} {y - 34} {x + 4} {y - 40}C{x} {y - 46} {x - 10} {y - 44} {x - 8} {y - 50}"/><circle cx="{x - 8}" cy="{y - 51}" r="3" class="tint ink thin"/>')
    x, y = spots[1]; c(f'<circle cx="{x}" cy="{y - 34}" r="11" class="ink heavy"/><circle cx="{x}" cy="{y - 34}" r="11" fill="none" stroke="{c.p["T"]}" stroke-width="3"/><circle cx="{x}" cy="{y - 34}" r="6" class="ink hair"/>')
    x, y = spots[2]; c(dragon_head(x - 2, y - 30, .42, cls="tint ink thin"))
    x, y = spots[3]; c(longhouse(c, x, y - 22, 40, 22))
    x, y = spots[4]; c(wreath(c, x, y - 34, 10, 12))
    x, y = spots[5]; c(f'<circle cx="{x}" cy="{y - 30}" r="9" class="tint ink thin"/><path class="ink thin" d="M{x} {y - 39}l1 -5"/><path class="wash ink hair" d="M{x + 1} {y - 41}c4 -4 9 -3 10 0c-4 3 -8 3 -10 0Z"/>')
    x, y = spots[6]; c(f'<path class="wash ink thin" d="M{x - 14} {y - 20}C{x - 16} {y - 36} {x - 8} {y - 46} {x} {y - 48}C{x + 8} {y - 46} {x + 16} {y - 36} {x + 14} {y - 20}C{x + 6} {y - 24} {x - 6} {y - 24} {x - 14} {y - 20}Z"/><path class="ink hair" d="M{x - 6} {y - 22}C{x - 6} {y - 32} {x - 4} {y - 40} {x} {y - 46}M{x + 6} {y - 22}C{x + 6} {y - 32} {x + 4} {y - 40} {x} {y - 46}"/>')
    c(sparkle(40, 236, 5), sparkle(340, 240, 5))
    c(crown(c, S, "Venus"))
    return c


# ---------------------------------------------------------------- the voids
def v067():
    c = Plate("void", 167, "Andhakasura, engraved white on black: the blind dark held up high on the trident, the drops that fall from it trying to become more of him, the river running beneath",
              glow=(190, 130, 200), sky=304)
    c(stars(c, 14, y1=120, avoid=lambda x, y: math.hypot(x - 190, y - 130) < 80))
    blot = [pol(190, 128, 50 + 12 * math.sin(a * 3) + 8 * math.cos(a * 5), math.degrees(a)) for a in [k * math.pi / 9 for k in range(18)]]
    c(f'<path class="plate ink heavy" d="{smooth(blot, True)}"/>', f'<path fill="url(#hx)" d="{smooth(blot, True)}" opacity=".7"/>')
    c(trident(190, 116, 190))
    for k, (x, y) in enumerate([(160, 196), (220, 202), (176, 236), (206, 250), (150, 268), (236, 276), (122, 290), (262, 292), (190, 288)]):
        r = 3 + (k % 3)
        c(f'<path class="tint ink hair" d="M{x} {y - r * 2}C{x + r} {y - r} {x + r} {y + r * .6} {x} {y + r}C{x - r} {y + r * .6} {x - r} {y - r} {x} {y - r * 2}Z"/>')
    c('<path class="ink hair" d="M110 304C120 296 134 296 144 304M236 304C246 296 260 296 270 304"/>')
    c(river_beneath(c))
    return c


def v070():
    c = Plate("void", 170, "Jalandhara, engraved white on black: the whirlpool where the ocean bore him, the discus that ended him spinning above it, and the sprigs of the tulsi his wife became, the river running beneath",
              glow=(190, 120, 210), sky=304)
    c(stars(c, 10, y1=90, avoid=lambda x, y: math.hypot(x - 190, y - 100) < 54))
    c(discus(c, 190, 100, 30))
    c(waves(c, 176, amp=7, length=36, hatch=False))
    spiral = []
    for k in range(80):
        t = k / 79; a = t * 4.4 * math.pi; r = 110 * (1 - t) + 4
        spiral.append((190 + r * math.cos(a), 244 + .34 * r * math.sin(a)))
    c(f'<path class="ink thin" d="{smooth(spiral[::2])}"/>', f'<path class="ink hair" d="{smooth([(x, y + 6) for x, y in spiral[6::2]])}"/>')
    c('<ellipse cx="190" cy="244" rx="8" ry="3" class="plate ink thin"/>')
    leafdef(c)
    for x0, side in [(40, 1), (340, -1)]:
        c(f'<path class="ink thin" d="M{x0} 304C{x0} 270 {x0 + side * 4} 240 {x0 + side * 2} 210"/>')
        for k in range(6):
            y = 290 - k * 14
            c(use("leaf", x0 + side * 1, y, .5, 50 * side), use("leaf", x0, y - 6, .5, -50 * side))
    c(river_beneath(c))
    return c


def v072():
    c = Plate("void", 172, "Maricha, engraved white on black: the golden deer with silver spots leaping through the forest, the arrow already loosed after it, the river running beneath",
              glow=(220, 180, 220), sky=304)
    c(stars(c, 10, y1=110))
    for x, h in [(40, 200), (80, 160), (330, 190), (360, 150)]:
        c(f'<path class="wash ink thin" d="M{x - 4} 304V{304 - h * .4}H{x + 4}V304Z"/><path class="wash ink thin" d="M{x} {304 - h}C{x - 30} {304 - h * .7} {x - 34} {304 - h * .44} {x} {304 - h * .4}C{x + 34} {304 - h * .44} {x + 30} {304 - h * .7} {x} {304 - h}Z"/><path class="ink hair" d="M{x} {304 - h * .9}V{304 - h * .45}M{x - 14} {304 - h * .6}L{x} {304 - h * .5}L{x + 14} {304 - h * .6}"/>')
    c(deer(c, 196, 226, 1.15))
    c('<path class="ink thin" d="M10 268L96 252"/><path class="light ink thin" d="M96 252L84 246L88 253L86 260Z"/><path class="tint ink hair" d="M10 268L0 262L4 269L-2 274ZM18 266L8 260L12 267L6 272Z"/>',
      '<path class="ink hair" d="M50 266L30 272M70 260L54 266"/>')
    c(ground(c, 300, hatch=False))
    c(river_beneath(c))
    return c


CARDS = {"b21": b21, "b22": b22, "b23": b23, "n21": n21, "n22": n22, "n23": n23, "v067": v067, "v070": v070, "v072": v072}
