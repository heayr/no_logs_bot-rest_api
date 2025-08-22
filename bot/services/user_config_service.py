import logging
import uuid
import io
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yookassa import Payment
from db.crud.user_crud import save_user, get_active_user_by_tg_id
from db.crud.transaction_crud import save_pending_transaction, get_transaction_by_id, update_transaction_status
from bot.services.xray_service import add_client, remove_client
from core.config import settings
import qrcode

def generate_vless_link(uuid: str) -> str:
    """
    Генерирует VLESS-ссылку для заданного UUID.
    """
    return f"vless://{uuid}@{settings.SERVER_IP}:{settings.SERVER_PORT}?security=reality&pbk={settings.REALITY_PBK}&sni={settings.SNI}&sid={settings.REALITY_SID}#NoLogs_{uuid}"

async def create_test_config(telegram_id: int, bot: Bot = None, minutes: int = 60, return_days: bool = False) -> tuple[str, float, str | None]:
    """
    Создаёт тестовый конфиг для пользователя.
    """
    try:
        user = get_active_user_by_tg_id(telegram_id)
        if user:
            logging.info(f"Пользователь уже имеет активный конфиг: telegram_id={telegram_id}, uuid={user['uuid']}")
            config_link = generate_vless_link(user['uuid'])
            expires_days = (datetime.fromisoformat(user['expires_at']) - datetime.now()).total_seconds() / (60 * 60 * 24)
            return config_link, expires_days, None

        new_uuid = str(uuid.uuid4())
        expires = datetime.now() + timedelta(minutes=minutes)
        expires_days = minutes / (60 * 24) if return_days else 0

        if add_client(new_uuid):
            save_user(telegram_id, new_uuid, expires)
            config_link = generate_vless_link(new_uuid)
            logging.info(f"Тестовый конфиг создан: telegram_id={telegram_id}, uuid={new_uuid}, expires={expires.isoformat()}")
            return config_link, expires_days, None
        else:
            logging.error(f"Не удалось добавить клиента в Xray: uuid={new_uuid}")
            return "", 0, "Ошибка при создании тестового конфига."
    except Exception as e:
        logging.error(f"Ошибка при создании тестового конфига: telegram_id={telegram_id}, {str(e)}")
        return "", 0, str(e)

async def send_payment_link(bot: Bot, chat_id: int, telegram_id: int, amount: float, order_id: str) -> tuple[str, str]:
    """
    Создаёт платёж через ЮKassa и возвращает ссылку на оплату и ID платежа.
    """
    try:
        user = get_active_user_by_tg_id(telegram_id)
        if user:
            logging.info(f"Пользователь уже имеет активный конфиг: telegram_id={telegram_id}, uuid={user['uuid']}")
            vless_link = generate_vless_link(user['uuid'])
            back_button = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
            ])
            await bot.send_message(chat_id, f"У вас уже есть активный конфиг:\n{vless_link}", reply_markup=back_button)
            return "", ""

        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/LudensTest_bot"
            },
            "capture": False,
            "description": f"No Logs подписка для {order_id}",
            "metadata": {
                "order_id": order_id,
                "telegram_id": str(telegram_id),
                "cms_name": "yookassa_sdk_python"
            }
        })

        logging.info(f"Платёж создан: payment_id={payment.id}, telegram_id={telegram_id}")
        payment_url = payment.confirmation.confirmation_url
        back_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ])
        await bot.send_message(chat_id, f"Ссылка для оплаты: {payment_url}", reply_markup=back_button)
        logging.info(f"Отправка платёжной ссылки: telegram_id={telegram_id}, order_id={order_id}")
        return payment_url, payment.id
    except Exception as e:
        logging.error(f"Ошибка при создании платежа: telegram_id={telegram_id}, {str(e)}")
        await bot.send_message(chat_id, "Ошибка при создании платежа. Попробуйте позже.")
        return "", ""

async def handle_payment_callback(data: dict, bot: Bot) -> None:
    """
    Обрабатывает вебхук от ЮKassa и создаёт платный конфиг.
    """
    try:
        payment_data = data.get('object', {})
        payment_status = payment_data.get('status')
        payment_id = payment_data.get('id')
        metadata = payment_data.get('metadata', {})
        telegram_id = int(metadata.get('telegram_id'))
        order_id = metadata.get('order_id')

        logging.info(f"Обработка вебхука ЮKassa: {data}")

        if payment_status != 'succeeded':
            logging.info(f"Платёж не успешен: status={payment_status}, telegram_id={telegram_id}")
            return

        transaction = get_transaction_by_id(order_id)
        if not transaction:
            logging.error(f"Транзакция не найдена: order_id={order_id}")
            await bot.send_message(telegram_id, "Ошибка: транзакция не найдена.")
            return

        if transaction['status'] == 'succeeded':
            logging.info(f"Транзакция уже обработана: order_id={order_id}, telegram_id={telegram_id}")
            return

        user = get_active_user_by_tg_id(telegram_id)
        if user:
            logging.info(f"Пользователь уже имеет активный конфиг: telegram_id={telegram_id}, uuid={user['uuid']}")
            await send_config(telegram_id, user['uuid'], bot, is_test=False)
            return

        logging.info(f"Создание платного пользователя: telegram_id={telegram_id}, days={transaction['days']}")
        new_uuid = str(uuid.uuid4())
        expires = datetime.now() + timedelta(days=transaction['days'])

        if add_client(new_uuid):
            save_user(telegram_id, new_uuid, expires)
            update_transaction_status(order_id, "succeeded")
            logging.info(f"Создан платный конфиг: telegram_id={telegram_id}, uuid={new_uuid}, expires={expires.isoformat()}")
            await send_config(telegram_id, new_uuid, bot, is_test=False)
        else:
            logging.error(f"Не удалось добавить клиента в Xray: uuid={new_uuid}")
            await bot.send_message(telegram_id, "Ошибка при создании конфига. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука ЮKassa: {str(e)}", exc_info=True)
        await bot.send_message(telegram_id, "Произошла ошибка при обработке платежа.")

async def send_config(telegram_id: int, uuid: str, bot: Bot, is_test: bool = False) -> None:
    """
    Отправляет конфиг пользователю в виде QR-кода и VLESS-ссылки.
    """
    try:
        vless_link = generate_vless_link(uuid)
        logging.info(f"Генерация VLESS-ссылки: uuid={uuid}, ip={settings.SERVER_IP}, port={settings.SERVER_PORT}")
        logging.info(f"VLESS-ссылка создана: {vless_link}")

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(vless_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        back_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ])
        await bot.send_photo(
            telegram_id,
            photo=img_byte_arr,
            caption=f"{'Тестовый' if is_test else 'Платный'} конфиг:\n{vless_link}",
            reply_markup=back_button
        )
        logging.info(f"Конфиг отправлен: telegram_id={telegram_id}, uuid={uuid}, is_test={is_test}")
    except Exception as e:
        logging.error(f"Ошибка при отправке конфига: telegram_id={telegram_id}, uuid={uuid}, {str(e)}")
        await bot.send_message(telegram_id, "Ошибка при отправке конфига. Попробуйте позже.")