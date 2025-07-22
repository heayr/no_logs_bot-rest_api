# app/bot/handlers/test_config.py

import logging
from aiogram import Router, types
from aiogram.types import BufferedInputFile
import html
from bot.services.user_config_service import create_test_user
from utils.qr import generate_qr_code  # создадим отдельно
from aiogram.enums.parse_mode import ParseMode

test_config_handler = Router()

@test_config_handler.message(lambda m: m.text == "🎁 Получить тест")
async def handle_test_request(message: types.Message):
    try:
        config_link, expires_days = await create_test_user(message.from_user.id, return_days=True)
        qr_code = generate_qr_code(config_link)

        caption = (
            f"🔒 <b>Ваш VPN-конфиг готов!</b>\n"
            f"⏳ Срок действия: {expires_days} день{'ей' if expires_days != 1 else ''}\n\n"
            f"📌 <b>Скопируйте эту ссылку:</b>\n<code>{html.escape(config_link)}</code>\n\n"
            f"📲 <b>Как использовать:</b>\n"
            f"1. Отсканируйте QR-код\n"
            f"2. Или вставьте ссылку вручную\n"
            f"3. Для v2RayTun просто вставьте ссылку"
        )

        await message.answer_photo(
            photo=BufferedInputFile(qr_code.getvalue(), filename="qrcode.png"),
            caption=caption,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logging.error(f"Ошибка при выдаче тестового конфига: {e}", exc_info=True)
        await message.answer("Произошла ошибка при выдаче конфига.")
