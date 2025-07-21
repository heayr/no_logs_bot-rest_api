# app/main.py

import asyncio
import logging
from fastapi import FastAPI
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from bot.handlers import register_handlers
from api.routes import users, health
from tasks.expired_user_cleaner import remove_expired_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = FastAPI(title="No Logs Bot")

app.include_router(users.router)
app.include_router(health.router)

@app.on_event("startup")
async def startup():
    #asyncio.create_task(run_scheduler())
    run_scheduler()
    asyncio.create_task(remove_expired_users())
    logging.info("🚀 Starting up...")
    init_db()
    register_handlers(dp)
    asyncio.create_task(dp.start_polling(bot))
    logging.info("🤖 Telegram bot polling started")

@app.get("/health")
async def health_check():
    return {"status": "ok"}


#async def run_scheduler():
#    while True:
#        await remove_expired_users()
#        await asyncio.sleep(3600)  # каждые 60 минут


def run_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_users, IntervalTrigger(minutes=1))
    scheduler.start()