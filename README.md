# The Wyrd Console — public site

Free chart (positions, mansions, gates, runes, karakas, dasha; the Dharma Weave is kept for the paid reading) with the
armillary, the colour room and the bench; a $44 reading assembled from the
Web of Wyrd register, unlocked by Stripe Checkout.

## What's where
- `app.py` — the web server (Flask)
- `config.py` — prices, wording around the reading, year range
- `wyrd/engine.py` — the chart pipeline, ported from the console and verified against it
- `wyrd/extras.py` — retrogrades, the panchanga of the birth day, Placidus cusps (kept out of the cast so it stays identical to the console)
- `wyrd/calendar.py` — the twelve-month calendar ("What's coming") and the public Today page
- `wyrd/ephemeris.py` — NASA JPL DE440 via Skyfield; Lahiri ayanamsa
- `wyrd/reading.py` — the paid reading (eight sections, all text from `lib/corpus.json`)
- `wyrd/places.py`, `scripts/build_places.py` — worldwide place search (GeoNames)
- `static/index.html` + `app.js` — the landing page: the birth form (with "I don't know my time") and saved charts
- `static/chart.html` + `chart.js` — the chart page (`/chart`): the map, the tabs and every land
- `static/learn.js` — **Learn your chart**: the thirteen-step guided path. Edit the lesson wording here.
- `static/glossary.js` — every term's plain definition. Edit the wording here; it appears wherever the term does.
- `static/wheel.js` — the chart wheel (simple and full views, tap to explore, compare overlay)
- `static/lands.js` — What's coming and Compare
- `static/today.html` + `today.js` — the public Today page (`/today`)
- `static/consult.html` — the unlisted 1:1 consultation page (see below)
- `static/a11y.css` — contrast and minimum text sizes for the whole site
- `static/viz.js` is extracted from the console
- `lib/corpus.json` — your register. Server-side only; never sent to the browser.
- `tests/` — `verify_engine.py` (port = console), `selfcheck.py` (ephemeris wired right)

## Your private admin
`/admin` lets you generate the full paid reading for anyone, with no checkout. In Render, set
`ADMIN_PASSWORD` (long; it's the only lock) and `SECRET_KEY` (any long random string; the blueprint
generates one). Without both, `/admin` doesn't exist. Sign in, enter the birth details, and the reading
opens in a new tab: print it to PDF to send. Eight wrong passwords lock sign-in for fifteen minutes.

## Pulse and Insights: the console notices what people use
The site counts what visitors do, anonymously: which lands they open and in what order, how far they
walk the learning path, which terms they look up, how many people they compare. No birth details, names
or IP addresses, and nothing at all from browsers that send Do Not Track or Global Privacy Control.
- **Insights** at `/admin/insights` shows it, with plain-language findings ("most people stop the
  learning path at step 5", "the most looked-up term is pada").
- The site adapts: each land suggests where other visitors most often go next.
- Counts are saved every ten minutes to the **`wyrd-data` branch** of this repository (never `main`, so
  saving never redeploys the site). In Render set `GITHUB_TOKEN`: a fine-grained GitHub token for this
  repository only, with **Contents: read and write**. Without it, counts live in memory until a restart.
- Mention the anonymous counting in your privacy policy.

## The torus
- `static/torus.js` — the map's centre: the chart as a luminous torus you can turn. The zodiac runs round
  the ring; the houses, signs, runes, gates, mansions and tropical signs wrap round the tube; the planets ride
  the outer edge; a field of light flows through it. Layers switch on and off and build up again.
- The harmonic body has its own torus field (the "Torus field" switch).

## Compare, Sukuyō and the Dharma Weave
- `static/compare.js` — Compare: two people in full, or a unit of three or four.
- `static/dynamics.js` — Compare's free words: the names of things (the Sukuyō relations by name, what each
  planet carries in a word, the houses as phases). Compare shows the facts of a bond for free.
- `lib/bond.json` — **the paid writing about a bond**: each Sukuyō relation's engine and question, every planet
  contact, the houses in words, and the bond's purpose and higher and lower paths. Written into the reading
  together by `wyrd/bond.py`, and never sent to the browser otherwise.
- `wyrd/sukuyo.py` — the birth shuku from the old Japanese lunar calendar (rebuilt from new moons and
  solar terms, checked against seventeen known lunar dates including the 2012 and 2017 leap months, where
  Japan and China differ), and the sanku relations with their distances.
- `static/dharma.js` — the free Dharma Weave land: how the dharma rave is made, with the person's numbers.
  The paid reading's section V now also reads the dharma Earths and shows what the dharma rave defines.

## The installable app
The site installs to a phone or computer like an app: "Install the app" appears on the first page
and the chart page wherever the browser supports it (on iPhone it explains Share → Add to Home Screen).
- `static/manifest.webmanifest` — the app's name, colours and icons (`static/icons/`)
- `static/sw.js` — works offline: pages come from the network when there is one and from the
  cache when there isn't. Saved charts open offline. Readings, checkout and consultations are
  never cached. If an update ever seems stuck, raise `VERSION` at the top of `sw.js`.

## Free and paid
The free side shows what everything **is** (positions, gates, runes, mansions, the rave, the clock,
transits, definitions of every term). What it **means** for a person is only in the paid reading,
and the Dharma Weave is computed for the reading only. `/sample` shows one complete reading for a
made-up chart so people can see what they'd buy; change the chart in `app.py` (`SAMPLE`).

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


## Selling: readings, membership and Professional

Everything is held in Stripe; there is no database.

- **$44 natal reading** — unchanged. Signed-in members pay the member price (`MEMBER_READING_CENTS`).
- **Membership** — $11/month or $111/year (`MEMBER_MONTHLY_CENTS`, `MEMBER_YEARLY_CENTS`): weekly Body Weather, chart kept on the account, member price on the reading.
- **The reading together** — `TOGETHER_CENTS` ($22) for two people and `TOGETHER_EXTRA_CENTS` ($11) for each extra person, up to nine; members take `TOGETHER_MEMBER_OFF` (20%) off. Bought from Compare once two or more people are added. A story of the table, what each person wakes in the others, and the seasons they share for the next thirty years. Its writing is a draft in `lib/together.json` for The Völva to rewrite; everyone's birth details ride in the payment, so the reading rebuilds from its link like the $44 one.
- **Professional** — `PRO_MONTHLY_CENTS` a month: the practice desk at `/pro` generates full readings for clients (`PRO_READINGS_A_MONTH` a month) and Body Weather for any client.

Prices are made inside each Stripe Checkout, so no products need creating in the dashboard. Who has paid is asked of Stripe (cached five minutes); a member's saved chart and Body Weather "last sent" week live in their Stripe customer's metadata.

**To switch it on** (Render → Environment):
1. Email for sign-in links and Body Weather: `SMTP_HOST=smtp.gmail.com`, `SMTP_USER` (your Gmail), `SMTP_PASSWORD` (a Google app password). Or `RESEND_API_KEY` once you have a domain. Until email is set, the plans show "Opening soon".
2. `OWNER_EMAIL` for your Monday summary. `JOBS_TOKEN` is generated by Render.
3. In Stripe → Settings → Billing → Customer portal, press Save once so members can cancel or change cards.
4. In GitHub → Settings → Secrets → Actions add `SITE_URL` and `JOBS_TOKEN` (same value as Render) for the Monday email (`.github/workflows/weekly.yml`).

Body Weather's centre lines are drafts in `lib/body_weather.json` for The Völva to rewrite; everything else in it comes from `lib/corpus.json`.

## The full reading

**The Numbers** (`wyrd/numbers.py`, `static/numbers.js`): life path, birthday and personal year from the birth date, and expression, soul urge and personality from the optional *full name at birth* on the form. Each number sits on two planets, the console's own Stavefall seat and the Vedic one. The free chart shows the numbers; the reading says what they mean (drafts in `lib/numbers.json`) and where the life path's planets stand and when their periods come. **Learn the numbers** at `/learn/numbers` teaches how they are counted and the two seatings (text in `lib/numbers.json` under LEARN), and every number term on the chart can be tapped for its definition. Sections now refer to each other by name, so adding one never breaks a "see section …".

Every reading opens with **a prologue**: a silly story of how you got here (who sent you, the costume you chose, the gift and the shadow packed with it, and the houseguests who arrive at each age), assembled from the chart. Its lines are drafts in `lib/story.json` for The Völva to rewrite; the numbered sections that follow decode it.

Fourteen sections: the Seat, the Engine (Moon), **the Planets** (all twelve, each read sidereally for karma and reality and tropically for experience, with dignity, rune and gates), the Soul-Planet, **the Runes** (the lit runes ranked, and the dasha periods that wake each one), the Work, **the Body** (all nine centres, every channel and the mansion and pada that feeds each gate), **Where You Thrive** (culture, places, work), the Dharma Weave, the Path of Dharma, the Clock (with the whole life by period), **the Numbers** and the Questions. The new sections draw on `lib/register_ext.json`, drafted for The Völva to edit.

## Gifts (admin only)

At `/admin/gifts` give anyone a Membership or Professional plan by email for 30 days (the default, for creators), 1, 3, 6 or 12 months, or for good. Nothing is charged and no card is asked for: the gift is kept as metadata on their Stripe customer and no subscription is made. They get an email inviting them to sign in. The list shows each gift and its last day; press **End** to revoke one. A gift works through its last day (UTC) and the account is back on the free site the day after, unless they pay for a plan, which a gift never touches. Access is checked against Stripe with a five-minute cache, so an ended gift can take up to five minutes to close everywhere. To gift a reading, fill in their birth details at `/admin` and press **Make a gift link**: the link opens their full reading, free, for two years.

## Search

`/reports`, `/membership`, `/learn` and a page for every gate, nakshatra and sign are server-rendered with titles, descriptions, share previews and structured data (price, FAQ). `/sitemap.xml` and `/robots.txt` tell Google what to read; private pages send noindex. Add the site to Google Search Console and submit the sitemap.

Tests: `python tests/members_check.py` (accounts, plans, Body Weather, weekly job, search pages; no Stripe calls).
`python tests/numbers_check.py` (life path, birthday, personal year and the name's numbers, browser against server; needs node). `python tests/karaka_check.py` (the karakas in both zodiacs; needs node). `python tests/together_check.py` (prices, checkout and the reading together). `python tests/gifts_check.py` (granting, expiry and revoking complimentary access; checks no checkout or subscription is ever made).
