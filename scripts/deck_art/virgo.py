"""Virgo: the 8, 9 and 10 of Jewels and of Shields (the Sun, Venus and Mercury), and the voids at
stations XLIX (Nisumbha), LII (Diti-Mula) and LIV (Danu-Garbha)."""
import math
from lib import *

S = "Virgo"


def b15():
    c = Plate("earth", 111, "8 of Jewels, engraved: jewels being set one by one into the face of a mandala's stone platform, six in place, the mallet and chisel at the seventh, the eighth waiting, under the seal of the Sun among the ears of wheat",
              glow=(190, 180, 220))
    emblems(c, "jewel")
    c(sun_rays(c, 190, 214, 70, 200, 186, 354, 12))
    c('<path class="wash ink heavy" d="M110 214A80 80 0 0 1 270 214Z"/><path class="ink thin" d="M124 214A66 66 0 0 1 256 214M140 214A50 50 0 0 1 240 214"/>',
      '<path class="ink hair" d="' + "".join(f"M{f(pol(190, 214, 50, a)[0])} {f(pol(190, 214, 50, a)[1])}L{f(pol(190, 214, 66, a)[0])} {f(pol(190, 214, 66, a)[1])}" for a in range(190, 360, 20)) + '"/>',
      '<path class="tint ink thin" d="M168 214A22 22 0 0 1 212 214Z"/>')
    c('<path class="wash ink heavy" d="M60 214H320V296H60Z"/><path class="hatchfill" d="M286 214H320V296H286Z"/><path class="wash ink heavy" d="M44 296H336V310H44Z"/>',
      '<path class="ink thin" d="M60 226H320M60 284H320"/>')
    for k in range(8):
        x = 80 + k * 31.4
        c(f'<path class="light ink thin" d="M{f(x - 12)} 236H{f(x + 12)}V274H{f(x - 12)}Z"/>')
        if k < 6: c(use("jewel", x, 257, .62))
    c(ground(c, 310, wob=3))
    x7 = 80 + 6 * 31.4
    c(f'<path class="light ink thin" d="M{f(x7 + 4)} 262L{f(x7 + 30)} 230L{f(x7 + 34)} 234L{f(x7 + 8)} 266Z"/><path class="mid ink thin" d="M{f(x7 + 30)} 230L{f(x7 + 40)} 218L{f(x7 + 46)} 222L{f(x7 + 34)} 234Z"/>')
    c(hammer(x7 + 66, 214, -40, .8))
    c(use("jewel", 312, 336, .7), '<path class="ink thin" d="M298 352C306 348 318 348 326 352"/>')
    c(sparkle(x7, 246, 5))
    c(crown(c, S, "Sun"))
    return c


def b16():
    c = Plate("earth", 112, "9 of Jewels, engraved: the wish-granting tree in a walled garden behind its roofed gate, nine jewels hanging ripe in its boughs, the star of Mercury exalted above, under the seal of Venus among the ears of wheat",
              glow=(190, 190, 220))
    emblems(c, "jewel")
    c(tree(c, 190, 300, 170, 92))
    for x, y in [(124, 168), (160, 132), (212, 124), (252, 160), (140, 214), (240, 206), (190, 172), (104, 222), (276, 222)]:
        c(f'<path class="ink hair" d="M{x} {y - 22}V{y - 14}"/>', use("jewel", x, y, .5))
    c(star_mark(c, "Mercury", 322, 128, 15))
    c('<path class="wash ink heavy" d="M-10 268H390V306H-10Z"/><path class="hatchfill" d="M-10 292H390V306H-10Z" opacity=".7"/>',
      '<path class="ink hair" d="M-10 280H390M20 268V280M60 268V280M100 268V280M140 268V280M240 268V280M280 268V280M320 268V280M360 268V280M40 280V292M80 280V292M120 280V292M260 280V292M300 280V292M340 280V292"/>',
      '<path class="light ink thin" d="M-10 262H390V268H-10Z"/><path class="ink hair" d="' + "".join(f"M{x} 262V268" for x in range(-6, 390, 6)) + '"/>',
      '<path class="wash ink heavy" d="M160 306V266H170V306ZM210 306V266H220V306Z"/><path class="plate ink thin" d="M170 306V270H210V306Z"/><path class="tint ink thin" d="M172 306V272H189V306ZM191 306V272H208V306Z"/>')
    c(pagoda_roof(c, 190, 266, 96, 26))
    c(ground(c, 306))
    for x in (40, 84, 296, 340):
        c(f'<path class="ink thin" d="M{x} 324V306"/><circle cx="{x}" cy="304" r="5" class="tint ink thin"/><path class="wash ink hair" d="M{x} 316c-6 -4 -10 -2 -10 2c4 2 8 2 10 -2ZM{x} 318c6 -4 10 -2 10 2c-4 2 -8 2 -10 -2Z"/>')
    c(crown(c, S, "Venus"))
    return c


def b17():
    c = Plate("earth", 113, "10 of Jewels, engraved: the treasure vase brimming under a fringed canopy, ten jewels heaped in its mouth and spilling to the ground, under the seal of Mercury among the ears of wheat",
              glow=(190, 200, 210))
    emblems(c, "jewel")
    c('<path class="ink heavy" d="M74 318V128M306 318V128"/><circle cx="74" cy="124" r="5" class="tint ink thin"/><circle cx="306" cy="124" r="5" class="tint ink thin"/>')
    val = "".join(f"Q{f(74 + (j + .5) * 232 / 8)} 168 {f(74 + (j + 1) * 232 / 8)} 150" for j in range(8))
    c(f'<path class="tint ink thin" d="M70 128H310V150{"".join(reversed([]))}" />' if False else
      f'<path class="tint ink thin" d="M70 128H310L306 150{"".join(f"Q{f(306 - (j + .5) * 232 / 8)} 168 {f(306 - (j + 1) * 232 / 8)} 150" for j in range(8))}Z"/>',
      '<path class="ink hair" d="M74 138H306"/>')
    for j in range(9):
        x = 74 + j * 232 / 8
        c(f'<path class="ink hair" d="M{f(x)} 150V172"/><path class="wash ink hair" d="M{f(x - 3)} 172H{f(x + 3)}L{f(x + 2)} 182H{f(x - 2)}Z"/>')
    c(ground(c, 312, wob=3))
    c(vase(c, 190, 312, .95))
    for x, y, s in [(190, 196, .62), (168, 206, .54), (212, 206, .54), (150, 302, .5), (230, 304, .5), (124, 320, .52), (256, 322, .52), (100, 338, .5), (282, 340, .5), (190, 340, .5)]:
        c(use("jewel", x, y, s))
    c(sparkle(130, 200, 5), sparkle(250, 200, 5), sparkle(110, 270, 4), sparkle(272, 268, 4))
    c(crown(c, S, "Mercury"))
    return c


def n15():
    c = Plate("earth", 114, "8 of Shields, engraved: six shields finished on the smith's rack, a seventh on the anvil under the hammer, the eighth leaning ready, sparks flying, under the seal of the Sun among the ears of wheat",
              glow=(190, 180, 220))
    emblems(c, "shield")
    c('<path class="wash ink heavy" d="M30 300V140H44V300ZM186 300V140H200V300Z"/><path class="ink heavy" d="M24 150H206M24 214H206"/><path class="ink thin" d="M30 278H200"/>')
    for x in (70, 115, 160):
        c(use("shield", x, 168, .95), use("shield", x, 234, .95))
    c(ground(c, 300))
    c(anvil(286, 280, 1.05))
    c(use("shield", 286, 226, .82))
    c(hammer(252, 210, 40, .9))
    c(use("shield", 352, 288, .9, 12))
    c(sparkle(300, 196, 5), sparkle(320, 210, 4), sparkle(270, 196, 4), '<path class="ink hair" d="M296 206l8 -12M306 212l12 -8M276 204l-4 -12"/>')
    c(crown(c, S, "Sun"))
    return c


def n16():
    c = Plate("earth", 115, "9 of Shields, engraved: nine shields hung along the wattle fence of an orchard, apples ripe on the trees, a falcon on the gatepost, the Magician's endless sign above, under the seal of Venus among the ears of wheat",
              glow=(190, 160, 220))
    emblems(c, "shield")
    c(apple_tree(c, 92, 250, 140, 76), apple_tree(c, 292, 250, 140, 76))
    c(lemniscate(c, 190, 150, 50, 16))
    c(ground(c, 290))
    c('<path class="wash ink heavy" d="M-10 236H390V290H-10Z"/>')
    weave = "".join(f"M{x} 236V290" for x in range(10, 390, 24))
    c(f'<path class="ink thin" d="{weave}"/>', '<path class="ink hair" d="' + "".join(f"M-10 {y}C20 {y - 4} 40 {y + 4} 70 {y}S130 {y - 4} 160 {y}S220 {y + 4} 250 {y}S310 {y - 4} 340 {y}S380 {y + 4} 390 {y}" for y in (246, 258, 270, 282)) + '"/>')
    c('<path class="wash ink heavy" d="M180 300V226H200V300Z"/><path class="hatchfill" d="M192 226H200V300H192Z"/>')
    for k in range(9):
        x = 26 + k * 41 + (8 if k > 3 else 0)
        c(use("shield", x if k != 4 else 190, 262 if k != 4 else 276, .78 if k != 4 else .62))
    c(falcon(190, 226, 1))
    c(crown(c, S, "Venus"))
    return c


def n17():
    c = Plate("earth", 116, "10 of Shields, engraved: ten shields hung along the eaves of the great hall, the hound lying before its open door, under the seal of Mercury among the ears of wheat",
              glow=(190, 160, 220))
    emblems(c, "shield")
    c(longhouse(c, 190, 302, 272, 140))
    for k in range(10):
        x = 76 + k * 25.4
        if abs(x - 190) < 20: continue
        c(use("shield", x, 280, .52))
    c(ground(c, 300))
    c(hound(110, 334, 1, c=c))
    c(crown(c, S, "Mercury"))
    return c


# ---------------------------------------------------------------- the voids
def v049():
    c = Plate("void", 149, "Nisumbha, engraved white on black: his sword broken and his shield split on the field, the Goddess's sword standing bright over them, the river running beneath",
              glow=(190, 150, 220), sky=304)
    emblems(c, "sword", "shield")
    c(stars(c, 12, y1=140, avoid=lambda x, y: abs(x - 190) < 50))
    c(sun_rays(c, 190, 120, 30, 120, 0, 350, 15, 3))
    c(hills(c, 296, [(50, 20), (330, 24)]))
    c(use("sword", 190, 180, 1.4))
    c('<path class="ink thin" d="M176 296C184 292 196 292 204 296"/>')
    c('<g transform="rotate(-78 108 282)"><path class="light ink thin" d="M102 300L102 246L108 236L114 246L114 300Z"/></g>',
      '<path class="tint ink thin" d="M128 270L134 292L140 290L134 268Z"/><path class="light ink thin" d="M60 288L96 276L98 282L62 294Z"/>')
    c('<path class="wash ink thin" d="M250 296A26 26 0 0 1 300 286L276 296Z"/><path class="wash ink thin" d="M282 300A26 26 0 0 1 330 296Z"/><path class="ink hair" d="M260 290L276 296M300 296L314 290"/>')
    c(river_beneath(c))
    return c


def v052():
    c = Plate("void", 152, "Diti-Mula, engraved white on black: the sealed jar of the womb set on its roots, the thunderbolt that cut it, and the winds rising out of the cut seven by seven, the river running beneath",
              glow=(190, 190, 230), sky=304)
    emblems(c, "vaj")
    c(stars(c, 10, y1=120))
    roots = "".join(f"M{190 + dx * .2} 290C{190 + dx * .5} 296 {190 + dx * .8} 300 {190 + dx} 304" for dx in (-110, -70, -36, 36, 70, 110))
    c(f'<path class="ink thin" d="{roots}"/>', '<path class="ink hair" d="M110 300l-8 4M146 302l-4 2M234 302l4 2M270 300l8 4"/>')
    c('<path class="wash ink heavy" d="M150 292C126 280 120 236 146 214C156 206 166 204 172 196L168 182H212L208 196C214 204 224 206 234 214C260 236 254 280 230 292Z"/>',
      '<path class="tint ink thin" d="M160 182C164 170 216 170 220 182Z"/><path class="ink thin" d="M158 182H222"/>',
      '<path class="plate ink thin" d="M190 180L182 210L196 232L184 262L190 292L198 262L208 232L194 210Z"/>',
      '<path class="ink hair" d="M138 240C160 248 220 248 242 240"/>')
    c(use("vaj", 190, 132, .95, 0))
    for k in range(7):
        x = 110 + k * 27
        c(f'<path class="ink thin" d="M{x} 180C{x - 10} 160 {x + 12} 150 {x} 132C{x - 8} 120 {x + 6} 110 {x - 2} 100"/>' if k != 3 else "",
          f'<path class="ink hair" d="M{x - 6} 176c-4 -8 2 -12 6 -10"/>' if k != 3 else "")
    c(river_beneath(c))
    return c


def v054():
    c = Plate("void", 154, "Danu-Garbha, engraved white on black: the sea-cave like a womb in the cliffs, the egg of the Danavas glowing in its dark, the tide breathing at its mouth, the river running beneath",
              glow=(190, 210, 150), sky=304)
    c(stars(c, 8, y1=70))
    c('<path class="wash ink heavy" d="M-10 304V100C40 80 100 76 150 86C200 74 260 78 300 92C340 84 370 92 390 104V304Z"/>',
      '<path class="ink hair" d="M20 120L40 160M60 110L70 140M300 118L320 150M340 112L356 146M30 200L50 240M330 200L350 250"/>')
    c('<path class="plate ink heavy" d="M110 304C100 240 118 160 190 136C262 160 280 240 270 304Z"/>',
      '<path class="ink thin" d="M126 304C118 250 134 176 190 154C246 176 262 250 254 304"/>',
      '<path class="ink hair" d="M142 304C136 256 150 196 190 174C230 196 244 256 238 304"/>')
    c(sun_rays(c, 190, 230, 28, 50, 0, 350, 20, 3))
    c('<ellipse cx="190" cy="230" rx="20" ry="26" class="light ink heavy"/><ellipse cx="190" cy="230" rx="13" ry="18" class="tint ink hair"/><path class="ink hair" d="M182 216C186 212 194 212 198 216"/>')
    c(waves(c, 286, amp=8, length=40, hatch=False))
    c(river_beneath(c))
    return c


CARDS = {"b15": b15, "b16": b16, "b17": b17, "n15": n15, "n16": n16, "n17": n17, "v049": v049, "v052": v052, "v054": v054}
