"""The site's own records: what the Order keeps for its members and the Inner Circle for its
practitioners. Everything else (payments, plans, the birth chart for Body Weather) stays in Stripe.

    DATABASE_URL=postgres://...   Postgres in production: Neon's free tier (neon.tech), or any Postgres
    (unset)                        SQLite, in DATA_DIR/wyrd.db (local runs and tests)

Tables, each keyed to the member's or practitioner's email:
  letters    every Monday's Body Weather letter, so members can reread past weeks
  kin        charts a member keeps for loved ones
  practice   a practitioner's practice name
  clients    a practitioner's clients: name, birth details, email, notes
  readings   every client reading generated, with a private token for its share link
"""
import json, os, secrets, sqlite3, threading, time

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS letters (email TEXT NOT NULL, week TEXT NOT NULL, html TEXT NOT NULL,
         created DOUBLE PRECISION NOT NULL, PRIMARY KEY (email, week))""",
    """CREATE TABLE IF NOT EXISTS kin (id TEXT PRIMARY KEY, email TEXT NOT NULL, label TEXT NOT NULL,
         birth TEXT NOT NULL, created DOUBLE PRECISION NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS practice (email TEXT PRIMARY KEY, name TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY, pro TEXT NOT NULL, name TEXT NOT NULL, email TEXT,
         birth TEXT NOT NULL, notes TEXT, created DOUBLE PRECISION NOT NULL, updated DOUBLE PRECISION NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS readings (token TEXT PRIMARY KEY, pro TEXT NOT NULL, client TEXT, name TEXT NOT NULL,
         birth TEXT NOT NULL, created DOUBLE PRECISION NOT NULL, sent_to TEXT)""",
    "CREATE INDEX IF NOT EXISTS kin_email ON kin (email)",
    "CREATE INDEX IF NOT EXISTS clients_pro ON clients (pro)",
    "CREATE INDEX IF NOT EXISTS readings_pro ON readings (pro)",
]
KIN_MAX = 8                  # charts a member may keep for loved ones
CLIENT_MAX = 500             # a generous ceiling, so a mistake can't fill the database

_lock, _ready = threading.Lock(), False


def url():
    return os.environ.get("DATABASE_URL", "").strip()


def _connect():
    u = url()
    if u:
        import psycopg
        if u.startswith("postgres://"): u = "postgresql://" + u[len("postgres://"):]
        return psycopg.connect(u, autocommit=True), "%s"
    path = os.environ.get("WYRD_DB_PATH") or os.path.join(
        os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")), "wyrd.db")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path, timeout=10); db.isolation_level = None
    return db, "?"


def _run(sql, args=(), fetch=None):
    """One statement on a fresh connection. SQL is written with ? and turned into %s for Postgres."""
    global _ready
    db, mark = _connect()
    try:
        cur = db.cursor()
        if not _ready:
            with _lock:
                if not _ready:
                    for s in SCHEMA: cur.execute(s)
                    _ready = True
        cur.execute(sql.replace("?", mark), args)
        if fetch == "one":
            row = cur.fetchone(); cols = [c[0] for c in cur.description] if cur.description else []
            return dict(zip(cols, row)) if row else None
        if fetch == "all":
            cols = [c[0] for c in cur.description] if cur.description else []
            return [dict(zip(cols, r)) for r in cur.fetchall()]
        return cur.rowcount
    finally:
        db.close()


def reset_for_tests():
    global _ready
    _ready = False


def _new_id(): return secrets.token_urlsafe(9)
def _clean(email): return (email or "").strip().lower()


# ---------------- the Order: letters ----------------
def save_letter(email, week, html):
    email = _clean(email)
    _run("DELETE FROM letters WHERE email = ? AND week = ?", (email, week))
    _run("INSERT INTO letters (email, week, html, created) VALUES (?, ?, ?, ?)", (email, week, html, time.time()))


def letters(email):
    return _run("SELECT week, created FROM letters WHERE email = ? ORDER BY week DESC", (_clean(email),), "all")


def letter(email, week):
    return _run("SELECT week, html, created FROM letters WHERE email = ? AND week = ?", (_clean(email), week), "one")


# ---------------- the Order: charts for loved ones ----------------
def kin(email):
    rows = _run("SELECT id, label, birth, created FROM kin WHERE email = ? ORDER BY created", (_clean(email),), "all")
    for r in rows: r["birth"] = json.loads(r["birth"])
    return rows


def kin_one(email, kid):
    r = _run("SELECT id, label, birth FROM kin WHERE email = ? AND id = ?", (_clean(email), kid), "one")
    if r: r["birth"] = json.loads(r["birth"])
    return r


def add_kin(email, label, birth):
    email = _clean(email)
    if len(kin(email)) >= KIN_MAX: raise ValueError(f"You can keep up to {KIN_MAX} charts.")
    kid = _new_id()
    _run("INSERT INTO kin (id, email, label, birth, created) VALUES (?, ?, ?, ?, ?)",
         (kid, email, label[:60], json.dumps(birth), time.time()))
    return kid


def remove_kin(email, kid):
    return _run("DELETE FROM kin WHERE email = ? AND id = ?", (_clean(email), kid))


# ---------------- the Inner Circle: the practice ----------------
def practice_name(email):
    r = _run("SELECT name FROM practice WHERE email = ?", (_clean(email),), "one")
    return r["name"] if r else ""


def set_practice_name(email, name):
    email, name = _clean(email), (name or "").strip()[:80]
    _run("DELETE FROM practice WHERE email = ?", (email,))
    if name: _run("INSERT INTO practice (email, name) VALUES (?, ?)", (email, name))


# ---------------- the Inner Circle: clients ----------------
def clients(pro):
    rows = _run("SELECT id, name, email, birth, notes, created, updated FROM clients WHERE pro = ? ORDER BY name", (_clean(pro),), "all")
    for r in rows: r["birth"] = json.loads(r["birth"])
    return rows


def client(pro, cid):
    r = _run("SELECT id, name, email, birth, notes, created, updated FROM clients WHERE pro = ? AND id = ?", (_clean(pro), cid), "one")
    if r: r["birth"] = json.loads(r["birth"])
    return r


def save_client(pro, name, birth, email="", notes="", cid=None):
    pro, now = _clean(pro), time.time()
    if cid:
        n = _run("UPDATE clients SET name = ?, email = ?, birth = ?, notes = ?, updated = ? WHERE pro = ? AND id = ?",
                 (name[:80], _clean(email)[:120], json.dumps(birth), (notes or "")[:4000], now, pro, cid))
        if not n: raise KeyError("no such client")
        return cid
    if len(clients(pro)) >= CLIENT_MAX: raise ValueError("Your client list is full.")
    cid = _new_id()
    _run("INSERT INTO clients (id, pro, name, email, birth, notes, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
         (cid, pro, name[:80], _clean(email)[:120], json.dumps(birth), (notes or "")[:4000], now, now))
    return cid


def remove_client(pro, cid):
    return _run("DELETE FROM clients WHERE pro = ? AND id = ?", (_clean(pro), cid))


# ---------------- the Inner Circle: readings ----------------
def add_reading(pro, name, birth, client_id=None):
    token = secrets.token_urlsafe(18)
    _run("INSERT INTO readings (token, pro, client, name, birth, created) VALUES (?, ?, ?, ?, ?, ?)",
         (token, _clean(pro), client_id, name[:80], json.dumps(birth), time.time()))
    return token


def readings(pro, client_id=None):
    if client_id:
        rows = _run("SELECT token, client, name, created, sent_to FROM readings WHERE pro = ? AND client = ? ORDER BY created DESC",
                    (_clean(pro), client_id), "all")
    else:
        rows = _run("SELECT token, client, name, created, sent_to FROM readings WHERE pro = ? ORDER BY created DESC", (_clean(pro),), "all")
    return rows


def reading_by_token(token):
    r = _run("SELECT token, pro, client, name, birth, created, sent_to FROM readings WHERE token = ?", (token,), "one")
    if r: r["birth"] = json.loads(r["birth"])
    return r


def mark_sent(pro, token, to):
    return _run("UPDATE readings SET sent_to = ? WHERE pro = ? AND token = ?", (_clean(to)[:120], _clean(pro), token))
