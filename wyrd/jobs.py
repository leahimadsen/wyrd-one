"""The Monday job: each member's Body Weather by email, and a short summary for you.

Run by the scheduled GitHub workflow (.github/workflows/weekly.yml), which
calls POST /jobs/weekly with JOBS_TOKEN. Each member's customer record in
Stripe remembers the last week sent, so running it twice sends nothing twice."""
import html, logging, time
from . import stripe_api, mailer, weather

log = logging.getLogger("wyrd.jobs")
LIVE = ("active", "trialing", "past_due")


def _live_subscriptions(secret):
    """Every live Wyrd subscription, with its customer."""
    out, after = [], None
    while True:
        q = {"status": "all", "limit": 100, "expand[]": "data.customer"}
        if after: q["starting_after"] = after
        r = stripe_api._call(secret, "GET", "/subscriptions?" + stripe_api.urllib.parse.urlencode(q))
        rows = r.get("data") or []
        from .billing import tier_of
        out += [dict(s, metadata={**(s.get("metadata") or {}), "tier": tier_of(s)}) for s in rows
                if s.get("status") in LIVE and tier_of(s) in ("member", "pro")]
        if not r.get("has_more") or not rows: return out
        after = rows[-1]["id"]


def weekly(eph, cast_for, birth_from, config):
    import json
    secret = config.STRIPE_SECRET
    if not secret: return {"error": "no Stripe key"}
    week = weather.monday().isoformat()
    sent = skipped = failed = 0
    seen = set()
    subs = _live_subscriptions(secret)
    from .billing import gifted, gift_of
    try:
        gifts = [c for c in gifted(secret) if gift_of(c.get("metadata") or {})["live"]]
    except stripe_api.StripeError as e:
        log.error("gift search: %s", e); gifts = []
    for c in [s.get("customer") or {} for s in subs] + gifts:
        if not isinstance(c, dict) or c.get("id") in seen: continue
        seen.add(c["id"])
        meta = c.get("metadata") or {}
        if meta.get("bw_week") == week or not meta.get("wyrd_birth") or not c.get("email"):
            skipped += 1; continue
        try:
            b = json.loads(meta["wyrd_birth"])
            report = weather.render(weather.week(eph, cast_for(birth_from(b))), (b.get("name") or "").split(" ")[0])
            link = f'<p style="font:14px sans-serif;color:#5f5a73;margin-top:30px">Read it on the site any time: <a href="{config.BASE_URL}/account/weather">your account</a>. Manage your place in the Order from <a href="{config.BASE_URL}/account">your account</a>.</p>'
            if mailer.send(c["email"], "Your Body Weather for the week", report + link):
                stripe_api.update_customer_metadata(secret, c["id"], {"bw_week": week}); sent += 1
            else:
                failed += 1
        except Exception as e:                    # one bad chart never stops the rest
            log.error("body weather for %s: %s", c.get("id"), e); failed += 1
    summary = {"week": week, "members": len(seen), "sent": sent, "skipped": skipped, "failed": failed}
    if config.OWNER_EMAIL:
        summary.update(_sales(secret))
        tiers = {}
        for s in subs: tiers[s["metadata"]["tier"]] = tiers.get(s["metadata"]["tier"], 0) + 1
        rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>" for k, v in
                       [("The Order", tiers.get("member", 0)), ("The Inner Circle", tiers.get("pro", 0)), ("Gifted", len(gifts)),
                        ("Readings sold, last 7 days", summary["readings"]), ("Sales, last 7 days", f'${summary["revenue"] / 100:.2f}'),
                        ("Body Weather sent", sent), ("Body Weather failed", failed)])
        mailer.send(config.OWNER_EMAIL, f"Wyrd Console: your week ({week})",
                    f'<h2>Your week</h2><table cellpadding="6">{rows}</table><p>Pulse insights: {config.BASE_URL}/admin/insights</p>')
    return summary


def _sales(secret):
    since = int(time.time()) - 7 * 86400
    q = stripe_api.urllib.parse.urlencode({"created[gte]": since, "status": "complete", "limit": 100})
    rows = stripe_api._call(secret, "GET", "/checkout/sessions?" + q).get("data") or []
    paid = [s for s in rows if s.get("payment_status") == "paid"]
    return {"readings": sum(1 for s in paid if s.get("mode") == "payment"),
            "revenue": sum(s.get("amount_total") or 0 for s in paid)}
