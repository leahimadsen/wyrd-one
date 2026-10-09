"""Stripe Checkout over plain HTTPS — no SDK needed.
The birth data rides in the session's metadata, so a paid reading can be
rebuilt from its session id alone: no database, nothing to lose."""
import json, os, urllib.parse, urllib.request, urllib.error

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
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise StripeError("Stripe could not be reached.") from e

# Stripe's tax category for what is sold here (digital, personal use). Required when the account
# uses Managed Payments, where Stripe is the seller and handles sales tax; harmless otherwise.
TAX_CODE = os.environ.get("STRIPE_TAX_CODE", "txcd_10103000")

def create_checkout(secret, *, base_url, price_id, price_cents, product_name, metadata, email=None, customer=None):
    f = {
        "mode": "payment",
        "success_url": f"{base_url}/reading?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{base_url}/chart?cancelled=1#reading",
        "allow_promotion_codes": "true",          # Substack discount codes work
        "line_items[0][quantity]": "1",
    }
    if price_id:
        f["line_items[0][price]"] = price_id
    else:
        f["line_items[0][price_data][currency]"] = "usd"
        f["line_items[0][price_data][unit_amount]"] = str(price_cents)
        f["line_items[0][price_data][product_data][name]"] = product_name
        if TAX_CODE: f["line_items[0][price_data][product_data][tax_code]"] = TAX_CODE
    if customer: f["customer"] = customer
    elif email: f["customer_email"] = email
    for k, v in metadata.items():
        f[f"metadata[{k}]"] = str(v)[:500]
        f[f"payment_intent_data[metadata][{k}]"] = str(v)[:500]
    return _call(secret, "POST", "/checkout/sessions", f)

def paid_session(secret, session_id):
    """The session, if and only if it has been paid for."""
    if not isinstance(session_id, str) or not session_id.startswith("cs_") or len(session_id) > 200:
        return None
    s = _call(secret, "GET", "/checkout/sessions/" + urllib.parse.quote(session_id, safe=""))
    return s if s.get("payment_status") in ("paid", "no_payment_required") else None

def save_birth_metadata(secret, session_id, metadata):
    """Attach birth details to the existing checkout; this never takes payment."""
    fields = {f"metadata[{k}]": str(v)[:500] for k, v in metadata.items()}
    return _call(secret, "POST", "/checkout/sessions/" + urllib.parse.quote(session_id, safe=""), fields)

def payment_link(secret, link_id):
    if not isinstance(link_id, str) or not link_id.startswith("plink_") or len(link_id) > 200:
        return None
    return _call(secret, "GET", "/payment_links/" + urllib.parse.quote(link_id, safe=""))


# ---------------- subscriptions: membership and professional ----------------
# Prices are made inside each checkout (price_data), like the $44 reading, so
# nothing has to be set up in the Stripe dashboard first. A plan's tier rides
# in the subscription's metadata, which is how the site knows what was bought.
def find_customers(secret, email):
    """Every Stripe customer with this email (checkout can make a second one for the same person)."""
    return _call(secret, "GET", "/customers?" + urllib.parse.urlencode({"email": email, "limit": 10})).get("data") or []

def find_customer(secret, email):
    rows = find_customers(secret, email)
    return next((c for c in rows if (c.get("metadata") or {}).get("wyrd") == "1"), rows[0] if rows else None)

def checkout_session(secret, session_id):
    if not isinstance(session_id, str) or not session_id.startswith("cs_") or len(session_id) > 200:
        return None
    return _call(secret, "GET", "/checkout/sessions/" + urllib.parse.quote(session_id, safe="") + "?expand[]=customer")

def create_customer(secret, email):
    return _call(secret, "POST", "/customers", {"email": email, "metadata[wyrd]": "1"})

def update_customer_metadata(secret, customer_id, fields):
    return _call(secret, "POST", "/customers/" + urllib.parse.quote(customer_id, safe=""),
                 {f"metadata[{k}]": str(v)[:500] for k, v in fields.items()})

def subscriptions(secret, customer_id):
    return _call(secret, "GET", "/subscriptions?" + urllib.parse.urlencode(
        {"customer": customer_id, "status": "all", "limit": 20})).get("data") or []

def subscription_checkout(secret, *, base_url, customer, tier, name, cents, interval, success, cancel, price_id=None):
    f = {"line_items[0][price]": price_id} if price_id else {
        "line_items[0][price_data][currency]": "usd",
        "line_items[0][price_data][unit_amount]": str(cents),
        "line_items[0][price_data][recurring][interval]": interval,
        "line_items[0][price_data][product_data][name]": name}
    if TAX_CODE and not price_id: f["line_items[0][price_data][product_data][tax_code]"] = TAX_CODE
    if customer: f["customer"] = customer          # signed in: their customer. Not signed in: Stripe asks for the email
    return _call(secret, "POST", "/checkout/sessions", {
        **f,
        "mode": "subscription",
        "line_items[0][quantity]": "1",
        "allow_promotion_codes": "true",
        "subscription_data[metadata][tier]": tier,
        "metadata[tier]": tier,
        "success_url": f"{base_url}{success}",
        "cancel_url": f"{base_url}{cancel}",
    })

def portal(secret, customer, return_url, upgrade=None):
    """Stripe's customer portal. With upgrade=sub_..., it opens straight on changing that plan."""
    f = {"customer": customer, "return_url": return_url}
    if upgrade:
        f.update({"flow_data[type]": "subscription_update", "flow_data[subscription_update][subscription]": upgrade})
    return _call(secret, "POST", "/billing_portal/sessions", f)

def search_customers(secret, query):
    out, page = [], None
    while True:
        q = {"query": query, "limit": 100}
        if page: q["page"] = page
        r = _call(secret, "GET", "/customers/search?" + urllib.parse.urlencode(q))
        out += r.get("data") or []
        if not r.get("has_more") or not r.get("next_page"): return out
        page = r["next_page"]
