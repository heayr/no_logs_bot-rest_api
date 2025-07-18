# app/bot/services/user_config_service.py

import uuid
from datetime import datetime, timedelta
from core.config import settings
from db.crud.user_crud import save_user
from bot.services.xray_service import add_to_xray

def create_test_config(tg_id: int) -> str:
    user_uuid = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=settings.TEST_DAYS)

    # Добавим в Xray config.json
    add_to_xray(user_uuid)

    # Сохраняем в БД
    save_user(tg_id, user_uuid, expires_at)

    return f"vless://{user_uuid}@{settings.AVAILABLE_IPS[0]}:443?encryption=none&security=reality&type=tcp#VPN-Try"
