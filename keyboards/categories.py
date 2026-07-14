from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.db import CATEGORIES, PRIORITIES

CATEGORY_ICONS = {
    "Еда": "🍽",
    "Техника": "💻",
    "Одежда": "👕",
    "Дом": "🏠",
    "Транспорт": "🚕",
    "Здоровье": "💊",
    "Развлечения": "🎮",
    "Подарки": "🎁",
    "Другое": "📌",
}

PRIORITY_ICONS = {
    "high": "🔥",
    "normal": "⚖️",
    "low": "🕒",
}


def get_category_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{CATEGORY_ICONS.get(category, '📌')} {category}", callback_data=f"category:{category}")]
        for category in CATEGORIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_item_actions(item_id: int, status: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    if status != "bought":
        buttons.append([InlineKeyboardButton(text="✅ Отметить купленным", callback_data=f"buy:{item_id}")])
    if status != "skipped":
        buttons.append([InlineKeyboardButton(text="🕒 Отложить", callback_data=f"skip:{item_id}")])
    buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{item_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_priority(priority: str) -> str:
    return f"{PRIORITY_ICONS.get(priority, '⚖️')} {PRIORITIES.get(priority, PRIORITIES['normal'])}"
