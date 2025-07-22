# app/bot/handlers/paid_config.py

import logging
import html
from aiogram import Router
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.enums.parse_mode import ParseMode

from bot.services.user_config_service import create_paid_user
from utils.qr import generate_qr_code

paid_config_handler = Router()

@paid_config_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery):
    await callback.answer()
    try:
        # create_paid_user возвращает tuple (link, days), поэтому распакуем
        config_link, expires_days = await create_paid_user(callback.from_user.id, return_days=True)

        qr_code = generate_qr_code(config_link)
        qr_file = BufferedInputFile(qr_code.getvalue(), filename="qrcode_paid.png")

        caption = (
            f"🔒 <b>Ваш VPN-конфиг готов!</b>\n"
            f"⏳ Срок действия: {expires_days} дней\n\n"
            f"📌 <b>Скопируйте эту ссылку:</b>\n"
            f"<code>{html.escape(config_link)}</code>\n\n"
            f"📲 <b>Как использовать:</b>\n"
            f"1. Отсканируйте QR-код\n"
            f"2. Или вставьте ссылку вручную\n"
            f"3. Для v2RayTun просто вставьте ссылку"
        )

        await callback.message.answer_photo(
            photo=qr_file,
            caption=caption,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logging.error(f"Ошибка при выдаче платного конфига для пользователя {callback.from_user.id}: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при выдаче платного конфига.")
