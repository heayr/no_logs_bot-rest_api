# bot/handlers/active_config.py
import logging
from datetime import datetime  # Добавлен импорт
from aiogram import Router, types
from aiogram.types import BufferedInputFile
from bot.services.user_config_service import generate_vless_link
from db.crud.user_crud import get_active_user_by_tg_id
from bot.keyboards.main_menu import get_back_to_menu_button
from core.config import settings
from utils.qr import generate_qr_code

active_config_handler = Router()

@active_config_handler.callback_query(lambda c: c.data == "get_active_config")
async def handle_active_config(callback: types.CallbackQuery):
    """
    Обработчик для получения активного конфига.
    """
    logging.debug(f"Callback get_active_config от tg_id={callback.from_user.id}")
    try:
        tg_id = callback.from_user.id
        user = get_active_user_by_tg_id(tg_id)
        if not user or "expires_at" not in user:
            logging.info(f"Активный конфиг не найден: tg_id={tg_id}")
            await callback.message.answer(
                "❌ У вас нет активного конфига. Получите тестовый доступ или оплатите подписку.",
                reply_markup=get_back_to_menu_button(),
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # Преобразуем expires_at в datetime, если это строка
        expires_at = user["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)

        config_link = generate_vless_link(
            user["uuid"],
            settings.AVAILABLE_IPS[0],
            443,
            settings.XRAY_PUBLIC_KEY,
            settings.XRAY_SHORT_ID,
            settings.XRAY_SNI
        )
        expires_days = (expires_at - datetime.now()).days
        if expires_days < 0:
            expires_days = 0  # Если срок истёк, показываем 0 дней

        qr_io = await generate_qr_code(config_link)
        caption = (
            f"🔒 <b>Ваш текущий конфиг</b>\n"
            f"⏳ Срок действия: {expires_days} дней\n\n"
            f"<code>{config_link}</code>\n\n"
            f"📲 Отсканируйте QR-код или скопируйте ссылку."
        )
        await callback.message.answer_photo(
            photo=BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
            caption=caption,
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
        await callback.answer("Активный конфиг отправлен!")
    except Exception as e:
        logging.error(f"Ошибка в handle_active_config: tg_id={tg_id}, {str(e)}", exc_info=True)
        await callback.message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
        await callback.answer()