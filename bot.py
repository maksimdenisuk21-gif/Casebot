import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("8622539879:AAHsmHbSBxsoTstBuEFk2m8NAlTEPDHLEzI")
WEBHOOK_URL = os.getenv("https://izuzus-2.onrender.com")

app = FastAPI()
bot = Bot(token=BOT_TOKEN)

telegram_app = Application.builder().token(BOT_TOKEN).build()

# команды

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎁 CaseFight работает (webhook)")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💎 Stars оплата будет добавлена")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("buy", buy))


# webhook endpoint
@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# запуск webhook при старте
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await bot.set_webhook(WEBHOOK_URL)


@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await telegram_app.shutdown()
