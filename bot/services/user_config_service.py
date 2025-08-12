# bot/services/user_config_service.py
import asyncio
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from core.config import settings
from bot.services.xray_service import add_client, remove_client
from db.crud.user_crud import save_user, get_active_user_by_tg_id, get_connection, delete_user_by_uuid
from db.crud.transaction_crud import confirm_transaction
from utils.formatters import generate_vless_link, format_expiration_message
from yookassa import Configuration, Payment
from yookassa.domain.request import PaymentRequest
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, input_file
from io import BytesIO
from PIL import Image
import qrcode
import html

# Настройка ЮKassa
Configuration.account_id = "1133698"
Configuration.secret_key = "test_XzPhDavE0PF5MfRT4zY22gdRU_K0PUsFGX-d8ZWrso0"

async def create_payment(tg_id: int, amount: float, order_id: str):
    try:
        idempotence_key = str(uuid4())
        payment_request = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"t.me/{settings.BOT_NAME}"
            },
            "description": f"No Logs VPN подписка для {order_id}",
            "metadata": {
                "order_id": order_id,
                "tg_id": str(tg_id)
            },
            "receipt": {
                "customer": {
                    "email": f"user_{tg_id}@example.com"
                },
                "items": [
                    {
                        "description": "Подписка No Logs VPN на 30 дней",
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{amount:.2f}",
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "payment_subject": "service",
                        "payment_mode": "full_payment"
                    }
                ]
            }
        }
        
        payment = Payment.create(payment_request, idempotence_key)
        return payment.confirmation.confirmation_url, payment.id
    except Exception as e:
        logging.error(f"Ошибка при создании платежа ЮKassa: {str(e)}", exc_info=True)
        raise

async def send_payment_link(bot: Bot, chat_id: int, tg_id: int, amount: float, order_id: str):
    try:
        payment_url, payment_id = await create_payment(tg_id, amount, order_id)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(payment_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", url=payment_url)]
        ])
        
        await bot.send_message(
            chat_id,
            f"💳 Оплатите {amount} RUB для активации подписки No Logs VPN.\n\n"
            f"📲 Нажмите кнопку ниже или отсканируйте QR-код.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await bot.send_photo(
            chat_id,
            photo=input_file.BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
            caption="Отсканируйте QR-код для оплаты",
            parse_mode="HTML"
        )
        logging.info(f"Платёжная ссылка отправлена для tg_id={tg_id}, order_id={order_id}")
        return payment_url, payment_id
    except Exception as e:
        logging.error(f"Ошибка при отправке платёжной ссылки для tg_id={tg_id}: {str(e)}", exc_info=True)
        await bot.send_message(
            chat_id,
            "❌ Произошла ошибка при создании платёжной ссылки. Пожалуйста, попробуйте позже.",
            parse_mode="HTML"
        )
        raise

async def handle_payment_callback(data: dict, bot: Bot):
    try:
        logging.info(f"Обработка callback ЮKassa: {data}")
        event = data.get("event")
        payment = data.get("object")
        order_id = payment["metadata"]["order_id"]
        tg_id = int(payment["metadata"]["tg_id"])
        payment_id = payment["id"]

        if event not in ["payment.succeeded", "payment.waiting_for_capture"]:
            logging.error(f"Неподдерживаемое событие ЮKassa: {event}")
            return False

        if event == "payment.waiting_for_capture":
            logging.info(f"Подтверждение платежа payment_id={payment_id} для order_id={order_id}")
            try:
                # Подтверждаем платёж
                idempotence_key = str(uuid4())  # Уникальный ключ для capture
                payment_response = Payment.capture(payment_id, idempotence_key)
                if payment_response.status == "succeeded":
                    logging.info(f"Платёж payment_id={payment_id} успешно подтверждён")
                else:
                    logging.error(f"Не удалось подтвердить платёж payment_id={payment_id}: {payment_response.status}")
                    return False
            except Exception as e:
                logging.error(f"Ошибка при подтверждении платежа payment_id={payment_id}: {str(e)}", exc_info=True)
                return False
            return True  # Ждём payment.succeeded

        if event == "payment.succeeded":
            logging.debug(f"Обработка payment.succeeded для order_id={order_id}, tg_id={tg_id}")
            transaction = await confirm_transaction(order_id)
            if not transaction:
                logging.error(f"Транзакция {order_id} не найдена или уже подтверждена")
                return False

            config_link, expires_days, error = await create_paid_user(tg_id, days=transaction["days"], return_days=True)
            if error:
                logging.error(f"Ошибка при создании конфига для tg_id={tg_id}: {error}")
                await bot.send_message(tg_id, f"❌ Ошибка при создании конфига: {error}")
                return False

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(config_link)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_io = BytesIO()
            qr_img.save(qr_io, format="PNG")
            qr_io.seek(0)

            caption = (
                f"🔒 <b>Ваш VPN-конфиг готов!</b>\n"
                f"⏳ Срок действия: {expires_days} дней\n\n"
                f"📌 <b>Скопируйте эту ссылку:</b>\n"
                f"<code>{html.escape(config_link)}</code>\n\n"
                f"📲 <b>Как использовать:</b>\n"
                f"1. Отсканируйте QR-код\n"
                f"2. Или вставьте ссылку вручную\n"
                f"3. Для v2RayTun просто вставьте ссылку"
            )

            await bot.send_photo(
                tg_id,
                photo=input_file.BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
                caption=caption,
                parse_mode="HTML"
            )
            logging.info(f"VLESS-ссылка выдана для tg_id={tg_id}, order_id={order_id}")
            return True
    except Exception as e:
        logging.error(f"Ошибка обработки callback ЮKassa: {str(e)}", exc_info=True)
        return False

async def create_paid_user(tg_id: int = 0, days: int = 30, transaction_id: str = None, return_days: bool = False):
    try:
        if not transaction_id:
            logging.warning(f"Тестирование create_paid_user без transaction_id для tg_id={tg_id}")

        user = get_active_user_by_tg_id(tg_id)
        if user:
            uid = user["uuid"]
            expires = datetime.utcnow() + timedelta(days=days)
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET expires_at = ? WHERE uuid = ?",
                (expires.isoformat(), uid)
            )
            conn.commit()
            conn.close()
            
            logging.info(f"Updated paid user {uid} (tg_id={tg_id}, new_expires={expires})")
        else:
            uid = str(uuid4())
            expires = datetime.utcnow() + timedelta(days=days)

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, add_client, uid)
            await loop.run_in_executor(None, save_user, tg_id, uid, expires)

            logging.info(f"Created new paid user {uid} (tg_id={tg_id}, expires={expires})")

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
        logging.error(f"Ошибка при создании/продлении платного конфига: {str(e)}", exc_info=True)
        if return_days:
            return None, None, str(e)
        return f"Ошибка при создании/продлении конфига: {str(e)}"

async def create_test_user(tg_id: int = 0, minutes: int = 1, return_days: bool = False):
    try:
        is_admin = str(tg_id) == str(settings.ADMIN_IDS)
        
        if not is_admin and get_active_user_by_tg_id(tg_id):
            if return_days:
                return None, None, "У вас уже есть активный конфиг. Пожалуйста, используйте его."
            return "У вас уже есть активный конфиг. Пожалуйста, используйте его."
        
        uid = str(uuid4())
        expires = datetime.utcnow() + timedelta(minutes=minutes)
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, add_client, uid)
        await loop.run_in_executor(None, save_user, tg_id, uid, expires)

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
        logging.error(f"Ошибка при создании тестового конфига: {str(e)}", exc_info=True)
        if return_days:
            return None, None, str(e)
        return f"Ошибка при создании конфига: {str(e)}"

async def delete_user(uuid: str) -> bool:
    loop = asyncio.get_running_loop()

    removed_from_xray = await loop.run_in_executor(None, remove_client, uuid)
    deleted_from_db = await loop.run_in_executor(None, delete_user_by_uuid, uuid)

    return removed_from_xray and deleted_from_db