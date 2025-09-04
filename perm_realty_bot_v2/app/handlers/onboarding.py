from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards import subs_kb, role_kb
from app.config import settings
from app.services.subscheck import verify_pair

router = Router()

class ProfileForm(StatesGroup):
    role = State()
    city = State()

async def start_onboarding(message_or_cb, bot):
    txt = (
        "🎉 <b>Оплата принята!</b>\n\n"
        "Чтобы получить доступ, подпишитесь на каналы и заполните анкету. "
        "Это помогает нам держать порядок и ускорять выдачу заявок.\n\n"
        "1) Подпишитесь на оба канала.\n"
        "2) Нажмите «Я подписался(ась)».\n"
        "3) Заполните короткую анкету."
    )
    markup = subs_kb(settings.main_channel_url, settings.support_channel_url)
    if hasattr(message_or_cb, "message"):  # CallbackQuery
        await message_or_cb.message.answer(txt, parse_mode="HTML", reply_markup=markup)
    else:
        await message_or_cb.answer(txt, parse_mode="HTML", reply_markup=markup)

@router.callback_query(F.data == "subs:check")
async def subs_check(cb: CallbackQuery, state: FSMContext):
    ok_main, ok_sup = await verify_pair(cb.bot, settings.main_channel_id, settings.support_channel_id, cb.from_user.id)
    if not (ok_main and ok_sup):
        missing = []
        if not ok_main: missing.append("главный канал")
        if not ok_sup: missing.append("канал поддержки")
        await cb.answer("Не найдена подписка на: " + ", ".join(missing), show_alert=True)
        return
    # proceed to profile
    await state.set_state(ProfileForm.role)
    await cb.message.answer("Отлично! Теперь выберите, кто вы:", reply_markup=role_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("profile:role:"))
async def set_role(cb: CallbackQuery, state: FSMContext):
    role = cb.data.split(":")[-1]
    await state.update_data(role=role)
    await state.set_state(ProfileForm.city)
    await cb.message.answer("🗺 В каком городе подключить помощника? Напишите город.")
    await cb.answer()

@router.message(ProfileForm.city)
async def set_city(m: Message, state: FSMContext):
    city = m.text.strip()
    data = await state.get_data()
    role = data.get("role", "buyer")
    await state.clear()
    # send to admin
    msg = (
        "🆕 <b>Анкета пользователя</b>\n"
        f"Пользователь: @{m.from_user.username or m.from_user.id}\n"
        f"ID: <code>{m.from_user.id}</code>\n"
        f"Роль: {'Покупатель' if role=='buyer' else 'Риелтор'}\n"
        f"Город: {city}"
    )
    await m.bot.send_message(chat_id=settings.admin_chat_id, text=msg, parse_mode="HTML")
    await m.answer("✅ Анкета принята! Заявка направлена администратору. В ближайшее время свяжемся.")
