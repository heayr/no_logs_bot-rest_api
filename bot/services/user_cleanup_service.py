# bot/services/user_cleanup_service.py
import logging
import asyncio
from db.crud.user_crud import get_expired_users, delete_user_by_uuid
from .xray_service import remove_client

async def delete_expired_users():
    """
    Удаляет пользователей с истёкшим сроком действия из базы данных и Xray.
    """
    try:
        expired_users = await get_expired_users()  # Предполагается, что get_expired_users асинхронная
        loop = asyncio.get_running_loop()

        for user in expired_users:
            uuid = user["uuid"]
            removed_from_xray = await loop.run_in_executor(None, remove_client, uuid)
            removed_from_db = await loop.run_in_executor(None, delete_user_by_uuid, uuid)
            logging.info(f"Удалён истёкший пользователь: uuid={uuid}, xray={removed_from_xray}, db={removed_from_db}")
    except Exception as e:
        logging.error(f"Ошибка при очистке истёкших пользователей: {str(e)}", exc_info=True)