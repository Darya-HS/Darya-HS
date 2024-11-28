from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import utils.keyboards as keyboards

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Hello! I'm your Study Planner Bot 🤖.\n"
        "Here are the things I can help you with:\n\n"
        "📝 **Profile Management**\n"
        "/register - Create your study profile\n"
        "/view_profile - View your current study profile\n"
        "/update_profile - Update your profile details\n\n"
        "⏰ **Time Management**\n"
        "/set_reminder - Set a daily study reminder\n"
        "/cancel_reminder - Cancel your daily reminder\n"
        "/pomodoro - Start a Pomodoro session\n"
        "/cancel_pomodoro - Cancel your current Pomodoro session\n\n"
        "🎯 **Goals and Progress**\n"
        "/set_goal - Set a new study goal\n"
        "/progress - View your study progress\n"
        "/log_time - Log study hours for a goal\n\n"
        "📚 **Flashcards**\n"
        "/add_flashcard - Add a new flashcard\n"
        "/view_flashcards - View all your flashcards\n"
        "/practice_flashcards - Practice your flashcards\n"
        "/delete_flashcard - Delete a flashcard\n\n"
        "🌐 **Website Management**\n"
        "/set_site - Set a website for quick access\n"
        "/site - Open your saved website\n"
        "/clear_site - Clear your saved website\n\n"
        "❌ **Other**\n"
        "/cancel - Cancel any ongoing action\n"
    )
    await update.message.reply_text(message, reply_markup=keyboards.get_main_keyboard())

async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Here are the commands you can use:\n\n"
        "📝 **Profile Management**\n"
        "/register - Create your study profile\n"
        "/view_profile - View your current study profile\n"
        "/update_profile - Update your profile details\n\n"
        "⏰ **Time Management**\n"
        "/set_reminder - Set a daily study reminder\n"
        "/cancel_reminder - Cancel your daily reminder\n"
        "/pomodoro - Start a Pomodoro session\n"
        "/cancel_pomodoro - Cancel your current Pomodoro session\n\n"
        "🎯 **Goals and Progress**\n"
        "/set_goal - Set a new study goal\n"
        "/progress - View your study progress\n"
        "/log_time - Log study hours for a goal\n\n"
        "📚 **Flashcards**\n"
        "/add_flashcard - Add a new flashcard\n"
        "/view_flashcards - View all your flashcards\n"
        "/practice_flashcards - Practice your flashcards\n"
        "/delete_flashcard - Delete a flashcard\n\n"
        "🌐 **Website Management**\n"
        "/set_site - Set a website for quick access\n"
        "/site - Open your saved website\n"
        "/clear_site - Clear your saved website\n\n"
        "❌ **Other**\n"
        "/cancel - Cancel any ongoing action\n"
    )
    await update.message.reply_text(message, reply_markup=keyboards.get_main_keyboard())

async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Action canceled.")
    return ConversationHandler.END