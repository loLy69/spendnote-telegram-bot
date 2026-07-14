from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from html import escape

from keyboards.categories import get_category_keyboard
from keyboards.main import MENU_LABELS, get_main_keyboard
from services.db import ItemInput, add_purchase
from services.fsm import AddPurchaseStates
from services.parser import ParsedPurchase, PurchaseParser


async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddPurchaseStates.waiting_for_name)
    await message.answer(
        "➕ <b>Новая покупка</b>\n\n"
        "Напиши название или сразу одной строкой:\n"
        "<i>хочу наушники 12000 техника важно</i>",
        parse_mode="HTML",
    )


def _build_item(user_id: int, parsed: ParsedPurchase, category: str | None = None) -> ItemInput:
    return ItemInput(
        user_id=user_id,
        name=parsed.name.strip(),
        price=int(parsed.price or 0),
        category=category or parsed.category or "Другое",
        status=parsed.status,
        priority=parsed.priority,
        note=parsed.note,
    )


async def _save_purchase(message: Message, state: FSMContext, item: ItemInput) -> None:
    item_id = add_purchase(item)
    await state.clear()
    await message.answer(
        "✅ <b>Сохранено</b>\n\n"
        f"#{item_id} {escape(item.name)}\n"
        f"💰 {item.price} ₽\n"
        f"📂 {item.category}\n"
        f"🎯 {'Куплено' if item.status == 'bought' else 'В плане'}",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
    )


async def _continue_or_save(message: Message, state: FSMContext, parsed: ParsedPurchase) -> None:
    if not parsed.name:
        await message.answer("Не вижу название покупки. Например: <i>кроссовки 9000 одежда</i>", parse_mode="HTML")
        return

    await state.update_data(parsed=parsed.__dict__)

    if parsed.price is None:
        await state.set_state(AddPurchaseStates.waiting_for_price)
        await message.answer(f"💰 Сколько примерно стоит <b>{escape(parsed.name)}</b>?", parse_mode="HTML")
        return

    if parsed.category is None:
        await state.set_state(AddPurchaseStates.waiting_for_category)
        await message.answer("📂 Выбери категорию:", reply_markup=get_category_keyboard())
        return

    await _save_purchase(message, state, _build_item(message.from_user.id, parsed))


async def handle_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    current_state = await state.get_state()

    if current_state == AddPurchaseStates.waiting_for_price.state:
        parsed = PurchaseParser.parse(text)
        price = parsed.price
        if price is None:
            await message.answer("Напиши цену цифрами, например: <b>12000</b>", parse_mode="HTML")
            return
        data = await state.get_data()
        original = ParsedPurchase(**data["parsed"])
        merged = ParsedPurchase(
            name=original.name,
            price=price,
            category=parsed.category or original.category,
            status=original.status,
            priority=original.priority,
            note=original.note,
            raw_text=original.raw_text,
        )
        await _continue_or_save(message, state, merged)
        return

    if current_state == AddPurchaseStates.waiting_for_category.state:
        category = PurchaseParser.detect_category(text)
        if not category:
            await message.answer("Выбери категорию кнопкой или напиши ее названием.")
            return
        data = await state.get_data()
        parsed = ParsedPurchase(**data["parsed"])
        await _save_purchase(message, state, _build_item(message.from_user.id, parsed, category))
        return

    if text in MENU_LABELS:
        return

    parsed = PurchaseParser.parse(text)
    await _continue_or_save(message, state, parsed)


async def handle_category(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    parsed_data = data.get("parsed")
    if not parsed_data:
        await callback.message.answer("Начни добавление заново: /add")
        await state.clear()
        await callback.answer()
        return

    category = callback.data.split(":", 1)[1]
    parsed = ParsedPurchase(**parsed_data)
    await _save_purchase(callback.message, state, _build_item(callback.from_user.id, parsed, category))
    await callback.answer()


def register_add_item_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_add, Command(commands=["add"]))
    dp.message.register(cmd_add, F.text == "➕ Добавить")
    dp.callback_query.register(handle_category, F.data.startswith("category:"))
    dp.message.register(handle_text, F.text & ~F.text.startswith("/") & ~F.text.in_(MENU_LABELS))
