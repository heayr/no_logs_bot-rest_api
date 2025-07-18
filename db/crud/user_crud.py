# app/db/crud/user_crud.py

import sqlite3
from core.config import settings

def save_user(tg_id: int, uuid: str, expires_at):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (telegram_id, uuid, expires_at) VALUES (?, ?, ?)", (
        tg_id, uuid, expires_at.isoformat()
    ))
    conn.commit()
    conn.close()
