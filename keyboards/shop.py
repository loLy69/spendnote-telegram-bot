"""
Клавиатуры для магазина и работы с товарами
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.products import PRODUCT_CATEGORIES


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории"""
    buttons = []
    for category_code, category_name in PRODUCT_CATEGORIES.items():
        buttons.append([
            InlineKeyboardButton(
                text=category_name,
                callback_data=f'category:{category_code}'
            )
        ])
    
    # Кнопка корзины
    buttons.append([
        InlineKeyboardButton(text='🛒 Корзина', callback_data='view_cart')
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного товара"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='➕ Добавить', callback_data=f'add_product:{product_id}'),
            InlineKeyboardButton(text='🛒 Корзина', callback_data='view_cart'),
        ],
        [
            InlineKeyboardButton(text='⬅️ Назад', callback_data='view_categories'),
        ]
    ])


def get_products_list_keyboard(category_code: str, products: list[dict]) -> InlineKeyboardMarkup:
    """Клавиатура для списка товаров в категории"""
    buttons = []
    
    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['emoji']} {product['name']} - {product['price']} ₽",
                callback_data=f"product:{product['product_id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text='🛒 Корзина', callback_data='view_cart'),
        InlineKeyboardButton(text='⬅️ Назад', callback_data='view_categories'),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
