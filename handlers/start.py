from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from handlers.list import send_list, cmd_stats, export_purchases
from services.db import get_total
from keyboards.categories import get_main_keyboard


async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        '💰 SpendNote\n\nУчет покупок и статистика\n\nВыбери действие ↓',
        reply_markup=get_main_keyboard(),
    )


async def handle_menu_action(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (message.text or '').strip()
    if text == '➕ Добавить':
        from handlers.add_item import cmd_add
        await cmd_add(message, state)
        return
    if text == '📋 Покупки':
        await send_list(message, None)
        return
    if text == '💰 Общая сумма':
        total = get_total(message.from_user.id)
        await message.answer(f'💰 Всего потрачено: {total} ₽')
        return
    if text == '📊 Статистика':
        await cmd_stats(message)
        return
    if text == '📤 Экспорт':
        await export_purchases(message)
        return
    if text == '🗑 Очистить':
        await message.answer('Отправь /clear для подтверждения')
        return


def register_start_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_start, Command(commands=['help', 'menu']))
    dp.message.register(handle_menu_action, F.text.in_({'➕ Добавить', '📋 Покупки', '💰 Общая сумма', '📊 Статистика', '📤 Экспорт', '🗑 Очистить'}))
