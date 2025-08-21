# bot/handlers/back.py
from aiogram import Router, types
from bot.keyboards.main_menu import main_menu

back_handler = Router()

@back_handler.callback_query(lambda c: c.data == "back_to_menu")
async def handle_back(callback: types.CallbackQuery):
    await callback.message.answer("Вы вернулись в главное меню 👇", reply_markup=main_menu)
    await callback.answer()
