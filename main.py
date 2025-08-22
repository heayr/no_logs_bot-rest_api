# main.py




import asyncio
import logging
import aiogram
from fastapi import FastAPI
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from bot.handlers import register_handlers
from tasks.expired_user_cleaner import remove_expired_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.routes.yookassa_webhook import router as webhook_router

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="No Logs Bot")

app.include_router(webhook_router)

@app.get("/health")
async def health_check():
    logging.info("Получен запрос на /health")
    return {"status": "ok"}

async def start_polling():
    logging.info("Запуск aiogram polling")
    try:
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
    try:
        init_db()
        logging.info("База данных инициализирована")
        register_handlers(dp)
        logging.info("Все хендлеры зарегистрированы")
        run_scheduler()
        asyncio.create_task(start_polling())
        logging.info("🚀 FastAPI и aiogram запущены")
    except Exception as e:
        logging.error(f"Ошибка при запуске приложения: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)