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
# The unlisted 1:1 consultation page lives at /c/<CONSULT_PATH>. Pick something
# nobody would guess (e.g. "inner-room-7k2q"). Leave it empty to switch the page off.
CONSULT_PATH = os.environ.get("CONSULT_PATH", "").strip()
# Your private admin at /admin: generate any reading without paying. It only
# exists when both are set (in Render: Environment). Use a long password.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET_KEY     = os.environ.get("SECRET_KEY", "")        # signs the admin login cookie; any long random string
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

# --- subscriptions. Prices are made inside each Stripe checkout, so nothing has
# to be set up in the Stripe dashboard. Change a number here to change a price
# for new subscribers; people already subscribed keep what they signed up at. ---
MEMBER_MONTHLY_CENTS = int(os.environ.get("MEMBER_MONTHLY_CENTS", "1100"))     # $11 a month
MEMBER_YEARLY_CENTS  = int(os.environ.get("MEMBER_YEARLY_CENTS", "11100"))     # $111 a year
MEMBER_READING_CENTS = int(os.environ.get("MEMBER_READING_CENTS", "3520"))     # the $44 reading at 20% off for members
PRO_MONTHLY_CENTS    = int(os.environ.get("PRO_MONTHLY_CENTS", "4400"))        # Professional, a month
PRO_READINGS_A_MONTH = int(os.environ.get("PRO_READINGS_A_MONTH", "30"))       # client readings included each month
MEMBER_NAME          = "Wyrd Membership"
# Real Stripe prices, so members can switch plans in the Stripe portal. When unset,
# each checkout makes its price from the cents above instead.
MEMBER_MONTHLY_PRICE = os.environ.get("STRIPE_MEMBER_MONTHLY_PRICE", "")
MEMBER_YEARLY_PRICE  = os.environ.get("STRIPE_MEMBER_YEARLY_PRICE", "")
PRO_MONTHLY_PRICE    = os.environ.get("STRIPE_PRO_MONTHLY_PRICE", "")
PRO_NAME             = "Wyrd Console Professional"
# Locks the weekly email job (POST /jobs/weekly) so only your scheduler can run it.
JOBS_TOKEN           = os.environ.get("JOBS_TOKEN", "")
OWNER_EMAIL          = os.environ.get("OWNER_EMAIL", "")       # where your Monday summary goes
