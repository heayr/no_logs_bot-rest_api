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

def get_user_by_tg_id(tg_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, uuid, expires_at FROM users WHERE telegram_id = ?", (tg_id,))
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

def get_active_user_by_tg_id(tg_id: int):
    conn = get_connection()
    c = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    c.execute(
        "SELECT id, telegram_id, uuid, expires_at FROM users WHERE telegram_id = ? AND expires_at > ? ORDER BY expires_at DESC LIMIT 1",
        (tg_id, now_iso)
    )
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

def get_active_user_config(tg_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT uuid, expires_at FROM users WHERE telegram_id = ?", (tg_id,))
    rows = cur.fetchall()
    conn.close()

    now = datetime.utcnow()

    for uuid, expires_at_str in rows:
        expires_at = datetime.fromisoformat(expires_at_str)
        if expires_at > now:
            return {"uuid": uuid, "expires_at": expires_at}

    return None

def has_active_config(tg_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM users WHERE telegram_id = ? AND expires_at > ?",
        (tg_id, now_iso)
    )
    count = c.fetchone()[0]
    conn.close()
    return count > 0