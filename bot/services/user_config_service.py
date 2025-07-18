# app/bot/services/user_config_service.py

import asyncio, logging
from datetime import datetime, timedelta
from uuid import uuid4


from core.config import settings
from bot.services.xray_service import add_client
from db.crud.user_crud import save_user   # sync‑функция

async def create_test_user(tg_id: int = 0) -> dict:
    uid = str(uuid4())
    expires = datetime.utcnow() + timedelta(days=settings.TEST_DAYS)

    # Добавляем клиента в Xray
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, add_client, uid)

    # Сохраняем в БД
    await loop.run_in_executor(None, save_user, tg_id, uid, expires)

    # Собираем ссылку с нужными параметрами из настроек
    pbk = settings.XRAY_PUBLIC_KEY  # публичный ключ Reality из конфига
    sid = settings.XRAY_SHORT_ID    # shortId из конфига
    sni = settings.XRAY_SNI         # например "www.cloudflare.com"
    host = settings.AVAILABLE_IPS[0]

    link = (
        f"vless://{uid}@{host}:443"
        f"?encryption=none"
        f"&security=reality"
        f"&flow=xtls-rprx-vision"
        f"&sni={sni}"
        f"&fp=chrome"
        f"&pbk={pbk}"
        f"&sid={sid}"
        f"&type=tcp"
        f"&headerType=none"
        f"#VPN-Test"
    )

    logging.info(f"Created test user {uid} (tg_id={tg_id})")
    return {"uuid": uid, "link": link, "expires_at": expires}
