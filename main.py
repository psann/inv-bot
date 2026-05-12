import os
import asyncio
import threading
from datetime import datetime, timedelta, timezone
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    web_app.run(host="0.0.0.0", port=10000)

async def send_later(bot, chat_id, message, send_time):
    now = datetime.now(timezone.utc)
    wait_seconds = (send_time - now).total_seconds()

    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)

    await bot.send_message(chat_id=chat_id, text=message)

async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    try:
        title, date_str, reminders = [x.strip() for x in text.split("|")]
        event_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        event_time = event_time.replace(tzinfo=timezone.utc)

        chat_id = update.effective_chat.id

        for r in reminders.split(","):
            mins = int(r.strip())
            send_time = event_time - timedelta(minutes=mins)

            if mins == 0:
                msg = f"⚔ {title} starts now!"
            else:
                msg = f"🔔 {title} starts in {mins} minutes!"

            asyncio.create_task(send_later(context.bot, chat_id, msg, send_time))

        await update.message.reply_text("Event scheduled!")

    except Exception:
        await update.message.reply_text(
            "Format error.\nUse:\n/event Tunnel Attack | 2026-05-14 14:00 | 60,30,0"
        )

threading.Thread(target=run_web).start()

bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("event", event))
bot_app.run_polling()
