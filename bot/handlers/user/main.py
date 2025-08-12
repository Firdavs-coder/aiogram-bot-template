from aiogram import Router
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message
from bot.database.models import User

user_router = Router(name="user")

@user_router.message(CommandStart())
async def welcome(message: Message):
    await message.reply("Hello")
