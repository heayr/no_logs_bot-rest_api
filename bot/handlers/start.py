# bot/handlers/start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu


start_handler = Router()


@start_handler.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! 👋\n\nВыберите действие:",
        reply_markup=main_menu
    )



