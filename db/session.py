# app/db/session.py

import sqlite3
from core.config import settings

def get_connection():
    return sqlite3.connect(settings.DATABASE_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Таблица users (без изменений)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            uuid TEXT UNIQUE,
            expires_at TEXT
        )
    """)
    
    # Новая таблица transactions для отслеживания финансов
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            telegram_id INTEGER,
            amount REAL,
            days INTEGER,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            payment_provider TEXT,
            payment_id TEXT
        )
    """)
    
    conn.commit()
    conn.close()