"""Capricorn: the 2, 3 and 4 of Jewels and of Shields (Jupiter, Mars and the Sun), and the voids at
stations LXXXV (Bali-Raja), LXXXVIII (Bana-Asura) and XC (Narakasura)."""
import math
from lib import *

S = "Capricorn"


def b27():
    c = Plate("earth", 151, "2 of Jewels, engraved: two jewels on lotus stands kept in balance by the endless knot between them, the lake and the hills behind, under the seal of Jupiter between the goat's horns",
              glow=(190, 190, 220))
    emblems(c, "jewel", "lotus")
    c(hills(c, 262, [(60, 30), (180, 16), (320, 34)]))
    c(sea(c, top=262, rows=6))
    c(rope("M104 214C130 260 160 270 190 230C220 190 250 200 276 214", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c(endless_knot(c, 190, 222, .9))
    for x, y in [(104, 208), (276, 208)]:
        c(f'<path class="ink thin" d="M{x} 300V{y + 30}"/>', use("lotus", x, y + 30, 1.2), use("jewel", x, y, 1.05))
    c(crown(c, S, "Jupiter"))
    return c


def b28():
    c = Plate("earth", 152, "3 of Jewels, engraved: a temple gate going up inside its scaffold, one jewel set in the lintel and two in the capitals, the plumb line hanging true, under the seal of Mars between the goat's horns",
              glow=(190, 190, 220))
    emblems(c, "jewel")
    c(ground(c, 316))
    c('<path class="ink thin" d="M70 316V130M310 316V130M60 160H320M60 240H320M70 160L150 240M310 160L230 240"/>')
    c('<path class="wash ink heavy" d="M110 316V180H148V316ZM232 316V180H270V316Z"/><path class="hatchfill" d="M136 180H148V316H136ZM258 180H270V316H258Z"/>',
      '<path class="ink hair" d="M110 214H148M110 250H148M110 286H148M232 214H270M232 250H270M232 286H270"/>',
      '<path class="wash ink heavy" d="M100 180V166H158V180ZM222 180V166H280V180Z"/>',
      '<path class="wash ink heavy" d="M96 166V140C120 124 160 118 190 118C220 118 260 124 284 140V166Z"/><path class="ink thin" d="M104 154C130 140 160 134 190 134C220 134 250 140 276 154"/>')
    c(use("jewel", 190, 140, .62), use("jewel", 129, 196, .5), use("jewel", 251, 196, .5))
    c('<path class="ink hair" d="M300 160V262"/><path class="tint ink thin" d="M300 262L294 272L300 284L306 272Z"/>')
    c(hammer(166, 316, 70, .8))
    c(crown(c, S, "Mars"))
    return c


def b29():
    c = Plate("earth", 153, "4 of Jewels, engraved: the walled mandala seen from above, a jewel held fast at each of its four corners, the star of Mars exalted over it, under the seal of the Sun between the goat's horns",
              glow=(190, 220, 200))
    emblems(c, "jewel", "lotus")
    c('<circle cx="190" cy="226" r="118" class="wash ink thin"/>', '<circle cx="190" cy="226" r="112" class="ink hair" stroke-dasharray="5 4"/>')
    c('<path class="light ink heavy" d="M110 146H270V306H110Z"/><path class="ink thin" d="M122 158H258V294H122Z"/>',
      '<path class="wash ink heavy" d="M172 146V132H208V146ZM172 306V320H208V306ZM110 208H96V244H110ZM270 208H284V244H270Z"/>',
      '<circle cx="190" cy="226" r="54" class="tint ink thin"/><circle cx="190" cy="226" r="44" class="light ink thin"/>',
      '<path class="ink hair" d="M122 158L162 198M258 158L218 198M122 294L162 254M258 294L218 254"/>')
    c(use("lotus", 190, 236, 1.2))
    for x, y in [(110, 146), (270, 146), (110, 306), (270, 306)]:
        c(f'<circle cx="{x}" cy="{y}" r="17" class="wash ink heavy"/>', use("jewel", x, y + 2, .58))
    c(star_mark(c, "Mars", 330, 120, 15))
    c(crown(c, S, "Sun"))
    return c


def n27():
    c = Plate("earth", 154, "2 of Shields, engraved: two shields kept moving in a loop of cord like the endless eight, over a rolling sea where two ships ride, under the seal of Jupiter between the goat's horns",
              glow=(190, 190, 220))
    emblems(c, "shield")
    c(waves(c, 262, amp=10, length=50), waves(c, 300, amp=8, length=44, hatch=False))
    c(longship(c, 80, 270, .36, True), longship(c, 300, 262, .3, True))
    c(lemniscate(c, 190, 200, 160, 54, "ink heavy"))
    c(use("shield", 142, 200, 1.2), use("shield", 238, 200, 1.2))
    c(crown(c, S, "Jupiter"))
    return c


def n28():
    c = Plate("earth", 155, "3 of Shields, engraved: three shields set into the carved doorway of a stave church, one above the arch and one on each post, under the seal of Mars between the goat's horns",
              glow=(190, 200, 220))
    emblems(c, "shield")
    c('<path class="tint ink heavy" d="M100 186L190 118L280 186Z"/><path class="tint ink heavy" d="M130 150L190 110L250 150Z"/>',
      '<path class="ink hair" d="M120 176L190 126L260 176M144 146L190 118L236 146"/>')
    c(dragon_head(116, 182, .42, cls="wash ink thin"), dragon_head(264, 182, .42, flip=True, cls="wash ink thin"))
    c('<path class="wash ink heavy" d="M110 330V186H270V330Z"/><path class="ink hair" d="' + "".join(f"M{x} 190V330" for x in range(118, 270, 10)) + '"/>')
    c('<path class="plate ink heavy" d="M156 330V250C156 228 172 214 190 214C208 214 224 228 224 250V330Z"/>',
      '<path class="light ink thin" d="M140 330V250C140 218 162 200 190 200C218 200 240 218 240 250V330H224V250C224 228 208 214 190 214C172 214 156 228 156 250V330Z"/>')
    knot = "".join(f"M{140 if side < 0 else 224} {y}c6 6 10 6 16 0M{140 if side < 0 else 224} {y + 6}c6 -6 10 -6 16 0" for side in (-1, 1) for y in range(266, 326, 12))
    c(f'<path class="ink hair" d="{knot}"/>')
    c(use("shield", 190, 182, .8), use("shield", 148, 252, .55), use("shield", 232, 252, .55))
    c(ground(c, 330, wob=3))
    c(crown(c, S, "Mars"))
    return c


def n29():
    c = Plate("earth", 156, "4 of Shields, engraved: four shields fixed fast to the shut gate of the steading, the tower on the crag behind struck by lightning for the Tower exalted, under the seal of the Sun between the goat's horns",
              glow=(300, 160, 200))
    emblems(c, "shield")
    c('<path class="wash ink heavy" d="M240 260C250 230 262 216 278 214H330C346 220 356 240 362 260Z"/><path class="hatchfill" d="M330 214C346 220 356 240 362 260H340C336 240 334 226 330 214Z"/>')
    c(tower(c, 304, 216, 40, 100))
    c(hills(c, 262, [(60, 16)], shade=False))
    c(ground(c, 300))
    c('<path class="wash ink heavy" d="M40 318V190H64V318ZM226 318V190H250V318Z"/><path class="hatchfill" d="M56 190H64V318H56ZM242 190H250V318H242Z"/><circle cx="52" cy="186" r="8" class="tint ink thin"/><circle cx="238" cy="186" r="8" class="tint ink thin"/>')
    c('<path class="wash ink heavy" d="M64 212H226V302H64Z"/><path class="ink thin" d="M64 230H226M64 284H226M64 212L226 302"/>',
      '<path class="ink hair" d="' + "".join(f"M{x} 212V302" for x in range(80, 226, 16)) + '"/>')
    c(use("shield", 52, 236, .72), use("shield", 238, 236, .72), use("shield", 110, 257, .82), use("shield", 180, 257, .82))
    c(crown(c, S, "Sun"))
    return c


# ---------------------------------------------------------------- the voids
def v085():
    c = Plate("void", 185, "Bali-Raja, engraved white on black: the three strides that took back the worlds, one on the earth, one among the stars, the third set gently on the generous king, with the dwarf's parasol and the water pot of the promise, the river running beneath",
              glow=(190, 160, 230), sky=304)
    c(stars(c, 20, y1=200, avoid=lambda x, y: math.hypot(x - 270, y - 96) < 40))
    c(footprint(270, 96, 1.2, 20), footprint(110, 268, 1.2, -10))
    c(crown_shape(190, 214, 52, 30, "tint ink thin"), footprint(190, 176, .9, 0))
    c(ground(c, 290, hatch=False))
    c(parasol(318, 296, .9), water_pot(60, 296, .9))
    c(river_beneath(c))
    return c


def v088():
    c = Plate("void", 188, "Bana-Asura, engraved white on black: the wheel of his thousand arms, the discus cutting through them until only four were left, the river running beneath",
              glow=(190, 170, 230), sky=304)
    c(stars(c, 10, y1=110, avoid=lambda x, y: math.hypot(x - 190, y - 170) < 130))
    cx, cy = 190, 170
    for k in range(24):
        a = k * 15
        cut = 30 < a < 200 and k not in (3, 10)
        r1 = 70 if cut else 118
        p0 = pol(cx, cy, 30, a - 4); p1 = pol(cx, cy, r1, a - 2); p2 = pol(cx, cy, r1, a + 2); p3 = pol(cx, cy, 30, a + 4)
        c(f'<path class="wash ink thin" d="M{f(p0[0])} {f(p0[1])}L{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}L{f(p3[0])} {f(p3[1])}Z"/>')
        if not cut:
            hx, hy = pol(cx, cy, r1 + 6, a)
            c(f'<circle cx="{f(hx)}" cy="{f(hy)}" r="6" class="tint ink thin"/>')
        else:
            hx, hy = pol(cx, cy, 70, a)
            c(f'<path class="ink thin" d="M{f(pol(cx, cy, 70, a - 3)[0])} {f(pol(cx, cy, 70, a - 3)[1])}L{f(pol(cx, cy, 70, a + 3)[0])} {f(pol(cx, cy, 70, a + 3)[1])}"/>')
    c(f'<circle cx="{cx}" cy="{cy}" r="30" class="plate ink heavy"/><circle cx="{cx}" cy="{cy}" r="22" class="ink hair"/>')
    c('<path class="ink hair" stroke-dasharray="4 4" d="M300 270C290 220 280 180 270 150"/>')
    c(discus(c, 284, 236, 22))
    for x, y in [(240, 280), (262, 292), (300, 286), (220, 296)]:
        c(f'<circle cx="{x}" cy="{y}" r="4" class="tint ink hair"/>')
    c(river_beneath(c))
    return c


def v090():
    c = Plate("void", 190, "Narakasura, engraved white on black: the broken walls of his fortress on the hill, the earrings he stole from the mother of the gods shining free above it, and the row of lamps lit for his ending, the river running beneath",
              glow=(190, 120, 220), sky=304)
    c(stars(c, 14, y1=130, avoid=lambda x, y: abs(x - 190) < 60 and y < 160))
    for x in (160, 220):
        c(f'<circle cx="{x}" cy="104" r="16" class="ink heavy"/><circle cx="{x}" cy="104" r="16" fill="none" stroke="#b583b1" stroke-width="3"/><path class="light ink thin" d="M{x} 120L{x - 6} 132L{x} 146L{x + 6} 132Z"/>',
          sparkle(x, 82, 5))
    c(hills(c, 258, [(190, 40)], cls="wash ink thin"))
    c('<path class="wash ink heavy" d="M110 228V188H126V196H140V188H156V200L170 196V226ZM210 224V196H224V188H240V196H254V188H270V228Z"/><path class="ink hair" d="M110 204H170M210 204H270M120 216H160M220 216H260"/>',
      '<path class="ink thin" d="M170 196L176 210L172 226M210 196L204 212L208 224"/>')
    c(ground(c, 278, hatch=False))
    for k in range(9):
        c(diya(42 + k * 37, 296, .72))
    c(river_beneath(c))
    return c


CARDS = {"b27": b27, "b28": b28, "b29": b29, "n27": n27, "n28": n28, "n29": n29, "v085": v085, "v088": v088, "v090": v090}
