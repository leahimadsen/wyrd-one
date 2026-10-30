"""Libra: the 2, 3 and 4 of Vajras and of Swords (the Moon, Saturn and Jupiter), and the voids at
stations LVIII (Tarakasura), LXI (Madhu) and LXIII (Kaitabha)."""
import math
from lib import *

S = "Libra"


def b18():
    c = Plate("air", 121, "2 of Vajras, engraved: two vajras crossed and held still over the moonlit lake, their reflection lying in the water, under the seal of the Moon within the balance",
              glow=(190, 190, 200))
    emblems(c, "vaj")
    c(crescent(312, 132, 18, "light ink thin"))
    c(mountain(c, -20, 150, (60, 200), 262), mountain(c, 230, 400, (330, 196), 262))
    c(sea(c, top=262, rows=7))
    c(use("vaj", 190, 196, 1.35, -30), use("vaj", 190, 196, 1.35, 30))
    c(rope("M176 188C184 198 196 198 204 188M176 204C184 194 196 194 204 204", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c('<g opacity=".55" transform="translate(0 600) scale(1 -1)">' + use("vaj", 190, 286, 1, -30) + use("vaj", 190, 286, 1, 30) + '</g>')
    c('<path class="ink hair" stroke-dasharray="10 4" d="M130 300H250M120 318H260M140 336H240"/>')
    c(crown(c, S, "Moon"))
    return c


def b19():
    c = Plate("air", 122, "3 of Vajras, engraved: three vajras driven through the rain-cloud, rain falling on a lotus that has closed below, under the seal of Saturn within the balance",
              glow=(190, 220, 200))
    emblems(c, "vaj", "lotus")
    c(rain(c, 40, 340, 190, 300, 60, -4, 14))
    c(cloud(c, 190, 196, 240, 60, "wash ink thin"), cloud(c, 120, 186, 110, 30, "light ink thin", False), cloud(c, 270, 184, 110, 30, "light ink thin", False))
    c(use("vaj", 190, 176, 1.15), use("vaj", 134, 182, 1.05, -24), use("vaj", 246, 182, 1.05, 24))
    c(sea(c, top=292, rows=5))
    c(pad(130, 312, 26, 6), pad(250, 316, 26, 6))
    c(rope("M190 340C190 326 188 312 190 296", c.p, 5, 3, ".6 2.2"), bud(190, 300, 1.1, 0, "tint ink thin"), ripples(190, 340, 36, 2))
    c(crown(c, S, "Saturn"))
    return c


def b20():
    c = Plate("air", 123, "4 of Vajras, engraved: four vajras laid to rest in a cave niche on the mountain, a butter lamp burning before them, the star of Saturn exalted outside, under the seal of Jupiter within the balance",
              glow=(190, 220, 200))
    emblems(c, "vaj")
    c('<path class="wash ink heavy" d="M-10 360V170C30 150 70 130 110 124C150 116 230 116 270 124C310 130 350 150 390 170V360Z"/>',
      '<path class="ink hair" d="M30 170L20 220M60 150L46 200M330 160L344 210M350 180L364 240M30 270L20 320M350 280L362 330"/>')
    c('<path class="plate ink heavy" d="M96 330V214C96 170 140 146 190 146C240 146 284 170 284 214V330Z"/>',
      '<path class="ink thin" d="M108 330V216C108 180 146 158 190 158C234 158 272 180 272 216V330"/>')
    c('<path class="light ink heavy" d="M104 300H276V314H104Z"/><path class="hatchfill" d="M104 308H276V314H104Z"/>')
    c(use("vaj", 150, 240, .9), use("vaj", 190, 232, .95), use("vaj", 230, 240, .9))
    c(use("vaj", 190, 292, .9, 90))
    c(flame(c, 190, 336, 20, 10), '<path class="tint ink thin" d="M176 338H204L200 346H180Z"/>')
    c(star_mark(c, "Saturn", 330, 120, 15))
    c(crown(c, S, "Jupiter"))
    return c


def n18():
    c = Plate("air", 124, "2 of Swords, engraved: two swords crossed and bound with cord above the still fjord, the crescent moon over the cliffs, under the seal of the Moon within the balance",
              glow=(190, 190, 200))
    emblems(c, "sword")
    c(crescent(80, 132, 18, "light ink thin"))
    c(sea(c, top=268, rows=6))
    c('<path class="wash ink heavy" d="M-10 360V150C20 156 50 190 70 230C84 250 100 262 118 268V360Z"/><path class="hatchfill" d="M70 230C84 250 100 262 118 268V360H90C88 310 80 260 70 230Z"/>',
      '<path class="wash ink heavy" d="M390 360V140C360 148 330 184 310 226C296 248 280 262 262 268V360Z"/><path class="hatchfill" d="M390 140C360 148 330 184 310 226C320 200 350 170 390 160Z"/>')
    c(use("sword", 190, 210, 1.15, -38), use("sword", 190, 210, 1.15, 38))
    c(rope("M174 198C184 210 196 210 206 198M174 222C184 210 196 210 206 222", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c(crown(c, S, "Moon"))
    return c


def n19():
    c = Plate("air", 125, "3 of Swords, engraved: a knotwork heart pierced by three swords, rain falling behind it out of a low sky, under the seal of Saturn within the balance",
              glow=(190, 220, 200))
    emblems(c, "sword")
    c(cloud(c, 190, 132, 330, 30, "wash ink thin"))
    c(rain(c, 10, 370, 138, 350, 90, -6, 16))
    c(knot_heart(c, 190, 232, 1.2))
    c(use("sword", 190, 236, 1.2, 180), use("sword", 128, 230, 1.05, 180 - 28), use("sword", 252, 230, 1.05, 180 + 28))
    c(crown(c, S, "Saturn"))
    return c


def n20():
    c = Plate("air", 126, "4 of Swords, engraved: three swords hung above a stone tomb and a fourth laid on its lid, the world-serpent circling them for the World exalted, under the seal of Jupiter within the balance",
              glow=(190, 220, 200))
    emblems(c, "sword")
    c(serpent_ring(c, 190, 230, 116, 12))
    c(use("sword", 150, 180, .86, 180), use("sword", 190, 172, .9, 180), use("sword", 230, 180, .86, 180))
    c('<path class="wash ink heavy" d="M100 300V266L114 254H266L280 266V300Z"/><path class="hatchfill" d="M250 254H266L280 266V300H250Z"/>',
      '<path class="light ink thin" d="M96 266H284V274H96Z"/><path class="ink hair" d="M110 284H270M140 274V300M240 274V300"/>',
      '<path class="wash ink heavy" d="M92 300H288V312H92Z"/>')
    c(use("sword", 190, 248, .8, 90))
    c(crown(c, S, "Jupiter"))
    return c


# ---------------------------------------------------------------- the voids
def v058():
    c = Plate("void", 158, "Tarakasura, engraved white on black: the dark star pierced by the spear of light that only the war-god could carry, a peacock's feather drifting down, the river running beneath",
              glow=(190, 190, 230), sky=304)
    c(stars(c, 22, y1=290, avoid=lambda x, y: math.hypot(x - 190, y - 190) < 70 or abs((x - 330) * 1.3 + (y - 40)) < 26))
    pts = []
    for k in range(16):
        rr = 64 if k % 2 == 0 else 26
        pts.append(pol(190, 190, rr, k * 22.5 - 90))
    c('<path class="wash ink heavy" d="M' + "L".join(f"{f(a)} {f(b)}" for a, b in pts) + 'Z"/>', '<circle cx="190" cy="190" r="18" class="plate ink thin"/>')
    c('<path class="ink hair" d="M190 154V172M190 208V226M154 190H172M208 190H226"/>')
    c(vel(176, 176, 230, -140))
    c(feather(84, 286, .9, -24))
    c(river_beneath(c))
    return c


def v061():
    c = Plate("void", 161, "Madhu, engraved white on black: the honeycomb he was born of, dripping into the black ocean of the first night, the stolen books of the Veda sinking in the waves, the river running beneath",
              glow=(120, 140, 220), sky=304)
    c(stars(c, 12, y1=150, avoid=lambda x, y: x < 200 and y < 170))
    c(rope("M-10 70C40 60 100 66 150 58C170 54 186 46 200 40M110 64C120 50 132 44 146 42", c.p, 9, 6, ".8 3", fill=c.p["L"]))
    c('<path class="wash ink thin" d="M36 72C30 110 36 150 60 168C76 180 104 178 118 164C136 146 140 106 132 68Z"/>')
    c(honeycomb(48, 90, 1.0, 4, 5))
    for x, y in [(70, 186), (96, 200), (122, 178), (84, 226)]:
        c(f'<path class="tint ink thin" d="M{x} {y - 8}C{x + 5} {y - 2} {x + 6} {y + 4} {x} {y + 6}C{x - 6} {y + 4} {x - 5} {y - 2} {x} {y - 8}Z"/>')
    c(waves(c, 240, amp=9, length=44, hatch=False), '<rect x="0" y="252" width="380" height="52" fill="url(#hx)" opacity=".45"/>')
    c(ripples(84, 248, 40, 2))
    c(palm_books(270, 226, 1.2, -14), palm_books(310, 262, .9, 18))
    c(river_beneath(c))
    return c


def v063():
    c = Plate("void", 163, "Kaitabha, engraved white on black: the one dry island in all the flooded world, where he was ended, the discus spinning over it, the river running beneath",
              glow=(190, 130, 200), sky=304)
    c(stars(c, 12, y1=110, avoid=lambda x, y: math.hypot(x - 190, y - 120) < 60))
    c(sun_rays(c, 190, 120, 46, 80, 0, 350, 15, 3))
    c(discus(c, 190, 120, 34))
    c(waves(c, 230, amp=8, length=40, hatch=False), waves(c, 262, amp=8, length=48, hatch=False))
    c('<path class="light ink heavy" d="M110 262C120 236 150 222 190 222C230 222 260 236 270 262Z"/>',
      '<path class="ink hair" d="M140 252L150 240L166 246M200 236L214 248L230 244M176 256L186 246"/>',
      '<path fill="url(#hd)" d="M230 228C252 236 264 248 270 262H244C242 250 238 238 230 228Z" opacity=".8"/>')
    c(river_beneath(c))
    return c


CARDS = {"b18": b18, "b19": b19, "b20": b20, "n18": n18, "n19": n19, "n20": n20, "v058": v058, "v061": v061, "v063": v063}
