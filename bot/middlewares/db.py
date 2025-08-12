from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import sqlite3

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Open a new sqlite3 connection per request
        conn = sqlite3.connect(self.db_path)
        data["db_conn"] = conn
        try:
            result = await handler(event, data)
        finally:
            conn.close()
        return result