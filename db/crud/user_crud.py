# db/crud/user_crud.py


import sqlite3
from datetime import datetime
import logging
from core.config import settings

def get_active_user_by_tg_id(telegram_id: int) -> dict | None:
    """
    Получает активного пользователя по Telegram ID.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT telegram_id, uuid, expires_at FROM users WHERE telegram_id = ? AND expires_at > ?",
            (telegram_id, datetime.now().isoformat())
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"telegram_id": user[0], "uuid": user[1], "expires_at": user[2]}
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении пользователя: telegram_id={telegram_id}, {str(e)}")
        return None

def get_expired_users() -> list:
    """
    Получает список пользователей с истёкшим сроком действия конфига.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT telegram_id, uuid, expires_at FROM users WHERE expires_at <= ?",
            (datetime.now().isoformat(),)
        )
        users = cursor.fetchall()
        conn.close()
        return [{"telegram_id": user[0], "uuid": user[1], "expires_at": user[2]} for user in users]
    except Exception as e:
        logging.error(f"Ошибка при получении истёкших пользователей: {str(e)}")
        return []

def save_user(telegram_id: int, uuid: str, expires: datetime) -> None:
    """
    Сохраняет пользователя в базу данных.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (telegram_id, uuid, expires_at) VALUES (?, ?, ?)",
            (telegram_id, uuid, expires.isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Ошибка при сохранении пользователя: telegram_id={telegram_id}, uuid={uuid}, {str(e)}")

def delete_user_by_uuid(uuid: str) -> bool:
    """
    Удаляет пользователя из базы данных по UUID.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE uuid = ?", (uuid,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя: uuid={uuid}, {str(e)}")
        return False