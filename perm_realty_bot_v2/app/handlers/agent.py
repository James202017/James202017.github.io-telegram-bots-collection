from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards import agent_menu_kb, payment_method_kb
from app.services.db import has_active_subscription, list_recent_leads, insert_property
from app.config import settings

router = Router()

class AddProperty(StatesGroup):
    city = State()
    address = State()
    price = State()
    rooms = State()
    segment = State()
    url = State()

@router.callback_query(F.data == "agent:subscribe")
async def agent_subscribe(cb: CallbackQuery):
    await cb.message.edit_text(
        "⭐ <b>Подписка для агентов</b>\n"
        "• Лента актуальных заявок\n• Загрузка своих объектов\n• Прямая связь с клиентами\n\n"
        "Выберите способ оплаты:", parse_mode="HTML",
        reply_markup=payment_method_kb("agent")
    )
    await cb.answer()

@router.callback_query(F.data == "agent:leads")
async def agent_leads(cb: CallbackQuery):
    has_sub = await has_active_subscription(cb.from_user.id, "agent")
    if not has_sub:
        await cb.message.edit_text(
            "Доступ к ленте заявок открыт только по подписке.", parse_mode="HTML",
            reply_markup=agent_menu_kb(False)
        )
        await cb.answer()
        return
    leads = await list_recent_leads(10)
    if not leads:
        await cb.message.edit_text("Пока нет новых заявок.", reply_markup=agent_menu_kb(True))
    else:
        lines = ["📥 <b>Последние заявки</b>"]
        for _id, city, params_json, created_at in leads:
            lines.append(f"• #{_id} · {city} · {created_at}")
        await cb.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=agent_menu_kb(True))
    await cb.answer()

@router.callback_query(F.data == "agent:add_object")
async def agent_add_object(cb: CallbackQuery, state: FSMContext):
    has_sub = await has_active_subscription(cb.from_user.id, "agent")
    if not has_sub:
        await cb.answer("Сначала оформите подписку.", show_alert=True)
        return
    await state.set_state(AddProperty.city)
    await cb.message.edit_text("🗺 Город объекта:")
    await cb.answer()

@router.message(AddProperty.city)
async def ap_city(m: Message, state: FSMContext):
    await state.update_data(city=m.text.strip() or settings.city_default)
    await state.set_state(AddProperty.address)
    await m.answer("📍 Адрес (улица, дом):")

@router.message(AddProperty.address)
async def ap_address(m: Message, state: FSMContext):
    await state.update_data(address=m.text.strip())
    await state.set_state(AddProperty.price)
    await m.answer("💰 Цена (руб):")

@router.message(AddProperty.price)
async def ap_price(m: Message, state: FSMContext):
    try:
        price = int(m.text.replace(" ", ""))
    except Exception:
        await m.answer("Введите число, например 8500000")
        return
    await state.update_data(price=price)
    await state.set_state(AddProperty.rooms)
    await m.answer("🛏 Комнат: (0=студия)")

@router.message(AddProperty.rooms)
async def ap_rooms(m: Message, state: FSMContext):
    try:
        rooms = int(m.text)
    except Exception:
        await m.answer("Введите число, например 2")
        return
    await state.update_data(rooms=rooms)
    await state.set_state(AddProperty.segment)
    await m.answer("🏢 Сегмент: напишите 'новостройка' или 'вторичка'")

@router.message(AddProperty.segment)
async def ap_segment(m: Message, state: FSMContext):
    seg = m.text.lower().strip()
    new_build = True if seg.startswith("нов") else False
    await state.update_data(new_build=new_build)
    await state.set_state(AddProperty.url)
    await m.answer("🔗 Ссылка на объект (страница, PDF, Google Drive и т.п.)")

@router.message(AddProperty.url)
async def ap_url(m: Message, state: FSMContext):
    data = await state.get_data()
    await insert_property(
        agent_user_id=m.from_user.id,
        city=data["city"],
        address=data["address"],
        price=data["price"],
        rooms=data["rooms"],
        new_build=data["new_build"],
        url=m.text.strip()
    )
    await state.clear()
    await m.answer("✅ Объект добавлен. Спасибо!")
