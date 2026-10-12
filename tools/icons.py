"""Draw the site icon: a little 90s window with a neon torus inside. One SVG, rendered to every size.

    python tools/icons.py

Writes static/icons/: icon.svg, favicon-32.png (bolder lines, for tabs), apple-touch-icon.png (180),
icon-192.png, icon-512.png and maskable-512.png (the window smaller, inside Android's safe zone).
Needs Playwright's Chromium (set CHROMIUM to its path if it isn't /opt/pw-browsers/chromium)."""
import os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "icons")

def svg(scale=1.0, small=False, bg=True):
    """scale: how much of the square the window fills (the maskable icon wants it smaller). small: bolder lines for 16-32px."""
    w = 512 * scale; x0 = (512 - w) / 2; y0 = x0 + (6 if scale < 1 else 0)
    k = w / 512                                    # everything below is drawn in a 512 window, then scaled
    sw = 1.8 if small else 1.0                     # line weight multiplier for tiny sizes
    grid = "" if small else "".join(f'<line x1="{x}" y1="112" x2="{x}" y2="470" stroke="#7ff6ff" stroke-opacity=".10" stroke-width="2"/>' for x in range(64, 470, 40)) + \
                             "".join(f'<line x1="42" y1="{y}" x2="470" y2="{y}" stroke="#7ff6ff" stroke-opacity=".10" stroke-width="2"/>' for y in range(140, 470, 40))
    meridians = "" if small else "".join(
        f'<path d="M{256 + dx} {232 + abs(dx) * .1} q{dx * .08} 70 {dx * .02} 128" fill="none" stroke="#ff7ae0" stroke-width="3" stroke-opacity=".7" filter="url(#glow)"/>'
        for dx in (-150, -95, -40, 40, 95, 150))
    btns = "" if small else "".join(f'<rect x="{x}" y="42" width="34" height="30" fill="#d9d4f5" stroke="#fff" stroke-width="3"/>' for x in (366, 406, 446))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#ff2a2a"/><stop offset=".18" stop-color="#ff7a00"/><stop offset=".34" stop-color="#ffd400"/>
      <stop offset=".5" stop-color="#22c55e"/><stop offset=".66" stop-color="#22d3ee"/><stop offset=".82" stop-color="#5b4bff"/><stop offset="1" stop-color="#ff2fa8"/></linearGradient>
    <linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="#ff2fa8"/><stop offset=".33" stop-color="#ffd400"/><stop offset=".66" stop-color="#22d3ee"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient>
    <radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6d8"/><stop offset=".45" stop-color="#ffb43a"/><stop offset="1" stop-color="#ffb43a" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{6 * sw}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  {'<rect width="512" height="512" rx="0" fill="#0b0322"/>' if bg else ''}
  <g transform="translate({x0} {y0}) scale({k})">
    <!-- the window: a bevelled frame, a rainbow title bar, the three buttons -->
    <rect x="16" y="16" width="480" height="480" fill="#120533"/>
    <path d="M16 496 V16 H496" fill="none" stroke="#e9e4ff" stroke-width="{12 * (1.3 if small else 1)}"/>
    <path d="M16 496 H496 V16" fill="none" stroke="#2a1170" stroke-width="{12 * (1.3 if small else 1)}"/>
    <rect x="30" y="30" width="452" height="{62 if not small else 78}" fill="url(#bar)"/>
    {btns}
    <rect x="34" y="{104 if not small else 120}" width="444" height="{372 if not small else 356}" fill="#05011a" stroke="#6b5bd6" stroke-width="4"/>
    {grid}
    <!-- the torus, in neon: the outer ring in rainbow, the hole and the tube's far edge in cyan -->
    <ellipse cx="256" cy="296" rx="186" ry="{96 if not small else 104}" fill="none" stroke="url(#ring)" stroke-width="{14 * sw}" filter="url(#glow)"/>
    <ellipse cx="256" cy="{280 if not small else 284}" rx="{74 if not small else 70}" ry="{26 if not small else 28}" fill="#05011a" stroke="#7ff6ff" stroke-width="{10 * sw}" filter="url(#glow)"/>
    {'' if small else '<path d="M86 300 Q256 400 426 300" fill="none" stroke="#7ff6ff" stroke-width="5" stroke-opacity=".75" filter="url(#glow)"/>'}
    {meridians}
    <circle cx="256" cy="{278 if not small else 282}" r="{20 if not small else 24}" fill="url(#core)"/>
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
