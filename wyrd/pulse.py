"""Pulse: what visitors do on the site, counted anonymously, so the console can
notice what people use and adapt to it.

  * Only named events from a fixed list are counted (which land was opened,
    how far the learning path got, which terms were looked up ...). No birth
    details, no IP addresses, no profiles. A visitor is a random id their
    browser makes up, used only to count visitors per day; the ids themselves
    are never stored.
  * Counts are kept in memory and saved every ten minutes into the repository,
    on a separate branch (DATA_BRANCH, default "wyrd-data") so saving never
    triggers a deploy. Without a GITHUB_TOKEN they live in memory only.
"""
import base64, json, os, re, threading, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPO", "leahimadsen/wyrd-one")
BRANCH = os.environ.get("DATA_BRANCH", "wyrd-data")
FLUSH_EVERY = 600

LANDS = {"map", "learn", "chart", "body", "dharma", "clock", "calendar", "armillary", "reading", "compare", "sky", "colour", "bench"}
EVENTS = {
    "land": lambda d: d in LANDS,
    "move": lambda d: "-" in d and all(x in LANDS for x in d.split("-", 1)),
    "learn": lambda d: d.isdigit() and 1 <= int(d) <= 40,
    "gloss": lambda d: re.fullmatch(r"[a-z0-9]{1,24}", d) is not None,
    "tap": lambda d: d in {"body", "des", "sign", "trop", "rune", "gate", "nak", "house"},
    "compare": lambda d: d in {"2", "3", "4"},
    "cast": lambda d: d in {"known", "unknown"},
    "calendar": lambda d: d in {"all", "you", "clock", "ingress", "station"},
    "act": lambda d: d in {"buy", "share", "save", "download", "install", "sample", "today", "edit", "level"},
}

_lock = threading.Lock()
_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # day -> event -> detail -> n (not yet saved)
_seen = defaultdict(set)                                              # day -> visitor ids (memory only)
_visitors = defaultdict(int)                                          # day -> new distinct visitors (not yet saved)
_last_flush = time.time()
_cache = {"at": 0, "data": None}


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def record(batch, vid):
    """Count a batch from one browser. Anything not on the list is dropped."""
    day = today()
    with _lock:
        if vid and re.fullmatch(r"[a-z0-9]{8,32}", vid) and vid not in _seen[day]:
            _seen[day].add(vid); _visitors[day] += 1
            for old in [d for d in _seen if d != day]: del _seen[old]
        for e in batch[:60]:
            if not isinstance(e, list) or len(e) != 2: continue
            ev, d = str(e[0])[:16], str(e[1])[:40]
            if ev in EVENTS and EVENTS[ev](d):
                _counts[day][ev][d] += 1
    if time.time() - _last_flush > FLUSH_EVERY:
        threading.Thread(target=flush, daemon=True).start()


# ---------- GitHub ----------
def _gh(method, path, body=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "wyrd-console"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read() or b"null")


def _ensure_branch():
    try:
        _gh("GET", f"/branches/{BRANCH}")
    except urllib.error.HTTPError as e:
        if e.code != 404: raise
        base = _gh("GET", "/git/ref/heads/main")["object"]["sha"]
        _gh("POST", "/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": base})


def _read(month):
    try:
        f = _gh("GET", f"/contents/pulse/{month}.json?ref={BRANCH}")
        return json.loads(base64.b64decode(f["content"])), f["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404: return {"days": {}}, None
        raise


def _merge(into, day, counts, visitors):
    d = into["days"].setdefault(day, {"visitors": 0, "events": {}})
    d["visitors"] += visitors
    for ev, details in counts.items():
        for k, n in details.items():
            d["events"].setdefault(ev, {}); d["events"][ev][k] = d["events"][ev].get(k, 0) + n


def flush():
    """Save the unsaved counts into the data branch, month by month."""
    global _last_flush
    with _lock:
        _last_flush = time.time()
        counts = {d: {e: dict(x) for e, x in v.items()} for d, v in _counts.items()}
        visitors = dict(_visitors)
        _counts.clear(); _visitors.clear()
    if not counts and not visitors: return
    if not TOKEN:                                  # nowhere to save: keep them in memory
        _restore(counts, visitors); return
    try:
        _ensure_branch()
        for month in sorted({d[:7] for d in set(counts) | set(visitors)}):
            for attempt in range(3):
                data, sha = _read(month)
                for day in [d for d in set(counts) | set(visitors) if d.startswith(month)]:
                    _merge(data, day, counts.get(day, {}), visitors.get(day, 0))
                body = {"message": f"pulse {month}", "branch": BRANCH,
                        "content": base64.b64encode(json.dumps(data, sort_keys=True).encode()).decode()}
                if sha: body["sha"] = sha
                try:
                    _gh("PUT", f"/contents/pulse/{month}.json", body); break
                except urllib.error.HTTPError as e:
                    if e.code not in (409, 422) or attempt == 2: raise   # someone else saved first: read again
        _cache["at"] = 0
    except Exception:
        _restore(counts, visitors)                 # try again next time


def _restore(counts, visitors):
    with _lock:
        for day, evs in counts.items():
            for ev, details in evs.items():
                for k, n in details.items(): _counts[day][ev][k] += n
        for day, n in visitors.items(): _visitors[day] += n


def data(months=3):
    """Everything counted so far: what is saved, plus what isn't yet."""
    if time.time() - _cache["at"] > 60 or _cache["data"] is None:
        saved = {"days": {}}
        if TOKEN:
            now = datetime.now(timezone.utc)
            for i in range(months):
                y, m = now.year, now.month - i
                while m < 1: y, m = y - 1, m + 12
                try:
                    part, _ = _read(f"{y:04d}-{m:02d}")
                    saved["days"].update(part["days"])
                except Exception:
                    pass
        _cache.update(at=time.time(), data=saved)
    out = json.loads(json.dumps(_cache["data"]))
    with _lock:
        for day in set(_counts) | set(_visitors):
            _merge(out, day, {e: dict(x) for e, x in _counts[day].items()}, _visitors.get(day, 0))
    return out


def next_lands(days=60):
    """For each land, where visitors most often go next."""
    moves = defaultdict(lambda: defaultdict(int))
    cutoff = datetime.fromtimestamp(time.time() - days * 86400, timezone.utc).strftime("%Y-%m-%d")
    for day, d in data().get("days", {}).items():
        if day < cutoff: continue
        for k, n in d["events"].get("move", {}).items():
            a, b = k.split("-", 1)
            if b not in ("map", a): moves[a][b] += n
    return {a: [b for b, _ in sorted(v.items(), key=lambda x: -x[1])[:2]] for a, v in moves.items() if sum(v.values()) >= 5}
