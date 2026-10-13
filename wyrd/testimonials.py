"""What people have said, from lib/testimonials.json, set out as cards on the pages that sell."""
import html, json, os

PATH = os.path.join(os.path.dirname(__file__), "..", "lib", "testimonials.json")


def load():
    try: return json.load(open(PATH, encoding="utf-8"))
    except (OSError, ValueError): return {"ITEMS": []}


def render(where):
    """The testimonials for one page, or nothing when there are none for it."""
    t = load()
    items = [i for i in t.get("ITEMS", []) if i.get("ok", True) and where in i.get("where", [where]) and i.get("quote")]
    if not items: return ""
    e = html.escape
    cards = "".join(f"""<figure class="tm-card"><span class="tm-mark" aria-hidden="true">“</span>
  <blockquote>{"".join(f"<p>{e(p)}</p>" for p in i["quote"].split(chr(10)) if p.strip())}</blockquote>
  <figcaption><b>{e(i.get("name", ""))}</b>{f' <span>· {e(i["about"])}</span>' if i.get("about") else ""}</figcaption></figure>""" for i in items)
    return f'<section class="tm" aria-label="{e(t.get("TITLE", "What people say"))}"><h2>{e(t.get("TITLE", "What people say"))}</h2><div class="tm-row">{cards}</div></section>'
