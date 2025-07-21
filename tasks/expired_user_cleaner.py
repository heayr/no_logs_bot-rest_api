import asyncio
import logging
from datetime import datetime
from db.session import get_connection
from bot.services.user_config_service import delete_user  # async функция удаления пользователя
from db.crud.user_crud import delete_user_by_uuid

async def remove_expired_users():
    logging.info("🧹 Проверка истёкших пользователей...")

    conn = get_connection()
    cursor = conn.cursor()

    # Достаем пользователей с истекшим сроком
    cursor.execute("SELECT uuid FROM users WHERE expires_at < ?", (datetime.utcnow().isoformat(),))
    expired = cursor.fetchall()

    if not expired:
        logging.info("✅ Нет просроченных пользователей")
        conn.close()
        return

    for (uuid,) in expired:
        try:
            logging.info(f"Удаляем пользователя с uuid={uuid}")
            delete_user_by_uuid(uuid)
        except Exception as e:
            logging.error(f"❌ Ошибка при удалении {uuid}: {e}")

    conn.close()
