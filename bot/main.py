from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3

from bot.misc import TgKeys
from bot.database.models import create_users_table
from bot.filters import register_all_filters
from bot.handlers import register_all_handlers
from bot.middlewares import DbSessionMiddleware


async def on_startup(dp: Dispatcher) -> None:
    """
    Function to be called on dispatcher startup.

    - Register all filters.
    - Register all handlers.
    """

    register_all_filters(dp)
    register_all_handlers(dp)


async def start_bot():
    """
    Main function to start the bot.
    """
    # Setup sqlite3 database and create tables
    db_path = './db.sqlite3'
    conn = sqlite3.connect(db_path)
    create_users_table(conn)
    conn.close()

    bot = Bot(token=TgKeys.TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware(db_path=db_path))

    # Register on_startup function for dispatcher startup
    await on_startup(dp)

    # Start polling for updates (without skipping updates)
    await dp.start_polling(bot)
