# bot/middlewares/active_config_check.py

import logging
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from db.crud.user_crud import get_active_user_by_tg_id
from core.config import settings

class ActiveConfigCheckMiddleware(BaseMiddleware):
    """
    Middleware для проверки активного конфига перед callback'ами.
    """
    async def __call__(self, handler, event: CallbackQuery, data: dict):
        tg_id = event.from_user.id
        if str(tg_id) == str(settings.ADMIN_IDS):
            return await handler(event, data)  # Админы пропускаются

        if event.data in ["get_test_config", "get_paid_config"]:
            user = get_active_user_by_tg_id(tg_id)
            if user:
                logging.info(f"Активный конфиг найден для tg_id={tg_id}, прерываем обработку")
                await event.message.answer(
                    "🔒 У вас уже есть активный конфиг. Пожалуйста, используйте его.",
                    parse_mode="HTML"
                )
                await event.answer()
                return  # Прерываем обработку
        return await handler(event, data)  # Продолжаем обработку