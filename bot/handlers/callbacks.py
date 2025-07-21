#bot/handlers/callbacks.py

from aiogram import Router, types
from aiogram.types import CallbackQuery
from bot.services.user_config_service import create_paid_user

callback_handler = Router()

@callback_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery):
    await callback.answer()
    try:
        msg = await create_paid_user(tg_id=callback.from_user.id)
        await callback.message.answer(msg)
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
