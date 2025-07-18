# app/bot/handlers/start.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

start_handler = Router()

@start_handler.message(Command("start"))
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🎁 Получить тест")]],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать! Получите тестовый конфиг на 1 день:", reply_markup=kb)
