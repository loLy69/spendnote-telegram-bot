from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

MENU_LABELS = {
    "➕ Добавить",
    "📌 План",
    "✅ Куплено",
    "💰 Бюджет",
    "📊 Статистика",
    "📤 Экспорт",
    "🗑 Очистить",
    "❓ Помощь",
}


def get_main_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="➕ Добавить"), KeyboardButton(text="📌 План")],
        [KeyboardButton(text="✅ Куплено"), KeyboardButton(text="💰 Бюджет")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📤 Экспорт")],
        [KeyboardButton(text="🗑 Очистить"), KeyboardButton(text="❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)
