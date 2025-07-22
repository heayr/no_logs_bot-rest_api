# app/bot/handlers/test_config.py

import logging
from core.config import settings
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import html
from bot.services.user_config_service import create_test_user
from utils.qr import generate_qr_code  # создадим отдельно
from aiogram.enums.parse_mode import ParseMode

test_config_handler = Router()

@test_config_handler.message(lambda m: m.text == "🎁 Получить тест")
async def handle_test_request(message: types.Message):
    try:
        config_link, expires_days, error = await create_test_user(
            message.from_user.id, 
            minutes=settings.TEST_MINUTES,
            return_days=True
        )
        
        if error:
            await message.answer(error)
        elif config_link and expires_days is not None:
            response = (
                f"🔒 Ваш тестовый VPN-конфиг:\n\n"
                f"{config_link}\n\n"
                f"⏳ Срок действия: {expires_days} дней\n\n"
                f"Для подключения используйте любой клиент V2RayN."
            )
            # Добавляем пометку для админа
            if str(message.from_user.id) == str(settings.ADMIN_IDS):
                response += "\n\n⚙️ Вы получили конфиг в обход ограничений (режим администратора)"
            await message.answer(response)
        else:
            await message.answer("Не удалось создать конфиг. Попробуйте позже.")
            
    except Exception as e:
        logging.error(f"Ошибка в handle_test_request: {str(e)}", exc_info=True)
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик команды /admin_test (только для админов)
@test_config_handler.message(Command("admin_test"))
async def handle_admin_test(message: types.Message):
    # Проверяем, что это админ
    if str(message.from_user.id) != str(settings.ADMIN_IDS):
        return await message.answer("⛔ Эта команда только для администратора")
    
    # Создаем тестовый конфиг на 1 минуту
    config_link, expires_days, error = await create_test_user(
        message.from_user.id,
        minutes=1,  # Очень короткий срок для тестов
        return_days=True
    )
    
    if config_link:
        await message.answer(
            f"⚙️ Тестовый конфиг (админ-режим):\n\n"
            f"{config_link}\n\n"
            f"Срок действия: {expires_days} минут\n\n"
            f"Этот конфиг создан в обход обычных ограничений."
        )
    elif error:
        await message.answer(f"Ошибка: {error}")
    else:
        await message.answer("Не удалось создать тестовый конфиг")