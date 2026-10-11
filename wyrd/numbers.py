"""A person's numbers: from the birth date, and from the full name at birth.

  Life path      the whole birth date (month, day and year each reduced, then summed)
  Birthday       the day of the month
  Personal year  the birth month and day with this year: the year you are in now
  Expression     every letter of the full birth name (Pythagorean: A=1 ... I=9, J=1 ...)
  Soul urge      its vowels (A E I O U; Y when a word has no other vowel)
  Personality    its consonants

11, 22 and 33 are kept as master numbers; each still sits on the planet of its
root (11 on 2's, 22 on 4's, 33 on 6's). Each number is given two planets, side
by side: the console's own Stavefall seating on the Planetary Ladder (static/viz.js)
and Vedic numerology (Ank Jyotish). static/numbers.js does the same sums in the
browser; tests/numbers_check.py keeps the two in step."""
import unicodedata

MASTERS = (11, 22, 33)
STAVEFALL = {1: ("Sun", "Crown"), 2: ("Moon", "Brow"), 3: ("Saturn", "Throat"), 4: ("Jupiter", "Heart"),
             5: ("Mars", "Solar plexus"), 6: ("Venus", "Sacrum"), 7: ("Mercury", "Root"),
             8: ("Rahu", "The pole above"), 9: ("Ketu", "The pole below")}
VEDIC = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
KINDS = ["life_path", "birthday", "personal_year", "expression", "soul_urge", "personality"]


def digits(n): return sum(int(c) for c in str(n))


def reduce(n, masters=True):
    while n > 9 and not (masters and n in MASTERS):
        n = digits(n)
    return n


def root(n): return reduce(n, masters=False)


def letters(name):
    """The name's letters A to Z, accents taken off; anything else is dropped."""
    plain = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().upper()
    return [w for w in ("".join(c if "A" <= c <= "Z" else " " for c in plain)).split() if w]


def value(c): return (ord(c) - 65) % 9 + 1


def vowels(word):
    v = [c for c in word if c in "AEIOU"]
    return v if v else [c for c in word if c == "Y"]


def name_numbers(name):
    words = letters(name)
    if not words: return {}
    total = lambda pick: reduce(sum(reduce(sum(value(c) for c in pick(w))) for w in words))
    vow = lambda w: vowels(w)
    con = lambda w: [c for c in w if c not in vowels(w)]
    return {"expression": total(lambda w: w), "soul_urge": total(vow), "personality": total(con)}


def of(date, full_name="", year=None):
    """{kind: number} for a birth date (YYYY-MM-DD) and, if given, the full birth name."""
    y, m, d = (int(x) for x in date.split("-"))
    out = {"life_path": reduce(reduce(m) + reduce(d) + reduce(digits(y))), "birthday": reduce(d)}
    if year: out["personal_year"] = reduce(reduce(m) + reduce(d) + reduce(digits(year)))
    out.update(name_numbers(full_name))
    return out


def planets(n):
    """The two planets a number sits on: Stavefall (planet, station) and Vedic."""
    r = root(n)
    return {"stavefall": STAVEFALL[r][0], "station": STAVEFALL[r][1], "vedic": VEDIC[r], "root": r}
