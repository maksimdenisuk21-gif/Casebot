import os
import json
import sqlite3
from fastapi import FastAPI, Request
from telegram import Update, LabeledPrice, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
tg_app = Application.builder().token(BOT_TOKEN).build()

# =====================
# DB (SQLite)
# =====================
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()


def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0
    return row[0]


def add_balance(user_id, amount):
    cursor.execute("""
    INSERT INTO users (user_id, balance)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
    """, (user_id, amount, amount))
    conn.commit()


# =====================
# START + MINI APP
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton(
        text="Open CaseFight",
        web_app=WebAppInfo(url="https://izuzus-2.onrender.com")
    )

    await update.message.reply_text(
        "CaseFight Online",
        reply_markup=ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    )


# =====================
# CREATE DEPOSIT
# =====================
async def create_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        amount = int(data["amount"])
    except:
        await update.message.reply_text("Error")
        return

    if amount < 50 or amount > 5000:
        await update.message.reply_text("50–5000 only")
        return

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Deposit",
        description=f"{amount} Stars deposit",
        payload=f"dep_{amount}",
        currency="XTR",
        prices=[LabeledPrice("deposit", amount)]
    )


# =====================
# PAYMENTS
# =====================
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    amount = payment.total_amount

    add_balance(user_id, amount)

    bal = get_balance(user_id)

    await update.message.reply_text(
        f"Paid: {amount} ⭐\nBalance: {bal}"
    )


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
# HANDLERS
# =====================
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, create_deposit))
tg_app.add_handler(PreCheckoutQueryHandler(precheckout))
tg_app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))


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
