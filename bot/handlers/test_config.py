# app/bot/handlers/test_config.py

import logging
from aiogram import Router, types
from bot.services.user_config_service import create_test_user

test_config_handler = Router()

@test_config_handler.message(lambda m: m.text == "🎁 Получить тест")
async def handle_test_request(message: types.Message):
    try:
        config_link = await create_test_user(message.from_user.id)
        await message.answer(f"Вот ваш конфиг на 1 день:\n\n<code>{config_link}</code>")
    except Exception as e:
        logging.error(f"Ошибка при выдаче тестового конфига для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при выдаче конфига.")
