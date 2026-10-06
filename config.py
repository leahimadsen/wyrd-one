"""Everything you might want to change lives here. Secrets come from the
environment (set them in your host's dashboard), never from this file."""
import os

BASE_URL        = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
STRIPE_SECRET   = os.environ.get("STRIPE_SECRET_KEY", "")        # sk_live_... or sk_test_...
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")          # optional: a $44 Price from your dashboard
# Only these consultation Payment Links may unlock a report after payment.
# Use Stripe's plink_... IDs, comma-separated; never the public buy.stripe.com URL.
CONSULTATION_PAYMENT_LINK_IDS = frozenset(
    value.strip() for value in os.environ.get("CONSULTATION_PAYMENT_LINK_IDS", "").split(",")
    if value.strip()
)
# Alternatively paste the public link you already send customers.
CONSULTATION_PAYMENT_LINK_URL = os.environ.get("CONSULTATION_PAYMENT_LINK_URL", "").strip()
PRICE_CENTS     = 4400
PRODUCT_NAME    = "Your Wyrd Reading"
# With no Stripe key set, "Buy" opens a free preview so you can proof readings locally.
# This is switched off automatically the moment a Stripe key exists.
DEV_PREVIEW     = not STRIPE_SECRET

DATA_DIR        = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
EPHEMERIS_FILE  = os.environ.get("EPHEMERIS_FILE", "de440s.bsp")  # covers 1849-2150
YEAR_MIN, YEAR_MAX = 1850, 2149

SITE_TITLE      = "The Wyrd Console"
AUTHOR          = "Saga Devi"

# --- your words around the reading. Edit freely; plain text or simple HTML. ---
READING_OPENING = (
    "What follows is assembled from your chart and from the register of the Web of Wyrd. "
    "Nothing in it is generic: every passage was written for one placement, and these are yours. "
    "Read it in order. The questions gathered at the end are the part that works."
)
READING_CLOSING = (
    "A chart is a set of engines, each with a light wield, a dark wield, and a place where it breaks. "
    "Work the questions and the reading does the rest."
)
