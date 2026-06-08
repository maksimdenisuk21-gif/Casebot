import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# =====================
# НАСТРОЙКИ (НЕ МЕНЯТЬ)
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()
bot = Bot(token=BOT_TOKEN)

tg_app = Application.builder().token(BOT_TOKEN).build()

# =====================
# КОМАНДЫ БОТА
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CaseFight работает")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Покупка через Stars позже")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("buy", buy))

# =====================
# WEBHOOK ПРИЁМ
# =====================
@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await tg_app.process_update(update)
    return {"ok": True}

# =====================
# СТАРТ СЕРВЕРА
# =====================
@app.on_event("startup")
async def startup():
    await tg_app.initialize()
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await tg_app.shutdown()
