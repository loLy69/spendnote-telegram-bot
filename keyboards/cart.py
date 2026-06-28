"""
Клавиатуры для корзины и оформления заказа
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_cart_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра корзины"""
    buttons = []
    
    # Кнопки для каждого товара в корзине
    for item in items:
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {item['name']}",
                callback_data=f"remove_from_cart:{item['product_id']}"
            )
        ])
    
    # Разделитель и кнопки действий
    buttons.append([
        InlineKeyboardButton(text='🧹 Очистить корзину', callback_data='clear_cart'),
    ])
    buttons.append([
        InlineKeyboardButton(text='✅ Оформить', callback_data='checkout'),
        InlineKeyboardButton(text='🛍️ В магазин', callback_data='view_categories'),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пустой корзины"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🛍️ В магазин', callback_data='view_categories'),
        ]
    ])


def get_checkout_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оформления заказа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_checkout'),
            InlineKeyboardButton(text='❌ Отмена', callback_data='view_cart'),
        ]
    ])


def get_order_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после успешного заказа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📋 История покупок', callback_data='view_purchases'),
            InlineKeyboardButton(text='🛍️ Продолжить покупки', callback_data='view_categories'),
        ]
    ])
