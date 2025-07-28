# app/bot/handlers/paid_config.py

import logging
import html
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, Text
from db.crud.transaction_crud import save_pending_transaction, get_confirmed_transaction
from bot.services.user_config_service import send_payment_link, create_paid_user, create_test_user
from core.config import settings
from io import BytesIO
import qrcode

payment_handler = Router()
logging.info("Инициализация payment_handler")

@payment_handler.message(Command("start"))
async def start_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер /start сработал для tg_id={tg_id}")
        await msg.answer(
            "👋 Добро пожаловать в No Logs VPN!\n"
            "Используйте /subscribe для подписки, /pay для оплаты, /config для получения конфига, или '🎁 Получить тест' для тестового доступа.",
            parse_mode="HTML"
        )
        logging.info(f"Инструкции отправлены для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке /start для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")

@payment_handler.message(Command("help"))
async def help_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер /help сработал для tg_id={tg_id}")
        await msg.answer(
            "ℹ️ Команды:\n"
            "/subscribe - оформить подписку\n"
            "/pay - оплатить подписку\n"
            "/config - получить конфиг\n"
            "🎁 Получить тест - тестовый доступ",
            parse_mode="HTML"
        )
        logging.info(f"Справка отправлена для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке /help для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")

@payment_handler.message(Command("subscribe"))
async def subscribe_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер /subscribe сработал для tg_id={tg_id}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", callback_data="start_payment")],
            [InlineKeyboardButton(text="Получить конфиг", callback_data="get_paid_config")]
        ])
        await msg.answer(
            "💳 Для активации подписки No Logs VPN оплатите 1000 RUB или запросите конфиг, если уже оплатили.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        logging.info(f"Кнопки подписки показаны для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке /subscribe для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")

@payment_handler.message(Command("pay"))
async def pay_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер /pay сработал для tg_id={tg_id}")
        amount = 1000
        days = 30
        order_id = f"order_{tg_id}_{msg.chat.id}_{int(msg.date.timestamp())}"
        
        success = await save_pending_transaction(tg_id, order_id, amount, days)
        if not success:
            raise Exception("Не удалось сохранить транзакцию")
        
        payment_url, payment_id = await send_payment_link(bot, msg.chat.id, tg_id, amount, order_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", url=payment_url)],
            [InlineKeyboardButton(text="Получить конфиг", callback_data="get_paid_config")],
            [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
        ])
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(payment_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)

        await bot.send_photo(
            msg.chat.id,
            photo=qr_io,
            caption=f"💳 Оплатите {amount} RUB для активации подписки No Logs VPN.\n\n📲 Нажмите кнопку ниже или отсканируйте QR-код.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logging.info(f"Платёжная ссылка отправлена для tg_id={tg_id}, order_id={order_id}")
    except Exception as e:
        logging.error(f"Ошибка при создании платежа для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Ошибка при создании платёжной ссылки. Попробуйте позже.", parse_mode="HTML")

@payment_handler.message(Text(equals="🎁 Получить тест"))
async def test_config_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер '🎁 Получить тест' сработал для tg_id={tg_id}")
        config_link, expires_days, error = await create_test_user(tg_id, minutes=1, return_days=True)
        
        if error:
            await msg.answer(f"❌ Ошибка: {error}", parse_mode="HTML")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(config_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
        ])

        caption = (
            f"🎁 <b>Ваш тестовый VPN-конфиг готов!</b>\n"
            f"⏳ Срок действия: {expires_days} дней (1 минута)\n\n"
            f"📌 <b>Скопируйте эту ссылку:</b>\n"
            f"<code>{html.escape(config_link)}</code>\n\n"
            f"📲 <b>Как использовать:</b>\n"
            f"1. Отсканируйте QR-код\n"
            f"2. Или вставьте ссылку вручную\n"
            f"3. Для v2RayTun просто вставьте ссылку"
        )

        await bot.send_photo(
            msg.chat.id,
            photo=qr_io,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logging.info(f"Тестовый конфиг выдан для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при выдаче тестового конфига для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Произошла ошибка при выдаче тестового конфига.", parse_mode="HTML")

@payment_handler.message(Command("config"))
async def config_command(msg: Message, bot: Bot):
    try:
        tg_id = msg.from_user.id
        logging.debug(f"Хендлер /config сработал для tg_id={tg_id}")
        transaction = await get_confirmed_transaction(tg_id)
        
        if not transaction:
            await msg.answer("❌ Нет подтверждённых платежей. Используйте /pay для оплаты.", parse_mode="HTML")
            return

        config_link, expires_days, error = await create_paid_user(tg_id, days=transaction[3], return_days=True)
        
        if error:
            await msg.answer(f"❌ Ошибка: {error}", parse_mode="HTML")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(config_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Получить конфиг", callback_data="get_paid_config")],
            [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
        ])

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
            msg.chat.id,
            photo=qr_io,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logging.info(f"VLESS-ссылка выдана по /config для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при выдаче конфига для tg_id={msg.from_user.id}: {e}")
        await msg.answer("❌ Произошла ошибка при выдаче конфига.", parse_mode="HTML")

@payment_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery, bot: Bot):
    try:
        tg_id = callback.from_user.id
        logging.debug(f"Хендлер get_paid_config сработал для tg_id={tg_id}")
        transaction = await get_confirmed_transaction(tg_id)
        
        if not transaction:
            await callback.message.answer("❌ Нет подтверждённых платежей. Используйте /pay для оплаты.", parse_mode="HTML")
            await callback.answer()
            return

        config_link, expires_days, error = await create_paid_user(tg_id, days=transaction[3], return_days=True)
        
        if error:
            await callback.message.answer(f"❌ Ошибка: {error}", parse_mode="HTML")
            await callback.answer()
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(config_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
        ])

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
            callback.message.chat.id,
            photo=qr_io,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await callback.answer("Конфиг отправлен!")
        logging.info(f"VLESS-ссылка выдана по get_paid_config для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при выдаче конфига для tg_id={callback.from_user.id}: {e}")
        await callback.message.answer("❌ Произошла ошибка при выдаче конфига.", parse_mode="HTML")
        await callback.answer()

@payment_handler.callback_query(lambda c: c.data == "start_payment")
async def handle_start_payment(callback: CallbackQuery, bot: Bot):
    try:
        tg_id = callback.from_user.id
        logging.debug(f"Хендлер start_payment сработал для tg_id={tg_id}")
        amount = 1000
        days = 30
        order_id = f"order_{tg_id}_{callback.message.chat.id}_{int(callback.message.date.timestamp())}"
        
        success = await save_pending_transaction(tg_id, order_id, amount, days)
        if not success:
            raise Exception("Не удалось сохранить транзакцию")
        
        payment_url, payment_id = await send_payment_link(bot, callback.message.chat.id, tg_id, amount, order_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", url=payment_url)],
            [InlineKeyboardButton(text="Получить конфиг", callback_data="get_paid_config")],
            [InlineKeyboardButton(text="Вернуться", callback_data="back_to_menu")]
        ])
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(payment_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        qr_io.seek(0)

        await bot.send_photo(
            callback.message.chat.id,
            photo=qr_io,
            caption=f"💳 Оплатите {amount} RUB для активации подписки No Logs VPN.\n\n📲 Нажмите кнопку ниже или отсканируйте QR-код.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logging.info(f"Платёжная ссылка отправлена для tg_id={tg_id}, order_id={order_id}")
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка при создании платежа для tg_id={callback.from_user.id}: {e}")
        await callback.message.answer("❌ Ошибка при создания платёжной ссылки. Попробуйте позже.", parse_mode="HTML")
        await callback.answer()

@payment_handler.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, bot: Bot):
    try:
        tg_id = callback.from_user.id
        logging.debug(f"Хендлер back_to_menu сработал для tg_id={tg_id}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", callback_data="start_payment")],
            [InlineKeyboardButton(text="Получить конфиг", callback_data="get_paid_config")]
        ])
        await callback.message.edit_text(
            "💳 Для активации подписки No Logs VPN оплатите 1000 RUB или запросите конфиг, если уже оплатили.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        logging.info(f"Возврат в меню для tg_id={tg_id}")
    except Exception as e:
        logging.error(f"Ошибка при возврате в меню для tg_id={callback.from_user.id}: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")
        await callback.answer()