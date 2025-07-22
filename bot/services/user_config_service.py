#/bot/services/user_config_service.py

import asyncio
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from core.config import settings
from bot.services.xray_service import add_client, remove_client 
from db.crud.user_crud import save_user, get_user_by_tg_id, get_connection, get_user_by_tg_id, get_active_user_by_tg_id, delete_user_by_uuid
from utils.formatters import generate_vless_link, format_expiration_message

async def create_test_user(tg_id: int = 0, minutes: int = 1, return_days: bool = False):
    try:
        # Проверяем, является ли пользователь админом
        is_admin = str(tg_id) == str(settings.ADMIN_IDS)
        
        # Если не админ и есть активный конфиг - возвращаем ошибку
        if not is_admin and get_active_user_by_tg_id(tg_id):
            if return_days:
                return None, None, "У вас уже есть активный конфиг. Пожалуйста, используйте его."
            return "У вас уже есть активный конфиг. Пожалуйста, используйте его."
        
        uid = str(uuid4())
        expires = datetime.utcnow() + timedelta(minutes=minutes)
        
        # Сохраняем в Xray и базу данных
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, add_client, uid)
        await loop.run_in_executor(None, save_user, tg_id, uid, expires)

        # Генерируем ссылку
        host = settings.AVAILABLE_IPS[0]
        pbk = settings.XRAY_PUBLIC_KEY
        sid = settings.XRAY_SHORT_ID
        sni = settings.XRAY_SNI
        port = 443

        link = generate_vless_link(uid, host, port, pbk, sid, sni)
        days_left = max(0, (expires - datetime.utcnow()).days)

        if return_days:
            return link, days_left, None
        return format_expiration_message(link, days_left)
        
    except Exception as e:
        logging.error(f"Ошибка при создании тестового конфига: {str(e)}")
        if return_days:
            return None, None, str(e)
        return f"Ошибка при создании конфига: {str(e)}"

async def create_paid_user(tg_id: int = 0, days: int = 30, return_days: bool = False) -> str:
    # Проверяем, есть ли уже активный конфиг
    user = get_active_user_by_tg_id(tg_id)
    if user:
        # Если есть активный конфиг, продлеваем его
        uid = user["uuid"]
        expires = user["expires_at"] + timedelta(days=days)
        
        # Обновляем срок действия в базе
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET expires_at = ? WHERE uuid = ?",
            (expires.isoformat(), uid)
        )
        conn.commit()
        conn.close()
        
        logging.info(f"Extended paid user {uid} (tg_id={tg_id}, new_expires={expires})")
    else:
        # Создаем новый конфиг
        uid = str(uuid4())
        expires = datetime.utcnow() + timedelta(days=days)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, add_client, uid)
        await loop.run_in_executor(None, save_user, tg_id, uid, expires)

        logging.info(f"Created new paid user {uid} (tg_id={tg_id}, expires={expires})")

    # Формируем ссылку
    host = settings.AVAILABLE_IPS[0]
    pbk = settings.XRAY_PUBLIC_KEY
    sid = settings.XRAY_SHORT_ID
    sni = settings.XRAY_SNI
    port = 443

    link = generate_vless_link(uid, host, port, pbk, sid, sni)
    days_left = (expires - datetime.utcnow()).days
    message = format_expiration_message(link, days_left)

    if return_days:
        return link, days_left
    return message

async def delete_user(uuid: str) -> bool:
    loop = asyncio.get_running_loop()

    # Удаляем из xray config
    removed_from_xray = await loop.run_in_executor(None, remove_client, uuid)

    # Удаляем из базы
    deleted_from_db = await loop.run_in_executor(None, delete_user_by_uuid, uuid)

    return removed_from_xray and deleted_from_db