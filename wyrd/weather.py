"""Body Weather: one week of sky read through a person's two bodies.

For each day of the week (sampled at noon UT) the transiting planets' gates are
laid over the birth body and the Dharma body. A channel the chart can't close
alone, closed by the sky, switches its centres on for as long as it holds.
Gates the sky lights that the person already carries are named with their
register passage and question. The Moon's mansion for each day, the week's
stations and sign changes, and the current Vimshottari period run underneath.

Every interpretive sentence comes from lib/corpus.json, or for the centres
from lib/body_weather.json (Saga Devi's own lines)."""
import html, json, os
from datetime import datetime, timedelta, timezone
from . import engine as E, rave as RV, calendar as wcal

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = json.load(open(os.path.join(HERE, "lib", "corpus.json"), encoding="utf-8"))
CENTRE_LINES = json.load(open(os.path.join(HERE, "lib", "body_weather.json"), encoding="utf-8"))["centres"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SKY = E.RAVE + ["Earth"]
CENTRE_ORDER = [v[0] for v in RV.CENTRES.values()]


def monday(d=None):
    """The Monday (UTC) of the week holding d, as a date."""
    d = d or datetime.now(timezone.utc).date()
    return d - timedelta(days=d.weekday())


def _jd(day):
    return E.julian_day(day.year, day.month, day.day, 12.0)


def _first_sentence(t):
    t = (t or "").replace("<em>", "").replace("</em>", "").strip()
    for end in (". ", "? ", "! "):
        i = t.find(end)
        if 0 < i < 400: return t[:i + 1]
    return t[:400]


def _sky_gates(trop):
    out = {b: E.gate_of(trop[b])["gate"] for b in E.RAVE}
    out["Earth"] = E.gate_of(E.norm(trop["Sun"] + 180))["gate"]
    return out


FAST = {"Sun", "Earth", "Moon", "Mercury", "Venus", "Mars"}      # the week's movers; the rest hold for months


def _closed(have, gates):
    both = have | gates
    return {ch for ch in RV.CHANNELS if ch[0] in both and ch[1] in both}


def read_body(body, days):
    """What the week's sky does to one body. days: list of {planet: gate} per day.
    The season (Jupiter outward and the nodes) is read apart from the week (Sun, Earth,
    Moon, Mercury, Venus, Mars), so the report says what is new this week."""
    have = RV.gates(body)
    base_live, base_centres = RV.defines(body)
    base_set = set(base_live)
    centre = lambda g: RV.CENTRES[RV.CENTRE_OF[g]][0]
    season_ch, channels, lit, sky_gates, season_gates = set(), {}, {}, {}, {}
    for i, sky in enumerate(days):
        slow = {g for p, g in sky.items() if p not in FAST}
        season_now = _closed(have, slow) - base_set
        season_ch |= season_now
        gate_by = {}
        for planet, g in sky.items(): gate_by.setdefault(g, []).append(planet)
        for ch in _closed(have, set(gate_by)) - base_set - season_now:
            c = channels.setdefault(ch, {"days": set(), "by": set()})
            c["days"].add(i)
            for g in ch: c["by"].update(gate_by.get(g, []))
        for planet, g in sky.items():
            if g in have:
                bucket = sky_gates if planet in FAST else season_gates
                v = bucket.setdefault(g, {"days": set(), "by": set()})
                v["days"].add(i); v["by"].add(planet)
    season_centres = {centre(g) for ch in season_ch for g in ch} - set(base_centres)
    for ch, v in channels.items():
        for g in ch:
            n = centre(g)
            if n not in base_centres and n not in season_centres: lit.setdefault(n, set()).update(v["days"])
    rank = lambda kv: (kv[1]["by"] <= {"Moon"}, -len(kv[1]["days"]), kv[0])     # the Moon's one-day touches last
    return {
        "defined": base_centres,
        "season": {"channels": sorted(season_ch), "centres": [n for n in CENTRE_ORDER if n in season_centres],
                   "gates": [{"gate": g, "by": sorted(v["by"])} for g, v in sorted(season_gates.items())]},
        "channels": [{"channel": ch, "days": sorted(v["days"]), "by": sorted(v["by"])} for ch, v in sorted(channels.items(), key=rank)],
        "lit": [{"centre": n, "days": sorted(lit[n])} for n in CENTRE_ORDER if n in lit],
        "open": [n for n in CENTRE_ORDER if n not in base_centres and n not in season_centres and n not in lit],
        "gates": [{"gate": g, "days": sorted(v["days"]), "by": sorted(v["by"])} for g, v in sorted(sky_gates.items(), key=rank)],
    }


def week(eph, chart, start=None):
    start = start or monday()
    dates = [start + timedelta(days=i) for i in range(7)]
    jds = [_jd(d) for d in dates]
    many = getattr(eph, "positions_many", None)
    rows = many(jds) if many else [(eph.positions(j), eph.ayanamsa(j)) for j in jds]
    days, moons = [], []
    for trop, ay in rows:
        days.append(_sky_gates(trop))
        moons.append(E.nak_index(E.norm(trop["Moon"] - ay)))
    S = wcal.samples(eph, jds[0] - 1, 8)
    events = [e for e in wcal.sky_events(S) if jds[0] - 0.5 <= e["jd"] < jds[0] + 6.5]
    for e in events:
        e["day"] = max(0, min(6, int(round(e["jd"] - jds[0]))))
    dasha = E.vimshottari(chart["sid"]["Moon"], chart["jd"], jds[3])
    return {"start": start.isoformat(), "dates": [d.isoformat() for d in dates],
            "natal": read_body(chart["natal"], days), "dharma": read_body(chart["dharma"], days),
            "moon": moons, "events": events, "dasha": dasha}


# ---------------- writing it out ----------------
def _days(ix):
    if len(ix) == 7: return "all week"
    if len(ix) == 1: return DAYS[ix[0]]
    runs, a = [], ix[0]
    for p, q in zip(ix, ix[1:] + [None]):
        if q != p + 1:
            runs.append(DAYS[a] if a == p else f"{DAYS[a]} to {DAYS[p]}"); a = q
    return ", ".join(runs)


def _gate(g):
    return f"Gate {g} · {html.escape(CORPUS['GATE_NAME'].get(str(g), ''))}"


def _section(title, body, intro):
    e = html.escape
    out = [f'<h2 style="font:600 22px Georgia,serif;margin:28px 0 6px">{e(title)}</h2><p style="color:#5f5a73;margin:0 0 12px">{e(intro)}</p>']
    if body["season"]["centres"]:
        sc = body["season"]
        chans = ", ".join(f"{a}–{b}" for a, b in sc["channels"])
        out.append(f'<p style="color:#5f5a73;font-size:14px">The season, held for months by the slower planets: {e(", ".join(sc["centres"]))} '
                   f'switched on through {e(chans)}. This is the backdrop to the week below.</p>')
    if body["lit"]:
        for c in body["lit"]:
            out.append(f'<p style="margin:10px 0"><b>{e(c["centre"])} switched on</b> <span style="color:#5f5a73">· {_days(c["days"])}</span><br>{e(CENTRE_LINES[c["centre"]]["lit"])}</p>')
        chans = "; ".join(f'{a}–{b} ({_days(v["days"])}, through {", ".join(v["by"])})' for v in body["channels"] for a, b in [v["channel"]])
        out.append(f'<p style="color:#5f5a73;font-size:14px">Channels closed by the sky: {e(chans)}.</p>')
    else:
        out.append('<p>The fast planets close no new channels in this body this week. It runs on its own definition and the season.</p>')
    if body["open"]:
        out.append(f'<p style="margin:10px 0"><b>Open all week: {e(", ".join(body["open"]))}</b></p>')
        for n in body["open"][:2]:
            out.append(f'<p style="margin:6px 0"><span style="color:#5f5a73">{e(n)}:</span> {e(CENTRE_LINES[n]["open"])}</p>')
    for g in body["gates"][:3]:
        reg = CORPUS["REGISTER"].get(str(g["gate"]), {})
        out.append(f'<p style="margin:14px 0"><b>{_gate(g["gate"])}</b> <span style="color:#5f5a73">· lit by {e(", ".join(g["by"]))}, {_days(g["days"])}</span><br>'
                   f'{e(_first_sentence(reg.get("l")))}<br><i>{e(_first_sentence(reg.get("a")))}</i></p>')
    return "".join(out)


def render(w, name=""):
    """The report as simple HTML that reads the same in an email and on the site."""
    e = html.escape
    start = datetime.fromisoformat(w["start"]).strftime("%-d %B %Y")
    parts = [f'<div style="font:16px/1.6 Georgia,serif;color:#1d1a2b;max-width:620px">',
             f'<p style="font:600 12px sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#9a6a12;margin:0">Body Weather · week of {e(start)}</p>',
             f'<h1 style="font:600 30px Georgia,serif;margin:6px 0 14px">{e(name) + ", your" if name else "Your"} week in the body</h1>',
             _section("Your birth body", w["natal"], "How this week's planets land in the body you were born with."),
             _section("Your Dharma body", w["dharma"], "The same week through the D9 Dharma body: where it carries the path and where it pulls."),
             '<h2 style="font:600 22px Georgia,serif;margin:28px 0 6px">The thread through the week</h2>']
    d = w["dasha"]
    parts.append(f'<p>You are in the {e(d["maha"])} period, {e(d["antar"])} sub-period.</p><ul style="padding-left:18px">')
    for i, n in enumerate(w["moon"]):
        nk = CORPUS["NAKSHATRA"][n]
        parts.append(f'<li><b>{DAYS[i]}</b>: Moon in {e(nk[0])} ({e(nk[5])}). {e(nk[6])}</li>')
    parts.append('</ul>')
    if w["events"]:
        lines = []
        for ev in w["events"]:
            if ev["kind"] == "station": lines.append(f'{DAYS[ev["day"]]}: {ev["body"]} turns {ev["turns"]} in {ev["sign"]}')
            elif ev["kind"] == "ingress": lines.append(f'{DAYS[ev["day"]]}: {ev["body"]} enters {ev["sign"]}')
        parts.append(f'<p>{e("; ".join(lines))}.</p>')
    parts.append('</div>')
    return "".join(parts)
