# app/bot/handlers/__init__.py

from aiogram import Dispatcher
from .start import start_handler
from .test_config import test_config_handler
from .paid_config import paid_config_handler


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        start_handler,
        test_config_handler,
	paid_config_handler
    )
