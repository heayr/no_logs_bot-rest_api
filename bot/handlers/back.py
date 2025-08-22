# bot/handlers/back.py
import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.main_menu import get_main_inline_menu

back_handler = Router()

@back_handler.callback_query(lambda c: c.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery):
    """
    Обработчик возврата в главное меню.
    """
    logging.debug(f"Callback back_to_menu от tg_id={callback.from_user.id}")
    try:
        await callback.message.answer(
            "🔒 Выберите действие:",
            reply_markup=get_main_inline_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка в handle_back_to_menu: tg_id={callback.from_user.id}, {str(e)}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")
        await callback.answer()