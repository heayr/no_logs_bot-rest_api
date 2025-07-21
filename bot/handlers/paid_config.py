#bot/handlers/paid_config.py


import logging
from aiogram import Router, types
from aiogram.types import CallbackQuery
from bot.services.user_config_service import create_paid_user

paid_config_handler = Router()

@paid_config_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery):
    await callback.answer()
    try:
        config_link = await create_paid_user(callback.from_user.id)
        await callback.message.answer(f"🔐 Ваш конфиг на 30 дней:\n\n<code>{config_link}</code>")
    except Exception as e:
        logging.error(f"Ошибка при выдаче платного конфига для пользователя {callback.from_user.id}: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при выдаче платного конфига.")
