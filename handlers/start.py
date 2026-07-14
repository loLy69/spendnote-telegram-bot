from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main import get_main_keyboard
from services.db import upsert_user


WELCOME_TEXT = (
    "💸 <b>SpendNote</b>\n\n"
    "Умный блокнот покупок: сохраняет желания, считает бюджет и помогает понять, что покупать сейчас, а что можно отложить.\n\n"
    "Можно писать естественно:\n"
    "• <i>хочу ноутбук 80000 техника важно</i>\n"
    "• <i>купил кофе 250 еда</i>\n"
    "• <i>кроссовки 9000 одежда заметка: дождаться скидки</i>"
)


HELP_TEXT = (
    "❓ <b>Как пользоваться</b>\n\n"
    "Команды:\n"
    "/add - добавить покупку пошагово\n"
    "/list - план покупок\n"
    "/list bought - купленные покупки\n"
    "/buy ID - отметить покупку купленной\n"
    "/skip ID - отложить покупку\n"
    "/delete ID - удалить запись\n"
    "/budget 60000 - установить месячный бюджет\n"
    "/stats - статистика и нагрузка на бюджет\n"
    "/export - получить файл с данными\n"
    "/clear - очистить свои данные\n\n"
    "Быстрый режим: просто отправь покупку сообщением. Бот сам найдет цену, категорию, статус и приоритет."
)


async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = message.from_user
    if user:
        upsert_user(user.id, user.username, user.full_name)
    await message.answer(WELCOME_TEXT, reply_markup=get_main_keyboard(), parse_mode="HTML")


async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=get_main_keyboard(), parse_mode="HTML")


def register_start_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_help, F.text == "❓ Помощь")
