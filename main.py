# This file is part of Study Planner Bot.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.profile import registration_handler, update_profile_handler, timezone_handler, view_profile
from handlers.reminder import reminder_handler, cancel_reminder
from handlers.goals import set_goal_handler, log_time_handler, view_progress
from handlers.site import set_site_handler, open_site, clear_site
from handlers.flashcards import flashcard_handler, practice_flashcard_handler, delete_flashcard_handler, view_flashcards
from handlers.general import start, help_button
from handlers.pomodoro import start_pomodoro, cancel_pomodoro

TOKEN = 0 #change to real token
application = Application.builder().token(TOKEN).build()
application.job_queue

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)(^/?help$)"), help_button))
application.add_handler(registration_handler)
application.add_handler(CommandHandler("view_profile", view_profile))
application.add_handler(update_profile_handler)
application.add_handler(reminder_handler)
application.add_handler(CommandHandler("cancel_reminder", cancel_reminder))
application.add_handler(timezone_handler)
application.add_handler(CommandHandler("pomodoro", start_pomodoro))
application.add_handler(CommandHandler("cancel_pomodoro", cancel_pomodoro))
application.add_handler(set_goal_handler)
application.add_handler(CommandHandler("progress", view_progress))
application.add_handler(log_time_handler)
application.add_handler(set_site_handler)
application.add_handler(CommandHandler("site", open_site))
application.add_handler(CommandHandler("clear_site", clear_site))
application.add_handler(flashcard_handler)
application.add_handler(practice_flashcard_handler)
application.add_handler(delete_flashcard_handler)
application.add_handler(CommandHandler("view_flashcards", view_flashcards))

if __name__ == "__main__":
    application.run_polling()

