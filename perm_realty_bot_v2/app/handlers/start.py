from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards import buyer_menu_kb, agent_menu_kb
from app.services.db import upsert_user, has_active_subscription

router = Router()

@router.callback_query(F.data.startswith("role:"))
async def choose_role(cb: CallbackQuery):
    role = cb.data.split(":")[1]
    await upsert_user(cb.from_user.id, cb.from_user.username, role)
    if role == "buyer":
        await cb.message.edit_text(
            "🏡 <b>Покупатель</b>\n\n"
            "Идея простая: <b>без риелторов</b>. Мы бесплатно подберём и сопроводим. "
            "Хотите начать подбор или подключить Премиум?", parse_mode="HTML",
            reply_markup=buyer_menu_kb()
        )
    else:
        has_sub = await has_active_subscription(cb.from_user.id, "agent")
        await cb.message.edit_text(
            "🧑‍💼 <b>Агент</b>\n\n"
            "Подписка открывает ленту заявок и загрузку ваших объектов. "
            "Выберите действие:", parse_mode="HTML",
            reply_markup=agent_menu_kb(has_sub)
        )
    await cb.answer()
