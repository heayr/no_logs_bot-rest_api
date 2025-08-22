# bot/handlers/paid_config.py


import logging
from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from datetime import datetime
from bot.services.user_config_service import send_payment_link
from db.crud.transaction_crud import get_confirmed_transaction, save_pending_transaction
from bot.keyboards.main_menu import get_back_to_menu_button, get_main_inline_menu

payment_handler = Router()

@payment_handler.callback_query(lambda c: c.data == "get_paid_config")
async def handle_paid_config(callback: CallbackQuery, bot: Bot):
    """
    Обработчик запроса платного конфига или ссылки на оплату.
    """
    logging.debug(f"Callback get_paid_config от tg_id={callback.from_user.id}")
    tg_id = callback.from_user.id
    try:
        # Проверяем, есть ли активная подтверждённая транзакция
        transaction = get_confirmed_transaction(tg_id)
        if transaction:
            logging.info(f"Найдена активная транзакция для tg_id={tg_id}, перенаправляем в меню")
            await callback.message.answer(
                "✅ У вас уже есть активная подписка. Нажмите '🔄 Мой конфиг', чтобы посмотреть детали.",
                reply_markup=get_main_inline_menu(),
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # Если транзакции нет, создаём ссылку на оплату
        amount = 200.00  # Цена подписки, замените на нужную
        days = 30
        order_id = f"order_{tg_id}_{callback.message.chat.id}_{int(datetime.now().timestamp())}"
        payment_url, payment_id = await send_payment_link(bot, callback.message.chat.id, tg_id, amount, order_id)
        if payment_url:
            success = await save_pending_transaction(tg_id, order_id, amount, days, payment_id)
            if not success:
                logging.error(f"Ошибка сохранения транзакции: tg_id={tg_id}, order_id={order_id}")
                await callback.message.answer(
                    "❌ Ошибка при сохранении транзакции. Попробуйте позже.",
                    reply_markup=get_back_to_menu_button(),
                    parse_mode="HTML"
                )
                await callback.answer()
                return
        await callback.answer("Ссылка на оплату отправлена!")
    except Exception as e:
        logging.error(f"Ошибка в handle_paid_config: tg_id={tg_id}, {str(e)}", exc_info=True)
        await callback.message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_back_to_menu_button(),
            parse_mode="HTML"
        )
        await callback.answer()

@payment_handler.callback_query(lambda c: c.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery):
    """
    Обработчик возврата в главное меню.
    """
    logging.debug(f"Callback back_to_menu от tg_id={callback.from_user.id}")
    try:
        await callback.message.answer(
            "🔒 Выберите действие:",
            reply_markup=get_main_inline_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка в handle_back_to_menu: tg_id={callback.from_user.id}, {str(e)}", exc_info=True)
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")
        await callback.answer()