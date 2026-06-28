from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.db import add_purchase
from services.fsm import AddPurchaseStates
from services.parser import PurchaseParser
from keyboards.categories import get_category_keyboard

MENU_LABELS = {
    '➕ Добавить',
    '📋 Покупки',
    '💰 Общая сумма',
    '📊 Статистика',
    '📤 Экспорт',
    '🗑 Очистить',
}


async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddPurchaseStates.waiting_for_name)
    await message.answer(
        '✨ Добавим покупку\n\nНапиши название или сразу: «футболка 2500 одежда»',
    )


async def _save_purchase(message: Message, state: FSMContext, name: str, price: int, category: str) -> None:
    add_purchase(message.from_user.id, name, price, category)
    await state.clear()
    await message.answer(
        f'✅ Сохранено!\n💰 {price} ₽ за {name}\n📁 {category}',
    )


async def handle_text(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    text = (message.text or '').strip()
    parsed = PurchaseParser.parse(text)

    if current_state is None and text not in MENU_LABELS:
        await cmd_add(message, state)
        current_state = await state.get_state()

    if current_state == AddPurchaseStates.waiting_for_name.state:
        if not parsed.name or (parsed.name == 'Товар' and not parsed.price):
            await message.answer('❌ Не понимаю. Напиши название или сразу: айфон 120000')
            return

        await state.update_data(name=parsed.name)
        if parsed.price is not None and parsed.category is not None:
            await _save_purchase(message, state, parsed.name, parsed.price, parsed.category)
            return

        if parsed.price is not None:
            await state.update_data(price=parsed.price)
            await state.set_state(AddPurchaseStates.waiting_for_category)
            await message.answer(
                f'💰 Цена: {parsed.price} ₽\n\n📂 Выбери категорию:',
                reply_markup=get_category_keyboard(),
            )
            return

        await state.set_state(AddPurchaseStates.waiting_for_price)
        await message.answer('💰 Теперь напиши цену в рублях')
        return

    if current_state == AddPurchaseStates.waiting_for_price.state:
        price = parsed.price
        if price is None:
            try:
                price = int(text.replace(' ', '').replace('\u00A0', ''))
            except ValueError:
                await message.answer('❌ Напиши цену цифрами (например, 2000)')
                return

        data = await state.get_data()
        name = data.get('name', '')
        await state.update_data(price=price)

        if parsed.category is not None:
            await _save_purchase(message, state, name, price, parsed.category)
            return

        await state.set_state(AddPurchaseStates.waiting_for_category)
        await message.answer(
            f'📂 Выбери категорию для {name}:',
            reply_markup=get_category_keyboard(),
        )
        return

    if current_state == AddPurchaseStates.waiting_for_category.state:
        category = PurchaseParser.detect_category(text)
        if category is not None:
            data = await state.get_data()
            name = data.get('name', '')
            price = data.get('price')
            if not name or price is None:
                await message.answer('❌ Ошибка. Начни заново /add')
                await state.clear()
                return
            await _save_purchase(message, state, name, int(price), category)
            return
        await message.answer('❌ Выбери категорию через кнопки')
        return


async def handle_category(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    name = data.get('name', '')
    price = data.get('price')
    category = callback.data.split(':', 1)[-1]

    if not name or price is None:
        await callback.message.answer('❌ Ошибка. Начни заново /add')
        await state.clear()
        await callback.answer()
        return

    add_purchase(callback.from_user.id, name, int(price), category)
    await callback.message.answer(
        f'✅ Сохранено!\n💰 {price} ₽ — {name}\n📁 {category}',
    )
    await state.clear()
    await callback.answer()


def register_add_item_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_add, Command(commands=['add']))
    dp.message.register(
        handle_text,
        F.text
        & ~F.text.startswith('/')
        & ~F.text.in_(MENU_LABELS),
    )
    dp.callback_query.register(handle_category, F.data.startswith('category:'))
