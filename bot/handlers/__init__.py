# bot/handlers/__init__.py
import logging
from aiogram import Dispatcher
from .start import start_handler
from .test_config import test_config_handler
from .paid_config import payment_handler
from .back import back_handler
from .admin import admin_handler
from .active_config import active_config_handler
from bot.middlewares.active_config_check import ActiveConfigCheckMiddleware

def register_handlers(dp: Dispatcher):
    logging.info("Регистрация роутеров в Dispatcher")
    dp.include_routers(
        start_handler,
        test_config_handler,
        payment_handler,
        back_handler,
        admin_handler,
        active_config_handler
    )
    dp.callback_query.middleware(ActiveConfigCheckMiddleware())
    logging.info(f"Роутеры зарегистрированы: {start_handler, test_config_handler, payment_handler, back_handler, admin_handler, active_config_handler}")