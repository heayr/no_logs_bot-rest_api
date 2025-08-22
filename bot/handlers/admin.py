# bot/handlers/admin.py
import logging
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot.services.xray_service import remove_client
from db.crud.user_crud import delete_user_by_uuid

admin_router = Router()

@admin_router.message(Command("admin_remove_user"))
async def handle_admin_remove_user(message: Message, bot: Bot) -> None:
    try:
        # Проверяем, что команда отправлена админом
        tg_id = message.from_user.id
        # Здесь должна быть проверка, является ли tg_id админом (например, через settings.ADMIN_IDS)
        # if tg_id not in settings.ADMIN_IDS:
        #     await message.answer("У вас нет прав для этой команды.")
        #     return

        # Получаем UUID из аргументов команды
        args = message.text.split()
        if len(args) != 2:
            await message.answer("Использование: /admin_remove_user <uuid>")
            return

        uuid = args[1]

        # Удаляем клиента из Xray
        xray_success = await remove_client(uuid)
        if not xray_success:
            logging.error(f"Не удалось удалить клиента из Xray: uuid={uuid}")
            await message.answer(f"Ошибка при удалении клиента из Xray: uuid={uuid}")
            return

        # Удаляем пользователя из базы данных
        db_success = await delete_user_by_uuid(uuid)
        if not db_success:
            logging.error(f"Не удалось удалить пользователя из базы: uuid={uuid}")
            await message.answer(f"Ошибка при удалении пользователя из базы: uuid={uuid}")
            return

        logging.info(f"Удаление пользователя {uuid} - Xray: {xray_success}, DB: {db_success}")
        await message.answer(f"Пользователь {uuid} успешно удалён.")

    except Exception as e:
        logging.error(f"Ошибка в handle_admin_remove_user: tg_id={tg_id}, {str(e)}", exc_info=True)
        await message.answer(f"Ошибка: {str(e)}")

admin_handler = admin_router