import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing in environment variables")

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
tg_app = Application.builder().token(BOT_TOKEN).build()

# =====================
# COMMANDS
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CaseFight bot online")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buy command works")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("buy", buy))

# =====================
# WEBHOOK
# =====================

@app.post("/")
async def webhook(req: Request):
    try:
        data = await req.json()
        print("UPDATE:", data)

        update = Update.de_json(data, bot)
        await tg_app.process_update(update)

        return {"ok": True}

    except Exception as e:
        print("ERROR:", e)
        return {"ok": False}

# =====================
# LIFECYCLE
# =====================

@app.on_event("startup")
async def startup():
    await tg_app.initialize()
    print("BOT STARTED")

@app.on_event("shutdown")
async def shutdown():
    await tg_app.shutdown()
