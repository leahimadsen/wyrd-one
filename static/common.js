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

/* ---------- Old Style dates ----------
   These places still kept the old Julian calendar within the site's years, so a birth record of the time runs
   12 days behind today's calendar (13 from March 1900). When the birthplace and date fall before the change
   there, the form asks which calendar the date is in; wyrd/oldstyle.py turns an Old Style date into the day the
   chart is cast for. Each row: country codes (or time zones), the first Gregorian day there, a name, a note.
   Dates from Wikipedia's "List of adoption dates of the Gregorian calendar by country". Places that changed
   before 1850 (Britain 1752, Sweden and Finland 1753) only need rows if the site's years reach back that far. */
const OLD_STYLE = [
  { cc: ["RU"], until: "1918-02-14", where: "Russia" },
  { cc: ["KZ", "UZ", "TM", "KG", "TJ"], until: "1918-02-14", where: "The Russian Empire" },
  { cc: ["BY"], until: "1918-02-14", where: "Belarus", note: "The Grodno region changed earlier, in September 1915." },
  { cc: ["UA"], until: "1918-03-01", where: "Ukraine", note: "The far west, then part of Austria-Hungary, already kept the Gregorian calendar." },
  { cc: ["EE"], until: "1918-03-01", where: "Estonia" },
  { cc: ["LV"], until: "1915-09-05", where: "Latvia", note: "Courland changed in May 1915, Livonia, with Riga, that September." },
  { cc: ["LT"], until: "1915-05-25", where: "Lithuania" },
  { cc: ["GE", "AM", "AZ"], until: "1918-05-01", where: "The Caucasus" },
  { cc: ["MD"], until: "1919-04-14", where: "Bessarabia", note: "It was Russian until 1918, then Romanian; Romania changed in April 1919." },
  { cc: ["RO"], until: "1919-04-14", where: "Romania", note: "Transylvania, the Banat and Bukovina, then part of Austria-Hungary, already kept the Gregorian calendar." },
  { cc: ["BG"], until: "1916-04-14", where: "Bulgaria" },
  { cc: ["RS"], until: "1919-01-28", where: "Serbia", note: "Vojvodina, then part of Hungary, already kept the Gregorian calendar." },
  { cc: ["ME"], until: "1919-01-28", where: "Montenegro" },
  { cc: ["MK", "XK"], until: "1919-01-28", where: "This region" },
  { cc: ["AL"], until: "1912-11-28", where: "Albania", note: "Catholic records already used the Gregorian calendar." },
  { cc: ["GR"], until: "1923-03-01", where: "Greece", note: "Mount Athos keeps the Julian calendar still." },
  { cc: ["TR"], until: "1917-03-01", where: "Turkey", note: "A Rumi date has the Julian days and months but its own year: change the year to the common era first. Hijri dates aren't covered." },
  { tz: ["America/Sitka", "America/Juneau", "America/Anchorage", "America/Yakutat", "America/Nome", "America/Metlakatla", "America/Adak"],
    until: "1867-10-18", where: "Russian Alaska" },
];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const longDate = s => { const [y, m, d] = s.split("-").map(Number); return `${d} ${MONTHS[m - 1]} ${y}`; };
/* a Julian-calendar YYYY-MM-DD as the same day in today's calendar, through its Julian day number */
function newStyle(date){
  const [y, m, d] = date.split("-").map(Number), a = Math.floor((14 - m) / 12), yy = y + 4800 - a, mm = m + 12 * a - 3;
  const jdn = d + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4) - 32083;
  return new Date((jdn - 2440588) * 86400000).toISOString().slice(0, 10);
}
function oldStyleFor(place, date){
  if (!place || !/^\d{4}-\d{2}-\d{2}$/.test(date || "")) return null;
  return OLD_STYLE.find(r => ((r.cc || []).includes(place.cc) || (r.tz || []).includes(place.tz)) && date < r.until) || null;
}
/* The calendar choice under a date of birth. It shows itself when the place and date call for it, or when the
   date is already marked Old Style (from the date input's data-cal="J", or set()). It sits below the place
   field, since picking the place is what calls it up. A posted form sends it as `name`; the others read
   value(). Tell it the place whenever the place changes. */
function calendarChoice(dateInput, { name = "cal" } = {}){
  const label = document.createElement("label");
  label.className = "f-name f-cal"; label.hidden = true;
  label.innerHTML = `Calendar of this date <span class="cal-why"></span>
    <select name="${esc(name)}"><option value="">New Style (Gregorian)</option><option value="J">Old Style (Julian)</option></select>
    <small class="cal-cast" hidden></small>`;
  const form = dateInput.form || dateInput.closest(".cast") || document, at = [...form.querySelectorAll(".f-place")]
    .find(p => p.closest(".tg-person") === dateInput.closest(".tg-person")) || dateInput.closest("label");
  at.after(label);
  const sel = label.querySelector("select"), why = label.querySelector(".cal-why"), out = label.querySelector(".cal-cast");
  let place = null;
  sel.value = dateInput.dataset.cal === "J" ? "J" : "";
  function update(){
    const date = dateInput.value, r = oldStyleFor(place, date), os = sel.value === "J";
    label.hidden = !r && !os;
    why.textContent = r ? `${r.where} kept the old Julian calendar until ${longDate(r.until)}. A record of the time gives the Old Style date; most modern sources give New Style.${r.note ? " " + r.note : ""}` : "";
    out.hidden = !(os && date);
    if (os && date){
      const ns = newStyle(date), days = Math.round((Date.parse(ns) - Date.parse(date)) / 86400000);
      out.textContent = `Cast for ${longDate(ns)}, ${days} days on, the same day in today's calendar.`;
    }
  }
  dateInput.addEventListener("input", update); dateInput.addEventListener("change", update); sel.addEventListener("change", update);
  update();
  return { value: () => sel.value || undefined, set(v){ sel.value = v === "J" ? "J" : ""; update(); }, place(p){ place = p; update(); } };
}
/* a birth's date for a list: as given, marked when Old Style */
const showDate = b => b.date + (b.cal === "J" ? " O.S." : "");

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

/* ---------- the share link: the birth details ride in the link itself, after the #, which browsers
   never send to a server: they can't land in a log or be told to another site ---------- */
const b64 = s => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64 = s => decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/"))));
const SHARE_KEYS = ["name", "date", "cal", "time", "place_id", "lat", "lon", "tz", "place_label", "unknown_time"];
function shareLink(birth){
  const o = {}; for (const k of SHARE_KEYS) if (birth[k] != null && birth[k] !== "" && birth[k] !== false) o[k] = birth[k];
  return `${location.origin}/chart#b=${b64(JSON.stringify(o))}`;
}
function fromLink(param){
  try { const o = JSON.parse(unb64(param)); return o && o.date && o.time ? o : null; } catch (_) { return null; }
}

/* ---------- charts saved in this browser ---------- */
const SAVE_KEY = "wyrdSaved";
const sameBirth = (a, b) => a.date === b.date && (a.cal || "") === (b.cal || "") && a.time === b.time && String(a.place_id) === String(b.place_id) && (a.name || "") === (b.name || "");
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

window.WyrdCommon = { esc, placeSearch, calendarChoice, newStyle, showDate, cast, keep, current, fresh, shareLink, fromLink, savedList, isSaved, toggleSaved, refreshSaved, removeSaved, standalone, syncInstall };
})();
