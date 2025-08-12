# main.py
import aiogram
import asyncio
import logging
from fastapi import FastAPI, Request
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from bot.handlers import register_handlers
from tasks.expired_user_cleaner import remove_expired_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger  # Добавлен импорт
from aiogram.types import Message
from aiogram.filters import Command
from bot.services.user_config_service import handle_payment_callback

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="No Logs Bot")

# Хендлеры для /start и /help
@dp.message(Command("start"))
async def start_command(msg: Message):
    logging.debug(f"Обработка команды /start от tg_id={msg.from_user.id}")
    await msg.answer("👋 Добро пожаловать в No Logs VPN!\nИспользуйте /subscribe для подписки, /pay для оплаты, /config для получения конфига, или '🎁 Получить тест' для тестового доступа.")

@dp.message(Command("help"))
async def help_command(msg: Message):
    logging.debug(f"Обработка команды /help от tg_id={msg.from_user.id}")
    await msg.answer("ℹ️ Команды:\n/subscribe - оформить подписку\n/pay - оплатить подписку\n/config - получить конфиг\n🎁 Получить тест - тестовый доступ")

@app.get("/health")
async def health_check():
    logging.info("Получен запрос на /health")
    return {"status": "ok"}

@app.post("/webhook/yookassa")
async def payment_callback(request: Request):
    try:
        data = await request.json()
        logging.info(f"Получен запрос на /webhook/yookassa: {data}")
        success = await handle_payment_callback(data, bot)
        return {"status": "ok" if success else "error"}
    except Exception as e:
        logging.error(f"Ошибка обработки запроса /webhook/yookassa: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

async def start_polling():
    try:
        logging.info("Запуск aiogram polling")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {str(e)}", exc_info=True)
        raise

def run_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_users, IntervalTrigger(minutes=1))
    scheduler.start()
    logging.info("Планировщик задач запущен")

@app.on_event("startup")
async def startup():
    logging.info(f"Используем aiogram версии {aiogram.__version__}")
    init_db()
    register_handlers(dp)
    logging.info("Все хендлеры зарегистрированы")
    run_scheduler()
    asyncio.create_task(start_polling())
    logging.info("🚀 FastAPI и aiogram запущены")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)