"""
Обработчик корзины - просмотр, редактирование, оформление
Event-driven дизайн с использованием callback_query
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from state.fsm import CartState
from services.cart_service import cart_service
from keyboards.cart import (
    get_cart_keyboard,
    get_empty_cart_keyboard,
    get_checkout_keyboard,
)

router = Router()


def format_cart_message(summary: dict) -> str:
    """Форматировать сообщение с содержимым корзины"""
    if summary['is_empty']:
        return '🛒 <b>Корзина пуста</b>'
    
    lines = ['🛒 <b>Корзина</b>\n']
    for item in summary['items']:
        lines.append(
            f"  {item['name']}\n"
            f"    {item['qty']} × {item['price']} ₽ = {item['qty'] * item['price']} ₽"
        )
    
    lines.append(f"\n<b>Итого: {summary['total']} ₽</b>")
    return '\n'.join(lines)


@router.message(F.text == '🛒 Корзина')
async def cmd_cart(message: Message, state: FSMContext) -> None:
    """Открыть корзину через Reply кнопку"""
    await view_cart_inline(
        CallbackQuery(
            id='fake',
            from_user=message.from_user,
            chat_instance='fake',
            message=message,
        ),
        state,
    )


@router.callback_query(F.data == 'view_cart')
async def view_cart_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр корзины (через inline кнопку)"""
    await state.set_state(CartState.in_cart)
    
    summary = cart_service.get_cart_summary(callback.from_user.id)
    
    text = format_cart_message(summary)
    
    if summary['is_empty']:
        await callback.message.edit_text(text, reply_markup=get_empty_cart_keyboard())
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_cart_keyboard(summary['items']),
            parse_mode='HTML',
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith('remove_from_cart:'))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext) -> None:
    """Удалить товар из корзины"""
    product_id = callback.data.split(':')[1]
    
    success, message = cart_service.remove_product(callback.from_user.id, product_id)
    await callback.answer(message, show_alert=not success)
    
    # Обновить корзину
    if success:
        summary = cart_service.get_cart_summary(callback.from_user.id)
        text = format_cart_message(summary)
        
        if summary['is_empty']:
            await callback.message.edit_text(text, reply_markup=get_empty_cart_keyboard())
        else:
            await callback.message.edit_text(
                text,
                reply_markup=get_cart_keyboard(summary['items']),
                parse_mode='HTML',
            )


@router.callback_query(F.data == 'clear_cart')
async def clear_cart_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Подтверждение очистки корзины"""
    await state.set_state(CartState.in_cart)
    
    await callback.message.edit_text(
        '⚠️ <b>Очистить корзину?</b>',
        reply_markup=get_checkout_keyboard(),  # Переиспользуем для Yes/No
        parse_mode='HTML',
    )
    await callback.answer()


@router.callback_query(F.data == 'confirm_checkout')
async def confirm_clear_or_checkout(callback: CallbackQuery, state: FSMContext) -> None:
    """Подтверждение в зависимости от контекста"""
    current_state = await state.get_state()
    
    # Проверяем, была ли это очистка или оформление
    summary = cart_service.get_cart_summary(callback.from_user.id)
    
    # Это оформление заказа
    success, message, order_data = cart_service.checkout(callback.from_user.id)
    await callback.answer(message, show_alert=True)
    
    if success:
        # Корзина очищена, вернуть в меню
        await callback.message.edit_text(
            f'✅ <b>Спасибо за покупку!</b>\n\n{message}',
            reply_markup=get_empty_cart_keyboard(),
            parse_mode='HTML',
        )


@router.callback_query(F.data == 'checkout')
async def checkout(callback: CallbackQuery, state: FSMContext) -> None:
    """Оформить заказ"""
    summary = cart_service.get_cart_summary(callback.from_user.id)
    
    if summary['is_empty']:
        await callback.answer('❌ Корзина пуста', show_alert=True)
        return
    
    await state.set_state(CartState.checkout)
    
    text = (
        f"📋 <b>Оформление заказа</b>\n\n"
        f"Сумма: {summary['total']} ₽\n"
        f"Товаров: {summary['count']}\n\n"
        f"Подтвердить оформление?"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_checkout_keyboard(),
        parse_mode='HTML',
    )
    await callback.answer()


def register_cart_handlers(router_instance: Router) -> None:
    """Регистрация обработчиков корзины"""
    router_instance.include_router(router)
