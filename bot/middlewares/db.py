import logging
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.orm import Session

from bot.database.session import get_session
from bot.database.crud import UserCRUD

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware for database operations and automatic user saving"""
    
    def __init__(self):
        super().__init__()
        logger.info("DatabaseMiddleware initialized with SQLAlchemy")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Create database session for this request
        session = get_session()
        data["session"] = session
        data["user_crud"] = UserCRUD(session)
        
        try:
            # Auto-save user information if event is a Message
            if isinstance(event, Message) and event.from_user:
                user_crud = data["user_crud"]
                user = user_crud.create_user(
                    user_id=event.from_user.id,
                    name=event.from_user.full_name
                )
                data["current_user"] = user
                logger.info(f"User processed: ID={user.id}, Name={user.name}")
            
            # Continue with handler execution
            result = await handler(event, data)
            
        except Exception as e:
            logger.error(f"Error in DatabaseMiddleware: {e}")
            session.rollback()
            raise
        finally:
            # Always close the session
            session.close()
            
        return result