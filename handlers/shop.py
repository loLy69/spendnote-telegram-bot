"""
Обработчик магазина - просмотр категорий и товаров
Event-driven дизайн с использованием callback_query
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from state.fsm import UserState
from services.product_service import product_service
from services.cart_service import cart_service
from keyboards.shop import (
    get_categories_keyboard,
    get_products_list_keyboard,
    get_product_keyboard,
)

router = Router()


@router.message(F.text == '🛍️ Магазин')
async def cmd_shop(message: Message, state: FSMContext) -> None:
    """Вход в магазин"""
    await state.set_state(UserState.browsing)
    await message.answer(
        '🛍️ <b>Магазин</b>\n\nВыбери категорию:',
        reply_markup=get_categories_keyboard(),
        parse_mode='HTML',
    )


@router.callback_query(F.data == 'view_categories')
async def view_categories(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр категорий (через inline кнопку)"""
    await state.set_state(UserState.browsing)
    await callback.message.edit_text(
        '🛍️ <b>Магазин</b>\n\nВыбери категорию:',
        reply_markup=get_categories_keyboard(),
        parse_mode='HTML',
    )
    await callback.answer()


@router.callback_query(F.data.startswith('category:'))
async def view_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр товаров в категории"""
    category_code = callback.data.split(':')[1]
    
    products = product_service.get_products_by_category(category_code)
    if not products:
        await callback.answer('❌ В этой категории нет товаров', show_alert=True)
        return
    
    category_name = product_service.get_categories().get(category_code, category_code)
    
    text = f'📂 <b>{category_name}</b>\n\nТовары:'
    
    await callback.message.edit_text(
        text,
        reply_markup=get_products_list_keyboard(category_code, products),
        parse_mode='HTML',
    )
    await callback.answer()


@router.callback_query(F.data.startswith('product:'))
async def view_product(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр отдельного товара"""
    product_id = callback.data.split(':')[1]
    product = product_service.get_product(product_id)
    
    if not product:
        await callback.answer('❌ Товар не найден', show_alert=True)
        return
    
    await state.set_state(UserState.viewing_product)
    await state.update_data(current_product_id=product_id)
    
    text = (
        f"{product['emoji']} <b>{product['name']}</b>\n"
        f"💰 Цена: {product['price']} ₽\n\n"
        f"📝 {product['description']}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_product_keyboard(product_id),
        parse_mode='HTML',
    )
    await callback.answer()


@router.callback_query(F.data.startswith('add_product:'))
async def add_product_to_cart(callback: CallbackQuery, state: FSMContext) -> None:
    """Добавить товар в корзину"""
    product_id = callback.data.split(':')[1]
    
    success, message = cart_service.add_product(callback.from_user.id, product_id, qty=1)
    
    # Показать уведомление
    await callback.answer(message, show_alert=not success)
    
    if success:
        # Обновить сообщение с информацией о товаре
        product = product_service.get_product(product_id)
        text = (
            f"{product['emoji']} <b>{product['name']}</b>\n"
            f"💰 Цена: {product['price']} ₽\n\n"
            f"📝 {product['description']}\n\n"
            f"✅ Добавлен в корзину!"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_product_keyboard(product_id),
            parse_mode='HTML',
        )


def register_shop_handlers(router_instance: Router) -> None:
    """Регистрация обработчиков магазина"""
    router_instance.include_router(router)
