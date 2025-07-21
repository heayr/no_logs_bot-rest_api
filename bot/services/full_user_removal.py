# services/full_user_removal.py
#removed_from_xray = remove_client(uuid)
import logging
import asyncio
from db.crud.user_crud import delete_user_by_uuid
from .xray_service import remove_client

async def full_remove_user(uuid: str) -> dict:
    """
    Удаляет пользователя из Xray и из базы данных.
    Возвращает словарь с результатами.
    """
    try:
        loop = asyncio.get_running_loop()

        # ⬇️ remove_client вызывается в отдельном потоке, так как он синхронный
        removed_from_xray = await loop.run_in_executor(None, remove_client, uuid)

        # ⬇️ delete_user_by_uuid вызывается в отдельном потоке, так как он синхронный
        removed_from_db = await loop.run_in_executor(None, delete_user_by_uuid, uuid)

        logging.info(f"Удаление пользователя {uuid} - Xray: {removed_from_xray}, DB: {removed_from_db}")

        return {
            "status": "ok",
            "uuid": uuid,
            "removed_from_xray": removed_from_xray,
            "removed_from_db": removed_from_db,
        }

    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя {uuid}: {e}")
        return {
            "status": "error",
            "uuid": uuid,
            "error": str(e),
        }
