from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_chat_id: int = int(os.getenv("ADMIN_CHAT_ID", "0"))
    db_path: str = os.getenv("DB_PATH", "app/data/bot.db")
    city_default: str = os.getenv("CITY_DEFAULT", "Пермь")

    webhook_url: str = os.getenv("WEBHOOK_URL", "")
    webhook_secret_token: str = os.getenv("WEBHOOK_SECRET_TOKEN", "secret")
    port: int = int(os.getenv("PORT", "8080"))

    # подписки на каналы (пост-оплата)
    require_subscriptions: bool = os.getenv("REQUIRE_SUBSCRIPTIONS", "true").lower() == "true"
    main_channel_id: str | int = os.getenv("MAIN_CHANNEL_ID", "@your_main_channel")
    main_channel_url: str = os.getenv("MAIN_CHANNEL_URL", "https://t.me/your_main_channel")
    support_channel_id: str | int = os.getenv("SUPPORT_CHANNEL_ID", "@your_support_channel")
    support_channel_url: str = os.getenv("SUPPORT_CHANNEL_URL", "https://t.me/your_support_channel")
    profile_bot_url: str = os.getenv("PROFILE_BOT_URL", "").strip()

    # тарифы в звездах (XTR). Для Stars должен быть ровно один LabeledPrice.
    plans: dict = {
        "buyer": {
            "3d":  {"title": "Покупатель · 3 дня",  "days": 3,  "stars": 499},
            "7d":  {"title": "Покупатель · 7 дней",  "days": 7,  "stars": 1990},
            "30d": {"title": "Покупатель · 30 дней", "days": 30, "stars": 4990},
        },
        "agent": {
            "3d":  {"title": "Агент · 3 дня",  "days": 3,  "stars": 499},
            "7d":  {"title": "Агент · 7 дней",  "days": 7,  "stars": 1990},
            "30d": {"title": "Агент · 30 дней", "days": 30, "stars": 4990},
        }
    }

settings = Settings()
