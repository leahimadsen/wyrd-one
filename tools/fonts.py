"""Copy the site's web fonts into static/fonts, so visitors' browsers never ask Google for them
(Google would see every visitor's IP address and the page they were on).

    python tools/fonts.py

Run it again after changing a font below, or after adding kanji or kana to the Sukuyō pages
(the Japanese font is cut down to exactly the characters the site uses; tests/privacy_check.py
fails if a page uses one the font doesn't have)."""
import glob, hashlib, json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "static", "fonts")
API = "https://fonts.googleapis.com/css2?"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"   # asks for woff2

FONTS = {
    "texturina": "family=Texturina:ital,opsz,wght@0,12..72,300;0,12..72,400;0,12..72,500;0,12..72,600;1,12..72,300;1,12..72,400&display=swap",
    "wyrd90": "family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC&family=Noto+Sans+Runic&family=UnifrakturMaguntia"
              "&family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@400;500;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap",
    "mandala": "family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC&family=Crimson+Pro:ital,wght@0,400;0,500;1,400"
               "&family=IBM+Plex+Mono:wght@400;500&display=swap",
}


def jp_chars():
    """Every kanji and kana in the Sukuyō words and code: all the Japanese the site can show."""
    found = set()
    for p in glob.glob(os.path.join(HERE, "lib", "*.json")) + glob.glob(os.path.join(HERE, "wyrd", "*.py")):
        found |= {c for c in open(p, encoding="utf-8").read() if "　" <= c <= "鿿"}
    return "".join(sorted(found))


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return r.read()


def build(name, query):
    css = get(API + query).decode()
    def local(m):
        data = get(m.group(1))
        fn = hashlib.sha1(data).hexdigest()[:16] + ".woff2"
        with open(os.path.join(OUT, fn), "wb") as f: f.write(data)
        return f"url(/static/fonts/{fn})"
    css = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", local, css)
    with open(os.path.join(OUT, name + ".css"), "w", encoding="utf-8") as f:
        f.write(f"/* {name}: made by tools/fonts.py from Google Fonts (SIL Open Font License); served from this site */\n" + css)
    print(f"{name}: {css.count('@font-face')} faces")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*")): os.remove(old)
    for name, query in FONTS.items(): build(name, query)
    chars = jp_chars()
    build("jp", "family=Noto+Serif+JP:wght@500;700&display=swap&text=" + urllib.parse.quote(chars))
    with open(os.path.join(OUT, "jp-chars.json"), "w", encoding="utf-8") as f: json.dump(chars, f, ensure_ascii=False)
    sys.exit(0)
