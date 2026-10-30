"""Cancer: the 2, 3 and 4 of Lotuses and of Cups (Venus, Mercury and the Moon), and the voids at
stations XXXI (Puloman), XXXIV (Viprachitti) and XXXVI (Simhika)."""
import math
from lib import *

S = "Cancer"


def b09():
    c = Plate("water", 91, "2 of Lotuses, engraved: two lotuses opening on stalks that twine together out of still water, the star of Jupiter exalted shining between them, under the seal of Venus within the crab's claws",
              glow=(190, 150, 220))
    emblems(c, "lotus")
    c(hills(c, 262, [(50, 16), (150, 8), (320, 20)]))
    c(sea(c, top=262, rows=7))
    c(pad(80, 300, 26, 6), pad(304, 318, 30, 7), pad(46, 336, 22, 5), pad(336, 288, 18, 4))
    a = [(180, 322), (206, 292), (176, 262), (204, 228), (154, 190)]
    b = [(200, 322), (174, 292), (204, 262), (178, 228), (226, 190)]
    c(rope(smooth(a), c.p, 6, 3.6, ".6 2.4", fill=c.p["W"]), rope(smooth(b), c.p, 6, 3.6, ".6 2.4", fill=c.p["W"]))
    c('<path class="wash ink thin" d="M178 262C150 258 128 268 118 282C140 286 162 278 178 262Z"/><path class="ink hair" d="M176 264C156 268 138 276 124 282"/>',
      '<path class="wash ink thin" d="M204 246C230 240 252 248 262 262C240 268 218 262 204 246Z"/><path class="ink hair" d="M206 248C226 250 244 256 256 262"/>')
    c(ripples(190, 326, 44))
    c(use("lotus", 152, 192, 1.35, -16), use("lotus", 228, 192, 1.35, 16))
    c(star_mark(c, "Jupiter", 190, 136, 15))
    c('<path class="ink hair" stroke-dasharray="4 4" d="M150 344V356M230 344V356M190 340V356"/>')
    c(crown(c, S, "Venus"))
    return c


def b10():
    c = Plate("water", 92, "3 of Lotuses, engraved: three lotuses rising in flower from the treasure vase, its neck tied with scarves, set on a stone by the lake, under the seal of Mercury within the crab's claws",
              glow=(190, 160, 210))
    emblems(c, "lotus")
    c(sea(c, top=250, rows=5))
    c('<path class="wash ink heavy" d="M96 312H284L276 330H104Z"/><path class="hatchfill" d="M250 312H284L276 330H246Z"/><path class="ink hair" d="M100 320H280"/>')
    c(ground(c, 330, wob=3))
    c(vase(c))
    c(rope("M180 226C160 230 146 244 130 240C118 238 110 246 104 256", c.p, 6, 3.6, ".6 2.4", fill=c.p["T"]),
      rope("M200 226C220 230 234 244 250 240C262 238 270 246 276 256", c.p, 6, 3.6, ".6 2.4", fill=c.p["T"]))
    c(rope("M190 208C190 186 190 160 190 132M186 208C176 190 158 178 140 166M194 208C204 190 222 178 240 166", c.p, 5.4, 3.2, ".6 2.2"))
    c('<path class="wash ink thin" d="M188 190C168 180 154 186 146 198C164 204 178 200 188 190Z"/><path class="wash ink thin" d="M192 182C212 172 226 178 234 190C216 196 202 192 192 182Z"/>')
    c(use("lotus", 190, 134, 1.45), use("lotus", 140, 168, 1.15, -20), use("lotus", 240, 168, 1.15, 20))
    c(sparkle(106, 140, 6), sparkle(276, 136, 6), sparkle(84, 196, 4), sparkle(298, 200, 4))
    c(crown(c, S, "Mercury"))
    return c


def b11():
    c = Plate("water", 93, "4 of Lotuses, engraved: three lotuses resting open on the night pond, a fourth rising alone toward the full moon still a bud, under the seal of the Moon within the crab's claws",
              glow=(300, 150, 180), sky=236)
    emblems(c, "lotus")
    c(stars(c, 10, y0=100, y1=220, avoid=lambda x, y: math.hypot(x - 300, y - 150) < 50 or (120 < x < 260 and y < 110)))
    c(full_moon(c, 300, 150, 30))
    c(sea(c, top=236, rows=8))
    c('<path fill="none" stroke="#f8f9fb" stroke-width="3" stroke-dasharray="14 6" d="M282 246H318M276 262H324M286 278H314M280 294H320M290 310H310"/>')
    c('<path class="ink thin" d="M24 360C26 320 22 280 30 236M38 360C38 330 42 300 40 262M14 360C14 336 10 312 14 286"/>',
      '<path class="wash ink thin" d="M30 236C26 226 28 216 32 210C36 218 36 228 30 236ZM40 262C36 252 38 242 42 236C46 244 46 254 40 262Z"/>')
    for x, y in [(86, 280), (152, 300), (218, 284)]:
        c(pad(x, y + 6, 26, 6), use("lotus", x, y, 1.05), ripples(x, y + 12, 50, 2))
    c(rope("M300 340C300 310 292 260 300 214", c.p, 5.4, 3.2, ".6 2.2"), bud(300, 216, 1.2))
    c('<path class="wash ink thin" d="M298 300C278 296 266 304 262 314C280 318 292 312 298 300Z"/>', ripples(300, 342, 30, 2))
    c(crown(c, S, "Moon"))
    return c


def n09():
    c = Plate("water", 94, "2 of Cups, engraved: two cups set side by side on a carved bench beneath a bower of two birches, Gebo cut between them, under the seal of Venus within the crab's claws",
              glow=(190, 170, 200))
    emblems(c, "cup")
    c(hills(c, 270, [(70, 18), (300, 22)]))
    c(ground(c, 300))
    for side in (1, -1):
        x0 = 190 - side * 136
        c(f'<path class="light ink heavy" d="M{x0 - 7} 332C{x0 - 6} 260 {x0 - 3} 180 {x0 - 2} 104H{x0 + 3}C{x0 + 4} 180 {x0 + 6} 260 {x0 + 7} 332Z"/>')
        marks = "".join(f"M{f(x0 - 6 + (k % 2) * 3)} {f(320 - k * 15)}h{f(5 + (k % 3) * 2)}" for k in range(15))
        c(f'<path class="ink thin" d="{marks}"/>')
        boughs = f"M{x0} 150C{x0 + side * 40} 120 {x0 + side * 90} 112 {x0 + side * 128} 126M{x0} 196C{x0 + side * 34} 170 {x0 + side * 70} 168 {x0 + side * 96} 184M{x0} 124C{x0 + side * 20} 110 {x0 + side * 40} 104 {x0 + side * 60} 106"
        c(rope(boughs, c.p, 5, 2.8, ".6 2.2", fill=c.p["L"]))
        for t in (.25, .5, .75, 1):
            bx, by = x0 + side * 128 * t, 150 - 40 * math.sin(t * 2.6) + (t > .8) * 8
            c(leaves(c, bx, by + 10, 8, 26, 20, 160, (.5, .75)))
        for t in (.4, .8, 1):
            c(leaves(c, x0 + side * 96 * t, 190 - 26 * math.sin(t * 2.4) + 8, 6, 20, 20, 160, (.5, .7)))
    c('<path class="wash ink heavy" d="M96 266H284V278H96Z"/><path class="hatchfill" d="M96 272H284V278H96Z"/>',
      '<path class="wash ink heavy" d="M108 278H128L124 314H112ZM252 278H272L268 314H256Z"/>',
      '<path class="ink hair" d="M112 286C116 290 120 290 124 286M114 296C118 300 122 300 124 296M256 286C260 290 264 290 268 286M258 296C262 300 266 300 268 296"/>',
      '<path class="light ink thin" d="M170 280H210V312H170Z"/><path class="ink hair" d="M174 284H206V308H174Z"/>')
    c(rune("Gebo", 190, 296, 22, 2.2, cls="ink"))
    c(use("cup", 156, 236, 1.05, -4), use("cup", 224, 236, 1.05, 4))
    c(rope("M164 246C176 256 204 256 216 246", c.p, 5, 3, ".6 2.2", fill=c.p["T"]))
    c(crown(c, S, "Venus"))
    return c


def n10():
    c = Plate("water", 95, "3 of Cups, engraved: three cups raised together over the feast table, apples heaped and spilling, the sun-wheel of Fortune turning above, under the seal of Mercury within the crab's claws",
              glow=(190, 150, 210))
    emblems(c, "cup")
    c(sun_rays(c, 190, 150, 50, 140, 0, 350, 15, 3))
    c(sun_wheel(c, 190, 150, 44))
    c('<path class="wash ink heavy" d="M56 270H324V284H56Z"/><path class="hatchfill" d="M56 278H324V284H56Z"/>',
      '<path class="wash ink heavy" d="M84 284L70 340H82L98 284ZM296 284L310 340H298L282 284Z"/><path class="ink thin" d="M76 316H304"/>')
    c(ground(c, 330, wob=3))
    for x, y in [(88, 262), (100, 258), (112, 263), (94, 250), (106, 249), (272, 262), (286, 260), (280, 249), (300, 264)]:
        c(f'<circle cx="{x}" cy="{y}" r="7" class="tint ink thin"/><path class="ink hair" d="M{x - 3} {y - 3}a4 4 0 0 1 4 -2"/><path class="ink thin" d="M{x} {y - 7}l1 -4"/>')
    c('<circle cx="140" cy="336" r="7" class="tint ink thin"/><path class="wash ink hair" d="M140 329c3 -6 8 -6 10 -4c-3 4 -7 5 -10 4Z"/><circle cx="250" cy="344" r="7" class="tint ink thin"/><path class="ink thin" d="M250 337l1 -4"/>',
      '<path class="wash ink thin" d="M80 268C84 276 120 276 124 268ZM262 268C266 276 302 276 306 268Z"/>')
    c(use("cup", 140, 236, 1.05, -18), use("cup", 190, 216, 1.1), use("cup", 240, 236, 1.05, 18))
    c(sparkle(166, 196, 4), sparkle(214, 196, 4))
    c(crown(c, S, "Mercury"))
    return c


def n11():
    c = Plate("water", 96, "4 of Cups, engraved: three cups standing on the shore, a fourth borne in on a wave under the moon, offered and not yet taken, under the seal of the Moon within the crab's claws",
              glow=(300, 140, 170), sky=230)
    emblems(c, "cup")
    c(stars(c, 9, y0=100, y1=210, avoid=lambda x, y: math.hypot(x - 300, y - 140) < 46 or (120 < x < 260 and y < 110)))
    c(crescent(300, 140, 26, "light ink thin"))
    c(waves(c, 230, amp=8, length=44), waves(c, 256, amp=8, length=52, hatch=False))
    c('<path class="wash ink heavy" d="M206 268C232 258 258 224 296 222C334 224 358 256 384 266Z"/>',
      '<path fill="url(#hd)" d="M296 222C334 224 358 256 384 266H340C330 246 316 230 296 222Z"/>',
      '<path class="ink thin" d="M232 256c6 -8 14 -8 16 -2c-4 2 -8 1 -8 -2M340 248c6 -6 14 -4 14 2c-4 2 -8 0 -7 -3"/>',
      '<path class="ink hair" d="M240 262C256 250 272 236 290 232M300 232C320 236 336 250 350 262"/>')
    c(use("cup", 296, 198, .9), ripples(296, 224, 26, 1))
    c('<path class="wash ink heavy" d="M-20 300C60 290 130 300 200 322C250 336 300 346 400 344V380H-20Z"/>',
      '<path class="hatchfill" d="M-20 326C60 318 140 326 210 344C250 354 320 360 400 360V380H-20Z"/>',
      '<path class="ink hair" d="M10 314C50 310 90 314 120 320M140 330C170 334 196 340 220 346"/>')
    c(use("cup", 62, 278, .9), use("cup", 116, 286, .9), use("cup", 170, 298, .9))
    c(crown(c, S, "Moon"))
    return c


# ---------------------------------------------------------------- the voids
def v031():
    c = Plate("void", 131, "Puloman, engraved white on black: the fire on the altar that told the truth, the newborn's glance blazing out of the dark, and the thief burned to a heap of ash, the river running beneath",
              glow=(250, 140, 200), sky=304)
    c(stars(c, 12, y1=110, avoid=lambda x, y: math.hypot(x - 250, y - 130) < 60))
    c(sun_rays(c, 250, 130, 26, 110, 90, 200, 9, 3), sun_rays(c, 250, 130, 26, 60, 200, 450, 15, 3))
    c('<circle cx="250" cy="130" r="22" class="light ink heavy"/><circle cx="250" cy="130" r="14" class="tint ink thin"/><path class="ink thin" d="M240 130C244 124 256 124 260 130C256 136 244 136 240 130Z"/><circle cx="250" cy="130" r="3" class="fill-ink"/>')
    c('<path class="wash ink heavy" d="M60 304V270H160V304Z"/><path class="wash ink heavy" d="M72 270V252H148V270Z"/><path class="ink hair" d="M60 286H160M86 270V304M134 270V304M96 252V270M124 252V270"/>',
      flame(c, 110, 252, 70, 40), flame(c, 92, 252, 40, 20), flame(c, 128, 252, 46, 22))
    c('<path class="mid ink thin" d="M220 304C226 284 246 274 270 272C296 270 318 284 326 304Z"/><path fill="url(#hd)" d="M270 272C296 270 318 284 326 304H296C294 290 284 278 270 272Z"/>')
    for k in range(26):
        x = c.rng.uniform(232, 316); y = c.rng.uniform(150, 268)
        c(f'<circle cx="{f(x)}" cy="{f(y)}" r="{c.rng.choice([1, 1.4, 1.8])}" class="ink hair"/>')
    c('<path class="ink hair" d="M246 270C240 250 252 236 246 214M272 266C278 246 266 232 274 210M298 270C292 252 304 240 298 222"/>')
    c(river_beneath(c))
    return c


def v034():
    c = Plate("void", 134, "Viprachitti, engraved white on black: the lord of the Danavas, his crown left on a throne of rock at the floor of the sea, the eclipse his son would make burning above the waves, the river running beneath",
              glow=(190, 70, 160), sky=304)
    c(stars(c, 12, y1=130, avoid=lambda x, y: math.hypot(x - 190, y - 70) < 56))
    c(sun_rays(c, 190, 70, 30, 54, 0, 350, 12, 4))
    c('<circle cx="190" cy="70" r="30" class="light ink thin"/><circle cx="190" cy="70" r="26" class="plate ink thin"/><circle cx="190" cy="70" r="20" class="ink hair"/>')
    c(waves(c, 140, amp=8, length=40, cls="wash ink thin", hatch=False))
    c('<rect x="0" y="152" width="380" height="152" fill="url(#hx)" opacity=".4"/>')
    for x, y, r in [(120, 190, 2.4), (130, 170, 1.6), (262, 180, 2), (270, 210, 1.4), (190, 168, 1.6)]:
        c(f'<circle cx="{x}" cy="{y}" r="{r}" class="ink hair"/>')
    c('<path class="wash ink heavy" d="M108 304V262C108 254 114 250 120 250H136V214C136 206 142 202 150 202H230C238 202 244 206 244 214V250H260C266 250 272 254 272 262V304Z"/>',
      '<path fill="url(#hd)" d="M228 202H230C238 202 244 206 244 214V250H260C266 250 272 254 272 262V304H240V214C240 208 236 204 228 202Z"/>',
      '<path class="ink hair" d="M136 250H244M120 270H260M148 214V250M232 214V250M140 290L160 280M220 294L250 282"/>')
    c(crown_shape(190, 250, 62, 38, "tint ink thin"))
    c('<path class="wash ink thin" d="M60 304C56 290 64 282 60 268C68 278 70 290 72 304ZM312 304C316 288 308 278 314 264C320 276 322 290 320 304Z"/>')
    c(river_beneath(c))
    return c


def v036():
    c = Plate("void", 136, "Simhika, engraved white on black: claws rising from under the sea to seize the shadow of the one leaping over it toward the far shore of Lanka, the river running beneath",
              glow=(190, 120, 220), sky=304)
    c(stars(c, 14, y1=150))
    c('<path class="wash ink thin" d="M292 176L304 146L314 152L322 128L330 136L338 116L346 132L358 124L366 150L380 176Z"/><path class="ink hair" d="M314 152V176M330 136V176M346 132V176"/>')
    c('<path class="ink hair" d="M30 118C90 92 160 82 230 92C270 98 300 108 330 120" stroke-dasharray="3 5"/>')
    c(waves(c, 180, amp=7, length=36, cls="wash ink thin", hatch=False))
    c('<rect x="0" y="190" width="380" height="114" fill="url(#hx)" opacity=".5"/>')
    sh = "M112 196C132 186 160 184 186 188C208 184 234 186 252 192C262 186 272 188 278 194C266 196 260 200 252 202C232 206 206 206 186 204C160 208 134 206 112 196Z"
    c(f'<path class="plate ink thin" d="{sh}"/>', '<path class="plate ink thin" d="M114 196C96 190 84 180 88 168C92 158 106 160 106 170C106 176 100 178 98 174"/>',
      '<path class="ink hair" stroke-dasharray="2 3" d="M130 194H250"/>')
    c(claw(c, 146, 198, 106, 10, 4, 28, "tint ink thin", 40), claw(c, 236, 200, 104, -10, 4, 28, "tint ink thin", 40))
    c(river_beneath(c))
    return c


CARDS = {"b09": b09, "b10": b10, "b11": b11, "n09": n09, "n10": n10, "n11": n11, "v031": v031, "v034": v034, "v036": v036}
