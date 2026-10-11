"""Cut an engraving out of its paper, for the body diagram: only the ink is kept, as a
transparent PNG, so the figure sits straight on the page with no grey or yellow box.

    python tools/engraving.py scan.jpg static/look/anatomy.png [width]

Then set FIGURE w, h and the seven station points in lib/medical.json to fit the new image."""
import sys
from PIL import Image, ImageOps

def cut(src, dst, paper=None, ink=40, knee=18, width=None):
    g = ImageOps.grayscale(Image.open(src))
    if width and g.width > width: g = g.resize((width, round(g.height * width / g.width)), Image.LANCZOS)
    if paper is None:                                   # the paper's tone: the bright end of the scan
        hist = g.histogram(); total = sum(hist); seen = 0
        for v in range(255, -1, -1):
            seen += hist[v]
            if seen > total * 0.35: paper = v; break
    # darker than the paper becomes ink; the paper itself goes fully transparent
    # the knee drops the paper's own speckle, a little darker than its tone
    top = paper - knee
    alpha = g.point(lambda v: 0 if v >= top else min(255, int((top - v) * 255 / max(1, top - ink))))
    out = Image.new("RGBA", g.size, (24, 18, 14, 0)); out.putalpha(alpha)
    out.save(dst, optimize=True)
    print(f"{dst}: {g.size[0]}x{g.size[1]}, paper tone {paper}")

if __name__ == "__main__":
    cut(sys.argv[1], sys.argv[2], width=int(sys.argv[3]) if len(sys.argv) > 3 else None)
