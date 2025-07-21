# app/db/crud/user_crud.py

import sqlite3
from core.config import settings
from db.session import get_connection
from datetime import datetime

def save_user(tg_id: int, uuid: str, expires_at):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (telegram_id, uuid, expires_at) VALUES (?, ?, ?)", (
        tg_id, uuid, expires_at.isoformat()
    ))
    conn.commit()
    conn.close()


def delete_user_by_uuid(uuid: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE uuid = ?", (uuid,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_user_by_uuid(uuid: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, uuid, expires_at FROM users WHERE uuid = ?", (uuid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "telegram_id": row[1],
            "uuid": row[2],
            "expires_at": datetime.fromisoformat(row[3]),
        }
    return None