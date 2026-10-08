# The Wyrd Console — public site

Free chart (positions, mansions, gates, Dharma Weave, karakas, dasha) with the
armillary, the colour room and the bench; a $44 reading assembled from the
Web of Wyrd register, unlocked by Stripe Checkout.

## What's where
- `app.py` — the web server (Flask)
- `config.py` — prices, wording around the reading, year range
- `wyrd/engine.py` — the chart pipeline, ported from the console and verified against it
- `wyrd/ephemeris.py` — NASA JPL DE440 via Skyfield; Lahiri ayanamsa
- `wyrd/reading.py` — the paid reading (eight sections, all text from `lib/corpus.json`)
- `wyrd/places.py`, `scripts/build_places.py` — worldwide place search (GeoNames)
- `static/index.html` + `app.js` — the landing page: the high seat and the birth form
- `static/chart.html` + `chart.js` + `map.css` — the chart page (`/chart`): the map with the
  chart as its hub, and each land (section) on its own tab
- `static/consult.html` — the unlisted 1:1 consultation page (see below)
- `static/viz.js` is extracted from the console
- `lib/corpus.json` — your register. Server-side only; never sent to the browser.
- `tests/` — `verify_engine.py` (port = console), `selfcheck.py` (ephemeris wired right)

## Run it on your own computer
    pip install -r requirements.txt
    python scripts/build_places.py      # downloads world places once (~10 MB)
    python app.py                        # open http://localhost:8000

With no Stripe key set, "Get my reading" opens a free PREVIEW so you can proof
readings. Setting a Stripe key switches previews off.

## Launch on Render (about 20 minutes)
1. Make a private GitHub repository and upload this folder to it.
2. In Render: New → Blueprint → pick the repository. It reads `render.yaml`.
3. Fill in the three settings it asks for:
   - `BASE_URL` — the address the site will live at, e.g. `https://chart.webofwyrd.com`
   - `STRIPE_SECRET_KEY` — from Stripe → Developers → API keys. Use the **test** key first.
   - `STRIPE_PRICE_ID` — optional; leave empty and the price comes from `config.py` ($44).
4. Deploy. When it's live, open Render's Shell for the service and run
   `python tests/selfcheck.py` — it must say SELF-CHECK PASSED.
5. Buy a reading on the live site with Stripe's test card 4242 4242 4242 4242
   (any future date, any CVC). Check the reading opens.
6. Swap `STRIPE_SECRET_KEY` to your **live** key. Add your domain under Settings →
   Custom Domains and point the DNS record it shows you at Render.

Discount codes made in Stripe (Products → Coupons → Promotion codes) work at
checkout, so you can give your Substack readers a code.

## The unlisted 1:1 consultation page
1. In Stripe, make a Payment Link for the consultation. Under **After payment**, choose
   "Don't show confirmation page" and redirect to
   `https://YOUR-SITE/consultation?session_id={CHECKOUT_SESSION_ID}`
2. In Render, set `CONSULTATION_PAYMENT_LINK_URL` to that link (the `buy.stripe.com/...` address),
   and `CONSULT_PATH` to a word nobody would guess, e.g. `inner-room-7k2q`.
3. The page is now at `https://YOUR-SITE/c/inner-room-7k2q`. It isn't linked anywhere and search
   engines are told to skip it, so only people you send it to will find it. Change `CONSULT_PATH`
   to retire an old link; leave it empty to switch the page off.
4. After paying, the client gives their birth details and their reading opens.

## Where readings live
A reading is rebuilt from its Stripe session each time it's opened; the link in
the buyer's browser after payment is permanent. If someone loses theirs, find
the payment in Stripe, copy the Checkout Session id (cs_...), and send them
`https://YOUR-SITE/reading?session_id=cs_...`.

## Credits the site must keep
GeoNames (CC BY 4.0) in the footer. NASA JPL ephemeris data is public domain.
