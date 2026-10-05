"""Stripe Checkout over plain HTTPS — no SDK needed.
The birth data rides in the session's metadata, so a paid reading can be
rebuilt from its session id alone: no database, nothing to lose."""
import json, urllib.parse, urllib.request, urllib.error

API = "https://api.stripe.com/v1"

class StripeError(Exception):
    pass

def _call(secret, method, path, fields=None):
    data = urllib.parse.urlencode(fields or {}).encode() if fields is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {secret}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try: msg = json.load(e)["error"]["message"]
        except Exception: msg = str(e)
        raise StripeError(msg)

def create_checkout(secret, *, base_url, price_id, price_cents, product_name, metadata, email=None):
    f = {
        "mode": "payment",
        "success_url": f"{base_url}/reading?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{base_url}/?cancelled=1",
        "allow_promotion_codes": "true",          # Substack discount codes work
        "line_items[0][quantity]": "1",
    }
    if price_id:
        f["line_items[0][price]"] = price_id
    else:
        f["line_items[0][price_data][currency]"] = "usd"
        f["line_items[0][price_data][unit_amount]"] = str(price_cents)
        f["line_items[0][price_data][product_data][name]"] = product_name
    if email: f["customer_email"] = email
    for k, v in metadata.items():
        f[f"metadata[{k}]"] = str(v)[:500]
        f[f"payment_intent_data[metadata][{k}]"] = str(v)[:500]
    return _call(secret, "POST", "/checkout/sessions", f)

def paid_session(secret, session_id):
    """The session, if and only if it has been paid for."""
    if not session_id.startswith("cs_") or len(session_id) > 200:
        return None
    s = _call(secret, "GET", "/checkout/sessions/" + urllib.parse.quote(session_id))
    return s if s.get("payment_status") in ("paid", "no_payment_required") else None
