from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🙋‍♂️ Я покупатель", callback_data="role:buyer")
    kb.button(text="🧑‍💼 Я агент", callback_data="role:agent")
    kb.button(text="ℹ️ Как это работает", callback_data="about")
    kb.adjust(1,1,1)
    return kb.as_markup()

def buyer_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔎 Начать подбор", callback_data="buyer:search")
    kb.button(text="⭐ Премиум", callback_data="buyer:premium")
    kb.button(text="⬅️ Назад", callback_data="back:home")
    kb.adjust(1,1,1)
    return kb.as_markup()

def agent_menu_kb(has_subscription: bool):
    kb = InlineKeyboardBuilder()
    if has_subscription:
        kb.button(text="📥 Лента заявок", callback_data="agent:leads")
        kb.button(text="➕ Добавить объект", callback_data="agent:add_object")
    else:
        kb.button(text="⭐ Оформить подписку", callback_data="agent:subscribe")
    kb.button(text="⬅️ Назад", callback_data="back:home")
    kb.adjust(1,1,1)
    return kb.as_markup()

def payment_method_kb(role: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="⭐ Оплата звёздами (XTR)", callback_data=f"pay:stars:{role}")
    kb.button(text="🏦 Оплата по СБП", callback_data=f"pay:sbp:{role}")
    kb.button(text="⬅️ Назад", callback_data=f"{role}:menu")
    kb.adjust(1,1,1)
    return kb.as_markup()

def plans_kb(role: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="3 дня · 499⭐", callback_data=f"plan:{role}:3d")
    kb.button(text="7 дней · 1 990⭐", callback_data=f"plan:{role}:7d")
    kb.button(text="30 дней · 4 990⭐", callback_data=f"plan:{role}:30d")
    kb.button(text="⬅️ Назад", callback_data=f"pay:stars:{role}")
    kb.adjust(1,1,1,1)
    return kb.as_markup()

def sbp_confirm_kb(role: str, plan: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Я оплатил(а) по СБП", callback_data=f"sbp:paid:{role}:{plan}")
    kb.button(text="⬅️ Назад", callback_data=f"pay:sbp:{role}")
    kb.adjust(1,1)
    return kb.as_markup()

def admin_approve_kb(user_id: int, plan: str, role: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"admin:approve:{user_id}:{role}:{plan}")
    kb.button(text="❌ Отклонить", callback_data=f"admin:reject:{user_id}:{role}:{plan}")
    kb.adjust(2)
    return kb.as_markup()

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def subs_kb(main_url: str, sup_url: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Главный канал", url=main_url)
    kb.button(text="🆘 Канал поддержки", url=sup_url)
    kb.button(text="✅ Я подписался(ась)", callback_data="subs:check")
    kb.adjust(1,1,1)
    return kb.as_markup()

def role_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🙋‍♂️ Покупатель", callback_data="profile:role:buyer")
    kb.button(text="🧑‍💼 Риелтор", callback_data="profile:role:agent")
    kb.adjust(1,1)
    return kb.as_markup()
