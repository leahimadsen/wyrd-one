"""The prologue: a silly, true story of how you came to be here, told before the reading.

Every line comes from lib/story.json (drafted for The Völva to rewrite) and the
Moon's shakti from corpus.json; this file only chooses which lines a chart calls
for. It is unnumbered, so the reading's own section numbers stay as they are."""
import html, json, math, os

from . import engine as E

S = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "story.json"), encoding="utf-8"))


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def opening(C, dasha, who, engine_rows, n=2):
    """The story's first paragraphs, as the free chart's taste of the reading."""
    import re
    return "".join(re.findall(r"<p>.*?</p>", tell(C, dasha, who, engine_rows))[:n])


def tell(C, dasha, who, engine_rows):
    """The prologue's HTML. engine_rows is corpus.json's ENGINE (one row per mansion)."""
    first = (who or "").strip().split(" ")[0]
    if first in ("A", "An", "The"): first = ""          # "A sample chart" isn't anyone's name
    named = fill(S["NAMED"], name=html.escape(first)) if first else ""
    seat = E.SIGNS[math.floor(E.norm(C["ascS"]) / 30)]
    e = engine_rows[E.nak_index(C["sid"]["Moon"])]
    ak = C["karaka"]["Atmakaraka"]

    born, last = C["jd"], S.get("UNTIL_AGE", 96)
    timing = []
    for i, m in enumerate(dasha["maha"]):
        age = max(0, int((m["to" if i == 0 else "from"] - born) / E.YEAR))
        if i and age > last: break
        key = "NEXT" if i else ("FIRST" if age else "FIRST_BRIEF")
        line = fill(S[key], visitor=S["VISITOR"][m["lord"]], age=age)
        timing.append(line + (S["NOW"] if m["now"] else ""))

    paras = [
        fill(S["OPENING"], named=named),
        S["SOUL_INTRO"] + " " + S["SOUL"][ak],
        fill(S["COSTUME_INTRO"], costume=S["COSTUME"][seat]) + (S["COSTUME_UNKNOWN"] if C.get("unknownTime") else ""),
        fill(S["GIFT"], mansion=e[0], shakti=e[2], shakti_name=e[1]),
        S["TIMING_INTRO"],
        " ".join(timing),
    ]
    body = "".join(f"<p>{p}</p>" for p in paras)
    return f"""<section class="rd-sec rd-story" id="s-story"><h2>{S["TITLE"]}</h2><div class="rd-sub">{S["SUB"]}</div>
      {body}<p class="rd-kenning">{S["CLOSING"]}</p></section>"""
