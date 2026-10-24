"""Sign-in by email link. No passwords and nothing stored.

The link carries the email address, sealed with SECRET_KEY (wyrd/sealed.py), and stops working
after twenty minutes. Opening it shows a button; the sign-in happens when that
button is pressed, so mail scanners that open links ahead of the reader
don't sign anyone in."""
import re
from itsdangerous import BadSignature, SignatureExpired
from .sealed import Sealer

LINK_MINUTES = 20
EMAIL = re.compile(r"[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}")


def clean_email(e):
    e = (e or "").strip().lower()
    return e if len(e) <= 254 and EMAIL.fullmatch(e) else None


def safe_next(u):
    """Only paths on this site, never another address."""
    return u if isinstance(u, str) and u.startswith("/") and not u.startswith("//") and "\\" not in u and len(u) < 200 else "/account"


def _s(secret):
    return Sealer(secret, "wyrd-sign-in")


def make_token(secret, email, next_url="/account"):
    return _s(secret).dumps({"e": email, "n": safe_next(next_url)})


def read_token(secret, token):
    """(email, next) for a good link, or (None, None)."""
    if not isinstance(token, str) or len(token) > 1000: return None, None
    try:
        d = _s(secret).loads(token, max_age=LINK_MINUTES * 60)
    except (BadSignature, SignatureExpired):
        return None, None
    e = clean_email(d.get("e")) if isinstance(d, dict) else None
    return (e, safe_next(d.get("n"))) if e else (None, None)
