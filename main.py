from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers.add_item import register_add_item_handlers
from handlers.delete import register_delete_handlers
from handlers.list import register_list_handlers
from handlers.start import register_start_handlers
from services.db import init_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="add", description="Добавить покупку"),
            BotCommand(command="list", description="План покупок"),
            BotCommand(command="buy", description="Отметить купленным"),
            BotCommand(command="budget", description="Бюджет"),
            BotCommand(command="stats", description="Статистика"),
            BotCommand(command="export", description="Экспорт"),
            BotCommand(command="help", description="Помощь"),
        ]
    )


async def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "your_bot_token_here":
        raise RuntimeError("BOT_TOKEN is not set. Add it to .env")

    init_db()

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    register_start_handlers(dp)
    register_list_handlers(dp)
    register_delete_handlers(dp)
    register_add_item_handlers(dp)

    await set_bot_commands(bot)
    logger.info("SpendNote bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
