from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main import get_main_menu_keyboard, get_start_keyboard


async def cmd_start(message: Message, state: FSMContext) -> None:
    """Команда /start - главное меню"""
    await state.clear()
    await message.answer(
        '💰 <b>SpendNote & Shop</b>\n\n'
        'Учет покупок, магазин и корзина\n\n'
        'Выбери действие ↓',
        reply_markup=get_start_keyboard(),
        parse_mode='HTML',
    )


async def cmd_help(message: Message) -> None:
    """Команда /help"""
    await message.answer(
        '❓ <b>Справка</b>\n\n'
        '🛍️ <b>Магазин</b> - Просмотр товаров и категорий\n'
        '🛒 <b>Корзина</b> - Управление корзиной\n'
        '📋 <b>Мои покупки</b> - История ваших покупок\n\n'
        'Используйте кнопки для навигации.',
        parse_mode='HTML',
    )


def register_start_handlers(dp: Dispatcher) -> None:
    """Регистрация основных обработчиков"""
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command(commands=['help']))

