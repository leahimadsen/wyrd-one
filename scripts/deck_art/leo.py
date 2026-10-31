"""Leo: the 5, 6 and 7 of Double Vajras and of Wands (Saturn, Jupiter and Mars), and the voids at
stations XL (Hiranyakashipu), XLIII (Mahishasura) and XLV (Sumbha)."""
import math
from lib import *

S, RUNE2 = "Leo", ("Hagalaz", "Nauthiz")


def b12():
    c = Plate("fire", 101, "5 of Double Vajras, engraved: five double vajras clashing in the air above the fire, sparks struck between them and smoke rising, under the seal of Saturn within the lion's mane",
              glow=(190, 200, 220))
    emblems(c, "vv")
    c(flames(c, 360, n=11, hmin=40, hmax=96))
    c(smoke(c, 70, 250, 80, 3), smoke(c, 300, 246, 90, 3))
    for x, y, s, r in [(112, 176, .78, 12), (268, 172, .78, -18), (190, 222, .9, 30), (120, 266, .7, -24), (262, 268, .72, 22)]:
        c(use("vv", x, y, s, r))
    c(sparkle(150, 200, 8), sparkle(230, 196, 8), sparkle(160, 246, 6), sparkle(222, 250, 6), sparkle(190, 160, 6))
    c('<path class="ink hair" d="M140 196l-8 -6M144 206l-10 2M236 192l8 -6M240 202l10 0M164 240l-8 4M218 244l8 4"/>')
    c(crown(c, S, "Saturn"))
    return c


def b13():
    c = Plate("fire", 102, "6 of Double Vajras, engraved: the banner of victory raised on its pole, six double vajras borne about it, the sun's rays behind, under the seal of Jupiter within the lion's mane",
              glow=(190, 190, 230))
    emblems(c, "vv")
    c(sun_rays(c, 190, 200, 60, 200, 180, 360, 12))
    c(hills(c, 300, [(60, 18), (190, 10), (320, 20)]))
    c('<path class="ink heavy" d="M190 340V118"/><path class="tint ink thin" d="M184 120H196L190 104Z"/><circle cx="190" cy="124" r="5" class="light ink thin"/>')
    c('<path class="light ink heavy" d="M160 134H220V150H160Z"/><path class="ink hair" d="M160 142H220"/>')
    for k, (y0, y1, cls) in enumerate([(150, 186, "tint"), (186, 220, "wash"), (220, 252, "tint")]):
        w = 30 + k * 4
        scal = "".join(f"Q{f(190 - w + (j + .5) * 2 * w / 6)} {f(y1 + 8)} {f(190 - w + (j + 1) * 2 * w / 6)} {f(y1)}" for j in range(6))
        c(f'<path class="{cls} ink thin" d="M{190 - w} {y0}H{190 + w}V{y1}{"".join(reversed([]))}{scal.replace("Q", "Q")}Z" transform="translate(0 0)"/>' if False else
          f'<path class="{cls} ink thin" d="M{190 - w} {y0}H{190 + w}V{y1}" />')
        c(f'<path class="{cls} ink thin" d="M{190 - w} {y0}H{190 + w}V{y1}' + "".join(f"Q{f(190 + w - (j + .5) * 2 * w / 6)} {f(y1 + 8)} {f(190 + w - (j + 1) * 2 * w / 6)} {f(y1)}" for j in range(6)) + 'Z"/>')
        c(f'<path class="ink hair" d="M{190 - w + 8} {y0 + 4}V{y1 - 2}M{190 - w / 2} {y0 + 4}V{y1}M{190 + w / 2} {y0 + 4}V{y1}M{190 + w - 8} {y0 + 4}V{y1 - 2}"/>')
    c('<path fill="url(#hd)" d="M206 150H220V186H226V220H230V252H212V150Z" opacity=".8"/>')
    c(rope("M220 138C240 130 252 142 270 134C282 130 290 136 300 130M220 146C238 144 248 154 264 150C276 148 284 154 292 152", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    for x, y in [(92, 166), (70, 232), (100, 298), (288, 166), (310, 232), (280, 298)]:
        c(use("vv", x, y, .5))
    c(crown(c, S, "Jupiter"))
    return c


def b14():
    c = Plate("fire", 103, "7 of Double Vajras, engraved: one double vajra holding the summit, six more rising against it out of the fire below, under the seal of Mars within the lion's mane",
              glow=(190, 170, 200))
    emblems(c, "vv")
    c('<path class="wash ink heavy" d="M60 360L140 210C150 194 162 186 172 186H208C218 186 230 194 240 210L320 360Z"/>',
      '<path class="hatchfill" d="M208 186C218 186 230 194 240 210L320 360H256C246 300 226 240 208 186Z"/>',
      '<path class="ink hair" d="M150 236L130 270M166 226L150 290M228 236L242 262M118 300L100 330"/>')
    c(use("vvh", 190, 150, .72))
    for x, y, r in [(40, 236, 40), (66, 306, 28), (110, 350, 14), (270, 350, -14), (314, 306, -28), (340, 236, -40)]:
        c(flame(c, x, y + 34, 30, 18), use("vv", x, y, .5, r))
    c(crown(c, S, "Mars"))
    return c


def n12():
    c = Plate("fire", 104, "5 of Wands, engraved: five runestaves crossed in a melee over the trampled field, dust rising, under the seal of Saturn within the lion's mane",
              glow=(190, 200, 220))
    emblems(c, "stave", runes=RUNE2)
    c(hills(c, 280, [(70, 22), (300, 26)]))
    c(ground(c, 300))
    c('<path class="ink hair" d="M40 306c10 -8 20 -8 30 0M120 314c8 -6 16 -6 24 0M250 312c10 -8 20 -8 30 0M310 304c8 -6 16 -6 24 0"/>')
    for x, y, r in [(150, 236, -34), (232, 230, 30), (190, 226, -6), (120, 250, 18), (264, 252, -18)]:
        c(use("stave", x, y, .82, r))
    c(sparkle(176, 166, 6), sparkle(208, 174, 6), sparkle(160, 214, 4), sparkle(222, 212, 4))
    c(crown(c, S, "Saturn"))
    return c


def n13():
    c = Plate("fire", 105, "6 of Wands, engraved: the victor's pole crowned with a wreath and a carved dragon's head, five staves raised behind it, under the seal of Jupiter within the lion's mane",
              glow=(190, 190, 230))
    emblems(c, "stave", runes=RUNE2)
    c(sun_rays(c, 190, 250, 60, 210, 186, 354, 14))
    c(hills(c, 290, [(50, 14), (330, 18)]))
    for x, r in [(80, -16), (124, -8), (256, 8), (300, 16), (168, -3)]:
        c(use("stave", x, 260, .72, r))
    c('<path class="wash ink heavy" d="M184 340V150H196V340Z"/><path class="hatchfill" d="M191 150H196V340H191Z"/><path class="ink thin" d="M184 300H196M184 306H196M184 200H196M184 206H196"/>')
    c(rune("Hagalaz", 190, 252, 22, 2, cls="ink"), rune("Nauthiz", 190, 278, 18, 2, cls="ink"))
    c(dragon_head(190, 112, .9, cls="tint ink thin"))
    c(wreath(c, 190, 176, 20))
    c(ground(c, 316))
    c(crown(c, S, "Jupiter"))
    return c


def n14():
    c = Plate("fire", 106, "7 of Wands, engraved: one runestave held upright on the crag, six more thrust up against it from the slope below, under the seal of Mars within the lion's mane",
              glow=(240, 170, 200))
    emblems(c, "stave", runes=RUNE2)
    c('<path class="wash ink heavy" d="M150 360C170 300 188 250 200 214L214 200H272L290 216C306 260 330 310 360 360Z"/>',
      '<path class="hatchfill" d="M272 200L290 216C306 260 330 310 360 360H316C300 300 286 248 272 200Z"/>',
      '<path class="ink hair" d="M214 222L204 250M232 214L224 240M196 262L180 300M260 236L266 270"/>')
    c(use("stave", 244, 172, .62))
    c('<path class="ink thin" d="M230 204C236 200 252 200 258 204"/>')
    for x, y, r in [(36, 296, 40), (70, 312, 34), (106, 330, 28), (48, 244, 48), (90, 262, 42), (132, 290, 34)]:
        c(use("stave", x, y, .56, r))
    c(ground(c, 340, hatch=False))
    c(crown(c, S, "Mars"))
    return c


# ---------------------------------------------------------------- the voids
def v040():
    c = Plate("void", 140, "Hiranyakashipu, engraved white on black: the threshold at twilight, neither in nor out, neither day nor night, the lion's claws bursting from the pillar beside it, the river running beneath",
              glow=(190, 250, 200), sky=304)
    c(stars(c, 8, y1=130, avoid=lambda x, y: 120 < x < 260))
    c(sun_rays(c, 190, 262, 36, 120, 190, 350, 12, 3))
    c('<path class="light ink thin" d="M154 262A36 36 0 0 1 226 262Z"/>')
    c('<path class="wash ink heavy" d="M110 304V130H270V304H246V154H134V304Z"/><path class="hatchfill" d="M246 154H270V304H246Z"/>',
      '<path class="tint ink thin" d="M100 116H280V132H100Z"/><path class="ink hair" d="M110 124H270M134 154H246"/>',
      '<path class="ink thin" d="M134 262H246"/><path class="light ink heavy" d="M120 304V288H260V304Z"/><path class="ink hair" d="M120 296H260"/>')
    c('<path class="wash ink heavy" d="M300 304V136H340V304Z"/><path class="wash ink thin" d="M294 128H346V136H294ZM294 304H346V296H294Z"/>',
      '<path class="plate ink thin" d="M320 146L306 180L322 206L304 236L320 264L312 292L320 300L332 292L338 264L332 236L344 206L334 180Z"/>')
    c('<g transform="rotate(-62 320 230)">' + claw(c, 320, 170, 70, -4, 4, 22, "tint ink thin", 34) + '</g>')
    c(river_beneath(c))
    return c


def v043():
    c = Plate("void", 143, "Mahishasura, engraved white on black: the great buffalo's head with its sweeping horns brought down on the battlefield, the Goddess's trident driven into the earth before it, the river running beneath",
              glow=(190, 150, 220), sky=304)
    c(stars(c, 12, y1=120))
    c(hills(c, 300, [(40, 30), (130, 16), (260, 22), (350, 34)], cls="wash ink thin"))
    c(buffalo_face(c, 176, 214, 1.05))
    c(trident(290, 140, 160, 0))
    c('<path class="ink thin" d="M270 300C278 296 302 296 310 300"/>')
    c(river_beneath(c))
    return c


def v045():
    c = Plate("void", 145, "Sumbha, engraved white on black: his crown falling out of the sky where he fought with no ground beneath him, the Goddess's spear of light that ended it, the river running beneath",
              glow=(240, 110, 230), sky=304)
    c(stars(c, 22, y1=280, avoid=lambda x, y: abs((y - 40) - (x - 290) * -1.6) < 30 or math.hypot(x - 150, y - 210) < 50))
    c('<path class="light ink thin" d="M300 30L170 236L176 240Z"/><path fill="none" stroke="#b583b1" stroke-width="1.6" d="M304 34L178 240"/>',
      '<path class="light ink thin" d="M176 228L168 250L188 240Z"/>')
    c(sun_rays(c, 300, 30, 10, 40, 0, 350, 30, 4))
    c('<g transform="rotate(-28 150 214)">' + crown_shape(150, 230, 70, 42, "tint ink thin") + '</g>')
    c('<path class="ink hair" d="M116 170C110 150 116 134 108 116M140 166C136 146 142 130 136 112M166 172C164 152 170 136 166 120"/>')
    for x, y in [(110, 260), (196, 266), (140, 286), (88, 230)]:
        c(f'<circle cx="{x}" cy="{y}" r="2.4" class="light ink hair"/>')
    c(river_beneath(c))
    return c


CARDS = {"b12": b12, "b13": b13, "b14": b14, "n12": n12, "n13": n13, "n14": n14, "v040": v040, "v043": v043, "v045": v045}
