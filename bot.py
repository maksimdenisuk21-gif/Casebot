import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

tg_app = Application.builder().token(BOT_TOKEN).build()

# =====================
# COMMANDS
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CaseFight bot online")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buy works")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("buy", buy))

# =====================
# WEBHOOK
# =====================

@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}

# =====================
# STARTUP
# =====================

@app.on_event("startup")
async def startup():
    await tg_app.initialize()
    print("BOT STARTED")

@app.on_event("shutdown")
async def shutdown():
    await tg_app.shutdown()
