from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from html import escape

from keyboards.main import get_main_keyboard
from services.db import clear_purchases, delete_purchase, get_purchase
from services.fsm import SettingsStates


async def cmd_delete(message: Message) -> None:
    args = message.text.split()[1:]
    if not args:
        await message.answer("Укажи ID: /delete 12")
        return
    try:
        item_id = int(args[0])
    except ValueError:
        await message.answer("ID должен быть числом.")
        return

    item = get_purchase(message.from_user.id, item_id)
    if not item:
        await message.answer("Не нашел такую покупку.")
        return

    delete_purchase(message.from_user.id, item_id)
    await message.answer(f"🗑 Удалено: #{item_id} {escape(item['name'])}", reply_markup=get_main_keyboard(), parse_mode="HTML")


async def handle_delete_callback(callback: CallbackQuery) -> None:
    item_id = int(callback.data.split(":", 1)[1])
    item = get_purchase(callback.from_user.id, item_id)
    if not item:
        await callback.answer("Покупка не найдена", show_alert=True)
        return
    delete_purchase(callback.from_user.id, item_id)
    await callback.message.edit_text(f"🗑 Удалено: #{item_id} {escape(item['name'])}", parse_mode="HTML")
    await callback.answer("Удалено")


async def cmd_clear(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_for_clear_confirmation)
    await message.answer(
        "🗑 Это удалит все твои покупки и планы.\n\n"
        "Напиши <b>удалить</b>, если уверен.",
        parse_mode="HTML",
    )


async def confirm_clear(message: Message, state: FSMContext) -> None:
    answer = (message.text or "").strip().lower()
    if answer == "удалить":
        count = clear_purchases(message.from_user.id)
        await message.answer(f"Готово. Удалено записей: {count}", reply_markup=get_main_keyboard())
    else:
        await message.answer("Очистка отменена.", reply_markup=get_main_keyboard())
    await state.clear()


def register_delete_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_delete, Command(commands=["delete"]))
    dp.callback_query.register(handle_delete_callback, F.data.startswith("delete:"))
    dp.message.register(cmd_clear, Command(commands=["clear"]))
    dp.message.register(cmd_clear, F.text == "🗑 Очистить")
    dp.message.register(confirm_clear, SettingsStates.waiting_for_clear_confirmation)
