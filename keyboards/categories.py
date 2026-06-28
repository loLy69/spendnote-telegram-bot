from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_category_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='👕 Одежда', callback_data='category:Одежда')],
        [InlineKeyboardButton(text='📱 Техника', callback_data='category:Техника')],
        [InlineKeyboardButton(text='🍔 Еда', callback_data='category:Еда')],
        [InlineKeyboardButton(text='✈️ Поездки', callback_data='category:Поездки')],
        [InlineKeyboardButton(text='🎮 Развлечения', callback_data='category:Развлечения')],
        [InlineKeyboardButton(text='🏠 Быт', callback_data='category:Быт')],
        [InlineKeyboardButton(text='📌 Другое', callback_data='category:Другое')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='➕ Добавить')],
        [KeyboardButton(text='📋 Покупки')],
        [KeyboardButton(text='💰 Общая сумма')],
        [KeyboardButton(text='📊 Статистика')],
        [KeyboardButton(text='📤 Экспорт')],
        [KeyboardButton(text='🗑 Очистить')],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)
