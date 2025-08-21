# bot/keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Главное меню
main_menu = ReplyKeyboardMarkup(
keyboard=[
[KeyboardButton(text="🎁 Получить тест")],
[KeyboardButton(text="💳 Купить доступ")]
],
resize_keyboard=True
)


# Меню покупки (inline)
paid_menu = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="Подписаться", callback_data="subscribe")],
[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
])


# Кнопка возврата
back_button = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
])