# This file is part of Study Planner Bot.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from datetime import time
import pytz
from utils.data import user_profiles, save_profiles
from states import REMINDER_TIME
from handlers.general import cancel_action

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    if user_id not in user_profiles:
        await update.message.reply_text("You don't have a profile yet. Use /register to create one")
        return ConversationHandler.END

    await update.message.reply_text("What time should I remind you to study? (e.g., 09:00 or 18:30)")
    return REMINDER_TIME

async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    reminder_time = update.message.text.strip()

    user_timezone = user_profiles.get(user_id, {}).get("timezone", "UTC")

    try:
        hour, minute = map(int, reminder_time.split(":"))
        timezone_obj = pytz.timezone(user_timezone)
        reminder_time_obj = time(hour, minute, tzinfo=timezone_obj)

        context.job_queue.run_daily(
            send_reminder,
            time=reminder_time_obj,
            data={"chat_id": update.message.chat_id, "user_id": user_id},
            name=f"reminder_{user_id}",
        )

        user_profiles[user_id]["reminder_time"] = reminder_time
        save_profiles()

        await update.message.reply_text(
            f"Your daily reminder has been set for {reminder_time} in your timezone ({user_timezone}) 🎉"
        )
        return ConversationHandler.END
    except (ValueError, IndexError) as e:
        await update.message.reply_text(
            "Invalid time format. Please try again with the HH:MM format (24-hour)"
        )
        return REMINDER_TIME

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        job_data = context.job.data
        chat_id = job_data["chat_id"]
        await context.bot.send_message(chat_id=chat_id, text="This is your scheduled reminder! Let's hit the books! 📚")

    except Exception as e:
        print(f"ERROR in send_reminder: {e}")

async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    job_name = f"reminder_{user_id}"

    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

    if user_id in user_profiles:
        user_profiles[user_id].pop("reminder_time", None)
        save_profiles()

    await update.message.reply_text("Your daily reminder has been canceled")
    
reminder_handler = ConversationHandler(
    entry_points=[CommandHandler("set_reminder", set_reminder)],
    states={
        REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_time)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)