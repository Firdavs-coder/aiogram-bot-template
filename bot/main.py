from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from bot.misc import TgKeys
from bot.database.session import get_session
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
    for admin_id in TgKeys.ADMINS:
        try:
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
    
    # Initialize SQLAlchemy database (tables are created automatically in session.py)
    logger.info("Database initialized with SQLAlchemy")

    bot = Bot(token=TgKeys.TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    logger.info("Middleware registered")

    # Register on_startup function for dispatcher startup
    await on_startup(dp, bot)

    # Start polling for updates (without skipping updates)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
