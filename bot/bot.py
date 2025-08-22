# bot/bot.py

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from core.config import settings

# Роутеры
from bot.handlers.start import start_handler
from bot.handlers.test_config import test_config_handler
from bot.handlers.paid_config import payment_handler

# Инициализация бота и диспетчера (как раньше)
bot = Bot(token=settings.API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(start_handler)
dp.include_router(test_config_handler)
dp.include_router(payment_handler)
