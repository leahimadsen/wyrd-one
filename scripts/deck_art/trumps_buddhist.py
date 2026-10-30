"""The Buddhist deck's twelve zodiac trumps, Aries to Pisces, each under the seal of its sign's ruler
within the sign's device. As early Buddhist art did, they show the Buddha only by what he left: his
seat, his footprints, his tree, his wheel."""
import math
from lib import *

RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
FAM = lambda s: ELEMENT[s % 4]


def T(s, seed, label, **kw):
    return Plate(FAM(s), seed, label, **kw)


def pipal(c):
    p = c.p
    c.d("pipal", f'<g id="pipal" stroke="{p["K"]}" stroke-linejoin="round"><path fill="{p["W"]}" stroke-width="1.1" d="M0 0C-10 -2 -14 -12 -10 -20C-6 -26 0 -24 0 -30C0 -24 6 -26 10 -20C14 -12 10 -2 0 0Z"/>'
        f'<path fill="none" stroke-width="1" d="M0 -30L1 -38"/><path fill="none" stroke-width=".5" d="M0 -2V-28M0 -10L-6 -16M0 -10L6 -16M0 -18L-5 -22M0 -18L5 -22"/></g>')


def bodhi(c, x, y, h=170, spread=110, n=46):
    """The Bodhi tree: a great crown of foliage, its heart-shaped, drip-tipped leaves hanging from the rim."""
    pipal(c)
    out = [tree(c, x, y, h, spread)]
    for k in range(n):
        cx, cy, r = c.canopy[k % len(c.canopy)]
        a = c.rng.uniform(20, 160) if k % 3 else c.rng.uniform(-170, -10)
        lx, ly = pol(cx, cy, r * c.rng.uniform(.82, 1.02), a)
        if ly < 100: continue
        out.append(use("pipal", lx, ly, round(c.rng.uniform(.5, .7), 2), (a - 90) if a > 0 else (a + 90)))
    return "".join(out)


def seat(c, x, y, w=120, cls="wash ink heavy"):
    """The empty seat: a stone slab with its cushion, a lotus cut on its face."""
    return (f'<path class="{cls}" d="M{x - w / 2} {y}V{y - 30}H{x + w / 2}V{y}Z"/><path class="hatchfill" d="M{x + w / 2 - 18} {y - 30}H{x + w / 2}V{y}H{x + w / 2 - 18}Z"/>'
            f'<path class="tint ink thin" d="M{x - w / 2 + 4} {y - 30}C{x - w / 2 + 6} {y - 42} {x + w / 2 - 6} {y - 42} {x + w / 2 - 4} {y - 30}Z"/>'
            f'<path class="ink hair" d="M{x - w / 2} {y - 22}H{x + w / 2}M{x - w / 2} {y - 8}H{x + w / 2}"/>'
            f'<path class="ink hair" d="M{x - 12} {y - 10}C{x - 10} {y - 18} {x - 4} {y - 20} {x} {y - 21}C{x + 4} {y - 20} {x + 10} {y - 18} {x + 12} {y - 10}M{x - 6} {y - 10}C{x - 5} {y - 15} {x - 2} {y - 17} {x} {y - 18}C{x + 2} {y - 17} {x + 5} {y - 15} {x + 6} {y - 10}"/>')


def foot_wheel(x, y, s=1, r=0):
    """A footprint of the Buddha, a wheel on its sole."""
    return footprint(x, y, s, r, "light ink thin") + f'<g transform="translate({f(x)} {f(y)}) rotate({r}) scale({s})"><circle cx="0" cy="-2" r="7" class="tint ink hair"/><path class="ink hair" d="M-7 -2H7M0 -9V5M-5 -7L5 3M5 -7L-5 3"/></g>'


def tb00():
    s = 0
    c = T(s, 300, "The King, engraved: the wheel-turning king's empty throne, the wheel of his reign blazing above it, under the seal of Mars between the ram's horns",
          glow=(190, 160, 210))
    c(sun_rays(c, 190, 150, 44, 140, 0, 350, 12, 3))
    c(sun_wheel(c, 190, 150, 38))
    c(flames(c, 360, n=11, hmin=24, hmax=54))
    c('<path class="wash ink heavy" d="M92 334H288L296 348H84Z"/><path class="wash ink heavy" d="M104 322H276V334H104Z"/>')
    c('<path class="wash ink heavy" d="M126 270V216C126 202 136 196 150 196H230C244 196 254 202 254 216V270Z"/><path class="hatchfill" d="M232 196C244 198 254 204 254 216V270H236Z"/>',
      '<path class="ink thin" d="M136 266V218C136 210 142 206 150 206H230C238 206 244 210 244 218V266"/>',
      '<path class="tint ink thin" d="M112 270H268C270 278 266 284 258 286H122C114 284 110 278 112 270Z"/><path class="ink hair" d="M118 278H262"/>',
      '<path class="wash ink heavy" d="M120 286H260V300H120Z"/>')
    for x, k in ((134, -1), (246, 1)):
        c(f'<path class="wash ink thin" d="M{x - 10} 300H{x + 10}L{x + 8} 312C{x + 14} 314 {x + 14} 322 {x + 6} 322H{x - 6}C{x - 14} 322 {x - 14} 314 {x - 8} 312Z"/><path class="ink hair" d="M{x - 6} 322V316M{x} 322V316M{x + 6} 322V316"/>',
          f'<path class="light ink thin" d="M{x - 4 * k} 268C{x - 18 * k} 262 {x - 20 * k} 246 {x - 10 * k} 240C{x - 4 * k} 236 {x + 2 * k} 240 {x} 246C{x - 6 * k} 246 {x - 8 * k} 254 {x - 2 * k} 256"/>')
    emblems(c, "jewel")
    c(use("jewel", 140, 186, .5), use("jewel", 240, 186, .5))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb01():
    s = 1
    c = T(s, 301, "The Buddha, engraved: the empty seat beneath the Bodhi tree where he woke, his two footprints set before it, under the seal of Venus between the bull's horns",
          glow=(190, 200, 200))
    c(bodhi(c, 190, 262, 120, 110, 40))
    c(ground(c, 262))
    c(seat(c, 190, 268, 128))
    c(foot_wheel(166, 326, .9, -4), foot_wheel(214, 326, .9, 4))
    c(sparkle(94, 240, 5), sparkle(290, 236, 5))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb02():
    s = 2
    c = T(s, 302, "The Two Paths, engraved: the road forking at the old tree, one way to the palace gate and its banners, the other up into the forest and the mountains, under the seal of Mercury between the twin pillars",
          glow=(190, 180, 220))
    c(mountain(c, 200, 420, (318, 120), 236, snow=True))
    c(hills(c, 236, [(40, 12), (130, 8)]))
    for x, h in [(220, 70), (250, 84), (282, 66), (312, 90), (344, 74), (236, 54), (300, 60)]:
        c(f'<path class="wash ink thin" d="M{x} {246 - h}L{x - 14} {246 - h * .4}H{x - 6}L{x - 18} {246}H{x + 18}L{x + 6} {246 - h * .4}H{x + 14}Z"/><path class="ink hair" d="M{x} {246 - h}V246"/>')
    c('<path class="wash ink heavy" d="M30 246V180H62V164H90V180H122V246Z"/><path class="tint ink thin" d="M56 166L76 140L96 166Z"/><path class="hatchfill" d="M104 180H122V246H104Z"/>',
      '<path class="plate ink thin" d="M64 246V214C64 206 70 202 76 202C82 202 88 206 88 214V246Z"/><path class="ink hair" d="M30 194H122M30 208H62M90 208H122"/>',
      '<path class="ink thin" d="M76 140V120"/><path class="tint ink thin" d="M76 120L98 126L76 132Z"/><path class="ink thin" d="M40 180V160M112 180V160"/><path class="tint ink hair" d="M40 160l12 4l-12 4ZM112 160l12 4l-12 4Z"/>')
    c(ground(c, 246, wob=3))
    c('<path class="light ink thin" d="M150 360C164 330 176 306 186 288C170 276 130 262 96 248L104 246C138 256 176 268 192 282C204 270 236 256 270 242L276 246C246 260 212 278 198 290C206 310 218 334 232 360Z"/>',
      '<path class="ink hair" d="M172 340h10M180 316h8M188 298h6M130 262h8M150 270h7M232 258h8M216 266h7"/>')
    c(tree(c, 190, 300, 120, 52, leaves=True))
    emblems(c, "vaj")
    c(use("vaj", 190, 306, .62, 90))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb03():
    s = 3
    c = T(s, 303, "The Chariot, engraved: Nagasena's chariot taken apart and laid out by the water, its wheels, axle, pole, yoke and box, so that none of them is the chariot, under the seal of the Moon within the crab's claws",
          glow=(190, 180, 210))
    c(crescent(310, 128, 16, "light ink thin"))
    c(hills(c, 232, [(60, 14), (300, 10)], shade=False))
    c(sea(c, top=232, bottom=262, rows=2))
    c(ground(c, 262, wob=3))
    def wheel(x, y, r):
        sp = "".join(f"M{f(pol(x, y, 9, a)[0])} {f(pol(x, y, 9, a)[1])}L{f(pol(x, y, r - 5, a)[0])} {f(pol(x, y, r - 5, a)[1])}" for a in range(0, 360, 30))
        return (rope(f"M{f(x - r)} {f(y)}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0", c.p, 9, 6, ".8 3") + f'<path class="ink thin" d="{sp}"/>'
                f'<circle cx="{x}" cy="{y}" r="10" class="tint ink thin"/><circle cx="{x}" cy="{y}" r="3.4" class="fill-ink"/>')
    c(wheel(74, 222, 44), wheel(306, 222, 44))
    c('<path class="wash ink heavy" d="M136 250V200H244V250Z"/><path class="hatchfill" d="M222 200H244V250H222Z"/><path class="tint ink thin" d="M130 192H250V200H130Z"/>',
      '<path class="ink hair" d="M146 210H234M146 230H234M162 200V250M190 200V250M218 200V250"/>',
      '<path class="light ink thin" d="M136 196C136 172 160 160 190 160C220 160 244 172 244 196"/><path class="ink hair" d="M150 192C152 178 168 170 190 170C212 170 228 178 230 192"/>')
    c(rope("M70 300H310", c.p, 8, 5, ".8 3", fill=c.p["L"]), '<circle cx="70" cy="300" r="5" class="tint ink thin"/><circle cx="310" cy="300" r="5" class="tint ink thin"/>')
    c(rope("M110 330L270 318", c.p, 7, 4.4, ".8 3", fill=c.p["W"]))
    c('<path class="wash ink thin" d="M262 312C272 300 292 300 300 312C292 316 272 316 262 312Z"/><path class="wash ink thin" d="M296 312C306 300 326 300 334 312C326 316 306 316 296 312Z"/>')
    c('<path class="ink hair" stroke-dasharray="3 4" d="M118 222H136M244 222H262M190 250V296M100 300V330M300 300V318"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def lion(c, x, y, s=1, face=0):
    """A lion of the Sarnath capital: a heavy mane of flame-like locks, a long face, the mouth open in the roar.
    face: -1 turned left, 0 to the front, 1 turned right."""
    out = []
    for ring, (r0, r1, cls) in enumerate([(24, 46, "wash ink thin"), (22, 36, "tint ink thin")]):
        for a in range(-210 + ring * 9, 31, 15):
            b0, b1 = pol(x, y, r0 * s, a - 6), pol(x, y, r0 * s, a + 6)
            tip = pol(x, y, r1 * s, a - 9); m1 = pol(x, y, (r0 + r1) / 2 * s, a + 9); m2 = pol(x, y, (r0 + r1) / 2 * s, a - 13)
            out.append(f'<path class="{cls}" d="M{f(b0[0])} {f(b0[1])}Q{f(m2[0])} {f(m2[1])} {f(tip[0])} {f(tip[1])}Q{f(m1[0])} {f(m1[1])} {f(b1[0])} {f(b1[1])}Z"/>')
    fx = x + face * 7 * s
    q = lambda dx, dy: f"{f(fx + dx * s)} {f(y + dy * s)}"
    out.append(f'<path class="wash ink thin" d="M{q(-16, -14)}C{q(-12, -26)} {q(12, -26)} {q(16, -14)}C{q(20, -2)} {q(16, 14)} {q(12, 22)}C{q(8, 30)} {q(-8, 30)} {q(-12, 22)}C{q(-16, 14)} {q(-20, -2)} {q(-16, -14)}Z"/>')
    out.append(f'<path class="ink thin" d="M{q(-12, -10)}C{q(-8, -14)} {q(-4, -14)} {q(-2, -10)}M{q(2, -10)}C{q(4, -14)} {q(8, -14)} {q(12, -10)}"/>'
               f'<path class="ink hair" d="M{q(-2, -10)}C{q(-3, 0)} {q(-4, 6)} {q(-6, 10)}M{q(2, -10)}C{q(3, 0)} {q(4, 6)} {q(6, 10)}M{q(-14, -2)}C{q(-12, 2)} {q(-10, 4)} {q(-8, 4)}M{q(14, -2)}C{q(12, 2)} {q(10, 4)} {q(8, 4)}"/>'
               f'<circle cx="{f(fx - 7 * s)}" cy="{f(y - 8 * s)}" r="{f(1.5 * s)}" class="fill-ink"/><circle cx="{f(fx + 7 * s)}" cy="{f(y - 8 * s)}" r="{f(1.5 * s)}" class="fill-ink"/>'
               f'<path class="mid ink thin" d="M{q(-6, 10)}C{q(-4, 8)} {q(4, 8)} {q(6, 10)}L{q(0, 15)}Z"/>'
               f'<path class="mid ink thin" d="M{q(-9, 18)}C{q(-6, 28)} {q(6, 28)} {q(9, 18)}C{q(4, 20)} {q(-4, 20)} {q(-9, 18)}Z"/>'
               + "".join(f'<circle cx="{f(fx + dx * s)}" cy="{f(y + dy * s)}" r="{f(.9 * s)}" class="fill-ink"/>' for dx, dy in [(-10, 13), (-12, 16), (10, 13), (12, 16)]))
    return "".join(out)


def tb04():
    s = 4
    c = T(s, 304, "The Lion's Roar, engraved: the lions of the Sarnath capital back to back on their column, roaring to the four quarters, the wheel of the teaching on their abacus, under the seal of the Sun within the lion's mane",
          glow=(190, 190, 220))
    for k in range(4):
        r = 120 + k * 22
        c(f'<path class="ink hair" d="M{f(190 - r * .9)} {f(196 - r * .3)}A{r} {r} 0 0 1 {f(190 - r * .5)} {f(196 - r * .86)}M{f(190 + r * .9)} {f(196 - r * .3)}A{r} {r} 0 0 0 {f(190 + r * .5)} {f(196 - r * .86)}" stroke-dasharray="{6 - k} 5"/>')
    c(ground(c, 330, wob=3))
    c('<path class="light ink heavy" d="M176 330V292H204V330Z"/><path class="hatchfill" d="M196 292H204V330H196Z"/>')
    c('<path class="wash ink heavy" d="M150 252C150 272 168 292 190 292C212 292 230 272 230 252Z"/>',
      '<path class="ink hair" d="M160 254C162 268 172 282 182 288M176 254C176 268 182 280 186 290M204 254C204 268 198 280 194 290M220 254C218 268 208 282 198 288"/>',
      '<path class="wash ink heavy" d="M138 228H242V252H138Z"/><path class="hatchfill" d="M226 228H242V252H226Z"/>')
    for x in (156, 190, 224):
        c(f'<circle cx="{x}" cy="240" r="8" class="light ink thin"/><path class="ink hair" d="M{x - 8} 240H{x + 8}M{x} 232V248M{x - 5.6} 234.4L{x + 5.6} 245.6M{x + 5.6} 234.4L{x - 5.6} 245.6"/>')
    c('<path class="wash ink thin" d="M120 228C124 210 132 200 140 196L150 228ZM260 228C256 210 248 200 240 196L230 228Z"/>',
      '')
    for x, k in ((124, -1), (256, 1), (190, 0)):
        lx = x + k * 4
        c(f'<path class="wash ink thin" d="M{lx - 14} 228V200H{lx - 4}V228ZM{lx + 4} 228V200H{lx + 14}V228Z"/><path class="ink hair" d="M{lx - 12} 228v-5M{lx - 9} 228v-5M{lx - 6} 228v-5M{lx + 6} 228v-5M{lx + 9} 228v-5M{lx + 12} 228v-5"/>')
    c(lion_face(c, 126, 180, 1.05), lion_face(c, 254, 180, 1.05), lion_face(c, 190, 166, 1.25))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb05():
    s = 5
    c = T(s, 305, "The Ascetic, engraved: an empty mat of kusha grass under a tree in the forest, the alms bowl and the ringed staff beside it, under the seal of Mercury among the ears of wheat",
          glow=(190, 190, 210))
    c(tree(c, 56, 300, 170, 70), tree(c, 330, 300, 150, 60))
    c(tree(c, 200, 276, 150, 96))
    c(ground(c, 290))
    c('<path class="wash ink thin" d="M130 306L250 300L258 316L122 322Z"/>',
      '<path class="ink hair" d="' + "".join(f"M{126 + k * 8} {321 - k * .4}L{132 + k * 8} {305 - k * .4}" for k in range(16)) + '"/>')
    c('<path class="mid ink heavy" d="M266 330C266 316 278 308 292 308C306 308 318 316 318 330Z"/><path class="ink thin" d="M262 330H322"/><path class="light ink thin" d="M272 316C280 312 304 312 312 316"/>')
    c('<path class="ink heavy" d="M160 330L188 200"/>')
    c('<path class="light ink thin" d="M188 200C180 192 180 178 190 172C200 168 208 176 206 186C204 194 196 200 188 200Z"/><path class="ink thin" d="M190 172V164"/>',
      '<circle cx="180" cy="192" r="4" class="tint ink thin"/><circle cx="204" cy="182" r="4" class="tint ink thin"/><circle cx="182" cy="178" r="3.4" class="tint ink thin"/><circle cx="202" cy="196" r="3.4" class="tint ink thin"/>')
    c(water_pot(240, 332, .7))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb06():
    s = 6
    c = T(s, 306, "Karma, engraved: the cart wheel rolling on after the ox's hoofprints down the long road, as the wheel follows the foot of the ox, under the seal of Venus within the balance",
          glow=(190, 160, 210))
    c(hills(c, 200, [(60, 16), (180, 8), (320, 20)]))
    c(ground(c, 210, wob=2))
    c('<path class="light ink thin" d="M176 210L204 210L330 360H40Z"/>')
    for k in range(9):
        t = k / 8
        y = 218 + (300 - 218) * t
        sc = .2 + t * .32
        c(f'<g transform="translate({f(190 + (k % 2 * 2 - 1) * (6 + 22 * t))} {f(y)}) scale({sc:.2f})"><path class="mid ink thin" d="M-9 0C-12 -10 -10 -22 -3 -24C-1 -14 -1 -6 -2 2ZM9 0C12 -10 10 -22 3 -24C1 -14 1 -6 2 2Z"/></g>')
    c('<path class="ink thin" d="M186 212L120 360M196 212L262 360"/><path class="ink hair" d="M188 212L130 360M194 212L252 360"/>')
    x, y, r = 250, 300, 50
    sp = "".join(f"M{f(pol(x, y, 10, a)[0])} {f(pol(x, y, 10, a)[1])}L{f(pol(x, y, r - 6, a)[0])} {f(pol(x, y, r - 6, a)[1])}" for a in range(8, 368, 30))
    c(rope(f"M{x - r} {y}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0", c.p, 10, 7, ".8 3"), f'<path class="ink thin" d="{sp}"/>',
      f'<circle cx="{x}" cy="{y}" r="12" class="tint ink thin"/><circle cx="{x}" cy="{y}" r="4" class="fill-ink"/>',
      '<path class="ink hair" d="M314 280l22 -4M318 296l26 0M314 312l22 4"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb07():
    s = 7
    c = T(s, 307, "Impermanence, engraved: the Diamond Sutra's last verse, a star at dawn, a bubble on the stream, lightning in a summer cloud, a lamp flickering, dew on the grass, under the seal of Mars between the scorpion's tails",
          glow=(90, 200, 160))
    c(sun_rays(c, 70, 216, 20, 110, 196, 300, 12, 3), '<path class="light ink thin" d="M50 216A20 20 0 0 1 90 216Z"/>')
    c(sparkle(112, 140, 14, "light ink thin"), sparkle(112, 140, 6, "tint ink hair"))
    c(cloud(c, 284, 150, 140, 36, "wash ink thin"))
    c('<path class="tint ink thin" d="M284 154L270 182L282 182L266 214L298 176L286 176L300 154Z"/>')
    c(hills(c, 216, [(200, 10), (330, 14)], shade=False))
    c(sea(c, top=230, bottom=270, rows=2))
    c(ground(c, 216, wob=2, hatch=False))
    c(sea(c, top=234, bottom=272, rows=2))
    for x, y, r in [(180, 252, 9), (204, 256, 5), (152, 258, 4)]:
        c(f'<circle cx="{x}" cy="{y}" r="{r}" class="light ink thin"/><path class="ink hair" d="M{x - r * .5} {y - r * .4}a{r * .5} {r * .5} 0 0 1 {r * .5} {-r * .3}"/>')
    c(ground(c, 290))
    c(diya(250, 318, 1.8), '<path class="ink hair" d="M262 268C266 260 260 254 266 246"/>')
    for x in (60, 78, 96, 114):
        c(f'<path class="ink thin" d="M{x} 340C{x - 2} 320 {x + 6} 308 {x + 12} 300"/><circle cx="{x + 12}" cy="303" r="3" class="light ink hair"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb08():
    s = 8
    c = T(s, 308, "The Middle Way, engraved: Sona's lute, its one true string tuned neither too tight nor too slack, the string drawn too tight snapped and the slack one hanging, under the seal of Jupiter beneath the drawn bow",
          glow=(190, 200, 220))
    c(flames(c, 360, n=11, hmin=18, hmax=40))
    body = "M70 300C90 318 190 322 250 300C262 296 266 286 258 280C220 290 130 292 84 282C72 280 64 290 70 300Z"
    c(f'<path class="wash ink heavy" d="{body}"/>', '<path fill="url(#hd)" d="M84 296C130 306 220 304 254 292C246 302 200 312 150 312C110 312 90 306 84 296Z"/>',
      '<path class="ink hair" d="M96 290C140 298 210 296 246 286"/><circle cx="170" cy="298" r="5" class="mid ink thin"/>')
    c(rope("M252 284C276 250 290 200 286 156C284 132 272 116 256 112", c.p, 11, 7, ".9 3", fill=c.p["L"]), '<path class="tint ink thin" d="M256 112C244 110 236 118 240 128C248 126 254 120 256 112Z"/>')
    pegs = [(287, 170), (288, 190), (286, 210), (282, 230), (276, 250), (268, 268)]
    feet = [(120, 290), (140, 291), (160, 292), (180, 291), (200, 290), (220, 288)]
    for k, ((px, py), (fx, fy)) in enumerate(zip(pegs, feet)):
        c(f'<circle cx="{px + 6}" cy="{py}" r="3" class="tint ink thin"/>')
        if k == 2:
            c(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.6" d="M{px} {py}L{fx} {fy}"/>', f'<path class="ink hair" d="M{px} {py}L{fx} {fy}"/>')
        elif k == 0:
            c(f'<path class="ink thin" d="M{px} {py}L{f(px + (fx - px) * .45)} {f(py + (fy - py) * .45)}c-6 4 -4 12 -12 10M{fx} {fy}L{f(fx + (px - fx) * .3)} {f(fy + (py - fy) * .3)}c4 -6 12 -4 10 -12"/>')
        elif k == 5:
            c(f'<path class="ink thin" d="M{px} {py}C{f((px + fx) / 2)} {f((py + fy) / 2 + 40)} {f(fx + 20)} {f(fy - 4)} {fx} {fy}"/>')
        else:
            c(f'<path class="ink thin" d="M{px} {py}L{fx} {fy}"/>')
    c(sparkle(170, 152, 8))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb09():
    s = 9
    c = T(s, 309, "Mara, engraved: the arrows and spears of his army raining down out of the dark onto the empty seat beneath the Bodhi tree and turning into flowers as they fall, under the seal of Saturn between the goat's horns",
          glow=(110, 250, 190))
    c('<path class="mid" d="M140 100H390V250C350 210 300 170 240 140C200 120 170 108 140 100Z" opacity=".55"/><path fill="url(#hx)" d="M140 100H390V250C350 210 300 170 240 140C200 120 170 108 140 100Z"/>')
    pipal(c)
    c(rope("M-10 132C30 128 70 140 104 162C120 172 130 186 136 200M40 134C50 120 66 112 84 112", c.p, 9, 6, ".8 3"))
    for x, y in [(10, 150), (36, 142), (62, 150), (88, 164), (110, 180), (126, 196), (56, 124), (80, 118), (24, 124)]:
        c(use("pipal", x, y + 26, .8, 180 + c.rng.uniform(-20, 20)))
    c(ground(c, 296))
    c(seat(c, 100, 300, 120))
    for k, (x, y) in enumerate([(330, 140), (290, 150), (350, 190), (300, 196), (250, 180), (320, 236)]):
        c(f'<g transform="translate({x} {y}) rotate(-140)"><path class="ink thin" d="M0 0V46"/><path class="light ink thin" d="M0 -8L-4 2H4Z"/><path class="tint ink hair" d="M0 46l-5 6M0 46l5 6M0 40l-5 6M0 40l5 6"/></g>')
    for k, (x, y, t) in enumerate([(220, 214, .4), (196, 236, .6), (176, 258, .8), (156, 276, 1), (236, 250, .7), (200, 274, .9), (130, 268, 1), (170, 290, 1)]):
        pet = "".join(f'<ellipse cx="{f(x + pol(0, 0, 5 * t, a)[0])}" cy="{f(y + pol(0, 0, 5 * t, a)[1])}" rx="{f(4.4 * t)}" ry="{f(2.6 * t)}" transform="rotate({a} {f(x + pol(0, 0, 5 * t, a)[0])} {f(y + pol(0, 0, 5 * t, a)[1])})" class="tint ink hair"/>' for a in range(0, 360, 72))
        c(pet, f'<circle cx="{x}" cy="{y}" r="{f(2.4 * t)}" class="light ink hair"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb10():
    s = 10
    c = T(s, 310, "The Tara, engraved: her star shining over the lake of tears, and the blue utpala rising from the water where the tear fell, under the seal of Saturn between the water-bearer's urns",
          glow=(190, 150, 210))
    pts = [pol(190, 150, 44 if k % 2 == 0 else 14, k * 22.5 - 90) for k in range(16)]
    c(sun_rays(c, 190, 150, 50, 92, 0, 350, 15, 2))
    c('<path class="light ink heavy" d="M' + "L".join(f"{f(a)} {f(b)}" for a, b in pts) + 'Z"/><circle cx="190" cy="150" r="10" class="tint ink thin"/>')
    c(stars(c, 12, y0=100, y1=230, avoid=lambda x, y: math.hypot(x - 190, y - 150) < 100))
    c('<path class="tint ink thin" d="M190 200C194 208 196 212 196 216C196 220 193 222 190 222C187 222 184 220 184 216C184 212 186 208 190 200Z"/>')
    c(hills(c, 244, [(50, 14), (330, 18)], shade=False))
    c(sea(c, top=244, rows=7))
    c(ripples(190, 300, 60, 3))
    c(rope("M190 300C190 284 186 270 190 254", c.p, 5, 3, ".6 2.2"))
    petal = "M0 2C-5 -4 -6 -18 0 -30C6 -18 5 -4 0 2Z"
    c("".join(f'<path class="{"tint" if abs(a) < 30 else "wash"} ink thin" transform="translate(190 258) rotate({a})" d="{petal}"/>' for a in (-56, 56, -28, 28, 0)))
    c('<path class="wash ink thin" d="M190 300C168 294 150 300 140 312C162 316 180 312 190 300Z"/><path class="wash ink thin" d="M190 296C212 290 230 296 240 308C218 312 200 308 190 296Z"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tb11():
    s = 11
    c = T(s, 311, "Nirvana, engraved: the lamp blown out on the near shore, its last smoke rising, the raft left on the bank, the wide water and the far shore beyond, the star of Venus exalted above, under the seal of Jupiter between the two fishes",
          glow=(190, 220, 180))
    c(star_mark(c, "Venus", 300, 132, 14))
    c('<path class="ink thin" d="M0 214C60 210 120 212 190 210C260 208 320 212 380 210"/><path class="ink hair" d="M0 210C40 204 80 200 120 206C150 196 180 202 210 206C250 198 300 202 380 206"/>')
    c(sea(c, top=214, bottom=300, rows=7))
    c('<path class="wash ink heavy" d="M-20 300C80 290 180 296 260 312C300 320 340 330 400 332V380H-20Z"/><path class="hatchfill" d="M-20 324C80 316 180 322 260 336C300 342 340 350 400 352V380H-20Z" opacity=".7"/>')
    c('<path class="wash ink heavy" d="M210 298L330 290L334 302L214 310Z"/><path class="ink hair" d="M214 304L332 296M236 296V308M262 294V306M288 292V304M312 290V302"/>', rope("M226 296L228 308M318 290L320 302", c.p, 4, 2.4, ".5 2", fill=c.p["T"]))
    c('<path class="tint ink thin" d="M84 330C88 340 120 340 124 330L130 326C118 328 90 328 78 326Z"/><path class="wash ink heavy" d="M64 344H144V352H64Z"/>',
      '<path class="ink hair" d="M118 326C124 312 112 304 120 290C128 278 118 268 126 256"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


CARDS = {f"tb{s:02d}": fn for s, fn in enumerate([tb00, tb01, tb02, tb03, tb04, tb05, tb06, tb07, tb08, tb09, tb10, tb11])}
