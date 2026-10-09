/* The Wyrd Console's service worker: what makes the site installable and lets
   it open without a connection.
   - The pages and their scripts come from the network when there is one, and
     from the cache when there isn't, so a deploy shows up on the next visit.
   - Readings, checkout and the consultation pages are never cached: they are
     private and paid for.
   Bump VERSION to throw the old cache away. */
const VERSION = "wyrd-v15";
const SHELL = ["/", "/chart", "/today", "/offline",
  "/static/console.css", "/static/site.css", "/static/map.css", "/static/learn.css", "/static/body.css", "/static/dasha.css", "/static/a11y.css", "/static/design.css",
  "/static/viz.js", "/static/glossary.js", "/static/common.js", "/static/body.js", "/static/design.js", "/static/runes.js", "/static/vargas.js", "/static/kuta.js", "/static/synastry.js", "/static/wheel.js", "/static/torus.js", "/static/dasha.js",
  "/static/transits.js", "/static/learn.js", "/static/lands.js", "/static/pulse.js", "/static/dharma.js", "/static/dynamics.js", "/static/compare.js", "/static/music.js", "/static/chart.js", "/static/app.js", "/static/today.js",
  "/static/icons/icon-192.png", "/static/icons/apple-touch-icon.png", "/static/icons/favicon-32.png"];
const NEVER = [/^\/admin/, /^\/api\/pulse/, /^\/reading/, /^\/consultation/, /^\/c\//, /^\/sample/, /^\/(account|signin|signout|auth|pro|billing|membership|jobs|welcome)/, /^\/api\/(subscribe|account|me)/, /^\/api\/(checkout|consultation|places|chart|calendar)/, /\.mp3$/];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || NEVER.some(r => r.test(url.pathname))) return;
  const key = req.mode === "navigate" ? url.pathname : req;          // one cached copy per page, whatever its query or hash
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok && res.type === "basic") { const copy = res.clone(); caches.open(VERSION).then(c => c.put(key, copy)); }
      return res;
    }).catch(async () => {
      const hit = await caches.match(key) || (url.pathname.startsWith("/static/") && await caches.match(url.pathname));
      if (hit) return hit;
      if (req.mode === "navigate") return caches.match("/offline");
      return new Response("", { status: 503, statusText: "Offline" });
    })
  );
});
