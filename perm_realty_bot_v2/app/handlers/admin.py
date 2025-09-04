from aiogram import Router, F
from aiogram.types import Message
from app.config import settings

router = Router()

@router.message(F.text == "/admin")
async def admin_menu(m: Message):
    if m.from_user.id != settings.admin_chat_id:
        return
    await m.answer("Админ: подтверждайте СБП из входящих фото/документов. Команды появятся позже.")
