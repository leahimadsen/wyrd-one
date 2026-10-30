"""The Nordic deck's twelve zodiac trumps, Aries to Pisces, each under the seal of its sign's ruler
within the sign's device, each drawn from the lore: the Eddas, the sagas, and for the Chariot the
older Bronze Age sun chariot found at Trundholm."""
import math
from lib import *

RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
FAM = lambda s: ELEMENT[s % 4]


def T(s, seed, label, **kw):
    return Plate(FAM(s), seed, label, **kw)


def wolf_lying(x, y, s=1, flip=False, cls="mid ink thin"):
    """A great wolf lying with its head up, facing left."""
    body = (f'<path class="{cls}" d="M-46 -4C-50 -14 -44 -24 -32 -26C-24 -40 -6 -46 10 -42C24 -46 44 -40 60 -30C76 -26 92 -18 98 -4C100 4 92 8 80 6H-40C-46 6 -48 2 -46 -4Z"/>'
            f'<path class="{cls}" d="M-34 -30C-40 -42 -42 -54 -36 -62L-30 -76L-24 -62C-18 -62 -12 -60 -8 -56L-2 -70L2 -54C6 -48 6 -40 2 -34C-8 -28 -24 -26 -34 -30Z"/>'
            f'<path class="{cls}" d="M-36 -46C-46 -46 -58 -44 -66 -40C-66 -34 -58 -30 -46 -30C-40 -30 -36 -34 -34 -38Z"/>'
            f'<circle cx="-24" cy="-48" r="2" class="light ink hair"/><path class="fill-ink" d="M-66 -40l-4 1l3 3Z"/>'
            f'<path class="ink hair" d="M-20 -36l-4 6M-12 -38l-3 6M-4 -40l-2 6M12 -38l-2 8M24 -36l-1 8M36 -32l0 8M48 -28l1 8M62 -22l2 8M-46 -36l-6 2M-48 -32l-6 3"/>'
            f'<path class="{cls}" d="M96 -6C110 -10 122 -22 126 -36C118 -32 108 -26 100 -18Z"/><path class="ink hair" d="M104 -16l6 -10M112 -20l4 -10"/>'
            f'<path class="ink thin" d="M-40 6C-48 8 -56 8 -62 6M-20 6C-28 10 -36 10 -42 8"/>')
    sx = -s if flip else s
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx} {s})">{body}</g>'


def wolf_running(x, y, s=1, cls="mid ink thin"):
    """A wolf at full stretch, running to the right."""
    body = (f'<path class="{cls}" d="M-50 -6C-40 -18 -10 -24 16 -22C30 -22 40 -26 50 -32C58 -36 68 -36 74 -30L88 -26L76 -20C70 -12 60 -8 50 -6C34 -2 10 2 -10 2C-30 4 -44 2 -50 -6Z"/>'
            f'<path class="{cls}" d="M62 -34L66 -46L72 -34Z"/><circle cx="72" cy="-28" r="1.6" class="light ink hair"/>'
            f'<path class="{cls}" d="M-50 -6C-64 -10 -78 -6 -92 4C-78 2 -64 2 -52 0Z"/>'
            f'<path class="ink heavy" d="M40 -6L62 6L80 4M30 -4L46 14L64 16M-30 0L-54 12L-74 10M-38 -2L-60 2L-80 -6"/>'
            f'<path class="ink hair" d="M-20 -18l-4 8M-6 -20l-2 8M8 -20l-1 8M24 -22l0 8M36 -26l2 8M-36 -12l-6 6"/>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({s})">{body}</g>'


def tn00():
    s = 0
    c = T(s, 400, "The Emperor, engraved: Hlidskjalf, the Allfather's high seat on its crag above the worlds, his two ravens Huginn and Muninn on its posts, under the seal of Mars between the ram's horns",
          glow=(190, 170, 220))
    c(cloud(c, 70, 292, 140, 26, "light ink thin"), cloud(c, 310, 300, 140, 26, "light ink thin"))
    c(hills(c, 330, [(40, 16), (330, 20)]))
    c('<path class="wash ink heavy" d="M120 360L146 290L140 250L156 226L224 226L240 250L234 290L260 360Z"/>',
      '<path class="hatchfill" d="M224 226L240 250L234 290L260 360H214C214 316 222 260 224 226Z"/>',
      '<path class="ink hair" d="M150 300L162 274M172 320L176 290M200 330L204 296M160 252L172 240"/>')
    c('<path class="wash ink heavy" d="M140 226V140H156V226ZM224 226V140H240V226Z"/><path class="hatchfill" d="M150 140H156V226H150ZM234 140H240V226H234Z"/>',
      '<path class="tint ink thin" d="M150 192H230V206H150Z"/><path class="wash ink heavy" d="M144 206H236V226H144Z"/><path class="ink hair" d="M144 216H236"/>',
      '<path class="ink thin" d="M156 160H224M156 176H224"/><path class="ink hair" d="' + "".join(f"M{x} 160V192" for x in range(166, 224, 12)) + '"/>')
    c(dragon_head(148, 140, .42, cls="tint ink thin"), dragon_head(232, 140, .42, flip=True, cls="tint ink thin"))
    c(raven(c, 130, 124, .7), raven(c, 250, 124, .7, flip=True))
    c(stars(c, 6, y0=100, y1=180, avoid=lambda x, y: 100 < x < 280))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn01():
    s = 1
    c = T(s, 401, "The Hierophant, engraved: the altar of the hof, the oath ring laid upon it, the blot bowl and its sprig for the sprinkling, the carved posts of the hall behind, under the seal of Venus between the bull's horns",
          glow=(190, 200, 210))
    c('<path class="wash ink heavy" d="M60 330V120H84V330ZM296 330V120H320V330Z"/><path class="hatchfill" d="M76 120H84V330H76ZM312 120H320V330H312Z"/>',
      '<path class="ink hair" d="M64 150C72 156 80 150 84 158M64 180C72 186 80 180 84 188M64 210C72 216 80 210 84 218M300 150C308 156 316 150 320 158M300 180C308 186 316 180 320 188M300 210C308 216 316 210 320 218"/>',
      '<path class="wash ink heavy" d="M40 120H340V106H40Z"/>')
    c(dragon_head(72, 112, .4, cls="tint ink thin"), dragon_head(308, 112, .4, flip=True, cls="tint ink thin"))
    c(ground(c, 330, wob=2))
    c('<path class="wash ink heavy" d="M110 330V264H270V330Z"/><path class="hatchfill" d="M244 264H270V330H244Z"/><path class="light ink thin" d="M102 254H278V266H102Z"/>',
      '<path class="ink hair" d="M110 286H270M110 308H270M150 264V330M230 264V330"/>')
    c('<ellipse cx="160" cy="248" rx="30" ry="9" class="ink heavy"/><ellipse cx="160" cy="248" rx="30" ry="9" fill="none" stroke="' + c.p["T"] + '" stroke-width="3"/><ellipse cx="160" cy="246" rx="30" ry="9" class="ink hair"/>')
    c('<path class="tint ink thin" d="M204 252C204 268 256 268 256 252Z"/><ellipse cx="230" cy="252" rx="26" ry="6" class="light ink thin"/><ellipse cx="230" cy="252" rx="20" ry="4" class="mid"/>',
      '<path class="ink thin" d="M238 250L270 196"/>')
    c(leaves(c, 270, 198, 9, 18, -170, 10, (.4, .6)))
    c(flame(c, 190, 352, 20, 12))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn02():
    s = 2
    c = T(s, 402, "The Lovers, engraved: Ask and Embla, the ash and the elm, two trees washed up on the shore and leaning together, their boughs grown into one, under the seal of Mercury between the twin pillars",
          glow=(190, 170, 220))
    c(waves(c, 250, amp=8, length=44), waves(c, 272, amp=7, length=40, hatch=False))
    c('<path class="light ink heavy" d="M-20 300C80 290 300 290 400 300V380H-20Z"/><path class="hatchfill" d="M-20 322C80 314 300 314 400 322V380H-20Z" opacity=".6"/>')
    c(tree(c, 112, 310, 160, 82, lean=50), tree(c, 268, 310, 160, 82, lean=-50))
    for x0 in (116, 264):
        c(f'<path class="ink thin" d="M{x0 - 14} 310C{x0 - 26} 316 {x0 - 36} 312 {x0 - 44} 320M{x0 + 14} 310C{x0 + 26} 312 {x0 + 36} 320 {x0 + 44} 316M{x0} 312C{x0 - 4} 322 {x0 + 2} 328 {x0 - 2} 336"/>')
    c('<path class="ink hair" d="M60 340c6 -4 12 -4 16 0M300 344c6 -4 12 -4 16 0M140 352c6 -4 12 -4 16 0"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn03():
    s = 3
    c = T(s, 403, "The Chariot, engraved: the Trundholm chariot of the Bronze Age, its horse on wheels drawing the great disc, the disc turned to its dark side for the moon's journey through the night, under the seal of the Moon within the crab's claws",
          glow=(260, 200, 190))
    c(stars(c, 12, y0=100, y1=200, avoid=lambda x, y: x > 170 and y > 120))
    c(hills(c, 300, [(60, 12), (320, 16)], shade=False))
    c(ground(c, 300))
    def wheel(x, y, r=17):
        sp = "".join(f"M{f(pol(x, y, 4, a)[0])} {f(pol(x, y, 4, a)[1])}L{f(pol(x, y, r - 3, a)[0])} {f(pol(x, y, r - 3, a)[1])}" for a in (0, 90))
        return f'<circle cx="{x}" cy="{y}" r="{r}" class="wash ink heavy"/><path class="ink thin" d="{sp}"/><circle cx="{x}" cy="{y}" r="4" class="tint ink thin"/>'
    c('<path class="ink heavy" d="M80 292H172M218 292H294"/>')
    for x in (84, 168, 222, 290):
        c(wheel(x, 296))
    c(horse(c, 124, 250, 1.05))
    c(rope("M176 222C196 222 210 224 204 226", c.p, 4, 2.4, ".5 2", fill=c.p["T"]), '<path class="ink thin" d="M160 290H200"/>')
    c('<circle cx="256" cy="228" r="52" class="mid ink heavy"/><circle cx="256" cy="228" r="44" class="ink thin"/>',
      '<path class="ink hair" d="' + "".join(f"M{f(pol(254, 230, 30, a)[0])} {f(pol(254, 230, 30, a)[1])}a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" for a in range(0, 360, 30)) + '"/>',
      '<circle cx="254" cy="230" r="14" class="ink thin"/><circle cx="254" cy="230" r="5" class="light ink hair"/>',
      '<path fill="url(#hx)" d="M254 178A52 52 0 0 1 254 282A52 52 0 0 1 254 178Z" opacity=".5"/>')
    c('<path class="ink heavy" d="M256 280V292"/>')
    c(crescent(80, 132, 14, "light ink thin"))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn04():
    s = 4
    c = T(s, 404, "Strength, engraved: Fenrir bound on his island with Gleipnir, the fetter made of a cat's footfall and the roots of a mountain, the sword set in his jaws, the cord made fast to the great stone, under the seal of the Sun within the lion's mane",
          glow=(190, 190, 220))
    c(sea(c, top=250, rows=6))
    c('<path class="wash ink heavy" d="M30 300C40 270 90 252 190 250C290 252 340 270 350 300Z"/><path class="hatchfill" d="M250 254C300 260 340 276 350 300H310C300 280 280 264 250 254Z"/>')
    c('<path class="wash ink heavy" d="M286 280C280 240 290 196 312 184C330 178 342 196 344 230C346 254 342 272 338 280Z"/><path class="hatchfill" d="M326 182C340 190 346 214 344 240C342 260 340 272 338 280H326C332 248 332 210 326 182Z"/>',
      '<path class="ink hair" d="M298 230L306 214M300 256L310 244M318 200L322 190"/>')
    c(wolf(c, 190, 272, 1.2, "lying", cls="light ink thin"))
    c('<path class="light ink thin" d="M84 240L80 206L84 198L88 206L90 240Z"/><path class="tint ink thin" d="M76 240H96V245H76Z"/><path class="wash ink thin" d="M83 245H89V256H83Z"/>')
    c(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" d="M150 226C156 246 170 262 190 264C214 266 222 236 244 236C262 236 270 256 292 262"/>',
      f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" d="M120 264C136 250 150 270 170 262C186 256 194 240 210 238"/>',
      '<path class="ink hair" d="M150 224C156 244 170 260 190 262C214 264 222 234 244 234C262 234 270 254 292 260"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn05():
    s = 5
    c = T(s, 405, "The Hermit, engraved: Mimir's well beneath the root of the World Tree, and in its water the eye the Allfather pledged for one drink of wisdom, shining up out of the dark, under the seal of Mercury among the ears of wheat",
          glow=(190, 250, 170))
    c(root(c, [(-20, 120), (40, 126), (96, 152), (130, 196), (150, 250)], 46, 12))
    c(root(c, [(400, 130), (340, 138), (290, 168), (256, 210), (240, 252)], 40, 10))
    c(root(c, [(40, 126), (20, 160), (10, 200)], 16, 5, "wash ink thin"), root(c, [(340, 138), (366, 170), (372, 206)], 14, 5, "wash ink thin"))
    c(ground(c, 262))
    c('<path class="wash ink heavy" d="M110 262V320C110 334 150 344 190 344C230 344 270 334 270 320V262Z"/><path class="hatchfill" d="M240 262V334C256 330 270 326 270 320V262Z"/>',
      '<path class="ink hair" d="M110 286C130 294 250 294 270 286M110 308C130 316 250 316 270 308M140 262V290M180 266V294M220 266V294M250 262V290M126 294V316M200 296V318M240 294V316"/>')
    c('<ellipse cx="190" cy="262" rx="80" ry="20" class="light ink heavy"/><ellipse cx="190" cy="262" rx="66" ry="14" class="mid ink thin"/>',
      '<ellipse cx="190" cy="262" rx="66" ry="14" fill="url(#hx)" opacity=".6"/>')
    c(sun_rays(c, 190, 262, 14, 34, 190, 350, 20, 4))
    c('<path class="light ink thin" d="M170 262C178 254 202 254 210 262C202 270 178 270 170 262Z"/><circle cx="190" cy="262" r="6" class="tint ink thin"/><circle cx="190" cy="262" r="2.4" class="fill-ink"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn06():
    s = 6
    c = T(s, 406, "Justice, engraved: the Law Rock at the heart of the Thing, the ring of standing stones about it, the spear and shield set up for the law to be spoken, under the seal of Venus within the balance",
          glow=(190, 190, 220))
    c(hills(c, 220, [(60, 18), (300, 24)]))
    c(ground(c, 226, wob=2))
    ring = [(190 + 150 * math.cos(math.radians(a)), 280 + 50 * math.sin(math.radians(a))) for a in range(0, 360, 30)]
    for x, y in sorted(ring, key=lambda p: p[1]):
        h = 26 + (y - 230) * .5
        c(f'<path class="wash ink thin" d="M{f(x - 9)} {f(y)}L{f(x - 8)} {f(y - h * .78)}L{f(x - 3)} {f(y - h)}L{f(x + 5)} {f(y - h * .92)}L{f(x + 9)} {f(y - h * .62)}L{f(x + 9)} {f(y)}Z"/>'
          f'<path class="hatchfill" d="M{f(x + 2)} {f(y - h * .96)}L{f(x + 5)} {f(y - h * .92)}L{f(x + 9)} {f(y - h * .62)}L{f(x + 9)} {f(y)}H{f(x + 2)}Z"/><path class="ink hair" d="M{f(x - 5)} {f(y - h * .5)}l4 2M{f(x - 4)} {f(y - h * .28)}l5 1"/>' if y < 280 else "")
    c('<path class="wash ink heavy" d="M130 290C134 262 160 246 190 246C220 246 246 262 250 290Z"/><path class="hatchfill" d="M214 250C234 258 246 272 250 290H226C226 274 222 260 214 250Z"/>',
      '<path class="ink hair" d="M146 280L160 266M176 270L184 258M204 268L214 260"/>')
    c('<path class="ink heavy" d="M190 250V130"/><path class="light ink thin" d="M190 112L182 132H198Z"/><path class="tint ink thin" d="M186 132H194V138H186Z"/>')
    emblems(c, "shield")
    c(use("shield", 190, 200, 1.05))
    for x, y in sorted(ring, key=lambda p: p[1]):
        h = 26 + (y - 230) * .5
        c(f'<path class="wash ink thin" d="M{f(x - 9)} {f(y)}L{f(x - 8)} {f(y - h * .78)}L{f(x - 3)} {f(y - h)}L{f(x + 5)} {f(y - h * .92)}L{f(x + 9)} {f(y - h * .62)}L{f(x + 9)} {f(y)}Z"/>'
          f'<path class="hatchfill" d="M{f(x + 2)} {f(y - h * .96)}L{f(x + 5)} {f(y - h * .92)}L{f(x + 9)} {f(y - h * .62)}L{f(x + 9)} {f(y)}H{f(x + 2)}Z"/><path class="ink hair" d="M{f(x - 5)} {f(y - h * .5)}l4 2M{f(x - 4)} {f(y - h * .28)}l5 1"/>' if y >= 280 else "")
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn07():
    s = 7
    c = T(s, 407, "Death, engraved: Gjallarbru, the bridge roofed with shining gold over the river Gjoll, leading on to the gate of Hel, under the seal of Mars between the scorpion's tails",
          glow=(300, 190, 200))
    c('<path class="mid ink heavy" d="M268 290V134H340V290Z"/><path fill="url(#hx)" d="M268 134H340V290H268Z" opacity=".5"/>',
      '<path class="ink thin" d="M262 134H346V122H262Z"/><path class="ink thin" d="' + "".join(f"M{x} 140V290" for x in range(280, 340, 12)) + '"/>',
      '<path class="ink thin" d="M274 196H334M274 250H334"/>')
    c(sea(c, top=262, rows=6))
    c('<path class="ink hair" d="M0 300C40 296 80 304 120 300M150 318C190 314 230 322 270 316"/>')
    c('<path class="wash ink heavy" d="M30 300C70 236 220 236 270 280V292C220 254 80 254 44 304Z"/>',
      '<path class="ink thin" d="M40 296C80 248 220 248 266 286"/>')
    for k in range(9):
        t = k / 8; x = 40 + t * 226; y = 296 - math.sin(math.pi * t) * 46 - t * 10
        c(f'<path class="ink thin" d="M{f(x)} {f(y)}V{f(y - 30)}"/>')
    c('<path class="tint ink thin" d="M30 268C70 202 220 200 274 248L270 236C220 186 70 188 22 258Z"/>',
      '<path class="ink hair" d="M40 252C80 204 210 200 262 236M50 244C90 202 200 198 254 230"/>')
    c(sparkle(120, 196, 5), sparkle(200, 194, 5))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn08():
    s = 8
    c = T(s, 408, "Temperance, engraved: the three vessels of the mead of poetry, Odrerir the kettle between the crocks Bodn and Son, the honeyed mead poured from one into another, under the seal of Jupiter beneath the drawn bow",
          glow=(190, 190, 220))
    c(ground(c, 314))
    for x in range(140, 250, 22):
        c(flame(c, x, 318, 16, 12))
    c('<path class="mid ink heavy" d="M140 248C140 296 160 314 190 314C220 314 240 296 240 248Z"/><path class="hatchfill" d="M214 250C230 254 240 260 240 248C240 288 226 308 206 312C218 294 220 270 214 250Z"/>',
      '<ellipse cx="190" cy="248" rx="50" ry="10" class="light ink heavy"/><ellipse cx="190" cy="248" rx="42" ry="6" class="tint"/>',
      '<path class="ink thin" d="M140 254C126 240 128 222 144 214M240 254C254 240 252 222 236 214"/>')
    for x, k in ((74, -1), (306, 1)):
        c(f'<path class="wash ink heavy" d="M{x - 30} 314C{x - 38} 290 {x - 36} 252 {x - 22} 238H{x + 22}C{x + 36} 252 {x + 38} 290 {x + 30} 314Z"/>',
          f'<ellipse cx="{x}" cy="238" rx="22" ry="5" class="light ink thin"/><path class="tint ink thin" d="M{x - 34} 268H{x + 34}V278H{x - 34}Z"/>',
          f'<path class="ink hair" d="M{x - 32} 290H{x + 32}"/>')
    c('<path class="wash ink heavy" d="M60 208C56 188 70 172 92 168L118 162L120 172L96 180C80 184 72 196 76 210Z"/>',
      f'<path fill="none" stroke="{c.p["T"]}" stroke-width="4" d="M118 168C136 172 150 196 156 238"/><path class="ink hair" d="M118 166C138 170 152 194 158 238"/>')
    c(sparkle(190, 200, 6), sparkle(272, 210, 4), sparkle(110, 140, 4))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn09():
    s = 9
    c = T(s, 409, "The Devil, engraved: the three stones set on edge in the cave where the bound one lies, the fetters across them, the serpent hung above dripping its venom into the bowl held beneath, under the seal of Saturn between the goat's horns",
          glow=(190, 160, 220))
    c('<path class="mid" d="M-10 100H390V360H-10Z" opacity=".25"/><path class="wash ink heavy" d="M-10 360V150C40 120 110 104 190 104C270 104 340 120 390 150V360H340C330 260 280 200 190 196C100 200 50 260 40 360Z"/>',
      '<path class="ink hair" d="M20 170L40 220M50 150L60 190M330 150L346 200M360 170L370 230"/>')
    c(ground(c, 314, wob=3))
    for x in (110, 190, 270):
        c(f'<path class="wash ink heavy" d="M{x - 26} 314L{x - 22} 262L{x - 6} 254H{x + 18}L{x + 26} 266L{x + 24} 314Z"/><path class="hatchfill" d="M{x + 10} 254H{x + 18}L{x + 26} 266L{x + 24} 314H{x + 8}Z"/>')
    c(rope("M74 274C120 284 160 268 190 278C220 288 260 270 306 282M80 296C120 304 160 292 190 300C220 308 260 294 300 302", c.p, 6, 3.6, ".7 2.4", fill=c.p["M"]))
    c(rope("M150 204C160 214 176 216 190 214C206 212 220 216 226 224", c.p, 11, 7, ".9 3", fill=c.p["T"]),
      '<path class="tint ink thin" d="M226 224C232 232 232 242 224 246C218 248 214 244 216 238Z"/><circle cx="224" cy="236" r="1.6" class="fill-ink"/>',
      '<path class="ink thin" d="M150 204C142 196 140 186 146 176"/>')
    c('<path class="tint ink thin" d="M222 250C224 256 226 260 222 262C218 262 218 256 222 250Z"/><path class="tint ink thin" d="M222 268C224 272 225 276 222 278C219 278 219 272 222 268Z"/>')
    c('<path class="light ink heavy" d="M200 290C202 304 242 304 244 290Z"/><ellipse cx="222" cy="290" rx="22" ry="4" class="tint"/><path class="ink thin" d="M244 292C252 292 258 296 260 302"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn10():
    s = 10
    c = T(s, 410, "The Star, engraved: Aurvandil's toe, thrown up into the sky to shine as a star, over the frozen rivers of Elivagar, the basket that carried him across left on the ice, under the seal of Saturn between the water-bearer's urns",
          glow=(190, 150, 220))
    pts = [pol(190, 152, 36 if k % 2 == 0 else 12, k * 30 - 90) for k in range(12)]
    c(sun_rays(c, 190, 152, 42, 88, 0, 350, 15, 2))
    c('<path class="light ink heavy" d="M' + "L".join(f"{f(a)} {f(b)}" for a, b in pts) + 'Z"/><circle cx="190" cy="152" r="8" class="tint ink thin"/>')
    c(stars(c, 16, y0=100, y1=230, avoid=lambda x, y: math.hypot(x - 190, y - 152) < 94))
    c(mountain(c, -30, 120, (40, 196), 250, snow=True), mountain(c, 260, 410, (340, 190), 250, snow=True))
    c('<path class="light ink thin" d="M-10 250H390V360H-10Z"/>')
    for y0 in (264, 300, 336):
        c(f'<path class="wash ink thin" d="M-10 {y0}C80 {y0 - 6} 160 {y0 + 6} 240 {y0}S340 {y0 - 6} 390 {y0}V{y0 + 14}C300 {y0 + 20} 220 {y0 + 8} 140 {y0 + 14}S40 {y0 + 20} -10 {y0 + 14}Z"/>',
          f'<path class="ink hair" d="M20 {y0 + 6}l14 2M90 {y0 + 4}l18 -2M170 {y0 + 6}l12 2M250 {y0 + 4}l16 0M320 {y0 + 6}l14 -2"/>')
    c('<path class="tint ink thin" d="M250 322C250 300 300 300 300 322C300 334 250 334 250 322Z"/><path class="ink thin" d="M252 316C262 308 288 308 298 316M256 300C258 286 292 286 294 300"/>',
      '<path class="ink hair" d="' + "".join(f"M{x} 304V332" for x in range(258, 296, 6)) + '"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn11():
    s = 11
    c = T(s, 411, "The Moon, engraved: the moon racing across the night sky with the wolf Hati hard behind, the sea below, the Empress's crown of twelve stars for Venus exalted, under the seal of Jupiter between the two fishes",
          glow=(280, 150, 190))
    c(stars(c, 14, y0=100, y1=230, avoid=lambda x, y: math.hypot(x - 286, y - 150) < 50 or (60 < x < 240 and 160 < y < 240)))
    c(full_moon(c, 290, 150, 30))
    c('<path class="ink hair" d="M246 150l-26 0M248 140l-20 -2M248 160l-20 2"/>')
    c(wolf(c, 140, 214, 1.05, "running", cls="light ink thin"))
    for k in range(12):
        x, y = pol(70, 128, 16, k * 30)
        c(sparkle(x, y, 3.6, "tint ink hair"))
    c(waves(c, 266, amp=9, length=46), waves(c, 292, amp=8, length=40, hatch=False))
    c('<path fill="none" stroke="#f8f9fb" stroke-width="3" stroke-dasharray="14 6" d="M272 284H308M268 302H312M276 320H304"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


CARDS = {f"tn{s:02d}": fn for s, fn in enumerate([tn00, tn01, tn02, tn03, tn04, tn05, tn06, tn07, tn08, tn09, tn10, tn11])}
