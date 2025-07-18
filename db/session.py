# app/db/session.py

import sqlite3
from core.config import settings

def init_db():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            uuid TEXT,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()
