"""Draw the site icon: a little window and a torus, in neon outline. One SVG, rendered to every size.

    python tools/icons.py

Writes static/icons/: icon.svg, favicon-32.png (bolder lines, for tabs), apple-touch-icon.png (180),
icon-192.png, icon-512.png and maskable-512.png (the window smaller, inside Android's safe zone).
Needs Playwright's Chromium (set CHROMIUM to its path if it isn't /opt/pw-browsers/chromium)."""
import os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "icons")

def svg(scale=1.0, small=False, bg=True):
    """The neon-outline window: a magenta frame with its title rule and three coloured dots, and a cyan torus inside.
    scale: how much of the square the window fills (the maskable icon wants it smaller). small: bolder lines for tabs."""
    w = 1.6 if small else 1.0; sd = 10 if small else 6
    t = f"translate({256 * (1 - scale)} {256 * (1 - scale)}) scale({scale})"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs><filter id="g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{sd}" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  {'<rect width="512" height="512" fill="#0b0322"/>' if bg else ''}
  <g transform="{t}">
    <g filter="url(#g)" fill="none">
      <rect x="60" y="72" width="392" height="368" rx="14" stroke="#ff4fd8" stroke-width="{12 * w}"/>
      <line x1="60" y1="130" x2="452" y2="130" stroke="#ff4fd8" stroke-width="{10 * w}"/>
      <ellipse cx="256" cy="292" rx="140" ry="74" stroke="#7ff6ff" stroke-width="{16 * w}"/>
      <ellipse cx="256" cy="282" rx="50" ry="17" stroke="#7ff6ff" stroke-width="{10 * w}"/>
    </g>
    <circle cx="334" cy="101" r="{9 * w}" fill="#22d3ee"/><circle cx="366" cy="101" r="{9 * w}" fill="#ffd400"/><circle cx="398" cy="101" r="{9 * w}" fill="#ff4fd8"/>
  </g>
</svg>'''

from playwright.sync_api import sync_playwright
SP = tempfile.mkdtemp()
jobs = [("icon.svg", svg(), None), ("favicon-32.png", svg(small=True), 32), ("apple-touch-icon.png", svg(), 180),
        ("icon-192.png", svg(), 192), ("icon-512.png", svg(), 512), ("maskable-512.png", svg(scale=.72), 512)]
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium"))
    for name, src, size in jobs:
        if size is None:
            open(os.path.join(OUT, name), "w").write(src); continue
        tmp = os.path.join(SP, name + ".svg"); open(tmp, "w").write(src)
        page = os.path.join(SP, name + ".html")
        open(page, "w").write(f'<html><body style="margin:0;background:#0b0322"><img src="{os.path.basename(tmp)}" width="{size}" height="{size}" style="display:block"></body></html>')
        pg = br.new_page(viewport={"width": size, "height": size}, device_scale_factor=1)
        pg.goto("file://" + page); pg.wait_for_timeout(400); pg.screenshot(path=os.path.join(OUT, name), clip={"x": 0, "y": 0, "width": size, "height": size}); pg.close()
    # a preview sheet: each size, plus the 32 drawn at 16 and as it sits in a tab
    pg = br.new_page(viewport={"width": 900, "height": 560})
    sheet = os.path.join(SP, "sheet.html"); open(sheet, "w").write(f'''<html><body style="margin:0;padding:20px;background:#fff;font:14px sans-serif;display:flex;gap:28px;align-items:end;flex-wrap:wrap">
      <figure><img src="file://{OUT}/icon-512.png" width="300"><figcaption>512</figcaption></figure>
      <figure><img src="file://{OUT}/maskable-512.png" width="160" style="border-radius:50%"><figcaption>Android, masked</figcaption></figure>
      <figure><img src="file://{OUT}/apple-touch-icon.png" width="90" style="border-radius:20px"><figcaption>iPhone</figcaption></figure>
      <figure><img src="file://{OUT}/favicon-32.png" width="32"><figcaption>tab 32</figcaption></figure>
      <figure><img src="file://{OUT}/favicon-32.png" width="16"><figcaption>16</figcaption></figure>
      <div style="display:flex;align-items:center;gap:8px;padding:8px 14px;background:#dee1e6;border-radius:8px 8px 0 0"><img src="file://{OUT}/favicon-32.png" width="16"> Your chart · The Wyrd Console</div>
    </body></html>'''); pg.goto("file://" + sheet)
    pg.wait_for_timeout(500); pg.screenshot(path=os.path.join(SP, "icons-sheet.png")); br.close()
print("icons written to", OUT, "; preview:", os.path.join(SP, "icons-sheet.png"))
