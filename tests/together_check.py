"""The Wyrd Reading Together: prices, checkout, and the reading itself, against a pretend Stripe.

    python tests/together_check.py

Nothing here talks to Stripe and the ephemeris isn't needed: the reading is
built from pretend charts, and checkout never casts one."""
import json, os, re, sys, time, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.update(STRIPE_SECRET_KEY="sk_test_fake", SECRET_KEY="k" * 40, BASE_URL="https://example")
sys.modules["wyrd.ephemeris"] = types.SimpleNamespace(Ephemeris=lambda *a: object())

from wyrd import billing, engine as E, stripe_api, together
import app as site

bad = 0
def check(name, ok):
    global bad
    print(("  ok   " if ok else "  FAIL ") + name)
    bad += not ok

# ---- prices ----
P = site.together_cents
check("two people: $22", P(2) == 2200)
check("each extra person: $11 more", P(3) == 3300 and P(9) == 9900)
check("members: 20% off", P(2, True) == 1760 and P(3, True) - P(2, True) == 880)

# ---- how the planets get on ----
S = together.season
check("same lord, same guest", S("Venus", "Venus") == "same")
check("Sun and Jupiter are allies", S("Sun", "Jupiter") == "allies")
check("Sun and Saturn are at odds", S("Sun", "Saturn") == "odds")
check("Moon and Saturn: uneasy (Saturn dislikes the Moon, the Moon minds no one)", S("Moon", "Saturn") == "uneasy")
check("Moon and Mars: warm on one side (Mars likes the Moon, the Moon is neutral)", S("Moon", "Mars") == "friendly")
check("Moon and Mercury: friend one way, enemy the other, so polite", S("Moon", "Mercury") == "polite")
check("Rahu is read like Saturn, Ketu like Mars", S("Rahu", "Sun") == "odds" and S("Ketu", "Jupiter") == "allies")
check("every pairing of the nine has a season", all(S(a, b) in together.T["SEASONS"] for a, _ in E.DASHA for b, _ in E.DASHA))
check("symmetric", all(S(a, b) == S(b, a) for a, _ in E.DASHA for b, _ in E.DASHA))

# ---- the reading, from pretend charts ----
SID = {b: (i * 37.3) % 360 for i, b in enumerate(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])}
def person(name, asc, moon, ak, unknown=False, gates=(26, 10, 20, 7, 31), date="1987-08-01", full_name=""):
    natal = {"personality": {f"b{i}": {"gate": g, "line": 1} for i, g in enumerate(gates)}, "design": {}}
    C = {"ascS": asc, "sid": dict(SID, Moon=moon), "karaka": {"Atmakaraka": ak}, "jd": 2447000.0, "natal": natal}
    if unknown: C["unknownTime"] = True
    return {"name": name, "C": C, "dasha": E.dasha_tree(C, 2447000.0 + 35 * E.YEAR), "date": date, "full_name": full_name}

two = together.build([person("Freya", 10, 100, "Venus"), person("Odin <b>", 200, 250, "Saturn", unknown=True)])
check("opens with the table story", two.index("Prologue: The Table") < two.index("Who Sits at the Table"))
check("the story names who sent each", "Freya had been sent by Venus" in two and "had been sent by Saturn" in two)
check("names can't add HTML", "Odin <b>" not in two and "Odin &lt;b&gt;" in two)
check("both directions of waking", "What Freya wakes" in two and "What Odin &lt;b&gt; wakes" in two)
check("unknown birth time is said", "houses are counted from the Sun" in two)
check("no blank left unfilled", not re.findall(r"\{[a-z_]+\}", two))
years = [int(y) for y in re.findall(r"<tr><td>(\d{4})</td>", two)]
check("the next thirty years, in order", years and years == sorted(years) and years[-1] - years[0] <= 30)
check("for two, every sub-period says how the shorter guests get on", "The two shorter guests are" in two)
check("sections numbered I to VIII", all(f'<div class="rd-num">{n}</div>' in two for n in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")))

nine = together.build([person(f"P{i}", i * 40, i * 33 + 5, ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"][i % 7]) for i in range(9)])
check("nine people: everyone wakes the other eight", all(nine.count(f"What P{i} wakes") == 1 for i in range(9)) and nine.count("'s soul-planet, ") == 72)
check("nine people: every pair's season now", nine.count("&amp;") >= 36)

# ---- the bond in words: paid, and only paid ----
from wyrd import bond as BOND
import glob
shu = lambda i: {"index": i, "kanji": "", "read": ""}
A, Bp = person("Freya", 10, 100, "Venus"), person("Odin", 200, 250, "Saturn")
A["shuku"], Bp["shuku"] = shu(3), shu(7)
r = BOND.relation(A, Bp)
pair_html = together.build([A, Bp])
check("the Sukuyō relation is written out", BOND.B["SUKUYO"][r["pair"]]["text"] in pair_html)
check("what the bond is for, and both paths", all(h in pair_html for h in ("What this bond is for", "The higher path", "The lower path", "Weaving the two")))
cs = BOND.contacts(A, Bp)
check("the strongest contact is written out", cs and BOND.contact_text(cs[0], {"name": "Freya"}, {"name": "Odin"}).split(" <em")[0][:60] in pair_html)
check("every planet in the other's houses, in words", pair_html.count("in Odin's") >= 9 and pair_html.count("in Freya's") >= 9)
check("the bond's question joins the questions", BOND.B["SUKUYO"][r["pair"]]["ask"] in pair_html.split("The Questions")[1])
check("sections numbered I to VIII", all(f'<div class="rd-num">{n}</div>' in pair_html for n in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")))
check("the bond comes after the story and the table", pair_html.index("Prologue") < pair_html.index("Who Sits at the Table") < pair_html.index("<h2>The Bond</h2>"))
check("no shuku, no Sukuyō, and nothing breaks", "Sukuyō ·" not in two and "The higher path" in two)

shipped = "".join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(ROOT, "static", "*.js")) + glob.glob(os.path.join(ROOT, "static", "*.html")))
paid = [v["text"][:50] for v in BOND.B["SUKUYO"].values()] + [v["core"][:50] for v in BOND.B["PAIRS"].values()] + \
       [v["high"][:50] for v in BOND.B["BOND"].values()] + [v["ask"][:40] for v in BOND.B["SUKUYO"].values()]
check("none of the paid writing is sent to the browser", not [x for x in paid if x in shipped])

# ---- the contents ----
from wyrd import reading as RD
toc = RD.contents(pair_html)
links = re.findall(r'href="#(s-[a-z0-9-]+)"', toc)
check("contents list the story and all eight sections", len(links) == 9 and links[0] == "s-story")
check("every contents link has a section to land on", all(f'id="{l}"' in pair_html for l in links))
check("a button brings the contents back from anywhere", 'class="rd-totop" href="#contents"' in toc)

# ---- checkout ----
CALLS = []
def fake_call(secret, method, path, fields=None):
    CALLS.append((method, path, fields))
    if path == "/checkout/sessions": return {"url": "https://checkout.example/s"}
    if path.startswith("/customers?"): return {"data": []}
    raise AssertionError(path)
stripe_api._call = fake_call
client = site.app.test_client()
B = lambda n, **k: {"name": n, "date": "1990-05-17", "time": "14:30", "lat": 51.5, "lon": -0.13, "tz": "Europe/London", "place_label": "London, England", **k}

r = client.post("/api/checkout-together", json={"people": [B("Freya"), B("Odin", unknown_time=True), B("Loki")]})
f = CALLS[-1][2]
check("checkout opens", r.status_code == 200 and r.get_json()["url"].startswith("https://checkout"))
check("three people cost $33", f["line_items[0][price_data][unit_amount]"] == "3300")
check("receipt names the reading and the count", "Together, for 3" in f["line_items[0][price_data][product_data][name]"])
check("it's a one-off payment, not a subscription", f["mode"] == "payment")
check("cancelling goes back to Compare", f["cancel_url"].endswith("#compare"))
meta = {k[9:-1]: v for k, v in f.items() if k.startswith("metadata[")}
check("within Stripe's metadata limits", len(meta) <= 50 and all(len(v) <= 500 for v in meta.values()))
people = site.together_people(meta)
check("everyone's details come back from the payment", [p["name"] for p in people] == ["Freya", "Odin", "Loki"]
      and people[1].get("unknown_time") == "1" and "unknown_time" not in people[0])
check("and they still make valid births", all(site.birth_from(p) for p in people))

check("one person is refused", client.post("/api/checkout-together", json={"people": [B("A")]}).status_code == 400)
check("ten people are refused", client.post("/api/checkout-together", json={"people": [B(str(i)) for i in range(10)]}).status_code == 400)
r = client.post("/api/checkout-together", json={"people": [B("Freya"), B("Odin", date="1990-02-31")]})
check("a bad birth names the person", r.status_code == 400 and "Odin" in r.get_json()["error"])

billing.status = lambda s, e, fresh=False: {"member": True, "pro": False, "customer": "cus_m"}
c2 = site.app.test_client()
with c2.session_transaction() as s: s["email"] = "m@x.co"
c2.post("/api/checkout-together", json={"people": [B("Freya"), B("Odin")]})
f = CALLS[-1][2]
check("members pay $17.60 for two", f["line_items[0][price_data][unit_amount]"] == "1760" and f["customer"] == "cus_m")
check("the page is told members' prices", c2.get("/api/me").get_json()["together"] == {"two": 1760, "extra": 880, "max": 9})

check("a bad paid session can't open a reading", site.app.test_client().get("/reading?session_id=nope").status_code == 404)

print("TOGETHER CHECK", "PASSED" if not bad else f"FAILED ({bad})")
sys.exit(1 if bad else 0)
