from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards import plans_kb, admin_approve_kb, agent_menu_kb, buyer_menu_kb
from app.services.payments import send_stars_invoice, handle_precheckout, handle_successful_payment
from app.services.subscriptions import get_plan
from app.config import settings

router = Router()

@router.callback_query(F.data.startswith("pay:stars:"))
async def pay_stars(cb: CallbackQuery):
    role = cb.data.split(":")[2]
    await cb.message.edit_text("Выберите тариф:", reply_markup=plans_kb(role))
    await cb.answer()

@router.callback_query(F.data.startswith("plan:"))
async def plan_choose(cb: CallbackQuery):
    _, role, plan = cb.data.split(":")
    await send_stars_invoice(cb.bot, cb.from_user.id, role, plan)
    await cb.answer("Счёт отправлен в личные сообщения.")

class SBP(StatesGroup):
    waiting_screenshot = State()
    role = State()
    plan = State()

@router.callback_query(F.data.startswith("pay:sbp:"))
async def pay_sbp(cb: CallbackQuery, state: FSMContext):
    role = cb.data.split(":")[2]
    # предлагаем выбрать тариф через те же кнопки
    await cb.message.edit_text(
        "🏦 <b>Оплата по СБП</b>\n"
        "1) Выберите тариф.\n"
        "2) Переведите сумму на номер <b>+7 912 986-86-88</b> (Т‑Банк/Тинькофф).\n"
        "3) Нажмите «Я оплатил(а)» и пришлите скрин чека — админ подтвердит подписку.",
        parse_mode="HTML",
        reply_markup=plans_kb(role)
    )
    await cb.answer()

@router.callback_query(F.data.startswith("sbp:paid:"))
async def sbp_paid(cb: CallbackQuery, state: FSMContext):
    _, _, role, plan = cb.data.split(":")
    await state.update_data(role=role, plan=plan)
    await state.set_state(SBP.waiting_screenshot)
    await cb.message.edit_text("📸 Пришлите скриншот чека СБП одним сообщением.")
    await cb.answer()

@router.message(SBP.waiting_screenshot, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def sbp_receive(m: Message, state: FSMContext):
    data = await state.get_data()
    plan = get_plan(data["role"], data["plan"])
    caption = (
        f"💳 <b>Проверка СБП</b>\n"
        f"Пользователь: @{m.from_user.username or m.from_user.id}\n"
        f"Роль: {data['role']}\nТариф: {plan['title']} ({plan['stars']}⭐)"
    )
    if m.photo:
        file_id = m.photo[-1].file_id
        await m.bot.send_photo(chat_id=settings.admin_chat_id, photo=file_id, caption=caption, parse_mode="HTML",
                               reply_markup=admin_approve_kb(m.from_user.id, data['plan'], data['role']))
    elif m.document:
        await m.bot.send_document(chat_id=settings.admin_chat_id, document=m.document.file_id, caption=caption, parse_mode="HTML",
                                  reply_markup=admin_approve_kb(m.from_user.id, data['plan'], data['role']))
    await m.answer("Спасибо! Чек отправлен администратору. Уведомим, как только подпишем доступ.")
    await state.clear()

@router.pre_checkout_query()
async def on_pre_checkout(pcq):
    await handle_precheckout(pcq, pcq.bot)

@router.message(F.successful_payment)
async def on_success_payment(m: Message):
    await handle_successful_payment(m)
    # После оплаты — проверка подписок и анкета
    from app.handlers.onboarding import start_onboarding
    await start_onboarding(m, m.bot)
    try:
        role, _ = m.successful_payment.invoice_payload.split(":", 1)
    except Exception:
        role = "buyer"
    if role == "agent":
        await m.answer("Перейдите в меню агента:", reply_markup=agent_menu_kb(True))
    else:
        await m.answer("Перейдите в меню покупателя:", reply_markup=buyer_menu_kb())

@router.callback_query(F.data.startswith("admin:approve:"))
async def admin_approve(cb: CallbackQuery):
    parts = cb.data.split(":")
    _, _, user_id, role, plan = parts
    from app.services.db import set_subscription
    p = get_plan(role, plan)
    expires = await set_subscription(int(user_id), role, p["days"])
    await cb.bot.send_message(int(user_id), 
        f"✅ Администратор подтвердил оплату по СБП. Доступ активен до <b>{expires.strftime('%d.%m.%Y %H:%M')}</b> UTC.",
        parse_mode="HTML"
    )
    from app.handlers.onboarding import start_onboarding
    class _X: pass
    tmp = _X(); tmp.answer = lambda *a, **k: cb.bot.send_message(int(user_id), *a, **k)
    await start_onboarding(tmp, cb.bot)
    await cb.message.edit_text(cb.message.html_text + "\n\n✅ Подтверждено.", parse_mode="HTML")
    await cb.answer("Подписка активирована.")

@router.callback_query(F.data.startswith("admin:reject:"))
async def admin_reject(cb: CallbackQuery):
    parts = cb.data.split(":")
    _, _, user_id, role, plan = parts
    await cb.bot.send_message(int(user_id), 
        "❌ К сожалению, платёж по СБП не найден. Проверьте реквизиты и пришлите корректный чек.",
    )
    await cb.message.edit_text(cb.message.html_text + "\n\n❌ Отклонено.", parse_mode="HTML")
    await cb.answer("Отклонено.")
