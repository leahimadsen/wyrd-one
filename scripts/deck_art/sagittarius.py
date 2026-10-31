"""Sagittarius: the 8, 9 and 10 of Double Vajras and of Wands (Mercury, the Moon and Saturn), and the
voids at stations LXXVI (Hayagriva-Asura), LXXIX (Vrishaparvan) and LXXXI (Kalanemi)."""
import math
from lib import *

S, RUNE2 = "Sagittarius", ("Tiwaz", "Berkano")


def speed(x, y, a, n=3, length=40, gap=7):
    """Lines streaming behind something flying toward angle a."""
    dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
    px, py = -dy, dx
    return "".join(f'<path class="ink hair" d="M{f(x - dx * 26 + px * (k - (n - 1) / 2) * gap)} {f(y - dy * 26 + py * (k - (n - 1) / 2) * gap)}l{f(-dx * length * (1 - abs(k - (n - 1) / 2) * .3))} {f(-dy * length * (1 - abs(k - (n - 1) / 2) * .3))}"/>' for k in range(n))


def b24():
    c = Plate("fire", 141, "8 of Double Vajras, engraved: eight double vajras flying swift across the open sky above the valley, under the seal of Mercury beneath the drawn bow",
              glow=(190, 190, 230))
    emblems(c, "vv")
    c(hills(c, 300, [(40, 50), (120, 24), (270, 30), (350, 56)]))
    c(sea(c, top=318, rows=2, x0=100, x1=300))
    a = -24
    for k, (x, y) in enumerate([(70, 214), (140, 186), (210, 158), (280, 130), (110, 270), (180, 242), (250, 214), (320, 186)]):
        c(speed(x, y, a, 3, 48), use("vv", x, y, .44, 20 + k * 7))
    c(crown(c, S, "Mercury"))
    return c


def b25():
    c = Plate("fire", 142, "9 of Double Vajras, engraved: eight double vajras standing guard in a ring about the ninth, the moon rising behind them, under the seal of the Moon beneath the drawn bow",
              glow=(190, 300, 160))
    emblems(c, "vv")
    c('<circle cx="190" cy="300" r="44" class="light ink thin"/><circle cx="190" cy="300" r="40" class="ink hair"/>')
    c(hills(c, 300, [(40, 20), (330, 24)], shade=False))
    c(use("vvh", 190, 210, .66))
    for x, y in ring_of(8, 190, 210, 86):
        c(use("vv", x, y, .4))
    c('<circle cx="190" cy="210" r="86" class="ink hair" stroke-dasharray="3 5"/>')
    c(crown(c, S, "Moon"))
    return c


def b26():
    c = Plate("fire", 143, "10 of Double Vajras, engraved: ten double vajras heaped up into a heavy cairn over smouldering embers, under the seal of Saturn beneath the drawn bow",
              glow=(190, 180, 220))
    emblems(c, "vv")
    c(ground(c, 330))
    for row, (y, n, x0) in enumerate([(330, 9, 62), (312, 8, 76), (296, 6, 104)]):
        for k in range(n):
            x = x0 + k * 32 + c.rng.uniform(-3, 3)
            c(f'<ellipse cx="{f(x)}" cy="{y}" rx="17" ry="10" class="wash ink thin"/><path class="hatchfill" d="M{f(x + 4)} {y - 9}A17 10 0 0 1 {f(x + 4)} {y + 9}A12 8 0 0 0 {f(x + 4)} {y - 9}Z" opacity=".8"/>')
    for x in (80, 126, 174, 222, 270, 312):
        c(flame(c, x, 346, 16, 12))
    for k, (x, y) in enumerate([(110, 268), (163, 268), (216, 268), (269, 268), (136, 222), (190, 222), (244, 222), (163, 176), (217, 176), (190, 132)]):
        c(use("vv", x, y, .56, k * 11))
    c(crown(c, S, "Saturn"))
    return c


def n24():
    c = Plate("fire", 144, "8 of Wands, engraved: eight runestaves flying together across the valley, the river below, under the seal of Mercury beneath the drawn bow",
              glow=(190, 190, 230))
    emblems(c, "stave", runes=RUNE2)
    c(hills(c, 300, [(40, 60), (120, 28), (270, 34), (350, 64)]))
    c(sea(c, top=318, rows=2, x0=90, x1=310))
    for k in range(8):
        x, y = 140 + k * 11 + (k % 2) * 18, 140 + k * 20 - (k % 2) * 6
        c(use("stave", x, y, .42, 62), speed(x - 30, y + 18, -28, 1, 40, 8))
    c(crown(c, S, "Mercury"))
    return c


def n25():
    c = Plate("fire", 145, "9 of Wands, engraved: eight runestaves standing as a palisade at moonrise, the ninth planted before them on guard, under the seal of the Moon beneath the drawn bow",
              glow=(290, 220, 160))
    emblems(c, "stave", runes=RUNE2)
    c('<circle cx="292" cy="214" r="34" class="light ink thin"/><circle cx="292" cy="214" r="30" class="ink hair"/>')
    c(hills(c, 250, [(80, 14), (300, 8)], shade=False))
    c(ground(c, 290))
    for k in range(8):
        x = 52 + k * 39
        c(use("stave", x, 214, .6))
    c('<path class="ink thin" d="M28 190H360M28 250H360"/>')
    c(use("stave", 190, 258, .8), '<path class="ink thin" d="M178 352C186 348 194 348 202 352"/>')
    c(crown(c, S, "Moon"))
    return c


def n26():
    c = Plate("fire", 146, "10 of Wands, engraved: ten runestaves lashed into one heavy bundle and dragged on a sledge through the snow, under the seal of Saturn beneath the drawn bow",
              glow=(190, 180, 220))
    emblems(c, "stave", runes=RUNE2)
    c(hills(c, 250, [(60, 30), (300, 20)], cls="light ink thin"))
    c(ground(c, 300, cls="light ink thin"))
    c('<path class="ink hair" d="M0 330C80 322 160 320 240 316M0 340C80 334 160 332 240 328"/>')
    c('<g transform="rotate(-10 190 250)">' + "".join(use("stave", 190 + (k % 2) * 6, 218 + k * 6.6, .7, 90) for k in range(10))
      + rope("M126 210V290M250 210V290", c.p, 6, 3.6, ".7 2.4", fill=c.p["T"]) + '</g>')
    c('<path class="wash ink heavy" d="M60 300H290C310 300 322 290 324 276C326 266 336 264 338 272C340 290 320 312 292 312H60Z"/>',
      '<path class="ink thin" d="M80 300V288M140 300V284M200 300V280M260 300V276"/><path class="ink thin" d="M60 304L20 316"/>')
    c(crown(c, S, "Saturn"))
    return c


# ---------------------------------------------------------------- the voids
def v076():
    c = Plate("void", 176, "Hayagriva-Asura, engraved white on black: the great horned fish rising out of the flood with the stolen books of the Veda, the horse-headed thief's bridle sinking into the deep, the river running beneath",
              glow=(190, 130, 220), sky=304)
    c(stars(c, 10, y1=90))
    c(waves(c, 150, amp=8, length=40, hatch=False), '<rect x="0" y="162" width="380" height="142" fill="url(#hx)" opacity=".45"/>')
    c(fish(c, 196, 186, 2.2, -16, cls="tint ink thin", fin="wash ink thin"))
    c('<path class="light ink thin" d="M282 132C288 114 298 102 310 94C304 110 298 122 294 136Z"/><path class="ink hair" d="M288 128C292 116 298 108 304 102"/>')
    c(palm_books(206, 126, .9, -12), palm_books(260, 104, .7, 10))
    c('<path class="ink thin" d="M88 270C100 262 118 262 128 270C118 280 100 280 88 270Z"/><path class="ink thin" d="M108 262V248M108 278V292"/>',
      '<path class="light ink thin" d="M84 264H92V276H84ZM124 264H132V276H124Z"/>',
      '<path class="ink hair" d="M128 270C150 262 170 266 190 258C206 252 222 256 236 250M88 270C70 276 52 274 40 282"/>')
    for x, y, r in [(150, 240, 2.4), (160, 220, 1.6), (100, 236, 2)]:
        c(f'<circle cx="{x}" cy="{y}" r="{r}" class="ink hair"/>')
    c(river_beneath(c))
    return c


def v079():
    c = Plate("void", 179, "Vrishaparvan, engraved white on black: the well in the grove where his daughter's quarrel threw a friend, the garments strewn by the bathing pool where it began, the river running beneath",
              glow=(190, 180, 220), sky=304)
    c(stars(c, 10, y1=100))
    c(tree(c, 70, 300, 150, 60), tree(c, 320, 296, 130, 54))
    c('<ellipse cx="250" cy="282" rx="80" ry="16" class="wash ink thin"/><ellipse cx="250" cy="282" rx="64" ry="10" class="ink hair"/>')
    c('<path class="wash ink heavy" d="M96 296V246H170V296Z"/><ellipse cx="133" cy="246" rx="37" ry="9" class="plate ink heavy"/><path class="ink hair" d="M96 262H170M96 278H170M114 246V262M152 246V262M132 262V278M104 278V296M160 278V296"/>',
      '<path class="ink thin" d="M104 244V206M162 244V206M100 206H166"/><path class="light ink thin" d="M128 206V224H138V206"/>')
    c('<path class="tint ink thin" d="M160 246C170 252 178 264 174 280C172 286 166 284 166 278C168 266 162 256 154 250Z"/>',
      '<path class="tint ink thin" d="M200 292C214 284 236 288 246 296C232 300 214 300 200 292Z"/><path class="light ink thin" d="M262 300C276 290 300 292 312 300C298 306 276 306 262 300Z"/>',
      '<path class="ink hair" d="M206 292C218 290 232 292 240 296M268 300C280 296 296 296 306 300"/>')
    c(river_beneath(c))
    return c


def v081():
    c = Plate("void", 181, "Kalanemi, engraved white on black: the false hermitage he built beside the lake, the crocodile waiting in its water, and the mountain of healing herbs carried glowing through the sky beyond, the river running beneath",
              glow=(290, 100, 160), sky=304)
    c(stars(c, 10, y1=110, avoid=lambda x, y: math.hypot(x - 290, y - 100) < 70))
    c(sun_rays(c, 290, 100, 36, 70, 0, 350, 20, 4))
    c('<path class="light ink heavy" d="M246 120L270 78L284 90L300 66L320 98L334 120Z"/><path class="ink hair" d="M262 110C270 104 282 104 290 110M296 100C304 94 314 96 318 104"/>',
      '<path class="ink thin" d="M248 122C270 130 310 130 334 122"/>')
    for x, y in [(268, 104), (284, 96), (304, 90), (312, 108)]:
        c(sparkle(x, y, 4, "tint ink hair"))
    c('<path class="wash ink heavy" d="M44 250L88 210L132 250Z"/><path class="ink hair" d="M58 246L88 216L118 246M70 246L88 228"/><path class="wash ink heavy" d="M54 250V290H122V250Z"/><path class="plate ink thin" d="M80 290V266H96V290Z"/>',
      flame(c, 140, 290, 22, 12))
    c(ground(c, 290, hatch=False))
    c('<ellipse cx="250" cy="282" rx="110" ry="18" class="wash ink thin"/><ellipse cx="250" cy="282" rx="94" ry="12" class="ink hair"/>')
    c(crocodile(c, 254, 284, .82))
    c(river_beneath(c))
    return c


CARDS = {"b24": b24, "b25": b25, "b26": b26, "n24": n24, "n25": n25, "n26": n26, "v076": v076, "v079": v079, "v081": v081}
