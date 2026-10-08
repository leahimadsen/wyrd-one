'use strict';
/* music: browsers only allow sound after a tap, so it starts on the button */
(() => {
  const a = document.getElementById("music"), b = document.getElementById("musicBtn");
  if (!a || !b) return;
  fetch(a.getAttribute("src"), { method: "HEAD" }).then(r => { if (r.ok) b.hidden = false; }).catch(() => {});
  a.volume = 0.35;
  const set = on => { b.setAttribute("aria-pressed", on); b.textContent = on ? "♪ Music on" : "♪ Music"; };
  b.addEventListener("click", () => {
    if (a.paused){ a.play().then(() => set(true)).catch(() => {}); try { localStorage.setItem("wyrdMusic", "1"); } catch (_) {} }
    else { a.pause(); set(false); try { localStorage.setItem("wyrdMusic", "0"); } catch (_) {} }
  });
  /* if they turned it on last visit, resume on their first tap anywhere */
  let wanted = false; try { wanted = localStorage.getItem("wyrdMusic") === "1"; } catch (_) {}
  if (wanted) document.addEventListener("pointerdown", function once(e){
    if (e.target === b) return;
    a.play().then(() => set(true)).catch(() => {});
    document.removeEventListener("pointerdown", once);
  });
})();
