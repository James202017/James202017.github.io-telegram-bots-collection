from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from app.keyboards import start_kb
from app.config import settings
import os

router = Router()

WELCOME_TEXT = (
    "🎯 <b>Давай без риелторов?</b>\n"
    "Мы подберём, проверим и сопроводим покупку квартиры — <b>бесплатно</b> для покупателей.\n\n"
    "Для агентов это сервис с реальными заявками и доступом к каталогу.\n\n"
    "• Работаем только с <b>проверенными застройщиками</b>\n"
    f"• География: <b>{settings.city_default}</b> и вся Россия\n"
    "• Умный подбор по фильтрам, уведомления о новых вариантах\n"
    "• Оплата подписки: ⭐️ Stars в Telegram или 🏦 СБП (Т-Банк)\n\n"
    "Выберите роль, чтобы продолжить👇"
)

@router.message(F.text == "/start")
async def cmd_start(m: Message):
    welcome_img_path = "app/assets/welcome.jpg"
    if os.path.exists(welcome_img_path):
        photo = FSInputFile(welcome_img_path)
        await m.answer_photo(photo=photo, caption=WELCOME_TEXT, parse_mode="HTML", reply_markup=start_kb())
    else:
        await m.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=start_kb())

@router.message(F.text == "/menu")
async def cmd_menu(m: Message):
    await cmd_start(m)

@router.callback_query(F.data == "about")
async def about(cb: CallbackQuery):
    await cb.message.edit_text(
        "🤖 <b>Как это работает</b>\n\n"
        "Покупателям мы бесплатно подбираем варианты у проверенных застройщиков и на рынке. "
        "Никаких скрытых комиссий. Можно остаться инкогнито.\n\n"
        "Агентам — подписка даёт доступ к ленте заявок и загрузке своих объектов.\n\n"
        "Готовы продолжить? Вернитесь назад и выберите роль.",
        parse_mode="HTML"
    )
    await cb.answer()

@router.message(F.text == "/profile")
async def cmd_profile(m: Message):
    from app.handlers.onboarding import start_onboarding
    await start_onboarding(m, m.bot)
