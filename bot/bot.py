# app/bot/bot.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from core.config import settings

session = AiohttpSession()
bot = Bot(token=settings.API_TOKEN, parse_mode=ParseMode.HTML, session=session)
dp = Dispatcher()
