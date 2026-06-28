"""
Главное меню и основные клавиатуры
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🛍️ Магазин', callback_data='view_categories'),
            InlineKeyboardButton(text='🛒 Корзина', callback_data='view_cart'),
        ],
        [
            InlineKeyboardButton(text='📋 Мои покупки', callback_data='view_purchases'),
            InlineKeyboardButton(text='❓ Помощь', callback_data='help'),
        ]
    ])


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура после /start"""
    buttons = [
        [KeyboardButton(text='🛍️ Магазин')],
        [KeyboardButton(text='📋 История'), KeyboardButton(text='🛒 Корзина')],
        [KeyboardButton(text='❓ Помощь')],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Сохраняем старые функции для совместимости
def get_category_keyboard() -> InlineKeyboardMarkup:
    from keyboards.shop import get_categories_keyboard
    return get_categories_keyboard()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Старая версия для совместимости"""
    buttons = [
        [KeyboardButton(text='➕ Добавить')],
        [KeyboardButton(text='📋 Покупки')],
        [KeyboardButton(text='💰 Общая сумма')],
        [KeyboardButton(text='📊 Статистика')],
        [KeyboardButton(text='📤 Экспорт')],
        [KeyboardButton(text='🗑 Очистить')],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)
