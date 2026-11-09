"""
db.py  —  OWNER: Person A (Cyber / Replit owner)
The shared database. The bot writes reports here; the dashboard reads them.
This is the ONLY thing the two halves of the project share.
"""
import sqlite3
from datetime import datetime

DB_PATH = "haqeeq.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    # The registry of genuine official posts (the "trusted source of truth").
    c.execute("""CREATE TABLE IF NOT EXISTS official_posts (
        id TEXT PRIMARY KEY,
        title TEXT,
        issuer TEXT,
        date TEXT,
        hash8 TEXT,
        hash16 TEXT,
        image_path TEXT
    )""")
    # Every message a citizen forwards, plus the verdict the engine gave it.
    c.execute("""CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        sender TEXT,
        kind TEXT,
        verdict TEXT,
        matched_id TEXT,
        distance INTEGER,
        emirate TEXT,
        detail TEXT,
        image_path TEXT
    )""")
    # Official government entities / domains (seeded from open data) for the trusted list.
    c.execute("""CREATE TABLE IF NOT EXISTS entities (
        name TEXT,
        kind TEXT,
        source TEXT
    )""")
    conn.commit()
    conn.close()


def add_report(sender, kind, verdict, matched_id=None, distance=None,
               emirate=None, detail=None, image_path=None):
    conn = get_conn()
    conn.execute(
        """INSERT INTO reports
           (ts, sender, kind, verdict, matched_id, distance, emirate, detail, image_path)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (datetime.utcnow().isoformat(timespec="seconds"), sender, kind, verdict,
         matched_id, distance, emirate, detail, image_path),
    )
    conn.commit()
    conn.close()


def get_reports(limit=100):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_official_posts():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM official_posts").fetchall()
    conn.close()
    return [dict(r) for r in rows]
