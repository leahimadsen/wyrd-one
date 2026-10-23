"""The privacy policy (/privacy) and the script that clears what this browser keeps.

Every sentence here describes what the code does. When the site starts keeping something new,
sending it somewhere new, or keeping it longer, change the words here and PRIVACY_UPDATED in config.py."""
from html import escape as e

# What the site keeps in a browser, by key. "Clear this browser" removes exactly these.
BROWSER_KEYS = {
    "wyrdChart": ("session storage", "the chart open in this tab, so the chart page can draw it; gone when the tab closes"),
    "wyrdSaved": ("local storage", "the charts you chose to save, so they're here next time"),
    "wyrdLearn": ("local storage", "how far you've walked the learning path"),
    "wyrdVid":   ("local storage", "a random id for the anonymous counts below; it never leaves with anything else and the server never stores it"),
    "wyrdMusic": ("local storage", "whether you switched the music on"),
}

# Clears every key above (and any other wyrd* key), and the offline copies the app keeps.
CLEAR_SCRIPT = """<script>
(() => {
  const btn = document.getElementById("clearBrowser"), out = document.getElementById("clearDone");
  if (!btn) return;
  btn.hidden = false;
  btn.onclick = async () => {
    for (const s of [window.localStorage, window.sessionStorage]) {
      try { Object.keys(s).filter(k => k.startsWith("wyrd")).forEach(k => s.removeItem(k)); } catch (_) {}
    }
    try { if (window.caches) for (const k of await caches.keys()) await caches.delete(k); } catch (_) {}
    out.hidden = false;
  };
})();</script>"""

CLEAR_BUTTON = """<p><button class="alt" type="button" id="clearBrowser" hidden>Clear what this browser keeps</button></p>
<p class="note-box" id="clearDone" hidden>Done. Saved charts, learning progress and the offline copies are gone from this browser.</p>"""


def page(author, contact, updated, operator="", substack=""):
    """(title, description, body) for /privacy."""
    who = e(operator) if operator else e(author)
    mail = f'<a href="mailto:{e(contact)}">{e(contact)}</a>'
    keys = "".join(f"<li><code>{k}</code> ({where}): {what}</li>" for k, (where, what) in BROWSER_KEYS.items())
    sub = f' (<a href="{e(substack)}">{e(substack.split("//")[-1])}</a>)' if substack else ""
    body = f"""<h1>Privacy</h1>
<p class="muted">Last changed {e(updated)}</p>
<p class="lede">Your birth details are personal. This page says plainly what the Wyrd Console keeps, where, for how long,
and how to have it removed.</p>

<h2>The short version</h2>
<ul>
<li><b>A free chart isn't stored on our server.</b> Your birth details are sent to cast it and then forgotten; the chart stays in your own browser.</li>
<li><b>We never see your card.</b> Payments happen on Stripe's pages.</li>
<li><b>No advertising, no tracking cookies, nothing sold.</b> We count what people use on the site anonymously, and not at all if your browser sends Do Not Track or Global Privacy Control.</li>
<li><b>You can have it all removed.</b> Members can download or delete their records from <a href="/account/data">Your data</a>; anyone can write to {mail}.</li>
</ul>

<h2>Who runs the site</h2>
<p>The Wyrd Console is run by {who}, who decides what happens to the information described here.
Write to {mail} about anything on this page.</p>

<h2>What you give us, and what it's for</h2>
<h3>Casting a free chart</h3>
<p>Your date, time and place of birth (and a name and full name at birth, if you add them) go to our server to calculate the chart,
and come straight back. The server doesn't save them. Your browser keeps the chart while the tab is open, and keeps the charts
you choose to save on your device. A "Copy link" share link carries the birth details inside the link itself, so anyone you send it to can see them.</p>

<h3>Buying a reading</h3>
<p>The birth details for the reading (and the full name at birth, if given, for the numbers) are stored with your payment at Stripe.
That is how the reading rebuilds itself every time you open its link, without us keeping a copy. Stripe collects your email address
and payment details; we use the email to send you the reading's links, once. Anyone with your reading's link can open it, so keep it as you would a receipt.
For a reading together, each person's details ride with the payment in the same way: please only add people who are happy for you to.</p>

<h3>Membership: the Order, the Inner Circle and the Lightning Path</h3>
<p>Your email address signs you in: we send a link that works for twenty minutes, and there is no password to keep.
Your plan lives at Stripe, along with the chart you choose for Body Weather. We keep each week's Body Weather letter so you can reread it,
the charts you keep for loved ones, and what you write to {e(author)} between calls.</p>

<h3>The Inner Circle's practice desk</h3>
<p>Practitioners keep their clients' names, birth details, email addresses and notes here, and the readings made for them.
A practitioner who adds a client is responsible for having that person's permission; clients can also write to {mail}.</p>

<h3>Writing to us</h3>
<p>The contact form sends your name, email address and message to {e(author)} by email, and keeps a copy on the site so it isn't lost.</p>

<h3>The masterclass and the newsletter</h3>
<p>Subscribing to The Web of Wyrd happens on Substack{sub}, in a box Substack provides. Substack's own privacy policy covers what you give it there.</p>

<h2>What we count, anonymously</h2>
<p>To learn what helps, the site counts what people do on it: which parts of the chart are opened and in what order, how far the
learning path goes, which terms are looked up, how many people are compared. Only these named events are counted, as daily totals.
No birth details, names, email addresses or IP addresses go into the counts, and no profile of anyone is made. To count visitors per day
your browser makes up a random id; the server uses it to tell one visitor from another that day and never writes it down.
If your browser sends <b>Do Not Track</b> or <b>Global Privacy Control</b>, nothing at all is counted.</p>

<h2>Cookies and what your browser keeps</h2>
<p>There are no advertising or third-party tracking cookies. One cookie is set only when you sign in: it holds your signed-in email,
signed so it can't be forged, and lasts thirty days or until you sign out. Your browser also keeps:</p>
<ul>{keys}</ul>
<p>The installable app keeps copies of the site's pages so it works offline; readings, checkout and account pages are never kept.
All of this stays on your device and you can remove it here at any time:</p>
{CLEAR_BUTTON}

<h2>Who else handles it</h2>
<p>We use a small number of services to run the site. Each handles only what it needs, for us:</p>
<ul>
<li><b>Stripe</b> takes payments and holds plans, receipts, and the birth details stored with a reading or a member's chart.</li>
<li><b>Render</b> hosts the site. Like any web host it keeps short-lived server logs of requests (the address asked for, the time and your IP address), used for keeping the site running. Because a shared chart link carries its birth details in the address, opening one appears in those logs too.</li>
<li><b>Neon</b> (Postgres) holds the members' and practitioners' records described above.</li>
<li><b>Our email provider</b> (Google Mail or Resend) sends sign-in links, readings and letters, and carries messages to {e(author)}.</li>
<li><b>Google Fonts</b> supplies some of the lettering; your browser fetches the fonts from Google, which sees your IP address when it does.</li>
<li><b>GitHub</b> stores the anonymous daily counts. No personal information goes there.</li>
</ul>
<p>We don't sell, rent or trade personal information, or share it for advertising. We'd hand it over only if the law required it.
Some of these services are in the United States; they protect what they hold under their own data-protection terms.</p>

<h2>How long it's kept</h2>
<ul>
<li>Free charts: not kept on our server at all.</li>
<li>Readings and payments: with the payment record at Stripe, which keeps payment records as long as tax and accounting law require. Ask us and we'll remove the birth details from it (the reading's link then stops working).</li>
<li>Members' letters, loved ones' charts, messages and practitioners' client records: until you delete them, ask us to, or close your account.</li>
<li>Contact-form messages: until we delete them once they're no longer needed, or sooner if you ask.</li>
<li>Sign-in links: twenty minutes. The sign-in cookie: thirty days.</li>
<li>Server logs: the host's short rolling window.</li>
</ul>

<h2>Your choices and rights</h2>
<p>You can ask for a copy of what we hold about you, ask us to correct it, to delete it, or to stop using it, and you can object to the anonymous counting
(your browser's Global Privacy Control setting does that automatically). If you're signed in, <a href="/account/data">Your data</a> lets you download your records
or delete them yourself, straight away. Otherwise write to {mail} from the address the information is held under, and we'll answer within thirty days.
Wherever you live, these choices are yours; if you're in the UK, the European Union or California the law guarantees them, and you can complain to your
data-protection authority if you think we've got something wrong. We'd be glad to hear from you first.</p>

<h2>Keeping it safe</h2>
<p>The site runs over encrypted connections only. Sign-in uses expiring links rather than passwords, so there are no passwords to leak.
Card details never reach us. Private pages (readings, accounts, the practice desk) are never cached or shown to search engines, and only {e(author)}
can open the site's administration. No system is perfect: if something ever went wrong with your information, we'd tell you.</p>

<h2>Children</h2>
<p>The Wyrd Console is meant for adults. Please don't buy a reading or a membership if you're under 16. A parent may cast a chart for a child; it isn't stored, as above.</p>

<h2>Changes</h2>
<p>If what we keep or how we use it changes, this page changes first, with its date at the top. A change that matters to members will be emailed to them.</p>"""
    return ("Privacy · The Wyrd Console",
            "What the Wyrd Console keeps about you, where, for how long, and how to have it removed.", body)
