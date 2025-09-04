from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards import buyer_menu_kb, payment_method_kb
from app.services.db import insert_lead, list_properties
from app.config import settings

router = Router()

class BuyerForm(StatesGroup):
    city = State()
    budget = State()
    rooms = State()
    segment = State()

@router.callback_query(F.data == "buyer:search")
async def buyer_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BuyerForm.city)
    await cb.message.edit_text("🗺 Укажите город (по умолчанию: Пермь):")
    await cb.answer()

@router.message(BuyerForm.city)
async def buyer_city(m: Message, state: FSMContext):
    city = m.text.strip() if m.text.strip() else settings.city_default
    await state.update_data(city=city)
    await state.set_state(BuyerForm.budget)
    await m.answer("💰 Максимальный бюджет (в рублях), например: 9000000")

@router.message(BuyerForm.budget)
async def buyer_budget(m: Message, state: FSMContext):
    try:
        budget = int(m.text.replace(" ", ""))
    except Exception:
        await m.answer("Введите число, например: 9000000")
        return
    await state.update_data(budget=budget)
    await state.set_state(BuyerForm.rooms)
    await m.answer("🛏 Количество комнат (студия=0). Пример: 1, 2, 3")

@router.message(BuyerForm.rooms)
async def buyer_rooms(m: Message, state: FSMContext):
    try:
        rooms = int(m.text)
    except Exception:
        await m.answer("Введите число, например: 2")
        return
    await state.update_data(rooms=rooms)
    await state.set_state(BuyerForm.segment)
    await m.answer("🏢 Сегмент: напишите 'новостройка' или 'вторичка' (или 'любой')")

@router.message(BuyerForm.segment)
async def buyer_segment(m: Message, state: FSMContext):
    segment_raw = m.text.lower().strip()
    new_build = None
    if segment_raw.startswith("нов"):
        new_build = True
    elif segment_raw.startswith("втор"):
        new_build = False

    data = await state.get_data()
    await insert_lead(m.from_user.id, "buyer", data.get("city", settings.city_default), {
        "budget": data["budget"],
        "rooms": data["rooms"],
        "segment": segment_raw
    })

    # Отправка заявки админу
    lead_text = (
        "📨 <b>Новая заявка (покупатель)</b>\n"
        f"Пользователь: @{m.from_user.username or m.from_user.id}\n"
        f"ID: <code>{m.from_user.id}</code>\n"
        f"Город: {data.get('city', settings.city_default)}\n"
        f"Бюджет: {data['budget']} ₽\n"
        f"Комнат: {data['rooms']}\n"
        f"Сегмент: {segment_raw}"
    )
    await m.bot.send_message(settings.admin_chat_id, lead_text, parse_mode="HTML")

    # демо-выдача из локальной БД объектов агента
    props = await list_properties(
        city=data.get("city", settings.city_default),
        max_price=data["budget"],
        rooms=data["rooms"],
        new_build=new_build,
        limit=5
    )
    if props:
        lines = ["🔎 <b>Подходящие варианты:</b>"]
        for city, address, price, rooms, nb, url in props:
            nb_txt = "новостройка" if nb else "вторичка"
            lines.append(f"• {address} — {price:,} ₽, {rooms}-к, {nb_txt}\n{url or ''}")
        await m.answer("\n".join(lines).replace(",", " "), parse_mode="HTML")
    else:
        await m.answer("Пока подходящих вариантов нет — добавим вас в уведомления и пришлём первые предложения.")

    await m.answer(
        "🎁 Хотите ускорить поиск и получить приоритет? Подключите <b>Премиум</b> (приоритетные уведомления, "
        "личный менеджер, ранний доступ к скидкам).", parse_mode="HTML",
        reply_markup=payment_method_kb("buyer")
    )
    await state.clear()

@router.callback_query(F.data == "buyer:premium")
async def buyer_premium(cb: CallbackQuery):
    await cb.message.edit_text(
        "⭐ <b>Премиум для покупателей</b>\n"
        "• Приоритетные подборы\n• Ранний доступ к спецакциям\n• Личный менеджер\n\n"
        "Выберите способ оплаты:", parse_mode="HTML",
        reply_markup=payment_method_kb("buyer")
    )
    await cb.answer()
