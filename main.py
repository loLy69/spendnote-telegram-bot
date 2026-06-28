import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from handlers.start import register_start_handlers
from handlers.add_item import register_add_item_handlers
from handlers.list import register_list_handlers
from handlers.delete import register_delete_handlers
from services.db import init_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main() -> None:
    token = os.getenv('BOT_TOKEN', '').strip()
    if not token:
        raise RuntimeError('BOT_TOKEN is not set. Please add it to .env')

    bot = Bot(token=token)
    dp = Dispatcher()

    init_db()
    register_start_handlers(dp)
    register_add_item_handlers(dp)
    register_list_handlers(dp)
    register_delete_handlers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
