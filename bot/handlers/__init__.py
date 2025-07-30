# app/bot/handlers/__init__.py

import logging
from aiogram import Dispatcher
from .start import start_handler
from .test_config import test_config_handler
from .paid_config import payment_handler

def register_handlers(dp: Dispatcher):
    logging.info("Регистрация роутеров в Dispatcher")
    dp.include_routers(
        start_handler,
        test_config_handler,
        payment_handler
    )
    logging.info(f"Роутеры зарегистрированы: {start_handler, test_config_handler, payment_handler}")