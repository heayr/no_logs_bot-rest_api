# app/db/session.py

import sqlite3
from core.config import settings

def get_connection():
    return sqlite3.connect(settings.DATABASE_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            uuid TEXT UNIQUE,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()
