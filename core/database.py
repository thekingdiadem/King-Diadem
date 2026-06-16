"""
core/database.py — KING DIADEM
SQLite database — users + payments + decisions + sessions
thread-safe + WAL mode
"""
import sqlite3
import os
import threading

DB_FILE = os.getenv("DB_FILE", "king_diadem.db")
_local = threading.local()


def get_db() -> sqlite3.Connection:
    """คืน connection ที่ thread-safe"""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    """สร้าง tables ทั้งหมด — idempotent"""
    conn = get_db()
    c = conn.cursor()

    # Users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email       TEXT UNIQUE NOT NULL,
        password    TEXT,
        api_key     TEXT,
        credits     REAL    DEFAULT 10.0,
        plan        TEXT    DEFAULT 'basic',
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_seen   DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Payments
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email       TEXT    NOT NULL,
        amount      REAL    NOT NULL,
        plan        TEXT    DEFAULT 'basic',
        stripe_id   TEXT,
        status      TEXT    DEFAULT 'pending',
        timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Decision log
    c.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id  TEXT,
        email       TEXT,
        input       TEXT,
        route       TEXT,
        risk_score  REAL,
        ai_response TEXT,
        timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Sessions
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id          TEXT PRIMARY KEY,
        email       TEXT,
        title       TEXT,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Index
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_payments_email ON payments(email)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_decisions_email ON decisions(email)")

    conn.commit()
    print("✅ DB initialized")
