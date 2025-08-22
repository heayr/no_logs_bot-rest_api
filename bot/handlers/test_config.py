# bot/handlers/test_config.py


import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from bot.services.user_config_service import create_test_config
from bot.keyboards.main_menu import get_back_to_menu_button
from utils.qr import generate_qr_code
from core.config import settings

test_config_handler = Router()

@test_config_handler.callback_query(lambda c: c.data == "get_test_config")
async def handle_test_config(callback: types.CallbackQuery):
    """
    Обработчик запроса тестового конфига через callback.
    """
    logging.debug(f"Callback get_test_config от tg_id={callback.from_user.id}")
    try:
        tg_id = callback.from_user.id
        config_link, expires_days, error = await create_test_config(tg_id, minutes=settings.TEST_MINUTES, return_days=True)
        if error:
            logging.error(f"Ошибка создания тестового конфига: tg_id={tg_id}, {error}")
            await callback.message.answer(f"❌ Ошибка: {error}", reply_markup=get_back_to_menu_button(), parse_mode="HTML")
            await callback.answer()
            return

        qr_io = await generate_qr_code(config_link)
        caption = (
            f"🔒 <b>Тестовый доступ готов!</b>\n"
            f"⏳ Срок действия: {expires_days} дней\n\n"
            f"<code>{config_link}</code>\n\n"
            f"📲 Отсканируйте QR-код или скопируйте ссылку."
        )

        if str(tg_id) == str(settings.ADMIN_IDS):
            caption += "\n\n⚙️ Админ-режим: конфиг без ограничений."

        await callback.message.answer_photo(
            photo=BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
            caption=caption,
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
        await callback.answer("Тестовый конфиг отправлен!")
    except Exception as e:
        logging.error(f"Ошибка в handle_test_config: tg_id={tg_id}, {str(e)}", exc_info=True)
        await callback.message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
        await callback.answer()

@test_config_handler.message(Command("admin_test"))
async def handle_admin_test(message: types.Message):
    """
    Обработчик команды /admin_test для создания тестового конфига админом.
    """
    logging.debug(f"Команда /admin_test от tg_id={message.from_user.id}")
    try:
        if str(message.from_user.id) != str(settings.ADMIN_IDS):
            await message.answer("⛔ Эта команда только для администратора", parse_mode="HTML")
            return

        config_link, expires_days, error = await create_test_config(message.from_user.id, minutes=1, return_days=True)
        if error:
            logging.error(f"Ошибка создания админ тестового конфига: tg_id={message.from_user.id}, {error}")
            await message.answer(f"❌ Ошибка: {error}", reply_markup=get_back_to_menu_button(), parse_mode="HTML")
            return

        qr_io = await generate_qr_code(config_link)
        caption = (
            f"⚙️ <b>Тестовый конфиг (админ):</b>\n"
            f"⏳ Срок действия: {expires_days} минут\n\n"
            f"<code>{config_link}</code>\n\n"
            f"📲 Отсканируйте QR-код или скопируйте ссылку."
        )

        await message.answer_photo(
            photo=BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
            caption=caption,
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка в handle_admin_test: tg_id={message.from_user.id}, {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.", reply_markup=get_back_to_menu_button(), parse_mode="HTML")