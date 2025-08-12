from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import logging

from bot.misc import TgKeys
from bot.database.models import User
from bot.filters import register_all_filters
from bot.handlers import register_all_handlers
from bot.middlewares import DatabaseMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_startup(dp: Dispatcher, bot: Bot) -> None:
    """
    Function to be called on dispatcher startup.

    - Register all filters.
    - Register all handlers.
    - Send startup notification to admins.
    """
    logger.info("Bot is starting up...")
    
    register_all_filters(dp)
    register_all_handlers(dp)
    
    # Send startup message to all admins
    admin_ids = TgKeys.ADMINS.split(',') if ',' in TgKeys.ADMINS else [TgKeys.ADMINS]
    for admin_id in admin_ids:
        try:
            admin_id = int(admin_id.strip())
            await bot.send_message(admin_id, "🤖 Bot has started successfully!")
            logger.info(f"Startup notification sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send startup message to admin {admin_id}: {e}")
    
    logger.info("Bot startup completed!")


async def start_bot():
    """
    Main function to start the bot.
    """
    logger.info("Initializing bot...")
    
    # Setup sqlite3 database and create tables
    db_path = './db.sqlite3'
    logger.info(f"Setting up database at {db_path}")
    conn = sqlite3.connect(db_path)
    User.create_table(conn)
    conn.close()
    logger.info("Database setup completed")

    bot = Bot(token=TgKeys.TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middleware
    dp.message.middleware(DatabaseMiddleware(db_path=db_path))
    dp.callback_query.middleware(DatabaseMiddleware(db_path=db_path))
    logger.info("Middleware registered")

    # Register on_startup function for dispatcher startup
    await on_startup(dp, bot)

    # Start polling for updates (without skipping updates)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
