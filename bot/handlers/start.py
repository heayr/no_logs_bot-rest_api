# bot/handlers/start.py
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu

start_handler = Router()

@start_handler.message(Command("start"))
async def start_cmd(message: Message):
    """
    Обработчик команды /start.
    """
    logging.debug(f"Команда /start от tg_id={message.from_user.id}")
    try:
        await message.answer(
            "👋 Привет! Я помогу тебе настроить безопасный выход в интернет.\n\n"
            "Выбери действие в меню ниже:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка в start_cmd: tg_id={message.from_user.id}, {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")

@start_handler.message(Command("help"))
async def help_cmd(message: Message):
    """
    Обработчик команды /help.
    """
    logging.debug(f"Команда /help от tg_id={message.from_user.id}")
    try:
        await message.answer(
            "ℹ️ <b>О боте</b>\n\n"
            "Я помогу тебе настроить безопасный выход в интернет:\n"
            "- 🎁 <b>Тестовый доступ</b>: Получи бесплатный конфиг на 60 минут\n"
            "- 💳 <b>Оформить подписку</b>: Активируй подписку за 200 RUB на 30 дней\n"
            "- 🔄 <b>Мой конфиг</b>: Просмотри текущий конфиг\n"
            "- ℹ️ <b>О подписке</b>: Узнай подробности\n\n"
            "Выбери действие в меню:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка в help_cmd: tg_id={message.from_user.id}, {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")
