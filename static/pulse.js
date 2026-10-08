'use strict';
/* Pulse: anonymous counts of what people do, so the console can notice what is used.
   Never birth details, names or anything typed. Off entirely for browsers that send
   Do Not Track or Global Privacy Control. Events: Wyrd.pulse("land", "chart"), or
   data-pulse="act:share" on any element. */
(() => {
  const off = navigator.globalPrivacyControl === true || navigator.doNotTrack === "1" || window.doNotTrack === "1";
  let vid = "", queue = [];
  try { vid = localStorage.getItem("wyrdVid") || ""; if (!vid){ vid = Math.random().toString(36).slice(2, 10) + Date.now().toString(36); localStorage.setItem("wyrdVid", vid); } } catch (_) {}
  function send(){
    if (!queue.length) return;
    const body = JSON.stringify({ v: vid, e: queue.splice(0, 60) });
    try { if (!(navigator.sendBeacon && navigator.sendBeacon("/api/pulse", new Blob([body], { type: "text/plain" }))))
      fetch("/api/pulse", { method: "POST", body, keepalive: true }).catch(() => {}); } catch (_) {}
  }
  let soon = null;
  function pulse(ev, detail){
    if (off) return; queue.push([ev, String(detail)]);
    if (queue.length >= 30) send();
    clearTimeout(soon); soon = setTimeout(send, 1500);           // most counts leave long before the page does
  }
  setInterval(send, 8000);
  addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(); });
  addEventListener("pagehide", send);
  document.addEventListener("click", e => { const t = e.target.closest("[data-pulse]"); if (t){ const [a, b] = t.dataset.pulse.split(":"); pulse(a, b); } }, true);
  /* for the moment just before leaving the page (casting, checkout) */
  const pulseNow = (ev, detail) => { pulse(ev, detail); clearTimeout(soon); send(); };
  window.Wyrd = Object.assign(window.Wyrd || {}, { pulse, pulseNow });
})();
