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
    c = T(s, 400, "The Emperor, engraved: Hlidskjalf, the Allfather's high seat on its crag above the clouds of the worlds, its posts carved with dragons, his two ravens Huginn and Muninn perched on the rock beside it, under the seal of Mars between the ram's horns",
          glow=(190, 170, 220))
    c(stars(c, 8, y0=100, y1=170, avoid=lambda x, y: 110 < x < 270))
    c(cloud(c, 60, 300, 150, 34, "light ink thin"), cloud(c, 320, 306, 160, 34, "light ink thin"))
    c('<path class="wash ink heavy" d="M110 360L132 300L124 266L140 240L152 236H228L240 240L256 266L248 300L270 360Z"/>',
      '<path fill="url(#hd)" d="M228 236L240 240L256 266L248 300L270 360H226C230 320 232 276 228 236Z"/>',
      '<path class="ink hair" d="M136 300L150 276M152 330L158 300M196 340L200 306M218 316L224 290M146 254L160 246M232 254L240 270"/>')
    c('<path class="wash ink heavy" d="M140 236V226H240V236Z"/><path class="ink hair" d="M140 231H240"/>')
    c('<path class="wash ink heavy" d="M150 226V128C150 122 154 118 160 118H220C226 118 230 122 230 128V226Z"/><path fill="url(#hd)" d="M214 118H220C226 118 230 122 230 128V226H214Z" opacity=".85"/>')
    c('<path class="tint ink thin" d="M162 130H218V196H162Z"/>', rope("M168 140C180 152 200 152 212 140M168 186C180 174 200 174 212 186M168 140C182 160 198 168 212 186M212 140C198 160 182 168 168 186", c.p, 5, 3, ".6 2.2", fill=c.p["L"]))
    c('<path class="light ink heavy" d="M140 196H240V210H140Z"/><path class="ink thin" d="M146 210V226M234 210V226"/>')
    c('<path class="wash ink heavy" d="M136 226V106H150V226ZM230 226V106H244V226Z"/><path fill="url(#hd)" d="M146 106H150V226H146ZM240 106H244V226H240Z"/>',
      '<path class="ink hair" d="M136 130H150M136 160H150M136 190H150M230 130H244M230 160H244M230 190H244"/>')
    c(dragon_head(143, 104, .4, flip=True, cls="tint ink thin"), dragon_head(237, 104, .4, cls="tint ink thin"))
    c(raven(c, 116, 262, .82), raven(c, 266, 262, .82, flip=True))
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
    c(rope("M128 248C128 240 192 240 192 248C192 256 128 256 128 248Z", c.p, 10, 7, "1.4 2.4", fill=c.p["T"]), '<path class="ink hair" d="M134 246C150 243 170 243 186 246"/>', '<circle cx="128" cy="248" r="4" class="tint ink thin"/><circle cx="192" cy="248" r="4" class="tint ink thin"/>')
    c('<path class="tint ink thin" d="M204 252C204 268 256 268 256 252Z"/><ellipse cx="230" cy="252" rx="26" ry="6" class="light ink thin"/><ellipse cx="230" cy="252" rx="20" ry="4" class="mid"/>',
      '<path class="ink thin" d="M238 250L270 196"/>')
    c('<path class="ink thin" d="M266 200L274 186"/>' + "".join(f'<path class="ink hair" d="M{f(238 + t * 36)} {f(250 - t * 64)}l-7 -2M{f(238 + t * 36)} {f(250 - t * 64)}l5 -6M{f(240 + t * 36)} {f(246 - t * 64)}l-6 -4M{f(240 + t * 36)} {f(246 - t * 64)}l6 -3"/>' for t in [k / 10 for k in range(4, 11)]))
    c('<path class="ink hair" d="M118 330C140 336 160 334 180 330"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn02():
    s = 2
    c = T(s, 402, "The Lovers, engraved: Ask and Embla, the ash and the elm, washed up as two trees on the shore and leaning together, their boughs grown into one another between them, under the seal of Mercury between the twin pillars",
          glow=(190, 170, 220))
    c(sea(c, top=250, bottom=300, rows=4), chop(c, 262, 0, 380, 46), chop(c, 282, 20, 380, 52))
    c('<path class="light ink heavy" d="M-20 300C80 292 300 292 400 300V380H-20Z"/><path class="hatchfill" d="M-20 324C80 316 300 316 400 324V380H-20Z" opacity=".6"/>')
    c(tree(c, 112, 312, 196, 58, lean=22))
    ash = c.canopy
    c(tree(c, 270, 312, 164, 86, lean=-26))
    for pts, w0 in (([(128, 248), (158, 222), (196, 208), (232, 206), (254, 192)], 10), ([(254, 252), (226, 230), (190, 220), (154, 214), (128, 200)], 9)):
        c(root_arch(c, pts, w0, 3, cls="wash ink thin"))
    for x, y in ((206, 206), (176, 216)):
        c(clump(c, x, y, 13))
    for x0 in (112, 270):
        c(f'<path class="ink thin" d="M{x0 - 16} 312C{x0 - 28} 318 {x0 - 38} 314 {x0 - 46} 322M{x0 + 16} 312C{x0 + 28} 314 {x0 + 38} 322 {x0 + 46} 318M{x0 - 4} 314C{x0 - 8} 324 {x0 - 2} 330 {x0 - 6} 338M{x0 + 6} 314C{x0 + 10} 324 {x0 + 6} 332 {x0 + 12} 338"/>')
    c('<path class="ink hair" d="M40 344c6 -4 12 -4 16 0M320 346c6 -4 12 -4 16 0M180 350c6 -4 12 -4 16 0"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn03():
    s = 3
    c = T(s, 403, "The Chariot, engraved: the Trundholm chariot of the Bronze Age, its horse standing on wheels and drawing the great disc, the disc turned to its dark side for the moon's journey through the night, under the seal of the Moon within the crab's claws",
          glow=(260, 200, 190))
    c(stars(c, 14, y0=100, y1=200, avoid=lambda x, y: x > 200 and y > 140))
    c(crescent(78, 134, 14, "light ink thin"))
    c(hills(c, 306, [(60, 10), (320, 14)], shade=False))
    c(ground(c, 306))
    def wheel(x, y, r=13):
        sp = f"M{x - r + 2} {y}H{x + r - 2}M{x} {y - r + 2}V{y + r - 2}"
        return f'<circle cx="{x}" cy="{y}" r="{r}" class="wash ink heavy"/><circle cx="{x}" cy="{y}" r="{r - 3}" class="ink hair"/><path class="ink thin" d="{sp}"/><circle cx="{x}" cy="{y}" r="3.4" class="tint ink thin"/>'
    c('<path class="ink heavy" d="M70 284H294"/><path class="ink thin" d="M78 284V292M160 284V292M236 284V292M286 284V292"/>')
    for x in (78, 160, 236, 286):
        c(wheel(x, 294))
    c(horse(c, 118, 282, 1.12))
    c('<path class="ink thin" d="M244 266V284M228 278H262"/>')
    x0, y0, R = 260, 210, 58
    c(f'<circle cx="{x0}" cy="{y0}" r="{R}" class="mid ink heavy"/><circle cx="{x0}" cy="{y0}" r="{R}" fill="url(#hx)" opacity=".55"/>',
      f'<circle cx="{x0}" cy="{y0}" r="{R - 7}" class="ink thin"/><circle cx="{x0}" cy="{y0}" r="{R - 22}" class="ink thin"/><circle cx="{x0}" cy="{y0}" r="14" class="ink thin"/>')
    zig = "".join(f"{'M' if k == 0 else 'L'}{f(pol(x0, y0, R - 11 if k % 2 else R - 18, k * 7.5)[0])} {f(pol(x0, y0, R - 11 if k % 2 else R - 18, k * 7.5)[1])}" for k in range(49))
    c(f'<path fill="none" stroke="#f8f9fb" stroke-width="1.3" d="{zig}"/>')
    for a in range(0, 360, 36):
        sx, sy = pol(x0, y0, R - 29, a)
        c(f'<path fill="none" stroke="#f8f9fb" stroke-width="1.2" d="M{f(sx)} {f(sy)}m-4 0a4 4 0 1 1 4 4a2.4 2.4 0 1 1 -2 -2.4"/>')
    c(f'<circle cx="{x0}" cy="{y0}" r="6" fill="none" stroke="#f8f9fb" stroke-width="1.3"/>')
    c(rope("M196 196C210 194 222 196 232 204", c.p, 4, 2.4, ".5 2", fill=c.p["T"]))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn04():
    s = 4
    c = T(s, 404, "Strength, engraved: Fenrir bound on his island with Gleipnir, the fetter made of a cat's footfall and the roots of a mountain, the sword set in his jaws, the cord made fast to the great stone, under the seal of the Sun within the lion's mane",
          glow=(190, 190, 220))
    c(sea(c, top=250, rows=6))
    c('<path class="wash ink heavy" d="M30 300C40 270 90 252 190 250C290 252 340 270 350 300Z"/><path class="hatchfill" d="M250 254C300 260 340 276 350 300H310C300 280 280 264 250 254Z"/>')
    c('<path class="wash ink heavy" d="M282 282L280 246L292 214L304 196L322 188L340 198L350 222L352 254L346 282Z"/>',
      '<path fill="url(#hd)" d="M322 188L340 198L350 222L352 254L346 282H326L330 246L326 214Z" opacity=".9"/>',
      '<path class="ink thin" d="M292 214L312 222L326 214M312 222L310 252L330 246M280 246L310 252M310 252L304 282"/>',
      '<path class="ink hair" d="M296 238l6 -4M318 236l6 -6M334 262l6 -4M300 268l6 -2"/>')
    c(wolf(c, 190, 272, 1.2, "lying", cls="light ink thin"))
    c('<path class="light ink thin" d="M84 240L80 206L84 198L88 206L90 240Z"/><path class="tint ink thin" d="M76 240H96V245H76Z"/><path class="wash ink thin" d="M83 245H89V256H83Z"/>')
    c(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" d="M150 226C156 246 170 262 190 264C214 266 222 236 244 236C262 236 270 256 292 262"/>',
      f'<path fill="none" stroke="{c.p["T"]}" stroke-width="2.4" d="M120 264C136 250 150 270 170 262C186 256 194 240 210 238"/>',
      '<path class="ink hair" d="M150 224C156 244 170 260 190 262C214 264 222 234 244 234C262 234 270 254 292 260"/>')
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn05():
    s = 5
    c = T(s, 405, "The Hermit, engraved: the foot of the World Tree, one great root of it arching over Mimir's well with fine rootlets hanging toward the water, and in the water the eye the Allfather pledged for one drink of wisdom, shining up out of the dark, under the seal of Mercury among the ears of wheat",
          glow=(210, 250, 170))
    c(root_arch(c, [(112, 150), (96, 104), (80, 50), (72, -12)], 20, 30, cls="wash ink thin"), root_arch(c, [(250, 132), (282, 92), (310, 40), (320, -12)], 14, 22, cls="wash ink thin"))
    c(root_arch(c, [(24, 262), (50, 204), (96, 152), (150, 128), (206, 122), (258, 136), (300, 172), (322, 222), (332, 278)], 48, 20,
                rootlets=[(.3, 56), (.38, 82), (.46, 100), (.54, 94), (.62, 74), (.7, 50)]))
    c(root_arch(c, [(300, 172), (340, 168), (372, 182), (396, 204)], 16, 8, cls="wash ink thin"))
    c('<path class="wash ink heavy" d="M-10 360V214C14 206 40 214 58 232C74 250 84 268 92 290L96 360Z"/><path class="hatchfill" d="M40 216C60 228 76 250 86 276C90 290 92 300 94 320H70C70 280 60 244 40 216Z"/>',
      '<path class="ink hair" d="M10 236l10 4M26 252l8 6M14 280l10 2M44 270l6 8"/>')
    c(ground(c, 272))
    c('<path class="wash ink heavy" d="M110 272V320C110 334 150 344 190 344C230 344 270 334 270 320V272Z"/><path class="hatchfill" d="M240 272V334C256 330 270 326 270 320V272Z"/>',
      '<path class="ink hair" d="M110 294C130 302 250 302 270 294M110 316C130 324 250 324 270 316M140 272V298M180 276V302M220 276V302M250 272V298M126 302V324M200 304V326M240 302V324"/>')
    c('<ellipse cx="190" cy="272" rx="80" ry="20" class="light ink heavy"/><ellipse cx="190" cy="272" rx="66" ry="14" class="mid ink thin"/>',
      '<ellipse cx="190" cy="272" rx="66" ry="14" fill="url(#hx)" opacity=".6"/>')
    c(sun_rays(c, 190, 272, 14, 34, 190, 350, 20, 4))
    c('<path class="light ink thin" d="M170 272C178 264 202 264 210 272C202 280 178 280 170 272Z"/><circle cx="190" cy="272" r="6" class="tint ink thin"/><circle cx="190" cy="272" r="2.4" class="fill-ink"/>')
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
    c = T(s, 407, "Death, engraved: Gjallarbru, the bridge roofed with shining gold over the river Gjoll, leading on to the barred gate of Hel set in the cliff, under the seal of Mars between the scorpion's tails",
          glow=(300, 190, 200))
    c('<path class="wash ink heavy" d="M240 300L248 220L240 180L256 140L272 120L300 112L330 118L352 106L374 116L390 112V300Z"/>',
      '<path fill="url(#hd)" d="M330 118L352 106L374 116L390 112V300H344C346 240 340 170 330 118Z" opacity=".85"/>',
      '<path class="ink hair" d="M252 196L262 184M256 250L266 240M362 150L370 140M372 200L380 190M366 262L376 250"/>')
    c('<path class="plate ink heavy" d="M270 300V196C270 170 284 152 306 152C328 152 342 170 342 196V300Z"/>',
      '<path class="ink thin" d="M262 300V196C262 164 280 142 306 142C332 142 350 164 350 196V300"/>',
      '<path class="ink hair" d="M266 192C268 166 284 148 306 148C328 148 344 166 346 192"/>')
    c('<path class="light ink thin" d="' + "".join(f"M{x} 300V{f(196 - math.sqrt(max(0, 36 ** 2 - (x - 306) ** 2)) * .9 + 20)}" for x in range(278, 340, 10)) + '"/>',
      '<path class="light ink thin" d="M270 214H342M270 254H342"/>',
      "".join(f'<circle cx="{x}" cy="{y}" r="2" class="light ink hair"/>' for x in range(278, 340, 10) for y in (214, 254)))
    c(sea(c, top=262, rows=6))
    c('<path class="ink hair" d="M0 300C40 296 80 304 120 300M150 318C190 314 230 322 270 316"/>')
    c('<path class="wash ink heavy" d="M30 300C70 236 220 236 270 280V292C220 254 80 254 44 304Z"/>',
      '<path class="ink thin" d="M40 296C80 248 220 248 266 286"/>')
    for k in range(9):
        t = k / 8; x = 40 + t * 226; y = 296 - math.sin(math.pi * t) * 46 - t * 10
        c(f'<path class="ink thin" d="M{f(x)} {f(y)}V{f(y - 30)}"/>')
    c('<path class="tint ink thin" d="M30 268C70 202 220 200 274 248L270 236C220 186 70 188 22 258Z"/>',
      '<path class="ink hair" d="M40 252C80 204 210 200 262 236M50 244C90 202 200 198 254 230"/>')
    c('<path class="ink hair" d="M232 290C244 284 256 288 266 282M220 300C236 294 252 298 268 292"/>')
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
    horn = "M54 150C50 138 54 128 62 124C80 140 102 160 128 166L124 182C96 178 70 166 54 150Z"
    c(f'<path class="light ink heavy" d="{horn}"/>', f'<path fill="url(#hd)" d="M62 124C80 140 102 160 128 166L126 174C100 168 78 154 62 136Z" opacity=".6"/>',
      '<path class="tint ink thin" d="M54 150C50 138 54 128 62 124L66 128C60 132 58 140 60 148Z"/><path class="tint ink thin" d="M118 166L128 166L124 182L114 180Z"/>',
      '<path class="ink hair" d="M74 138C78 146 76 156 70 160M90 150C94 156 92 166 86 170M104 158C108 164 106 172 100 176"/>')
    c(f'<path fill="none" stroke="{c.p["T"]}" stroke-width="4" d="M126 176C140 184 150 206 156 238"/>', '<path class="ink hair" d="M126 174C142 182 152 204 158 238"/>')
    c(sparkle(190, 200, 6), sparkle(272, 210, 4), sparkle(110, 140, 4))
    c(crown(c, SIGNS[s], RULER[s]))
    return c


def tn09():
    s = 9
    c = T(s, 409, "The Devil, engraved: the three stones set on edge in the cave where the bound one lies, the iron fetters across them, the serpent hung from the roof above, its venom dripping into the bowl set beneath, under the seal of Saturn between the goat's horns",
          glow=(190, 230, 170))
    c('<path class="mid" d="M-10 96H390V330H-10Z" opacity=".3"/><rect x="-10" y="96" width="400" height="234" fill="url(#hx)" opacity=".35"/>')
    c('<path class="wash ink heavy" d="M-10 96H390V132L370 138L362 164L350 142L330 150L318 176L306 148L280 140L262 152L250 138L226 140L214 158L204 136L176 138L166 162L156 140L130 146L118 170L106 144L80 140L66 160L56 138L30 142L18 166L8 140L-10 142Z"/>',
      '<path fill="url(#hd)" d="M-10 120H390V132L370 138L362 164L350 142L330 150L318 176L306 148L280 140L262 152L250 138L226 140L214 158L204 136L176 138L166 162L156 140L130 146L118 170L106 144L80 140L66 160L56 138L30 142L18 166L8 140L-10 142Z" opacity=".8"/>')
    c('<path class="wash ink heavy" d="M-10 330V140L18 150L30 190L22 240L36 290L40 330Z"/><path class="wash ink heavy" d="M390 330V140L364 152L356 196L366 246L350 290L346 330Z"/>',
      '<path class="ink hair" d="M8 180L18 196M12 230L24 244M368 186L378 198M362 270L374 282"/>')
    c(ground(c, 314, wob=3))
    for x, top in ((110, 262), (190, 254), (270, 262)):
        c(f'<path class="wash ink heavy" d="M{x - 28} 314L{x - 26} {top + 6}L{x - 14} {top}H{x + 16}L{x + 28} {top + 8}L{x + 26} 314Z"/><path class="hatchfill" d="M{x + 10} {top}H{x + 16}L{x + 28} {top + 8}L{x + 26} 314H{x + 8}Z"/>'
          f'<path class="ink hair" d="M{x - 18} {top + 30}l8 4M{x - 6} {top + 44}l10 2"/>')
    for y in (282, 300):
        c(f'<path class="mid ink thin" d="M74 {y - 4}C120 {y + 4} 160 {y - 6} 190 {y}C220 {y + 6} 260 {y - 4} 306 {y + 2}V{y + 9}C260 {y + 3} 220 {y + 13} 190 {y + 7}C160 {y + 1} 120 {y + 11} 74 {y + 3}Z"/>'
          + "".join(f'<circle cx="{x}" cy="{y + 3}" r="1.6" class="light ink hair"/>' for x in (96, 134, 170, 210, 246, 284)))
    body = [(214, 150), (206, 168), (222, 184), (208, 200), (198, 214)]
    c(f'<path class="tint ink thin" d="{taper(body, 15, 9)}"/>', '<path class="ink hair" d="' + "".join(f"M{f(x - 5)} {f(y - 2)}q5 5 10 0" for x, y in densify(body, 3)[1:-1]) + '"/>')
    c('<path class="tint ink thin" d="M192 212C188 220 190 230 198 236C206 230 208 220 204 212Z"/><circle cx="194" cy="222" r="1.6" class="fill-ink"/><circle cx="202" cy="222" r="1.6" class="fill-ink"/>',
      '<path class="light ink hair" d="M195 234L196 240L197 234ZM199 234L200 240L201 234Z"/>')
    for y in (246, 252):
        c(f'<path class="light ink thin" d="M198 {y - 4}C200 {y} 201 {y + 2} 198 {y + 3}C195 {y + 2} 196 {y} 198 {y - 4}Z"/>')
    c('<path class="light ink heavy" d="M174 254C176 268 220 268 222 254Z"/><ellipse cx="198" cy="254" rx="24" ry="4.4" class="tint"/>')
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
