"""The free masterclass, How I Read the Wyrd Mandala: the Substack sign-up at /masterclass, and the guide.

The guide lives at /masterclass/<MASTERCLASS_PATH>, the link the Substack welcome email carries. Until that
path is set it lives at /masterclass/guide and the sign-up page links to it directly. Words are in
lib/masterclass.json; the worked stations' cards are the wheel's own (static/mandala.json)."""
import html, json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "lib", "masterclass.json"), encoding="utf-8"))
M = json.load(open(os.path.join(HERE, "static", "mandala.json"), encoding="utf-8"))
AYANAMSA_2026 = 24 + 13.5 / 60          # the wheel's own (static/mandala/wyrd-data.js FRAME)
e = html.escape


def cards_at(station):
    """The station's Buddhist card at its sidereal place and Nordic card at its tropical place, as the wheel lays them."""
    lo = (station - 1) * 10 / 3
    b = M["decans"][int((lo + 5 / 3) // 10) % 36]["buddhist"]
    n = M["decans"][int(((lo + 5 / 3 + AYANAMSA_2026) % 360) // 10) % 36]["nordic"]
    return {"buddhist": [b["minor"], b["trump"]], "nordic": [n["minor"], n["trump"]]}


def guide_slug(path):
    return path or "guide"


def _ps(xs): return "".join(f"<p>{e(x)}</p>" for x in xs)


def _steps(rows, cls="mc-steps"):
    return f'<ol class="{cls}">' + "".join(f"<li><b>{e(n)}.</b> {e(t)}</li>" for n, t in rows) + "</ol>"


def _lesson(L):
    out = [f'<section class="mc-lesson" id="{e(L["id"])}"><h2>{e(L["title"])}</h2>', _ps(L.get("paras", []))]
    if "steps" in L: out.append(_steps(L["steps"]))
    if "items" in L: out.append('<dl class="mc-wrong">' + "".join(f"<dt>{e(n)}</dt><dd>{e(t)}</dd>" for n, t in L["items"]) + "</dl>")
    if "blanks" in L: out.append('<ol class="mc-blanks">' + "".join(f"<li>{e(b)}</li>" for b in L["blanks"]) + "</ol>")
    return "".join(out) + "</section>"


def _worked(W):
    p = M["padas"][W["station"] - 1]
    c = W["cards"]
    head = (f'<p class="mc-record">{e(p["nak"])}, pada {p["pada"]} · Buddhist: {e(c["buddhist"][0])} under {e(c["buddhist"][1])} · '
            f'Nordic: {e(c["nordic"][0])} under {e(c["nordic"][1])}{" · Asura void: " + e(p["void"]) if p["void"] else ""}</p>')
    return f'<section class="mc-worked"><h3>{e(W["title"])}</h3>{head}{_steps(W["steps"])}</section>'


def contents():
    """The lessons in the order the guide gives them: the worked stations follow the method."""
    order = [L["title"] for L in T["LESSONS"]]
    order.insert(4, "Two stations, read all the way through")
    return order


def landing_page(base, substack, path):
    L = T["LANDING"]
    inside = "".join(f"<li>{e(t)}</li>" for t in contents())
    direct = "" if path else f'<p><a class="btn-cast" href="/masterclass/{guide_slug(path)}">{e(L["OPEN_NOW"])}</a></p>'
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> · <a href="/learn/mandala">The Wyrd Mandala</a></p>
<p class="eyebrow">{e(T["SUB"])}</p>
<h1>{e(T["TITLE"])}</h1>
<p class="lede">{e(L["LEDE"])}</p>
<p>{e(L["INSIDE_INTRO"])}</p>
<ol class="mc-inside">{inside}</ol>
<div class="cta mc-form" id="subscribe">
<p>{e(L["FORM_INTRO"])}</p>
<iframe src="{e(substack)}/embed" title="Subscribe to The Web of Wyrd on Substack" width="480" height="150" loading="lazy" frameborder="0" scrolling="no"></iframe>
<p><a class="btn-buy mc-sub" href="{e(substack)}/subscribe" target="_blank" rel="noopener">{e(T["SUBSCRIBE"])}</a></p>
<p class="muted">{e(L["FORM_AFTER"]).replace("{contact}", '<a href="/contact">the contact page</a>')}</p>
</div>
{direct}
<p>{e(L["WHY"])}</p>"""
    desc = ("A free masterclass by The Völva: how to read the Wyrd Mandala one station at a time, from the inside out, "
            "with two stations read all the way through and a worksheet for your own Moon. Free with The Web of Wyrd on Substack.")
    ld = ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Course", "name": T["TITLE"],
          "description": desc, "isAccessibleForFree": True, "provider": {"@type": "Person", "name": "The Völva"},
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}, ensure_ascii=False) + "</script>")
    return f'{T["TITLE"]}: a Free Masterclass · The Wyrd Console', desc, body, ld


def guide_page(substack):
    lessons = T["LESSONS"]
    worked = (f'<section class="mc-lesson" id="worked"><h2>Two stations, read all the way through</h2><p>{e(T["WORKED_INTRO"])}</p>'
              + "".join(_worked(W) for W in T["WORKED"]) + "</section>")
    C = T["CLOSE"]
    links = " · ".join(f'<a href="{e(u)}">{e(n)}</a>' for n, u in C["LINKS"])
    toc = "".join(f'<li><a href="#{e(i)}">{e(t)}</a></li>' for i, t in zip([L["id"] for L in lessons[:4]] + ["worked"] + [L["id"] for L in lessons[4:]], contents()))
    # the printed guide is a manuscript: parchment on every page, the knotwork in its corners, the emblem on the cover
    body = f"""<div class="mc-guide"><div class="mc-page" aria-hidden="true"><i class="mc-knot-tr"></i><i class="mc-knot-bl"></i></div>
<header class="mc-cover"><img class="mc-emblem" src="/static/look/emblem.png" alt="" width="237" height="240">
<p class="eyebrow">{e(T["SUB"])}</p>
<h1>{e(T["TITLE"])}</h1>
<p class="mc-by">The Völva · The Web of Wyrd</p></header>
<p class="mc-print-row"><button class="btn-cast mc-print" type="button" onclick="window.print()">{e(T["PRINT"])}</button> <span class="muted">{e(T["PRINT_NOTE"])}</span></p>
<nav class="mc-toc" aria-label="Contents"><ol>{toc}</ol></nav>
{"".join(_lesson(L) for L in lessons[:4])}
{worked}
{"".join(_lesson(L) for L in lessons[4:])}
<section class="mc-lesson" id="close"><h2>{e(C["TITLE"])}</h2>{_ps(C["PARAS"])}<p class="mc-links"><a class="btn-buy mc-sub" href="{e(substack)}/subscribe" target="_blank" rel="noopener">{e(T["SUBSCRIBE"])}</a></p><p class="mc-links">{links}</p></section>
<p class="mc-sign"><img src="/static/look/emblem.png" alt="" width="64" height="65"><br>The Völva · <a href="{e(substack)}">The Web of Wyrd</a></p></div>"""
    return f'{T["TITLE"]} · The Wyrd Console', T["SUB"] + ": " + T["TITLE"], body
