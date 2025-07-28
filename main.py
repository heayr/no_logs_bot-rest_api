# app/main.py

import asyncio
import logging
import aiogram
from fastapi import FastAPI, Request
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from bot.handlers import payment_handler
from bot.services.user_config_service import handle_payment_callback
from tasks.expired_user_cleaner import remove_expired_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from api.routes import health
from aiogram.types import Message
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="No Logs Bot")

app.include_router(health.router)

# Хендлеры для /start и /help
@payment_handler.message(Command("start"))
async def start_command(msg: Message):
    logging.debug(f"Обработка команды /start от tg_id={msg.from_user.id}")
    await msg.answer("👋 Добро пожаловать в No Logs VPN!\nИспользуйте /subscribe для подписки, /pay для оплаты, /config для получения конфига, или '🎁 Получить тест' для тестового доступа.")

@payment_handler.message(Command("help"))
async def help_command(msg: Message):
    logging.debug(f"Обработка команды /help от tg_id={msg.from_user.id}")
    await msg.answer("ℹ️ Команды:\n/subscribe - оформить подписку\n/pay - оплатить подписку\n/config - получить конфиг\n🎁 Получить тест - тестовый доступ")

# Отладочный хендлер для всех сообщений
@dp.message()
async def debug_all_messages(msg: Message):
    logging.debug(f"Получено сообщение: {msg.text} от tg_id={msg.from_user.id}")
    await msg.answer(f"Сообщение '{msg.text}' получено, но не обработано. Проверяю...")

@app.post("/callback")
async def payment_callback(request: Request):
    data = await request.json()
    success = await handle_payment_callback(data, bot)
    return {"status": "ok" if success else "error"}

@app.on_event("startup")
async def startup():
    logging.info(f"Используем aiogram версии {aiogram.__version__}")
    run_scheduler()
    asyncio.create_task(remove_expired_users())
    logging.info("🚀 Starting up...")
    init_db()
    try:
        dp.include_router(payment_handler)
        logging.info("payment_handler зарегистрирован")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {str(e)}")
        raise
    logging.info("🤖 Telegram bot polling started")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

def run_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_users, IntervalTrigger(minutes=1))
    scheduler.start()