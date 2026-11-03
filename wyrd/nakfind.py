"""What is my nakshatra? A free finder at /nakshatra-calculator.

The landing page is written for search: people type "what is my nakshatra" far more often than they type the
name of any one mansion. The form posts, so birth details stay out of the address and the logs; the answer page
is noindex. Every line about a mansion comes from The Völva's corpus (NAKSHATRA, ENGINE), as the mansion pages do.

The rune of the Moon follows the Runes page and the shared card: two runes to a whole-sign house, counted from
the rising sign. It needs a birth time, so it is only given when the time is known."""
import html, json
from . import engine as E
from .pages import C, NAKS, RUNES, slug, _ld, _crumbs, ORD27

e = html.escape
ARC = 360 / 27
PATH = "/nakshatra-calculator"

FAQ = [
    ("What is my nakshatra?",
     "Your nakshatra, or birth star, is the lunar mansion the Moon was passing through when you were born. The sky is cut "
     "into twenty-seven mansions of 13°20′, and the Moon crosses one in about a day, so it changes far faster than your sign."),
    ("Do I need my birth time?",
     "For your rising nakshatra, yes. For your Moon's, it helps: the Moon changes mansion about once a day, so on some dates "
     "the answer turns at a particular hour. Without a time, the finder tells you if your birth date falls on one of those days, "
     "and when the change happened."),
    ("Is this sidereal or tropical?",
     "Sidereal, measured with the Lahiri ayanamsa, which is how Jyotish counts the nakshatras. The positions come from NASA's "
     "JPL ephemeris."),
    ("What are the Moon, rising and Sun nakshatras?",
     "The Moon's mansion is your birth star: the mind, the moods, and the planet whose period your life opened in. The rising "
     "nakshatra is the one coming up over the eastern horizon at birth, read for the body and how you meet the world. The Sun's "
     "is where your purpose and vitality sit."),
    ("What is a pada?",
     "Each nakshatra splits into four padas, or quarters, of 3°20′. Each pada falls in one sign of the navamsa, the ninefold "
     "chart, and works through one of the four aims of life."),
]


def form(err=""):
    return f"""<form class="pg-form nk-find" method="post" action="{PATH}" autocomplete="off">
<label>Date of birth <input type="date" name="date" required min="1850-01-01" max="2149-12-31"></label>
<label>Time of birth <input type="time" name="time" id="nkTime"></label>
<label class="tick"><input type="checkbox" name="unknown_time" value="1" id="nkUnknown"> I don't know my birth time</label>
<label class="f-place">Place of birth
  <input name="place" id="placeInput" placeholder="Start typing a town or city" required
         role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="placeList">
  <ul id="placeList" role="listbox" hidden></ul></label>
<input type="hidden" name="place_id"><input type="hidden" name="lat"><input type="hidden" name="lon">
<input type="hidden" name="tz"><input type="hidden" name="place_label"><input type="hidden" name="cc">
<button class="btn-cast" type="submit">Find my nakshatra</button>
<p class="err" id="nkErr" role="alert">{e(err)}</p></form>"""


FORM_SCRIPT = """<script src="/static/common.js"></script>
<script>
(() => {
  const f = document.querySelector(".nk-find"); if (!f) return;
  const err = document.getElementById("nkErr"), unk = document.getElementById("nkUnknown"), t = document.getElementById("nkTime");
  let place = null;
  const cal = WyrdCommon.calendarChoice(f.date);
  WyrdCommon.placeSearch(document.getElementById("placeInput"), document.getElementById("placeList"), p => { place = p; cal.place(p); });
  unk.addEventListener("change", () => { t.disabled = unk.checked; });
  f.addEventListener("submit", ev => {
    err.textContent = "";
    if (!f.date.value){ ev.preventDefault(); err.textContent = "Enter your date of birth."; return; }
    if (!unk.checked && !t.value){ ev.preventDefault(); err.textContent = "Enter your time of birth, or tick that you don't know it."; return; }
    if (!place){ ev.preventDefault(); err.textContent = "Choose your birthplace from the list as you type."; document.getElementById("placeInput").focus(); return; }
    for (const k of ["lat", "lon", "tz"]) f[k].value = place[k];
    f.place_id.value = place.id; f.place_label.value = place.label; f.cc.value = place.cc || "";
  });
})();
</script>"""


def landing(base, err=""):
    rows = "".join(f'<li><a href="/learn/nakshatras/{s}">{e(C["NAKSHATRA"][i][0])}</a> '
                   f'<span class="muted">· {e(C["NAKSHATRA"][i][2])} · ruled by {e(C["NAKSHATRA"][i][1])}</span></li>' for s, i in NAKS)
    faq = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in FAQ)
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="/learn#nakshatras">Nakshatras</a></p>
<h1>What is my nakshatra?</h1>
<p class="lede">Give the date, time and place of your birth and find your nakshatra: the lunar mansion your Moon was in, with its pada, its deity, its ruling planet and its question. Your rising and Sun nakshatras come with it. Free, no sign-up.</p>
<div class="cta">{form(err)}</div>
<p>In Jyotish the Moon's mansion is your birth star. It names the planet whose period your life opened in on the Vimshottari clock, and it is the first thing a Vedic astrologer looks at after the rising sign. This finder works in the sidereal zodiac with the Lahiri ayanamsa, from NASA's JPL ephemeris, the same engine as the full chart.</p>
<h2>The twenty-seven nakshatras</h2>
<ul class="terms">{rows}</ul>
<h2>Questions</h2>{faq}"""
    ld = (_crumbs(base, [("Learn", "/learn"), ("Find your nakshatra", PATH)])
          + _ld({"@context": "https://schema.org", "@graph": [
              {"@type": "WebApplication", "name": "Nakshatra calculator", "url": base + PATH, "applicationCategory": "LifestyleApplication",
               "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
               "creator": {"@type": "Person", "name": "The Völva"}},
              {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}))
    return ("What Is My Nakshatra? Free Nakshatra Calculator · The Wyrd Console",
            "Find your nakshatra free: the lunar mansion and pada of your Moon, with your rising and Sun nakshatras, their deities and "
            "rulers, from your birth date, time and place. Sidereal (Lahiri), by The Völva.",
            body, ld)


# ---------------- the answer ----------------
def _sid(eph, jd, body):
    return E.norm(eph.positions(jd)[body] - eph.ayanamsa(jd))


def where(lon):
    """(mansion index, pada 1-4) of a sidereal longitude."""
    lon = E.norm(lon)
    i = int(lon // ARC) % 27
    return i, int((lon - i * ARC) // (ARC / 4)) + 1


def day_segments(eph, body, local_to_jd):
    """For an unknown birth time: the mansions a body passes through over the local day, as
    [(mansion, from minute, to minute)]. On the live ephemeris every minute of the day is looked up in one
    batch; otherwise it goes hour by hour and then to the minute."""
    many = getattr(eph, "positions_many", None)
    if many:
        try:
            rows = many([local_to_jd(m) for m in range(24 * 60)], bodies=[body])
            mins = [where(p[body] - ay)[0] for p, ay in rows]
            seg, start = [], 0
            for m in range(1, 24 * 60):
                if mins[m] != mins[m - 1]: seg.append((mins[m - 1], start, m)); start = m
            return seg + [(mins[-1], start, 24 * 60)]
        except Exception:
            pass
    at = lambda m: where(_sid(eph, local_to_jd(m), body))[0]
    marks = list(range(0, 24 * 60, 60)) + [24 * 60 - 1]
    seg, start, cur = [], 0, at(0)
    for a, b in zip(marks, marks[1:]):
        if at(b) == cur: continue
        lo, hi = a, b                                  # the change lies in (lo, hi]; narrow it to the minute
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if at(mid) == cur: lo = mid
            else: hi = mid
        seg.append((cur, start, hi)); start, cur = hi, at(hi)
    seg.append((cur, start, 24 * 60))
    return seg


def clock(m):
    h, mi = divmod(m, 60)
    return f"{(h % 12) or 12}:{mi:02d} {'am' if h < 12 else 'pm'}"


def _mansion(i, pada=None, label=""):
    n, g = C["NAKSHATRA"][i], C["ENGINE"][i]
    s = slug(n[0])
    p = f", pada {pada}" if pada else ""
    return f"""<section class="nk-one"><h2>{e(label)} {e(n[0])}{p}</h2>
<p class="lede">{e(n[6])}</p>
<dl class="facts"><dt>Deity</dt><dd>{e(n[2])}</dd><dt>Ruling planet</dt><dd>{e(n[1])}</dd><dt>Symbol</dt><dd>{e(n[3])}</dd>
<dt>Place</dt><dd>The {ORD27[i]} of the twenty-seven mansions</dd></dl>
<p class="rd-ask"><i>{e(g[10])}</i></p>
<p><a href="/learn/nakshatras/{s}">Read {e(n[0])} in full →</a></p></section>"""


def answer(eph, birth, known_time, local_to_jd):
    """The answer page's body. `birth` is app.birth_from's dict; `local_to_jd(minute)` gives the Julian day of a
    local minute of the birth date, for when the time is unknown."""
    u = birth["ut"]
    jd = E.julian_day(u["y"], u["mo"], u["d"], u["h"])
    parts, notes = [], []
    if known_time:
        moon = _sid(eph, jd, "Moon")
        mi, mp = where(moon)
        parts.append(_mansion(mi, mp, "Your Moon is in"))
        ascT, _ = eph.angles(jd, birth["place"]["lat"], birth["place"]["lon"])
        ai, ap = where(E.norm(ascT - eph.ayanamsa(jd)))
        cusp = int(E.norm(ascT - eph.ayanamsa(jd)) // 30) * 30
        ri = int(E.norm(moon - cusp) // 15)
        r = RUNES[ri]
        parts.append(f"""<section class="nk-one"><h2>The rune of your Moon: <span aria-hidden="true">{r[1]}</span> {e(r[2])}</h2>
<p>Two runes sit in each house of the chart, counted from your rising sign. Your Moon lights {e(r[2])}, the {"opening" if r[5] == "ingress" else "closing"} rune of house {r[4]}: {e(r[3])}.</p>
<p><a href="/learn/runes/{r[0]}">Read {e(r[2])} →</a></p></section>""")
        parts.append(_mansion(ai, ap, "Your rising nakshatra is"))
        si, sp = where(_sid(eph, jd, "Sun"))
        parts.append(_mansion(si, sp, "Your Sun is in"))
    else:
        seg = day_segments(eph, "Moon", local_to_jd)
        if len(seg) == 1:
            parts.append(_mansion(seg[0][0], None, "Your Moon is in"))
            notes.append("The Moon stayed in this mansion all day on your birth date, so it is yours whatever the time. "
                         "Its pada, your rising nakshatra and the rune of your Moon need the time.")
        else:
            name = lambda i: C["NAKSHATRA"][i][0]
            when = [f"{name(i)} before {clock(b)}" if not a else f"{name(i)} from {clock(a)}" + (f" until {clock(b)}" if b < 1440 else "")
                    for i, a, b in seg]
            notes.append(f"The Moon changed mansion on your birth date ({'; '.join(when)}, local time), so your nakshatra depends on the hour. "
                         "Both are below; if you can find your time, the finder will say which.")
            for i, _, _ in seg: parts.append(_mansion(i, None, "Your Moon may be in"))
        sseg = day_segments(eph, "Sun", local_to_jd)
        parts.append(_mansion(sseg[0][0], None, "Your Sun is in") if len(sseg) == 1 else
                     "".join(_mansion(i, None, "Your Sun may be in") for i, _, _ in sseg))
    note = "".join(f'<p class="note-box">{e(x)}</p>' for x in notes)
    keep = {"date": f'{birth["y"]:04d}-{birth["mo"]:02d}-{birth["d"]:02d}', "time": f'{birth["hh"]:02d}:{birth["mi"]:02d}' if known_time else "12:00",
            "unknown_time": (not known_time) or None, "place_id": birth["place"].get("id"), "lat": birth["place"]["lat"], "lon": birth["place"]["lon"],
            "tz": birth["place"]["tz"], "place_label": birth["place"].get("label", "")}
    if birth.get("os"): keep.update(date=birth["os"], cal="J", cc=birth["place"].get("cc"))   # the full chart keeps the date as the record gives it
    body = f"""<p class="crumbs"><a href="/learn">Learn</a> › <a href="{PATH}">Find your nakshatra</a></p>
<h1>Your nakshatra</h1>
{note}{"".join(parts)}
<div class="cta"><p>Your nakshatra is one thread. Your free chart draws your card from the Wyrd deck, lights your runes, and walks you through your signs, your gates and your Path of Dharma, one layer at a time.</p>
<p><button class="btn-cast" type="button" id="nkOpen">Open my full chart</button></p><p class="err" id="nkErr" role="alert"></p>
<p><a href="{PATH}">Find another nakshatra</a></p></div>"""
    script = f"""<script src="/static/common.js"></script>
<script>
(() => {{
  const birth = {json.dumps({k: v for k, v in keep.items() if v is not None}).replace("<", "\\u003c")};
  const b = document.getElementById("nkOpen"), err = document.getElementById("nkErr");
  b.addEventListener("click", async () => {{
    b.disabled = true; b.textContent = "Casting…"; err.textContent = "";
    try {{
      const j = await WyrdCommon.cast(birth);
      if (!WyrdCommon.keep(birth, j)) throw new Error("Your browser blocked this page from keeping your chart. Allow site data and try again.");
      location.href = "/chart";
    }} catch (x) {{ err.textContent = x.message; b.disabled = false; b.textContent = "Open my full chart"; }}
  }});
}})();
</script>"""
    return body, script
