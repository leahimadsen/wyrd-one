"""Links that carry private details (birth data in a gift or a reading together, an email in a sign-in
link) are sealed: encrypted and authenticated with a key made from SECRET_KEY, so the details can't be
read from the address, from a log or by a mail scanner, and can't be changed.

A drop-in for itsdangerous's URLSafeTimedSerializer: dumps(obj) and loads(token, max_age), raising
BadSignature (or SignatureExpired) when a link is forged, damaged or too old. Links made before sealing
(signed but readable) still open until they expire, so nothing already sent stops working."""
import base64, hashlib, json, zlib
from cryptography.fernet import Fernet, InvalidToken
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


class Sealer:
    def __init__(self, secret, salt):
        key = hashlib.sha256(f"wyrd-sealed:{salt}:{secret}".encode()).digest()
        self._f = Fernet(base64.urlsafe_b64encode(key))
        self._old = URLSafeTimedSerializer(secret, salt=salt)

    def dumps(self, obj):
        raw = zlib.compress(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(), 9)
        return self._f.encrypt(raw).decode().rstrip("=")

    def loads(self, token, max_age):
        if not isinstance(token, str): raise BadSignature("not a link")
        if token.startswith("gAAAAA"):                   # sealed: Fernet's version byte and timestamp
            try:
                raw = self._f.decrypt((token + "=" * (-len(token) % 4)).encode(), ttl=max_age)
            except InvalidToken:
                # a good seal past its time reads as expired; anything else is forged or damaged
                try: self._f.decrypt((token + "=" * (-len(token) % 4)).encode())
                except InvalidToken: raise BadSignature("bad link")
                raise SignatureExpired("link expired")
            try: return json.loads(zlib.decompress(raw))
            except (ValueError, zlib.error): raise BadSignature("bad link")
        return self._old.loads(token, max_age=max_age)   # made before links were sealed
