import asyncio
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from core.config import settings
from bot.services.xray_service import add_client
from db.crud.user_crud import save_user
from utils.formatters import generate_vless_link, format_expiration_message

async def create_test_user(tg_id: int = 0) -> str:
    uid = str(uuid4())
    expires = datetime.utcnow() + timedelta(days=settings.TEST_DAYS)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, add_client, uid)
    await loop.run_in_executor(None, save_user, tg_id, uid, expires)

    host = settings.AVAILABLE_IPS[0]
    pbk = settings.XRAY_PUBLIC_KEY
    sid = settings.XRAY_SHORT_ID
    sni = settings.XRAY_SNI
    port = 443

    link = generate_vless_link(uid, host, port, pbk, sid, sni)
    days = (expires - datetime.utcnow()).days
    message = format_expiration_message(link, days)

    logging.info(f"Created test user {uid} (tg_id={tg_id})")
    return message
