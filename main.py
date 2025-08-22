# main.py


import aiogram
import asyncio
import logging
from fastapi import FastAPI, Request
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from tasks.expired_user_cleaner import remove_expired_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.services.user_config_service import handle_payment_callback

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="No Logs Bot")

# --- Healthcheck ---
@app.get("/health")
async def health_check():
    logging.info("Получен запрос на /health")
    return {"status": "ok"}

# --- Webhook для Юкассы ---
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

# --- Aiogram polling ---
async def start_polling():
    try:
        logging.info("Запуск aiogram polling")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {str(e)}", exc_info=True)
        raise

# --- Планировщик очистки ---
def run_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_users, IntervalTrigger(minutes=1))
    scheduler.start()
    logging.info("Планировщик задач запущен")

# --- Startup ---
@app.on_event("startup")
async def startup():
    logging.info(f"Используем aiogram версии {aiogram.__version__}")
    init_db()
    run_scheduler()
    asyncio.create_task(start_polling())
    logging.info("🚀 FastAPI и aiogram запущены")

# --- Точка входа ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)