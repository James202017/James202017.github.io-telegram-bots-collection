from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram import Bot
from app.config import settings
from app.services.db import set_subscription
from app.services.subscriptions import get_plan

async def send_stars_invoice(bot: Bot, chat_id: int, role: str, plan_code: str):
    plan = get_plan(role, plan_code)
    title = plan["title"]
    description = f"Подписка: {title}\nДоступ к функциям на {plan['days']} дн."
    payload = f"{role}:{plan_code}"
    # Для Stars: provider_token = "" и currency = "XTR"; ровно один price.
    prices = [LabeledPrice(label=title, amount=plan["stars"])]
    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        currency="XTR",
        prices=prices,
        provider_token="",
        start_parameter="perm_realty_sub"
    )

async def handle_precheckout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Можно добавить собственные проверки payload, пользователя и т.д.
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

async def handle_successful_payment(message: Message):
    # payload вида "role:plan"
    payload = message.successful_payment.invoice_payload if message.successful_payment else ""
    try:
        role, plan_code = payload.split(":", 1)
    except Exception:
        role, plan_code = "buyer", "7d"
    plan = get_plan(role, plan_code)
    expires = await set_subscription(message.from_user.id, role, plan["days"])
    await message.answer(
        f"✅ Оплата получена! Доступ активен до: <b>{expires.strftime('%d.%m.%Y %H:%M')}</b> UTC\n"
        f"Команда: /menu",
        parse_mode="HTML"
    )
