from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.db import delete_purchase, clear_purchases
from services.fsm import AddPurchaseStates


async def cmd_delete(message: Message) -> None:
    args = message.text.split()[1:]
    if not args:
        await message.answer('❌ Использование: /delete <ID>')
        return
    try:
        purchase_id = int(args[0])
    except ValueError:
        await message.answer('❌ ID должен быть числом')
        return

    deleted = delete_purchase(message.from_user.id, purchase_id)
    if deleted:
        await message.answer(f'✅ Запись {purchase_id} удалена')
    else:
        await message.answer('❌ Запись не найдена')


async def cmd_clear(message: Message, state: FSMContext) -> None:
    await state.set_state(AddPurchaseStates.waiting_for_clear_confirmation)
    await message.answer('🗑 Точно? Напиши «да» для подтверждения')


async def confirm_clear(message: Message, state: FSMContext) -> None:
    if message.text and message.text.strip().lower() in {'да', 'yes', 'y'}:
        cleared = clear_purchases(message.from_user.id)
        if cleared:
            await message.answer(f'✅ Удалено {cleared} записей')
        else:
            await message.answer('❌ Нечего удалять')
    else:
        await message.answer('❌ Отменено')
    await state.clear()


def register_delete_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_delete, Command(commands=['delete']))
    dp.message.register(cmd_clear, Command(commands=['clear']))
    dp.message.register(confirm_clear, AddPurchaseStates.waiting_for_clear_confirmation)
