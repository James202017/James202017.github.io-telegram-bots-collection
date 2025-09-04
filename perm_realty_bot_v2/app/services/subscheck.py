from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from typing import Tuple

async def is_member(bot: Bot, chat_id: str | int, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in {"member", "administrator", "creator", "owner"}  # owner для совместимости
    except TelegramBadRequest:
        return False

async def verify_pair(bot: Bot, main_chat: str | int, sup_chat: str | int, user_id: int) -> Tuple[bool,bool]:
    a = await is_member(bot, main_chat, user_id)
    b = await is_member(bot, sup_chat, user_id)
    return a, b
