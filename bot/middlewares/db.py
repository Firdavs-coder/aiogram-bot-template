import sqlite3
import logging
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from bot.database.models import User

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware for database operations and automatic user saving"""
    
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        logger.info(f"DatabaseMiddleware initialized with db_path: {db_path}")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Create database connection for this request
        conn = sqlite3.connect(self.db_path)
        data["db_conn"] = conn
        
        try:
            # Auto-save user information if event is a Message
            if isinstance(event, Message) and event.from_user:
                user = User(
                    user_id=event.from_user.id,
                    name=event.from_user.full_name
                )
                user.save(conn)
                logger.info(f"User saved: ID={user.id}, Name={user.name}")
            
            # Continue with handler execution
            result = await handler(event, data)
            
        except Exception as e:
            logger.error(f"Error in DatabaseMiddleware: {e}")
            raise
        finally:
            # Always close the connection
            conn.close()
            
        return result