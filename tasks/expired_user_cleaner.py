import logging
from db.crud.user_crud import get_expired_users, delete_user_by_uuid
from bot.services.xray_service import remove_client

def remove_expired_users() -> None:
    """
    Удаляет пользователей с истёкшим сроком действия из базы данных и Xray.
    """
    try:
        expired_users = get_expired_users()
        for user in expired_users:
            telegram_id = user["telegram_id"]
            uuid = user["uuid"]
            logging.info(f"Удаление истёкшего пользователя: telegram_id={telegram_id}, uuid={uuid}")
            if remove_client(uuid):
                delete_user_by_uuid(uuid)
                logging.info(f"Пользователь удалён: telegram_id={telegram_id}, uuid={uuid}")
            else:
                logging.error(f"Не удалось удалить клиента из Xray: uuid={uuid}")
    except Exception as e:
        logging.error(f"Ошибка при удалении истёкших пользователей: {str(e)}")