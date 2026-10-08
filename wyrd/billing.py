"""Who has paid for what, asked of Stripe directly.

There is no database: Stripe holds the customers and subscriptions, and the
site asks it. Answers are kept in memory for a few minutes so pages stay
quick, and dropped the moment someone buys or changes a plan here. All of
this happens on the server; the browser is never trusted to say who paid."""
import json, os, threading, time
from . import stripe_api

PRICE_TIER = {p: t for p, t in ((os.environ.get("STRIPE_MEMBER_MONTHLY_PRICE"), "member"),
                                (os.environ.get("STRIPE_MEMBER_YEARLY_PRICE"), "member"),
                                (os.environ.get("STRIPE_PRO_MONTHLY_PRICE"), "pro")) if p}

LIVE = ("active", "trialing", "past_due")      # past_due: Stripe is still retrying the card
CACHE_SECONDS = 300
_cache, _lock = {}, threading.Lock()


def status(secret, email, fresh=False):
    """{"customer", "member", "pro", "plans": [...], "birth": {...} or None} for this email."""
    if not secret or not email: return _empty()
    with _lock:
        hit = _cache.get(email)
    if hit and not fresh and time.time() - hit[0] < CACHE_SECONDS: return hit[1]
    out = _empty()
    try:
        c = stripe_api.find_customer(secret, email)
        if c:
            out["customer"] = c["id"]
            meta = c.get("metadata") or {}
            try: out["birth"] = json.loads(meta["wyrd_birth"]) if meta.get("wyrd_birth") else None
            except ValueError: out["birth"] = None
            out["proUse"] = _use(meta)
            g = gift_of(meta)
            if g:
                out["gift"] = g
                if g["live"]: out[g["tier"]] = True
            for s in stripe_api.subscriptions(secret, c["id"]):
                item = ((s.get("items") or {}).get("data") or [{}])[0]
                tier = tier_of(s)
                if tier not in ("member", "pro"): continue
                plan = {"id": s["id"], "tier": tier, "status": s.get("status"),
                        "interval": ((item.get("price") or {}).get("recurring") or {}).get("interval"),
                        "periodEnd": s.get("current_period_end") or item.get("current_period_end"),
                        "cancelAtEnd": bool(s.get("cancel_at_period_end"))}
                out["plans"].append(plan)
                if plan["status"] in LIVE: out[tier] = True
    except stripe_api.StripeError:
        if hit: return hit[1]                      # Stripe unreachable: keep the last answer we had
        raise
    with _lock:
        _cache[email] = (time.time(), out)
        if len(_cache) > 5000: _cache.clear()
    return out


def tier_of(sub):
    """Which plan a subscription is: from the price it is on now (so a switch made in the Stripe
    portal counts at once), falling back to the tier written on it at checkout."""
    item = ((sub.get("items") or {}).get("data") or [{}])[0]
    price = (item.get("price") or {}).get("id")
    if price and price in PRICE_TIER: return PRICE_TIER[price]
    return (sub.get("metadata") or {}).get("tier")


def forget(email):
    with _lock:
        _cache.pop(email, None)


def customer_for(secret, email):
    """The Stripe customer for this email, made if there isn't one yet."""
    st = status(secret, email)
    if st["customer"]: return st["customer"]
    c = stripe_api.create_customer(secret, email)
    forget(email)
    return c["id"]


def save_birth(secret, email, birth):
    cid = customer_for(secret, email)
    stripe_api.update_customer_metadata(secret, cid, {"wyrd_birth": json.dumps(birth, separators=(",", ":"))[:500]})
    forget(email)


def month():
    return time.strftime("%Y-%m", time.gmtime())


def _use(meta):
    return int(meta.get("pro_count") or 0) if meta.get("pro_month") == month() else 0


def count_pro_reading(secret, email):
    """Add one to this month's professional readings. Returns the new count."""
    st = status(secret, email, fresh=True)
    n = st["proUse"] + 1
    stripe_api.update_customer_metadata(secret, st["customer"], {"pro_month": month(), "pro_count": n})
    forget(email)
    return n


def _empty():
    return {"customer": None, "member": False, "pro": False, "plans": [], "birth": None, "proUse": 0, "gift": None}


# ---------------- gifts: a membership or Professional plan given by The Völva ----------------
# Kept on the Stripe customer as metadata, so nothing is charged and no
# subscription exists. wyrd_gift_until is a date (YYYY-MM-DD) or "forever".
def gift_of(meta):
    tier, until = meta.get("wyrd_gift_tier"), meta.get("wyrd_gift_until")
    if meta.get("wyrd_gift") != "1" or tier not in ("member", "pro") or not until: return None
    live = until == "forever" or until >= time.strftime("%Y-%m-%d", time.gmtime())
    return {"tier": tier, "until": until, "live": live}


def give(secret, email, tier, until):
    cid = customer_for(secret, email)
    stripe_api.update_customer_metadata(secret, cid, {"wyrd_gift": "1", "wyrd_gift_tier": tier, "wyrd_gift_until": until})
    forget(email)


def end_gift(secret, email):
    st = status(secret, email, fresh=True)
    if st["customer"]:
        stripe_api.update_customer_metadata(secret, st["customer"], {"wyrd_gift": "0", "wyrd_gift_until": ""})
    forget(email)


def gifted(secret):
    """Every customer holding a gift, live or ended, for the admin list and the weekly job."""
    return [c for c in stripe_api.search_customers(secret, "metadata['wyrd_gift']:'1'") if gift_of(c.get("metadata") or {})]
