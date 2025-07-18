# app/main.py

import asyncio
import logging
from fastapi import FastAPI
from bot.bot import dp, bot
from core.config import settings
from db.session import init_db
from bot.handlers import register_handlers

app = FastAPI(title="VPN Bot API")

@app.on_event("startup")
async def startup():
    logging.info("🚀 Starting up...")
    init_db()
    register_handlers(dp)
    asyncio.create_task(dp.start_polling(bot))
    logging.info("🤖 Telegram bot polling started")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
