"""The Numbers, in the paid reading: each number with its two planets, what it
means (lib/numbers.json, drafted for The Völva), and where the life path's
planets stand in the chart and when their periods come."""
import json, os, time

from . import engine as E
from . import numbers as NUM
from . import oldstyle
from .reading_more import X as REG_EXT, ORD, E_year, the

T = json.load(open(os.path.join(os.path.dirname(__file__), "..", "lib", "numbers.json"), encoding="utf-8"))
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"}
LABEL = {"life_path": "Life path", "birthday": "Birthday", "personal_year": "Personal year",
         "expression": "Expression", "soul_urge": "Soul urge", "personality": "Personality"}


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def body(C, dasha, who, asks, year=None):
    """The section's HTML. who is the birth details (date, and full_name if given)."""
    year = year or int(time.strftime("%Y", time.gmtime()))
    nums = NUM.of(oldstyle.new_style(who), who.get("full_name", ""), year)     # an Old Style birth counts by its New Style day
    rows = []
    for kind in NUM.KINDS:
        if kind not in nums: continue
        n = nums[kind]; p = NUM.planets(n)
        master = f" <small>({p['root']})</small>" if n > 9 else ""
        rows.append(f"<tr><td>{LABEL[kind]}</td><td><b>{n}</b>{master}</td>"
                    f"<td>{GLYPH[p['stavefall']]} {p['stavefall']} · {p['station']}</td><td>{GLYPH[p['vedic']]} {p['vedic']}</td></tr>")
    table = f'<div class="rd-tw"><table><tr><th>Number</th><th></th><th>Stavefall seat</th><th>Vedic</th></tr>{"".join(rows)}</table></div>'

    meanings = []
    for kind in NUM.KINDS:
        if kind not in nums or kind == "personal_year": continue
        n = nums[kind]; m = T["NUMBER"][str(n)]
        meanings.append(f"""<h3 class="rd-tier">{LABEL[kind]} {n} · {m["name"]}</h3><p class="rd-kenning">{fill(T["KIND"][kind], year=year)}</p>
          <div class="rd-gifts"><div class="light"><h5>Light wield</h5><p>{m["light"]}</p></div>
          <div class="dark"><h5>Shadow</h5><p>{m["shadow"]}</p></div></div>""")

    # the life path's planets, in the chart and on the clock
    lp = nums["life_path"]; p = NUM.planets(lp); now = dasha["now"]
    def where(planet, system):
        l = C["sid"][planet]; h = E.house_of(l, C["ascS"])
        row = next((m for m in dasha["maha"] if m["lord"] == planet and m["to"] > C["jd"]), None)
        if not row: period = ""
        elif row["from"] <= now < row["to"]: period = fill(T["PERIOD_NOW"], **{"from": E_year(row["from"]), "to": E_year(row["to"])})
        elif row["to"] <= now: period = fill(T["PERIOD_PAST"], **{"from": E_year(max(row["from"], C["jd"])), "to": E_year(row["to"])})
        else: period = fill(T["PERIOD_AHEAD"], **{"from": E_year(row["from"]), "to": E_year(row["to"]), "age": int((row["from"] - C["jd"]) / E.YEAR)})
        name = the(planet); name = name[0].upper() + name[1:]
        return "<p>" + fill(T["PLANET_LINE"], planet=f"{GLYPH[planet]} {name}", system=system, sign=E.SIGNS[int(E.norm(l) // 30)],
                            house=ORD(h), life=REG_EXT["HOUSE_LIFE"][h - 1], period=period) + "</p>"
    lines = where(p["stavefall"], f"your Stavefall seat, the {p['station'].lower()}")
    lines += f'<p class="rd-kenning">{T["SAME_PLANET"]}</p>' if p["vedic"] == p["stavefall"] else where(p["vedic"], "the Vedic planet of " + str(p["root"]))

    py = nums["personal_year"]; m = T["NUMBER"][str(py)]
    year_line = f'<p>{fill(T["YEAR_LINE"], n=py, light=m["light"][0].lower() + m["light"][1:], shadow=m["shadow"][0].lower() + m["shadow"][1:])}</p>'
    asks.append((f"Life path {lp}", fill(T["ASK"], n=lp, name=T["NUMBER"][str(lp)]["name"]), False))
    return f"""<p>{T["INTRO"]} <a href="/learn/numbers">How the numbers are counted, and the two seatings →</a></p>{table}{'' if "expression" in nums else f'<p class="rd-note">{T["NO_NAME"]}</p>'}
      {"".join(meanings)}<h3 class="rd-tier">{T["PLANETS_TITLE"]}</h3>{lines}
      <h3 class="rd-tier">Personal year {py} · {year}</h3>{year_line}"""
