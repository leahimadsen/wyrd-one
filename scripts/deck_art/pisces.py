"""Pisces: the 8, 9 and 10 of Lotuses and of Cups (Saturn, Jupiter and Mars), and the voids at
stations CIII (Kamalaksha), CVI (Shankhasura) and CVIII (Ahi-Budhnya)."""
import math
from lib import *

S = "Pisces"


def house(c, x, y, w=70, h=40, cls="wash ink heavy"):
    return (f'<path class="{cls}" d="M{f(x - w / 2)} {f(y)}V{f(y - h)}H{f(x + w / 2)}V{f(y)}Z"/><path class="tint ink heavy" d="M{f(x - w / 2 - 8)} {f(y - h + 2)}L{f(x)} {f(y - h - w * .42)}L{f(x + w / 2 + 8)} {f(y - h + 2)}Z"/>'
            f'<path class="plate ink thin" d="M{f(x - 6)} {f(y)}V{f(y - 18)}H{f(x + 6)}V{f(y)}Z"/><path class="light ink thin" d="M{f(x + w / 4 - 5)} {f(y - 28)}h10v8h-10Z"/>')


def b33():
    c = Plate("water", 171, "8 of Lotuses, engraved: eight lotuses left flowering in the pond, five below and three above, the path leading away from it into the hills under the moon in eclipse, under the seal of Saturn between the two fishes",
              glow=(290, 140, 190))
    emblems(c, "lotus")
    c(eclipse(c, 292, 138, 24))
    c(hills(c, 236, [(250, 50), (330, 70), (380, 40)]))
    c(ground(c, 260))
    c('<path class="light ink thin" d="M200 360C230 320 250 300 270 280C284 266 296 256 306 236L312 238C304 258 294 272 282 286C264 306 246 326 226 360Z"/>',
      '<path class="ink hair" d="M228 340h8M246 318h7M262 298h6M278 280h5"/>')
    c('<ellipse cx="96" cy="300" rx="94" ry="36" class="wash ink thin"/><ellipse cx="96" cy="300" rx="80" ry="26" class="ink hair"/>')
    for k, x in enumerate([40, 68, 96, 124, 152]):
        c(use("lotus", x, 306, .78), pad(x + 4, 316, 14, 3))
    for x in (54, 82, 110):
        c(use("lotus", x, 278, .74))
    c('<path class="ink hair" stroke-dasharray="3 3" d="M138 280H160"/>')
    c(crown(c, S, "Saturn"))
    return c


def b34():
    c = Plate("water", 172, "9 of Lotuses, engraved: nine lotuses set in a full arc upon the altar under the parasol of honour, every wish granted, under the seal of Jupiter between the two fishes",
              glow=(190, 190, 220))
    emblems(c, "lotus")
    c(parasol(190, 196, .9))
    c('<path class="wash ink heavy" d="M60 260H320V276H60Z"/><path class="tint ink thin" d="M64 276H316V316C280 306 250 322 190 312C130 322 100 306 64 316Z"/><path class="ink hair" d="M90 276V308M130 276V312M170 276V310M210 276V310M250 276V312M290 276V308"/>')
    c(ground(c, 330, wob=3))
    for k in range(9):
        a = 180 + k * 22.5
        x, y = pol(190, 256, 116, a)
        c(use("lotus", x, y - 4, .82))
    c(sparkle(190, 216, 6), sparkle(100, 160, 4), sparkle(280, 160, 4))
    c(crown(c, S, "Jupiter"))
    return c


def b35():
    c = Plate("water", 173, "10 of Lotuses, engraved: ten lotuses blooming along a rainbow arched over the home by the water, its roof sweeping up at the eaves, the star of Venus exalted, under the seal of Mars between the two fishes",
              glow=(190, 200, 210))
    emblems(c, "lotus")
    c(rainbow(c, 190, 290, 160, w=8))
    for k in range(10):
        x, y = pol(190, 290, 148, 180 + 9 + k * 18)
        c(use("lotus", x, y + 6, .62))
    c(star_mark(c, "Venus", 190, 182, 15))
    c(ground(c, 290))
    c(hall(c, 190, 308, 70, 26), pagoda_roof(c, 190, 278, 118, 30))
    c(sea(c, top=318, rows=3))
    c(crown(c, S, "Mars"))
    return c


def n33():
    c = Plate("water", 174, "8 of Cups, engraved: eight cups left stacked on the shore, five below and three above, the path climbing away into the hills under the moon in eclipse, under the seal of Saturn between the two fishes",
              glow=(290, 140, 190))
    emblems(c, "cup")
    c(eclipse(c, 292, 138, 24))
    c(hills(c, 236, [(250, 50), (330, 70), (380, 40)]))
    c(sea(c, top=246, x0=0, x1=180, rows=4))
    c(ground(c, 290))
    c('<path class="light ink thin" d="M200 360C230 320 250 300 270 280C284 266 296 256 306 236L312 238C304 258 294 272 282 286C264 306 246 326 226 360Z"/>')
    for x in (40, 72, 104, 136, 168):
        c(use("cup", x, 308, .62))
    for x in (56, 88, 120):
        c(use("cup", x, 268, .62))
    c('<path class="ink thin" d="M24 324H184M40 284H136"/>')
    c(crown(c, S, "Saturn"))
    return c


def n34():
    c = Plate("water", 175, "9 of Cups, engraved: nine cups set out in an arc along the high curved bench, its cloth hanging to the floor, under the seal of Jupiter between the two fishes",
              glow=(190, 190, 220))
    emblems(c, "cup")
    c('<path class="wash ink heavy" d="M50 250C110 200 270 200 330 250V266C270 218 110 218 50 266Z"/>',
      '<path class="tint ink thin" d="M50 266C110 218 270 218 330 266V312C300 300 270 306 250 300C220 292 160 292 130 300C110 306 80 300 50 312Z"/>',
      '<path class="ink hair" d="M90 240V304M130 226V298M170 220V294M210 220V294M250 226V298M290 240V304"/>')
    c(ground(c, 316, wob=3))
    for k in range(9):
        t = k / 8
        x = 64 + t * 252; y = 248 - math.sin(math.pi * t) * 34
        c(use("cup", x, y - 24, .64))
    c(crown(c, S, "Jupiter"))
    return c


def n35():
    c = Plate("water", 176, "10 of Cups, engraved: ten cups shining along a rainbow arched over the farm, its longhouse, field and trees, the Empress's crown of twelve stars for Venus exalted, under the seal of Mars between the two fishes",
              glow=(190, 200, 210))
    emblems(c, "cup")
    c(rainbow(c, 190, 290, 160, w=8))
    for k in range(10):
        x, y = pol(190, 290, 150, 180 + 9 + k * 18)
        c(use("cup", x, y + 14, .5))
    for k in range(12):
        x, y = pol(190, 182, 20, k * 30)
        c(sparkle(x, y, 4.4, "tint ink hair"))
    c(ground(c, 290))
    c(longhouse(c, 190, 308, 150, 64, smoke=True))
    c(apple_tree(c, 60, 300, 90, 40, 4), apple_tree(c, 320, 300, 90, 40, 4))
    c('<path class="ink hair" d="M0 324C80 318 160 320 220 316M0 336C80 330 160 332 240 328M0 348C80 342 160 344 260 340"/>')
    c(crown(c, S, "Mars"))
    return c


# ---------------------------------------------------------------- the voids
def v103():
    c = Plate("void", 203, "Kamalaksha, engraved white on black: the silver city of the three, adrift in the open air between the earth and heaven, the winds streaming past it, the river running beneath",
              glow=(190, 170, 220), sky=304)
    c(stars(c, 18, y1=290, avoid=lambda x, y: 70 < x < 310 and 80 < y < 250))
    for y in (110, 136, 228, 252):
        c(f'<path class="ink hair" d="M20 {y}C80 {y - 8} 140 {y + 6} 200 {y - 2}S320 {y - 8} 370 {y}" stroke-dasharray="20 8"/>')
    for x, w, h in [(116, 30, 60), (152, 36, 90), (190, 42, 112), (228, 36, 90), (264, 30, 60)]:
        c(f'<path class="light ink thin" d="M{x - w / 2} 210V{210 - h}H{x + w / 2}V210Z"/><path fill="url(#sky)" d="M{x - w / 2} 210V{210 - h}H{x + w / 2}V210Z"/>',
          f'<path class="light ink thin" d="M{x - w / 2 - 2} {210 - h}C{x - w / 2} {210 - h - w * .7} {x} {210 - h - w} {x} {210 - h - w * 1.2}C{x} {210 - h - w} {x + w / 2} {210 - h - w * .7} {x + w / 2 + 2} {210 - h}Z"/>'
          f'<path fill="url(#hd)" d="M{x - w / 2 - 2} {210 - h}C{x - w / 2} {210 - h - w * .7} {x} {210 - h - w} {x} {210 - h - w * 1.2}C{x} {210 - h - w} {x + w / 2} {210 - h - w * .7} {x + w / 2 + 2} {210 - h}Z"/>',
          f'<path class="plate ink thin" d="M{x - 4} 210V198C{x - 4} 192 {x + 4} 192 {x + 4} 198V210Z"/><path class="ink hair" d="M{x - w / 2} {210 - h + 12}H{x + w / 2}M{x - w / 2} {210 - h + 20}H{x + w / 2}"/>')
    c('<path class="light ink heavy" d="M96 210H284C276 224 250 236 190 238C130 236 104 224 96 210Z"/><path fill="url(#sky)" d="M96 210H284C276 224 250 236 190 238C130 236 104 224 96 210Z"/><path class="ink hair" d="M120 220C150 228 230 228 260 220"/>')
    c(river_beneath(c))
    return c


def v106():
    c = Plate("void", 206, "Shankhasura, engraved white on black: the great conch he hid in on the floor of the sea, light coming from inside it, the weed swaying round it, the river running beneath",
              glow=(190, 250, 180), sky=304)
    c(waves(c, 96, amp=8, length=40, hatch=False), '<rect x="0" y="106" width="380" height="198" fill="url(#hx)" opacity=".4"/>')
    for x in (40, 70, 300, 336):
        c(f'<path class="ink thin" d="M{x} 300C{x - 10} 270 {x + 10} 250 {x} 220C{x - 10} 196 {x + 8} 180 {x} 160"/><path class="ink hair" d="M{x} 270l-10 -6M{x} 240l10 -6M{x} 210l-10 -6M{x} 184l10 -6"/>')
    c(sun_rays(c, 150, 244, 30, 70, 150, 230, 10, 3))
    c(conch(206, 250, 1.6, -8))
    for x, y, r in [(220, 170, 3), (232, 140, 2.2), (214, 120, 1.6), (240, 196, 2)]:
        c(f'<circle cx="{x}" cy="{y}" r="{r}" class="ink hair"/>')
    c(ground(c, 296, hatch=False))
    c(river_beneath(c))
    return c


def v108():
    c = Plate("void", 208, "Ahi-Budhnya, engraved white on black: the serpent of the deep coiled at the last gate of the wheel, keeping it, the river running beneath",
              glow=(190, 160, 220), sky=304)
    c(stars(c, 14, y1=120, avoid=lambda x, y: 100 < x < 280 and y > 60))
    c('<path class="wash ink heavy" d="M96 300V130H120V300ZM260 300V130H284V300Z"/><path class="hatchfill" d="M112 130H120V300H112ZM276 130H284V300H276Z"/>',
      '<path class="wash ink heavy" d="M80 130C120 110 260 110 300 130V114C260 94 120 94 80 114Z"/><path class="tint ink thin" d="M84 100H296V90H84Z"/><path class="ink hair" d="M100 122C140 110 240 110 280 122"/>',
      '<path class="plate ink thin" d="M120 300V150C150 140 230 140 260 150V300Z"/>')
    c(serpent_coil(c, 214, 290, 1))
    c(river_beneath(c))
    return c


CARDS = {"b33": b33, "b34": b34, "b35": b35, "n33": n33, "n34": n34, "n35": n35, "v103": v103, "v106": v106, "v108": v108}
