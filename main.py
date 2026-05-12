import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone

TOKEN = os.environ["BOT_TOKEN"]

scheduler = AsyncIOScheduler()
scheduler.start()

async def event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    title, date_str, reminders = [x.strip() for x in text.split("|")]

    event_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    event_time = event_time.replace(tzinfo=timezone.utc)

    reminder_list = reminders.split(",")

    chat_id = update.effective_chat.id

    for r in reminder_list:
        mins = int(r)

        send_time = event_time - timedelta(minutes=mins)

        if mins == 0:
            msg = f"⚔ {title} starts now!"
        else:
            msg = f"🔔 {title} starts in {mins} minutes!"

        scheduler.add_job(
            context.bot.send_message,
            "date",
            run_date=send_time,
            args=[chat_id, msg]
        )

    await update.message.reply_text("Event scheduled!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("event", event))

app.run_polling()
from flask import Flask
import threading

app_web = Flask(name)

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
