import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.db import init_db
from app.handlers import common, start, buyer, agent, payments, admin, onboarding

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.bot_token, parse_mode="HTML")
dp = Dispatcher()

# Routers
dp.include_router(common.router)
dp.include_router(start.router)
dp.include_router(buyer.router)
dp.include_router(agent.router)
dp.include_router(payments.router)
dp.include_router(admin.router)

dp.include_router(onboarding.router)

async def set_commands():
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="menu", description="Меню"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    await init_db()
    await set_commands()
    logging.info("Bot started")

# --- Webhook mode (optional) ---
app = FastAPI()

@app.on_event("startup")
async def _startup():
    await on_startup()
    if settings.webhook_url:
        await bot.set_webhook(url=settings.webhook_url, secret_token=settings.webhook_secret_token)

@app.post("/{token}")
async def telegram_webhook(token: str, request: Request):
    if not settings.webhook_url:
        raise HTTPException(status_code=404, detail="Webhook disabled")
    if token != settings.webhook_secret_token:
        raise HTTPException(status_code=403, detail="Bad token")
    update = await request.json()
    await dp.feed_update(bot, update)
    return JSONResponse({"ok": True})

# --- Polling mode (default) ---
async def polling():
    await on_startup()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    if settings.webhook_url:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=False)
    else:
        asyncio.run(polling())
