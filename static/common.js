'use strict';
/* Shared by every page: the place search, casting a chart, the share link
   and the charts this browser has saved. Nothing here leaves the browser
   except the chart request itself. */
(() => {
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));

/* ---------- place search: a combobox on any input + list pair ---------- */
function placeSearch(input, list, onPick){
  let timer = null, ctrl = null, active = -1, results = [];
  const show = items => {
    results = items; active = -1;
    list.innerHTML = items.length ? items.map((p, i) =>
      `<li role="option" id="${list.id}-${i}" data-i="${i}"><b>${esc(p.name)}</b> <span>${esc(p.label.slice(p.name.length + 2))}</span></li>`).join("")
      : `<li class="none">No match yet. Try the nearest larger town, or add the country after a comma.</li>`;
    list.hidden = false; input.setAttribute("aria-expanded", "true");
  };
  const hide = () => { list.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); };
  const pick = i => { const p = results[i]; if (!p) return; input.value = p.label; hide(); onPick(p); };
  input.addEventListener("input", () => {
    onPick(null); clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2){ hide(); return; }
    timer = setTimeout(async () => {
      if (ctrl) ctrl.abort(); ctrl = new AbortController();
      try { show(await (await fetch("/api/places?q=" + encodeURIComponent(q), { signal: ctrl.signal })).json()); } catch (_) {}
    }, 160);
  });
  input.addEventListener("keydown", e => {
    if (list.hidden || !results.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp"){
      e.preventDefault();
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + results.length) % results.length;
      list.querySelectorAll("li").forEach((li, i) => li.classList.toggle("on", i === active));
      input.setAttribute("aria-activedescendant", `${list.id}-${active}`);
    } else if (e.key === "Enter" && active >= 0){ e.preventDefault(); pick(active); }
    else if (e.key === "Escape") hide();
  });
  list.addEventListener("pointerdown", e => { const li = e.target.closest("li[data-i]"); if (li){ e.preventDefault(); pick(+li.dataset.i); } });
  input.addEventListener("blur", () => setTimeout(hide, 120));
}

/* ---------- casting ---------- */
async function cast(birth){
  const r = await fetch("/api/chart", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(birth) });
  let j = {}; try { j = await r.json(); } catch (_) {}
  if (!r.ok) throw new Error(j.error || (r.status === 429 ? "Too many charts in a minute. Wait a moment and try again." : "The chart couldn't be cast."));
  return j;
}
/* charts cast before the engine last changed meaning are re-cast (app.py CHART_V) */
const CHART_V = 8;
const fresh = result => !!(result && result.chart && result.chart.v === CHART_V);
function keep(birth, result){
  try { sessionStorage.setItem("wyrdChart", JSON.stringify({ birth, result })); return true; } catch (_) { return false; }
}
function current(){
  try { return JSON.parse(sessionStorage.getItem("wyrdChart") || "null"); } catch (_) { return null; }
}

/* ---------- the share link: the birth details ride in the link itself ---------- */
const b64 = s => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64 = s => decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/"))));
const SHARE_KEYS = ["name", "date", "time", "place_id", "lat", "lon", "tz", "place_label", "unknown_time"];
function shareLink(birth){
  const o = {}; for (const k of SHARE_KEYS) if (birth[k] != null && birth[k] !== "" && birth[k] !== false) o[k] = birth[k];
  return `${location.origin}/chart?b=${b64(JSON.stringify(o))}`;
}
function fromLink(param){
  try { const o = JSON.parse(unb64(param)); return o && o.date && o.time ? o : null; } catch (_) { return null; }
}

/* ---------- charts saved in this browser ---------- */
const SAVE_KEY = "wyrdSaved";
const sameBirth = (a, b) => a.date === b.date && a.time === b.time && String(a.place_id) === String(b.place_id) && (a.name || "") === (b.name || "");
function savedList(){ try { return JSON.parse(localStorage.getItem(SAVE_KEY) || "[]"); } catch (_) { return []; } }
function writeSaved(list){ try { localStorage.setItem(SAVE_KEY, JSON.stringify(list.slice(0, 40))); return true; } catch (_) { return false; } }
const isSaved = birth => savedList().some(s => sameBirth(s, birth));
/* a saved chart keeps its last cast too, so it can open without a connection */
function toggleSaved(birth, result){
  const list = savedList(), i = list.findIndex(s => sameBirth(s, birth));
  if (i >= 0) list.splice(i, 1); else list.unshift({ ...birth, savedAt: Date.now(), result });
  if (!writeSaved(list) && i < 0){ list[0].result = undefined; writeSaved(list); }   // storage full: keep the details at least
  return i < 0;
}
function refreshSaved(birth, result){
  const list = savedList(), i = list.findIndex(s => sameBirth(s, birth));
  if (i >= 0){ list[i].result = result; list[i].castAt = Date.now(); writeSaved(list); }
}
function removeSaved(i){ const list = savedList(); list.splice(i, 1); writeSaved(list); }

/* ---------- the installable app ---------- */
if ("serviceWorker" in navigator && location.protocol !== "file:")
  addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => {}));
const standalone = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
let deferred = null;
function syncInstall(){
  const can = !standalone() && (deferred || isIOS);
  document.querySelectorAll("[data-install]").forEach(b => { b.hidden = !can; });
}
addEventListener("beforeinstallprompt", e => { e.preventDefault(); deferred = e; syncInstall(); });
addEventListener("appinstalled", () => { deferred = null; syncInstall(); });
document.addEventListener("click", async e => {
  const b = e.target.closest("[data-install]"); if (!b) return;
  e.preventDefault();
  if (window.Wyrd && Wyrd.pulse) Wyrd.pulse("act", "install");
  if (deferred){ deferred.prompt(); await deferred.userChoice.catch(() => {}); deferred = null; syncInstall(); return; }
  if (isIOS) iosHelp();
});
function iosHelp(){
  if (document.getElementById("iosHelp")) return;
  const d = document.createElement("div");
  d.id = "iosHelp"; d.className = "ios-help"; d.setAttribute("role", "dialog"); d.setAttribute("aria-label", "Add to Home Screen");
  d.innerHTML = `<p><b>Add The Wyrd Console to your Home Screen</b></p>
    <ol><li>Tap the Share button in Safari (the square with an arrow pointing up).</li><li>Choose <b>Add to Home Screen</b>, then <b>Add</b>.</li></ol>
    <p class="fine">It opens full screen with its own icon, and your saved charts open even offline.</p>
    <button type="button" class="ios-x">Got it</button>`;
  document.body.appendChild(d);
  d.querySelector(".ios-x").addEventListener("click", () => d.remove());
  d.querySelector(".ios-x").focus();
}
document.addEventListener("DOMContentLoaded", syncInstall);
if (document.readyState !== "loading") syncInstall();

window.WyrdCommon = { esc, placeSearch, cast, keep, current, fresh, shareLink, fromLink, savedList, isSaved, toggleSaved, refreshSaved, removeSaved, standalone, syncInstall };
})();
