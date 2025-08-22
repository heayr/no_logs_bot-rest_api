# bot/handlers/start.py
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards.main_menu import get_main_inline_menu

start_handler = Router()

@start_handler.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start. Показывает приветственное сообщение и главное меню.
    """
    logging.debug(f"Команда /start от tg_id={message.from_user.id}")
    try:
        reply_markup = get_main_inline_menu()
        logging.debug(f"Отправка сообщения с клавиатурой: {reply_markup}")
        await message.answer(
            "🔒 Добро пожаловать в No Logs — безопасный выход в интернет!\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка в cmd_start: tg_id={message.from_user.id}, {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")