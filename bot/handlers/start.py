# app/bot/handlers/start.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

start_handler = Router()

@start_handler.message(Command("start"))
async def cmd_start(message: Message):
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🎁 Получить тест")]],
        resize_keyboard=True
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Получить конфиг на 30 дней", callback_data="get_paid_config")]
    ])

    await message.answer(
        "Добро пожаловать! 👋\n\n🎁 Вы можете получить тестовый конфиг на 1 день кнопкой внизу, либо приобрести доступ на 30 дней.",
        reply_markup=reply_kb
    )
    await message.answer("👇 Или сразу получить доступ на 30 дней:", reply_markup=inline_kb)
