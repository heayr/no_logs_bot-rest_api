# app/bot/bot.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from core.config import settings

session = AiohttpSession()

bot = Bot(
    token=settings.API_TOKEN,
    session=session,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # 👈 вот так теперь
)

dp = Dispatcher()
