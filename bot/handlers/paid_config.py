# app/bot/handlers/paid_config.py
import logging
import html
from datetime import datetime
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, input_file
from aiogram.filters import Command
from db.crud.transaction_crud import save_pending_transaction, get_confirmed_transaction
from bot.services.user_config_service import send_payment_link, create_paid_user
from utils.qr import generate_qr_code
from db.session import get_connection

payment_handler = Router()
logging.info("Инициализация payment_handler")


async def process_payment_request(bot: Bot, chat_id: int, tg_id: int):
    """Создать платёж и отправить интерфейс оплаты.
    Отправка сообщений/QR выполняется внутри send_payment_link (во избежание дублей).
    """
    amount = 200
    days = 30
    order_id = f"order_{tg_id}_{chat_id}_{int(datetime.now().timestamp())}"

    payment_url, payment_id = await send_payment_link(bot, chat_id, tg_id, amount, order_id)
    if not payment_url:
        return

    success = await save_pending_transaction(tg_id, order_id, amount, days, payment_id)
    if not success:
        await bot.send_message(chat_id, "❌ Ошибка при сохранении транзакции. Попробуйте позже.", parse_mode="HTML")
        raise Exception("Не удалось сохранить транзакцию")

    logging.info(f"Платёжная ссылка выдана (без дублей QR) для tg_id={tg_id}, order_id={order_id}, payment_id={payment_id}")

@payment_handler.message(Command("subscribe"))
async def subscribe_command(msg: Message, bot: Bot):
    """Меню подписки — только кнопка оплаты."""
    tg_id = msg.from_user.id
    logging.debug(f"Хендлер /subscribe сработал для tg_id={tg_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить подписку", callback_data="subscribe")]
    ])
    await msg.answer(
        "💳 Оплатите 200 RUB для активации подписки. Конфиг придёт автоматически после оплаты.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@payment_handler.message(Command("pay"))
async def pay_command(msg: Message, bot: Bot):
    tg_id = msg.from_user.id
    logging.debug(f"Хендлер /pay сработал для tg_id={tg_id}")
    await process_payment_request(bot, msg.chat.id, tg_id)

@payment_handler.callback_query(lambda c: c.data == "subscribe")
async def handle_start_payment(callback: CallbackQuery, bot: Bot):
    tg_id = callback.from_user.id
    logging.debug(f"Хендлер subscribe (callback) сработал для tg_id={tg_id}")
    await process_payment_request(bot, callback.message.chat.id, tg_id)
    await callback.answer()

@payment_handler.message(Command("config"))
async def config_command(msg: Message, bot: Bot):
    tg_id = msg.from_user.id
    transaction = get_confirmed_transaction(tg_id)

    if not transaction:
        await msg.answer("❌ Нет подтверждённых платежей. Используйте /pay для оплаты.", parse_mode="HTML")
        return

    config_link, expires_days, error = await create_paid_user(tg_id, days=transaction["days"], return_days=True)
    if error:
        await msg.answer(f"❌ Ошибка: {error}", parse_mode="HTML")
        return

    qr_io = await generate_qr_code(config_link)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
    ])

    caption = (
        f"🔒 <b>Ваш конфиг готов!</b>\n"
        f"⏳ Срок действия: {expires_days} дней\n\n"
        f"📌 <b>Скопируйте эту ссылку:</b>\n"
        f"<code>{html.escape(config_link)}</code>\n\n"
        f"📲 <b>Как использовать:</b>\n"
        f"1. Отсканируйте QR-код\n"
        f"2. Или вставьте ссылку вручную"
    )

    await bot.send_photo(
        msg.chat.id,
        photo=input_file.BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@payment_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery, bot: Bot):
    tg_id = callback.from_user.id
    transaction = get_confirmed_transaction(tg_id)

    if not transaction:
        await callback.message.answer("❌ Нет подтверждённых платежей. Используйте /pay для оплаты.", parse_mode="HTML")
        await callback.answer()
        return

    config_link, expires_days, error = await create_paid_user(tg_id, days=transaction["days"], return_days=True)
    if error:
        await callback.message.answer(f"❌ Ошибка: {error}", parse_mode="HTML")
        await callback.answer()
        return

    qr_io = await generate_qr_code(config_link)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
    ])

    caption = (
        f"🔒 <b>Ваш конфиг готов!</b>\n"
        f"⏳ Срок действия: {expires_days} дней\n\n"
        f"📌 <b>Скопируйте эту ссылку:</b>\n"
        f"<code>{html.escape(config_link)}</code>\n\n"
        f"📲 <b>Как использовать:</b>\n"
        f"1. Отсканируйте QR-код\n"
        f"2. Или вставьте ссылку вручную"
    )

    await bot.send_photo(
        callback.message.chat.id,
        photo=input_file.BufferedInputFile(qr_io.getvalue(), filename="qr_code.png"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer("Конфиг отправлен!")

@payment_handler.callback_query(lambda c: c.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery):
    # Показываем компактное меню действий
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Получить конфиг на 30 дней", callback_data="get_paid_config")],
        [InlineKeyboardButton(text="💳 Оплатить подписку", callback_data="subscribe")]
    ])
    await callback.message.answer("Главное меню. Выберите действие:", reply_markup=menu)
    await callback.answer()
