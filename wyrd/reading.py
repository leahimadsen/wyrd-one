"""
The paid reading, assembled in story order from The Völva's own register.
Every interpretive sentence comes from corpus.json; this file only chooses
which passages a chart calls for and lays them out.

  Prologue         a silly story of how you got here (wyrd/story.py, lib/story.json)
  I    The Seat            rising sign and mansion: frame, bearing, features
  II   The Engine          the Moon's mansion, worked in full
  III  The Matrix          Saturn as the builder of your reality, and the world seen from the Moon
  IV   The Planets         every planet: sidereal (karma, reality) and tropical (experience)
  V    The Soul-Planet     the Atmakaraka and its cabinet of seven
  VI   The Runes           the runes the chart lights, ranked, and the periods that wake them
  VII  The Work            personality and design Suns and Earths, from the register
  VIII The Body            centres, channels, and the mansions and padas that feed them
  IX   The Body's Old Map  medical astrology: signs, houses, mansions and planets on the body (wyrd/medical.py)
  X    Where You Thrive    culture, places and work
  XI   The Dharma Weave    the Pentagram Cross, the band, the dharma Suns
  XII  The Path of Dharma  Mission, Illuminations, the Diamond
  XIII The Clock           the periods running now, and the whole life by period
  XIV  The Numbers         life path, birthday, personal year, and the name's numbers, each on two planets
  XV   The Questions       every question the chart asked, gathered

Sections refer to each other by name ({{SEC:The Work}}); the numbers are filled in last.

The planets, runes, body and thriving sections draw on lib/register_ext.json too.
"""
import html, json, math, os
from datetime import datetime, timedelta

from . import engine as E
from . import vargas as VG
from . import rave as RV
from . import reading_more as MORE
from . import story as STORY
from . import reading_numbers as NUMBERS
from . import medical as MEDICAL

CORPUS = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "corpus.json"), encoding="utf-8"))
REG, ENG, NAKS, DEEP = CORPUS["REGISTER"], CORPUS["ENGINE"], CORPUS["NAKSHATRA"], CORPUS["NAK_DEEP"]
FRAME, HOUSES, SPHERES, WALK = CORPUS["SIGN_FRAME"], CORPUS["HOUSES"], CORPUS["SPHERES"], CORPUS["SPHERE_WALK"]
GATE_NAME, KGLOSS, SEQ = CORPUS["GATE_NAME"], CORPUS["KARAKA_GLOSS"], CORPUS["SEQUENCE"]

GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃",
         "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇", "Rahu": "☊", "Ketu": "☋", "Earth": "⊕"}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"]

esc = html.escape

FROM_BIRTH = {"Crucible"}      # by decision: the Crucible is open at birth, whatever its lord

def activation(gate, line, chart, dasha, sphere=None):
    """When a step of the path opens, by this person's own Vimshottari.
    The sphere's gate and line sit in a mansion (the register's gate -> mansion link);
    that mansion's Vimshottari lord rules the sphere, and the step opens when that
    lord's mahadasha arrives in this life."""
    if sphere in FROM_BIRTH:
        return {"lord": None, "state": "open", "text": "Open from birth"}
    m = E.gate_mansion(gate, line)
    if not m: return None
    lord = E.DASHA[m["primary"] % 9][0]
    row = next((r for r in dasha["maha"] if r["lord"] == lord), None)
    if not row: return None
    born = row.get("partial") or row["from"] <= chart["jd"]
    age = 0 if born else int((row["from"] - chart["jd"]) / E.YEAR)
    when = "from birth" if born else f"at {age} ({jd_date(row['from'])[-4:]})"
    state = "running now" if row["now"] else ("open" if row["past"] or born else "ahead")
    maha = f"your {lord} mahadasha"
    if state == "ahead":
        text = f"Opens {when} in {maha}"
    elif born:
        text = f"Open from birth, in {maha}" + (f", running now until {jd_date(row['to'])[-4:]}" if row["now"] else "")
    else:
        text = f"Opened {when} in {maha}" + (f", running now until {jd_date(row['to'])[-4:]}" if row["now"] else "")
    return {"lord": lord, "state": state, "text": text}

def fmt_lon(l):
    l = E.norm(l); d = l % 30; m = round((d - math.floor(d)) * 60)
    dd = math.floor(d)
    if m == 60: dd, m = dd + 1, 0
    return f"{E.sign_of(l)} {dd}°{m:02d}′"

def pada(l):
    return math.floor((E.norm(l) % E.NAK_ARC) / (E.NAK_ARC / 4)) + 1

def jd_date(jd):
    return (datetime(2000, 1, 1, 12) + timedelta(days=jd - 2451545.0)).strftime("%b %Y")

def anchor(title):
    import re
    return "s-" + re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", title).lower()).strip("-")

def contents(body):
    """The reading's contents, from its own headings: the story first, then each numbered section.
    A small button at the side of the page brings the list back from anywhere."""
    import re
    items = []
    for sid, num, title in re.findall(r'<section class="rd-sec[^"]*" id="([^"]+)">\s*(?:<div class="rd-num">([^<]*)</div>)?\s*<h2>(.*?)</h2>', body):
        items.append(f'<li><a href="#{sid}">{f"<span>{num}</span> " if num else ""}{title}</a></li>')
    return (f'<nav class="rd-toc" id="contents" aria-label="Contents"><h2>Contents</h2><ol>{"".join(items)}</ol></nav>'
            '<a class="rd-totop" href="#contents" aria-label="Back to the contents">Contents ↑</a>')

def section(n, title, sub, body):
    return f"""<section class="rd-sec" id="{anchor(title)}"><div class="rd-num">{{{{N}}}}</div>
      <h2>{title}</h2><div class="rd-sub">{sub}</div>{body}</section>"""

def pair(k, v):
    return f'<div class="rd-pair"><em>{k}</em><span>{v}</span></div>'

def register_entry(gate, line, side, label, asks):
    R = REG.get(str(gate))
    if not R:
        return f"<p>Gate {gate}.{line}</p>"
    m = E.gate_mansion(gate, line)
    design = side == "design"
    flags = ""
    if R.get("janus"):
        flags += '<span class="rd-flag">⟡ janus — two engines' + (", and this line is the seam" if m and m["seam"] else "") + "</span>"
    if R.get("gandanta"):
        flags += '<span class="rd-flag gand">⟁ gandanta — read gently</span>'
    asks.append((f"{label} · gate {gate}.{line}", R["a"], design))
    held = ('<div class="rd-held">The question is held — design-side runs unnamed until it is spoken. '
            'It waits for you at the end.</div>') if design else f'<div class="rd-ask">{R["a"]}</div>'
    return f"""<div class="rd-entry">
      <h3>{esc(label)} · {gate}.{line} · {R['t']}
        <span class="rd-side {'d' if design else 'p'}">{'design · unconscious' if design else 'personality · conscious'}</span></h3>
      <div class="rd-hdr">{R['h']} {flags}</div>
      <p>{R['e']}</p>
      <div class="rd-gifts"><div class="light"><h5>Light gift</h5><p>{R['l']}</p></div>
        <div class="dark"><h5>Dark gift</h5><p>{R['d']}</p></div></div>
      <div class="rd-repair"><h5>Distortion &amp; repair</h5><p>{R['r']}</p></div>
      {held}</div>"""

def dharma_defines(N, Dh):
    """What the dharma rave completes, beside the birth rave: channels and centres, named from the register."""
    live_d, cen_d = RV.defines(Dh)
    live_n, cen_n = RV.defines(N)
    title = lambda g: REG.get(str(g), {}).get("t", GATE_NAME.get(str(g), ""))
    rows = "".join(f"<tr{' class=hi' if c in live_n else ''}><td>{c[0]}–{c[1]}</td><td>{title(c[0])} · {title(c[1])}</td>"
                   f"<td>{'also at birth' if c in live_n else 'dharma only'}</td></tr>" for c in live_d)
    newly = [c for c in cen_d if c not in cen_n]
    lost = [c for c in cen_n if c not in cen_d]
    return f"""<h3 class="rd-tier">What the dharma defines</h3>
      {pair("Dharma centres", ", ".join(cen_d) or "none — every centre open")}
      {pair("Birth centres", ", ".join(cen_n) or "none — every centre open")}
      {pair("Opened by the dharma", ", ".join(newly) or "nothing the Birth Design leaves open")}
      {pair("Released by the dharma", ", ".join(lost) or "nothing the Birth Design defines")}
      {f'<div class="rd-tw"><table><tr><th>Channel</th><th>Its two gates</th><th></th></tr>{rows}</table></div>' if rows else
       '<p>The Dharma Design completes no channel: it works through single gates, each one open-ended.</p>'}"""

def dharma_table(N, Dh):
    """Every body, birth beside dharma, with the register's name for each dharma gate."""
    order = ["Sun", "Earth", "Moon", "Rahu", "Ketu", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    title = lambda g: REG.get(str(g), {}).get("t", GATE_NAME.get(str(g), ""))
    rows = []
    for b in order:
        for side, lab in (("personality", ""), ("design", "design ")):
            a, d = N[side].get(b), Dh[side].get(b)
            if not (a and d): continue
            same = a["gate"] == d["gate"]
            rows.append(f"<tr{' class=hi' if same else ''}><td>{GLYPH.get(b, '')} {lab}{b}</td><td>{a['gate']}.{a['line']}</td>"
                        f"<td>{d['gate']}.{d['line']} {title(d['gate'])}</td><td>{'repeats' if same else ''}</td></tr>")
    return f"""<h3 class="rd-tier">The whole weave</h3>
      <p>Every body at birth and in the dharma. Where a gate repeats, the repetition is load-bearing.</p>
      <div class="rd-tw"><table><tr><th>Body</th><th>Birth</th><th>Dharma</th><th></th></tr>{''.join(rows)}</table></div>"""

def build(chart, dasha, who):
    C = chart
    asks = []
    out = []

    # ---------- I · the Seat ----------
    asc = C["ascS"]; si = math.floor(E.norm(asc) / 30); nk = E.nak_index(asc); D = DEEP[nk]
    h1 = HOUSES[0]; half = "ingress" if E.deg_in(asc) < 15 else "egress"; rune = h1[half]
    d9 = math.floor(E.norm(9 * asc) / 30)
    unknown = bool(C.get("unknownTime"))
    out.append(section(0, "The Seat", f"{fmt_lon(asc)} {'Sun, read as the Seat' if unknown else 'rising'} · {D[0]} pada {pada(asc)}", f"""
      {'<p class="rd-note">Your birth time is unknown, so the rising sign can’t be known. As on your free chart, the houses are counted from your Sun’s sign (solar houses), and the Seat is read from your Sun. Your Moon may have stood in a neighbouring mansion: ' + ' or '.join(C.get("moonSpan") or []) + '.</p>' if unknown else ''}
      <p><b>{FRAME[si][0]}</b> {'as your Seat' if unknown else 'rising'} gives {FRAME[si][1]}</p>
      {MORE.rising(C)}
      <div class="rd-body"><h5>Bearing</h5><p>{D[10]}</p></div>
      <div class="rd-body"><h5>Features</h5><p>{D[11]}</p></div>
      {pair("The house of arrival", f'<span class="sw" style="background:{h1["hex"]}"></span>{h1["color"]} · {h1["phase"]}')}
      {pair("The rune at the gate", f'{rune[0]} {rune[1]} — {rune[2]}')}
      {pair("Matures toward", f"{E.SIGNS[d9]} — {FRAME[d9][1]}")}
      <p class="rd-note">Read this as tendencies the chart leans on. Genetics, health, work and era all outweigh it.</p>"""))

    # ---------- II · the Engine of the mind ----------
    mi = E.nak_index(C["sid"]["Moon"]); e = ENG[mi]; nkm = NAKS[mi]; Dm = DEEP[mi]
    asks.append((f"The Moon in {e[0]}", e[10], False))
    out.append(section(1, "The Engine", f"☽ Moon in {e[0]} · {fmt_lon(C['sid']['Moon'])} · pada {pada(C['sid']['Moon'])}", f"""
      <p class="rd-kenning">A keyword says what a placement is about; an engine says what it does, what its two
      moving parts are, and therefore exactly where it breaks.</p>
      {pair("Shakti", f"{e[1]} — {e[2]}")}
      <div class="rd-triad"><div><span>Above</span><em>{e[3]}</em></div>
        <div><span>Below</span><em>{e[4]}</em></div><div><span>Result</span><em>{e[5]}</em></div></div>
      <p>{e[6]}</p>
      <div class="rd-gifts"><div class="light"><h5>Light wield</h5><p>{e[7]}</p></div>
        <div class="dark"><h5>Dark wield</h5><p>{e[8]}</p></div></div>
      <div class="rd-repair"><h5>Distortion</h5><p>{e[9]}</p></div>
      {pair("Lord · deity · symbol", f"{nkm[1]} · {nkm[2]} · {nkm[3]}")}
      {pair("Does well", Dm[12])}{pair("Goes wrong", Dm[13])}
      {MORE.engine_more(C, dasha)}
      <div class="rd-ask">{e[10]}</div>"""))

    # ---------- the Matrix ----------
    out.append(section(0, "The Matrix", f"♄ Saturn in {E.SIGNS[math.floor(E.norm(C['sid']['Saturn']) / 30)]} · the world you live within", MORE.matrix(C, dasha)))

    # ---------- the planets, both zodiacs ----------
    out.append(section(0, "The Planets", "every planet, among the stars and in the seasons", MORE.planets(C)))

    # ---------- III · the soul-planet ----------
    K = C["karaka"]; ak = K["Atmakaraka"]; l = C["sid"][ak]
    stations = [(1, "the body"), (9, "the dharma"), (10, "the public"), (12, "the ancestral"), (60, "the sum of karmas")]
    naks = [NAKS[E.nak_index(E.norm(n * l))][0] for n, _ in stations]
    rep = sorted({x for i, x in enumerate(naks) if naks.index(x) != i})
    KT = C.get("karakaT") or E.karakas(C["trop"])
    rows = "".join(f"<tr{' class=hi' if k == 'Atmakaraka' else ''}><td>{k.replace('karaka', '')}</td>"
                   f"<td>{GLYPH[b]} {b}</td><td>{E.deg_in(C['sid'][b]):.2f}°</td>"
                   f"<td>{GLYPH[KT[k]]} {KT[k]} <small>{E.deg_in(C['trop'][KT[k]]):.2f}°</small></td><td>{KGLOSS[k]}</td></tr>"
                   for k, b in K.items())
    akT, moved, th = KT["Atmakaraka"], sum(K[k] != KT[k] for k in K), MORE.the
    tropical = (f"If you rank the planets in the tropical zodiac instead, which follows the seasons rather than the stars, the same planet comes out on top. "
                f"{th(ak)[0].upper() + th(ak)[1:]} is your soul-planet either way, so what you came here to do and how it feels to you line up." if akT == ak else
                f"If you rank the planets in the tropical zodiac instead, which follows the seasons rather than the stars, the order changes and <b>{th(akT)}</b> comes out on top. "
                f"This reading uses the sidereal order, where {th(ak)} is your soul-planet. {th(akT)[0].upper() + th(akT)[1:]} shows how that purpose feels to you from the inside, "
                f"the planet your life experiences as most its own.")
    tropical += ("" if not moved else " Every one of the seven places is different between the two zodiacs." if moved == 7 else
                 f" {['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six'][moved]} of the seven places {'is' if moved == 1 else 'are'} different between the two zodiacs.")
    out.append(section(2, "The Soul-Planet", f"Atmakaraka {GLYPH[ak]} {ak} · {fmt_lon(l)} · {E.nak_of(l)}", f"""
      <p>{KGLOSS['Atmakaraka']}</p>
      <p class="rd-kenning">{CORPUS['KARAKA_METHOD']}</p>
      <div class="rd-tw"><table><tr><th>Karaka</th><th>Sidereal</th><th>Degree</th><th>Tropical</th><th>Reads</th></tr>{rows}</table></div>
      <p class="rd-kenning">{tropical}</p>
      {pair(f"{ak} across the divisions", " · ".join(f"D{n} {naks[i]}" for i, (n, _) in enumerate(stations)))}
      {f'<p class="rd-kenning"><b>{", ".join(rep)}</b> repeats across divisions. A soul-planet that repeats a star, a house, or a rune is repeating the life\'s keynote.</p>' if rep else ''}      {MORE.karakas_more(C, dasha, asks)}"""))

    # ---------- the runes ----------
    out.append(section(0, "The Runes", "which runes your chart lights, and when they wake", MORE.runes(C, dasha)))

    # ---------- IV · the work ----------
    N = C["natal"]
    work = "".join([
        register_entry(N["personality"]["Sun"]["gate"], N["personality"]["Sun"]["line"], "personality", "Personality Sun", asks),
        register_entry(N["personality"]["Earth"]["gate"], N["personality"]["Earth"]["line"], "personality", "Personality Earth", asks),
        register_entry(N["design"]["Sun"]["gate"], N["design"]["Sun"]["line"], "design", "Design Sun", asks),
        register_entry(N["design"]["Earth"]["gate"], N["design"]["Earth"]["line"], "design", "Design Earth", asks)])
    out.append(section(3, "The Work", f"profile {N['profile']} · the equipment as issued", f"""
      <p class="rd-kenning">Personality is what you know you carry. Design runs underneath, and a design-side
      activation stays in distortion until it is named. So the design entries open on the engine and keep their
      question for the end.</p>{work}"""))

    # ---------- the body ----------
    out.append(section(0, "The Body", "your centres and channels, and the mansions that feed them", MORE.body(C)))
    out.append(section(0, MEDICAL.T["TITLE"], MEDICAL.T["SUB"], MEDICAL.body(C, dasha, asks)))
    out.append(section(0, "Where You Thrive", "culture, places and work", MORE.thrive(C)))

    # ---------- V · the dharma weave ----------
    Dh = C["dharma"]
    band = ("6/1 — the magenta point, the Mauve Zone's exact centre" if Dh["mauve"] else
            "inside the Mauve Zone — a pairing impossible at birth" if Dh["band"] == "Seam" else
            "an echo — a shape others are born holding, earned here")
    dps, dds = Dh["personality"]["Sun"], Dh["design"]["Sun"]
    repeats = [lab for lab, a, b in [("the Sun", dps, N["personality"]["Sun"]), ("the design Sun", dds, N["design"]["Sun"])]
               if a["gate"] == b["gate"]]
    out.append(section(4, "The Dharma Weave", f"dharma profile {Dh['profile']} · {Dh['band']}", f"""
      <p class="rd-kenning">Both Suns pass through the multiply-by-nine of the navamsa, so the 88° between them
      multiplies too: 792, less two full circles, leaves exactly 72. Every dharma chart ever cast carries its two
      Suns one fifth of the wheel apart. That is the Pentagram Cross.</p>
      {pair("Dharma profile", f"{Dh['profile']} · {Dh['band']}")}{pair("Band", band)}
      {pair("Birth Design profile", f"{N['profile']} · the equipment as issued")}
      {pair("The law", f"{Dh['suns']['gap']:.6f}° {'✓' if Dh['suns']['holds'] else '✗'}")}
      <p class="rd-kenning">The body is written under the messenger's number, the dharma under the lover's.</p>
      {f'<p class="rd-kenning">The dharma repeats {" and ".join(repeats)} of the birth chart. The repetition is load-bearing — that is a thing the life does not get to outgrow.</p>' if repeats else ''}
      <h3 class="rd-tier">The dharma cross</h3>
      <p>The four positions that carry the Dharma Design, as the four Suns and Earths carry the Birth Design: the dharma Sun and its Earth,
      and the dharma design Sun and its Earth. Read them as you read section {{SEC:The Work}}, conscious side first.</p>
      {register_entry(dps['gate'], dps['line'], 'personality', 'Dharma Sun', asks)}
      {register_entry(Dh['personality']['Earth']['gate'], Dh['personality']['Earth']['line'], 'personality', 'Dharma Earth', asks)}
      {register_entry(dds['gate'], dds['line'], 'design', 'Dharma design Sun', asks)}
      {register_entry(Dh['design']['Earth']['gate'], Dh['design']['Earth']['line'], 'design', 'Dharma design Earth', asks)}
      {dharma_defines(N, Dh)}
      {dharma_table(N, Dh)}
      {VG.thread(C)}"""))
    asks.append(("From Rashi to Dharma", VG.W["ASK"], False))

    # ---------- VI · the Path of Dharma ----------
    def steps(rave):
        """The incarnate path as a walk: one step per sphere, in order."""
        out, k = [], 0
        for seq, names in SEQ.items():
            out.append(f'<div class="rd-seq"><h3>{seq[0].upper() + seq[1:]}</h3>')
            for n in names:
                _, col, body, gloss = next(s for s in SPHERES if s[0] == n)
                g = rave[col].get(body)
                if not g: continue
                k += 1
                w = WALK.get(n, {}); R = REG.get(str(g["gate"]), {})
                t = R.get("t", GATE_NAME.get(str(g["gate"]), ""))
                act = activation(g["gate"], g["line"], C, dasha, n)
                if col == "design":
                    q = '<p class="rd-step-q held">This is design-side. Read the gate\'s engine in section {{SEC:The Work}} or {{SEC:The Dharma Weave}} first; its question waits in section {{SEC:The Questions}}.</p>'
                else:
                    q = f'<p class="rd-step-q">The question to carry: <em>{R.get("a", "")}</em></p>' if R.get("a") else ""
                out.append(f"""<div class="rd-step"><div class="rd-sn">Step {k}</div>
                  <div><h4>{n} <small>{col} {body}</small></h4>
                  <div class="rd-gate">gate {g['gate']}.{g['line']}, {t}</div>
                  {f'<div class="rd-opens {act["state"].split()[0]}">{GLYPH.get(act["lord"], "⊕")} {act["text"]}</div>' if act else ''}
                  <p>{w.get('what', gloss)}</p><p class="rd-how">{w.get('how', '')}</p>{q}</div></div>""")
            out.append("</div>")
        return "".join(out)
    def mature(rave_n, rave_d):
        rows = []
        for s_ in SPHERES:
            n, col, body = s_[0], s_[1], s_[2]
            a, b = rave_n[col].get(body), rave_d[col].get(body)
            if not (a and b): continue
            same = a["gate"] == b["gate"]
            t = REG.get(str(b["gate"]), {}).get("t", GATE_NAME.get(str(b["gate"]), ""))
            rows.append(f"<tr{' class=hi' if same else ''}><td>{n}</td><td>{a['gate']}.{a['line']}</td>"
                        f"<td>{b['gate']}.{b['line']} {t}</td><td>{'holds' if same else 'matures'}</td></tr>")
        return f'<div class="rd-tw"><table><tr><th>Sphere</th><th>Incarnate</th><th>Mature</th><th></th></tr>{"".join(rows)}</table></div>'
    shared = [s[0] for s in SPHERES if N[s[1]].get(s[2]) and Dh[s[1]].get(s[2])
              and N[s[1]][s[2]]["gate"] == Dh[s[1]][s[2]]["gate"]]
    out.append(section(5, "The Path of Dharma", "Mission · Illuminations · the Diamond", f"""
      <p>Eleven spheres, in order, and the order is the instruction. The first two are a pair and so are the third
      and fourth — each is drawn from a Sun or Earth, and Earth is always the exact opposite of its Sun, so you are
      reading a thing and its ground together.</p>
      <p>Work down the list in order. The Diamond Self comes last because it is a by-product; read first, it turns the
      whole path into a fortune. Design-side spheres are marked — those run unnamed until spoken, so read the engine
      before you ask the question.</p>
      <h3 class="rd-tier">Walking the path</h3>
      <p>Each step names when it opens in your life. A sphere's gate sits in one of the twenty-seven mansions, and
      that mansion's lord rules the sphere; the step opens when that lord's mahadasha arrives. Work the steps in
      order whatever their ages. A step that opened before you started is still waiting to be walked.</p>{steps(N)}
      <h3 class="rd-tier">The Path of Dharma · mature</h3>
      <p>The same eleven positions read on the Dharma Design. Where a sphere repeats a gate across both paths the
      repetition is load-bearing. Where they differ, the difference is the maturation: the same spectrum, walked further.</p>{mature(N, Dh)}
      {pair("Load-bearing", " · ".join(shared) + " repeat across both paths" if shared else "no sphere repeats — every one matures")}"""))

    # ---------- VII · the clock ----------
    cur, a, p = dasha["cur"], dasha["curA"], dasha["curP"]
    role = {b: k for k, b in K.items()}
    def lord(b): return f"{GLYPH.get(b, '')} {b}" + (f" · your {role[b].replace('karaka', '')}karaka" if b in role else "")
    out.append(section(6, "The Clock", "Vimshottari, from the Moon's mansion", f"""
      {pair("Mahadasha", f"{lord(cur['lord'])} · {jd_date(cur['from'])} – {jd_date(cur['to'])}")}
      {pair("Antardasha", f"{lord(a['lord'])} · {jd_date(a['from'])} – {jd_date(a['to'])}")}
      {pair("Pratyantar", f"{lord(p['lord'])} · {jd_date(p['from'])} – {jd_date(p['to'])}")}
      <div class="rd-tw"><table><tr><th>Period</th><th>From</th><th>To</th></tr>{''.join(
        f"<tr{' class=hi' if m['now'] else ''}><td>{GLYPH.get(m['lord'], '')} {m['lord']}</td><td>{jd_date(m['from'])}</td><td>{jd_date(m['to'])}</td></tr>"
        for m in dasha['maha'])}</table></div>
      <h3 class="rd-tier">Your life by period</h3>{MORE.periods(C, dasha)}"""))

    # ---------- the numbers ----------
    out.append(section(0, NUMBERS.T["TITLE"], NUMBERS.T["SUB"], NUMBERS.body(C, dasha, who, asks)))

    # ---------- VIII · the questions ----------
    qs = "".join(f'<li><div class="rd-ql">{esc(lab)}{" · held, design-side" if d else ""}</div><div>{q}</div></li>'
                 for lab, q, d in asks)
    out.append(section(7, "The Questions", "every question your chart asked, in the order it asked them",
                       f'<ol class="rd-qs">{qs}</ol>'))

    for i in range(len(out)):                       # number the sections in the order they stand
        out[i] = out[i].replace("{{N}}", ROMAN[i], 1)
    import re
    num = {re.search(r"<h2>(.*?)</h2>", s).group(1): ROMAN[i] for i, s in enumerate(out)}
    out = [re.sub(r"\{\{SEC:(.*?)\}\}", lambda m: num[m.group(1)], s) for s in out]
    return STORY.tell(C, dasha, (who or {}).get("name"), ENG) + "".join(out)     # the prologue opens it, unnumbered
