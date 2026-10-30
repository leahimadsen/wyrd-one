"""Aquarius: the 5, 6 and 7 of Vajras and of Swords (Venus, Mercury and the Moon), and the voids at
stations XCIV (Maya-Vijnana), XCVII (Vidyunmali) and XCIX (Tarakaksha)."""
import math
from lib import *

S = "Aquarius"


def flags(c, d, n=9, torn=()):
    """Prayer flags hung along a cord drawn through the points d."""
    out = [f'<path class="ink thin" d="{smooth(d)}"/>']
    (x0, y0), (x1, y1) = d[0], d[-1]
    for k in range(n):
        t = (k + .5) / n
        x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t + 18 * math.sin(math.pi * t)
        cls = ["tint", "wash", "light", "mid", "wash"][k % 5]
        if k in torn:
            out.append(f'<path class="{cls} ink thin" d="M{f(x - 6)} {f(y)}H{f(x + 6)}L{f(x + 8)} {f(y + 8)}L{f(x + 2)} {f(y + 6)}L{f(x - 4)} {f(y + 12)}Z"/>')
        else:
            out.append(f'<path class="{cls} ink thin" d="M{f(x - 6)} {f(y)}H{f(x + 6)}L{f(x + 10)} {f(y + 16)}H{f(x - 2)}Z"/><path class="ink hair" d="M{f(x - 2)} {f(y + 4)}h6M{f(x)} {f(y + 9)}h5"/>')
    return "".join(out)


def b30():
    c = Plate("air", 161, "5 of Vajras, engraved: three vajras gathered up and kept, two dropped on the stony ground, the storm still blowing over, under the seal of Venus between the water-bearer's urns",
              glow=(190, 220, 200))
    emblems(c, "vaj")
    c(storm(c, 120, depth=24, cls="light ink thin"))
    c(rain(c, 0, 380, 128, 250, 40, -14, 14))
    c(hills(c, 270, [(80, 30), (300, 20)]))
    c(ground(c, 290))
    c('<path class="ink hair" d="M30 160C80 150 120 156 170 148M210 170C260 160 300 166 360 156M60 200C100 194 140 198 180 192"/>')
    c(use("vaj", 266, 240, 1.05, -8), use("vaj", 290, 242, 1.05, 6), use("vaj", 314, 246, 1.05, 16))
    c(rope("M250 252C280 262 310 262 330 254", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c(use("vaj", 90, 320, .95, 84), use("vaj", 160, 334, .95, 102))
    c('<path class="wash ink thin" d="M40 340l8 -8l10 4l2 6ZM200 318l6 -6l10 2l2 6ZM120 350l8 -6l8 2l2 6Z"/>')
    c(crown(c, S, "Venus"))
    return c


def b31():
    c = Plate("air", 162, "6 of Vajras, engraved: six vajras standing upright on a raft crossing from the rough water toward the calm far shore, under the seal of Mercury between the water-bearer's urns",
              glow=(260, 200, 220))
    emblems(c, "vaj")
    c(hills(c, 226, [(260, 40), (340, 30)]))
    c(sea(c, top=226, rows=6))
    c(chop(c, 300, 0, 120, 30), chop(c, 330, 0, 200, 34))
    c('<path class="wash ink heavy" d="M110 292L270 270L276 284L116 306Z"/><path class="ink hair" d="M114 299L274 277M136 290L140 304M164 286L168 300M192 282L196 296M220 278L224 292M248 274L252 288"/>')
    c(rope("M130 286L132 302M256 270L258 286", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    for k, (x, y) in enumerate([(140, 252), (172, 246), (204, 242), (236, 238), (158, 268), (220, 260)]):
        c(use("vaj", x, y, .7))
    c(ripples(190, 316, 120, 1))
    c(crown(c, S, "Mercury"))
    return c


def b32():
    c = Plate("air", 163, "7 of Vajras, engraved: the windswept pass under torn prayer flags, five vajras blown away across the sky and two left standing in the snow, under the seal of the Moon between the water-bearer's urns",
              glow=(190, 170, 220))
    emblems(c, "vaj")
    c(mountain(c, -40, 190, (60, 140), 300, snow=True), mountain(c, 190, 420, (320, 130), 300, snow=True))
    c(flags(c, [(60, 150), (190, 196), (320, 140)], 11, torn=(2, 5, 8)))
    c(ground(c, 300, cls="light ink thin"))
    for k, (x, y, r) in enumerate([(132, 230, 60), (190, 248, 110), (250, 230, 150), (296, 200, 210), (330, 170, 250)]):
        c(use("vaj", x, y, .58, r), f'<path class="ink hair" d="M{x - 30} {y + 6}l-24 4M{x - 28} {y + 12}l-16 3"/>')
    c(use("vaj", 150, 300, .8), use("vaj", 210, 306, .8))
    c(crown(c, S, "Moon"))
    return c


def n30():
    c = Plate("air", 164, "5 of Swords, engraved: three swords gathered up together on the shore, two cast down on the sand, the storm moving off over the sea, under the seal of Venus between the water-bearer's urns",
              glow=(190, 220, 200))
    emblems(c, "sword")
    c(storm(c, 124, depth=24, cls="light ink thin"))
    c(waves(c, 230, amp=9, length=46), waves(c, 254, amp=7, length=40, hatch=False))
    c('<path class="wash ink heavy" d="M-20 280C80 266 200 268 400 282V380H-20Z"/><path class="hatchfill" d="M-20 300C80 290 200 292 400 304V380H-20Z" opacity=".7"/>')
    c(use("sword", 274, 236, .9, -10), use("sword", 300, 236, .9, 6), use("sword", 326, 240, .9, 20))
    c(rope("M262 268C286 276 314 276 336 268", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c(use("sword", 90, 318, .8, 80), use("sword", 170, 334, .8, 98))
    c('<path class="ink thin" d="M220 150l6 -4l6 4M240 164l5 -3l5 3M206 172l5 -3l5 3"/>')
    c(crown(c, S, "Venus"))
    return c


def n31():
    c = Plate("air", 165, "6 of Swords, engraved: six swords standing upright in a small boat crossing the fjord toward calm water and the far shore, under the seal of Mercury between the water-bearer's urns",
              glow=(260, 200, 220))
    emblems(c, "sword")
    c(hills(c, 236, [(300, 40), (360, 30)]))
    c(sea(c, top=236, rows=6))
    c(chop(c, 316, 110, 240, 30))
    c('<path class="wash ink heavy" d="M-10 360V160C30 170 60 210 80 244C90 256 100 262 110 264V360Z"/><path class="hatchfill" d="M80 244C90 256 100 262 110 264V360H96C94 316 88 270 80 244Z"/>')
    c('<path class="wash ink heavy" d="M130 286C150 300 250 300 274 286C282 280 286 270 290 262C294 258 298 260 296 266C292 284 284 300 262 308C230 316 160 316 136 302C128 298 124 292 130 286Z"/>',
      '<path class="ink hair" d="M136 294C160 304 246 304 270 292"/><path class="hatchfill" d="M140 302C170 312 240 312 268 302C250 312 160 314 140 302Z"/>')
    for k, x in enumerate([156, 178, 200, 222, 244, 190]):
        c(use("sword", x, 246 if k < 5 else 232, .66 if k < 5 else .74, 180))
    c(ripples(210, 316, 160, 1))
    c(crown(c, S, "Mercury"))
    return c


def n32():
    c = Plate("air", 166, "7 of Swords, engraved: two swords left standing by the tent at night, a trail of footprints leading away over the hill where the other five are being carried off, under the seal of the Moon between the water-bearer's urns",
              glow=(190, 150, 230))
    emblems(c, "sword")
    c(stars(c, 10, y0=100, y1=200))
    c(crescent(300, 132, 16, "light ink thin", flip=True))
    c(hills(c, 280, [(300, 60)]))
    c(ground(c, 300, cls="wash ink thin"))
    c('<path class="wash ink heavy" d="M30 300L84 206L138 300Z"/><path class="tint ink thin" d="M84 206L104 300H66Z"/><path class="ink thin" d="M84 206L84 196M76 194L84 206L92 194"/><path class="ink hair" d="M50 290L84 226L118 290"/>')
    c(use("sword", 158, 270, .7, 184), use("sword", 186, 274, .7, 176))
    for k in range(9):
        x = 210 + k * 14; y = 330 - k * 8 - (k % 2) * 4
        c(f'<ellipse cx="{x}" cy="{y}" rx="3" ry="5" transform="rotate(60 {x} {y})" class="ink hair"/>')
    c('<g transform="rotate(30 330 222)">' + "".join(use("sword", 314 + k * 9, 236, .5, 0) for k in range(5)) + '</g>')
    c(crown(c, S, "Moon"))
    return c


# ---------------------------------------------------------------- the voids
def v094():
    c = Plate("void", 194, "Maya-Vijnana, engraved white on black: the architect's lamp throwing a false city onto the dark, a ring of a hundred stars round nothing at all, the river running beneath",
              glow=(190, 290, 200), sky=304)
    for k in range(100):
        x, y = pol(190, 96, 52 + (k % 3) * 4, k * 3.6)
        c(f'<circle cx="{f(x)}" cy="{f(y)}" r="{.9 + (k % 4) * .25}" class="fill-ink"/>')
    c('<path class="tint" d="M180 270L60 140H320L200 270Z" opacity=".22"/><path class="ink hair" d="M180 270L60 140M200 270L320 140" stroke-dasharray="3 4"/>')
    c('<path class="ink hair" stroke-dasharray="4 4" d="M90 200V160H110V146H130V160H150V136L170 120L190 136V160H210V140H230V160H260V150H280V200"/>',
      '<path class="ink hair" stroke-dasharray="2 4" d="M110 200V176H124V200M200 200V174H216V200M250 200V180H262V200"/>')
    c(diya(190, 290, 1.6))
    c('<path class="wash ink heavy" d="M150 300H230V292H150Z"/>')
    c(river_beneath(c))
    return c


def v097():
    c = Plate("void", 197, "Vidyunmali, engraved white on black: the iron city of the three, set on the earth and garlanded with lightning, the river running beneath",
              glow=(190, 180, 220), sky=304)
    c(stars(c, 12, y1=110))
    c(ground(c, 290, hatch=False))
    for x, w, h in [(70, 34, 110), (130, 44, 150), (190, 50, 176), (250, 44, 150), (310, 34, 110)]:
        c(f'<path class="mid ink heavy" d="M{x - w / 2} 290V{290 - h}H{x + w / 2}V290Z"/>',
          f'<path class="ink thin" d="M{x - w / 2 - 4} {290 - h}V{290 - h - 12}H{x - w / 6}V{290 - h - 4}H{x + w / 6}V{290 - h - 12}H{x + w / 2 + 4}V{290 - h}Z"/>',
          '<path class="ink hair" d="' + "".join(f"M{x - w / 2} {y}H{x + w / 2}" for y in range(290 - h + 16, 290, 16)) + '"/>',
          "".join(f'<circle cx="{x - w / 2 + 5}" cy="{y}" r="1.2" class="fill-ink"/><circle cx="{x + w / 2 - 5}" cy="{y}" r="1.2" class="fill-ink"/>' for y in range(290 - h + 8, 290, 16)),
          f'<path class="plate ink thin" d="M{x - 5} 290V276C{x - 5} 270 {x + 5} 270 {x + 5} 276V290Z"/>')
    bolt = "M70 172L94 156L88 150L118 138L112 132L148 118L140 110L190 98L240 110L232 118L268 132L262 138L292 150L286 156L310 172"
    c(f'<path fill="none" stroke="#b583b1" stroke-width="5" stroke-linejoin="round" d="{bolt}"/><path class="ink thin" d="{bolt}"/>')
    c(river_beneath(c))
    return c


def v099():
    c = Plate("void", 199, "Tarakaksha, engraved white on black: the golden city of the three, built on cloud high in the heavens among the stars, the river running beneath",
              glow=(190, 150, 220), sky=304)
    c(stars(c, 26, y1=290, avoid=lambda x, y: 60 < x < 320 and 80 < y < 230))
    c(sun_rays(c, 190, 150, 80, 120, 0, 350, 10, 2))
    for x, w, h in [(110, 30, 70), (150, 38, 100), (190, 44, 126), (230, 38, 100), (270, 30, 70)]:
        c(f'<path class="tint ink thin" d="M{x - w / 2} 200V{200 - h}H{x + w / 2}V200Z"/>',
          f'<path class="tint ink thin" d="M{x - w / 2 - 2} {200 - h}C{x - w / 2} {200 - h - w * .7} {x} {200 - h - w} {x} {200 - h - w * 1.2}C{x} {200 - h - w} {x + w / 2} {200 - h - w * .7} {x + w / 2 + 2} {200 - h}Z"/>',
          f'<path class="plate ink thin" d="M{x - 4} 200V188C{x - 4} 182 {x + 4} 182 {x + 4} 188V200Z"/><path class="ink hair" d="M{x - w / 2} {200 - h + 12}H{x + w / 2}"/>')
    c(cloud(c, 190, 214, 260, 34, "wash ink thin"), cloud(c, 110, 226, 120, 20, "light ink thin", False), cloud(c, 280, 228, 120, 20, "light ink thin", False))
    c(river_beneath(c))
    return c


CARDS = {"b30": b30, "b31": b31, "b32": b32, "n30": n30, "n31": n31, "n32": n32, "v094": v094, "v097": v097, "v099": v099}
