# bot/keyboards/main_menu.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """
    Создаёт главное меню с кнопками для тестового доступа, оплаты подписки, активного конфига и информации о подписке.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Тестовый доступ", callback_data="get_test_config")],
        [InlineKeyboardButton(text="💳 Оформить подписку", callback_data="get_paid_config")],
        [InlineKeyboardButton(text="🔄 Мой конфиг", callback_data="get_active_config")],
        [InlineKeyboardButton(text="ℹ️ О подписке", callback_data="get_subscription_info")]
    ])
    return keyboard

def subscribe_menu() -> InlineKeyboardMarkup:
    """
    Создаёт меню для подписки с кнопкой оплаты и возврата в главное меню.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить подписку", callback_data="get_paid_config")],
        [InlineKeyboardButton(text="⬅️ Вернуться в меню", callback_data="back_to_menu")]
    ])
    return keyboard

def get_main_inline_menu() -> InlineKeyboardMarkup:
    """
    Создаёт главное меню (алиас для main_menu).
    """
    return main_menu()

def get_back_to_menu_button() -> InlineKeyboardMarkup:
    """
    Создаёт кнопку 'Назад' для возврата в главное меню.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Вернуться в меню", callback_data="back_to_menu")]
    ])
    return keyboard