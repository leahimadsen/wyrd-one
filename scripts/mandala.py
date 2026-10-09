"""Turn The Völva's mandala sheet (lib/wyrd-mandala-108.csv) into static/mandala.json, which the site reads."""
import csv, json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(HERE, "lib", "wyrd-mandala-108.csv"), encoding="utf-8")))
assert len(rows) == 108, "the mandala has 108 padas"
padas = [{"nak": r["nakshatra"], "pada": int(r["nak_pada"]), "minor": r["minor_card_outer"], "minorInner": r["minor_card_inner"],
          "ruler": r["decan_ruler"], "trump": r["trump_outer"], "trumpInner": r["trump_inner"], "void": r["asura_void"] or ""} for r in rows]
json.dump({"_note": "The Völva's 108-pada mandala (from lib/wyrd-mandala-108.csv): each pada of the sidereal zodiac, from Ashwini 1 at 0°, with its cards. Regenerate with scripts/mandala.py if the CSV changes.",
           "padas": padas}, open(os.path.join(HERE, "static", "mandala.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("static/mandala.json: 108 padas")
