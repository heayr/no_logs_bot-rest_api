# bot/keyboards/main_menu.py
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_inline_menu() -> InlineKeyboardMarkup:
    """
    Возвращает инлайн-клавиатуру главного меню.
    """
    logging.debug("Создание главного меню")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Получить тестовый доступ", callback_data="get_test_config")],
        [InlineKeyboardButton(text="💳 Оплатить подписку", callback_data="get_paid_config")],
        [InlineKeyboardButton(text="🔄 Мой конфиг", callback_data="get_active_config")]
    ])
    logging.debug(f"Главное меню создано: {keyboard}")
    return keyboard

def get_back_to_menu_button() -> InlineKeyboardMarkup:
    """
    Возвращает инлайн-кнопку для возврата в главное меню.
    """
    logging.debug("Создание кнопки 'Назад'")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])
    logging.debug(f"Кнопка 'Назад' создана: {keyboard}")
    return keyboard