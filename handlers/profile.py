# This file is part of Study Planner Bot.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import pytz
from states import USERNAME, UPDATE_PROFILE, UPDATE_GOAL_SELECTION, UPDATE_TIMEZONE, UPDATE_USERNAME, SELECT_FIELD, GOALS, UPDATE_GOAL_ACTION, EDIT_GOAL_HOURS
from utils.data import user_profiles, save_profiles
from handlers.general import cancel_action
from handlers.goals import update_goal_action, edit_goal_hours, update_goal_selection, collect_goals

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    
    if user_id in user_profiles:
        await update.message.reply_text(
            "You already have a profile. Use /view_profile to check it or /update_profile to modify it"
        )
        return ConversationHandler.END

    await update.message.reply_text("Welcome! Let's set up your profile. What is your name?")
    return USERNAME

async def collect_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    username = update.message.text.strip()

    user_profiles[user_id] = {
        "username": username,
        "timezone": "UTC",
        "goals": [],
    }
    save_profiles()

    await update.message.reply_text(
        "Profile created successfully! 🎉\n"
        "Default timezone is set to UTC. Use /set_timezone to change it if needed.\n"
        "You can now set study goals for your subjects using /set_goal"
    )
    return ConversationHandler.END

async def start_update_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    if user_id not in user_profiles:
        await update.message.reply_text("You don't have a profile yet. Use /register to create one")
        return ConversationHandler.END

    await update.message.reply_text(
        "What would you like to update?\n"
        "1. Username\n"
        "2. Timezone\n"
        "3. Goals\n\n"
        "Reply with the option number",
    )
    return UPDATE_PROFILE

async def update_profile_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip()
    if choice == "1":
        await update.message.reply_text("Enter your new username:")
        return UPDATE_USERNAME
    elif choice == "2":
        await update.message.reply_text("Enter your new timezone (e.g., Asia/Seoul):")
        return UPDATE_TIMEZONE
    elif choice == "3":
        user_id = str(update.message.from_user.id)
        goals = user_profiles[user_id].get("goals", [])
        if not goals:
            await update.message.reply_text("No goals to update. Use /set_goal to add one")
            return ConversationHandler.END

        goals_text = "\n".join(
            [f"{i + 1}. {goal['subject']} ({goal['goal_name']})" for i, goal in enumerate(goals)]
        )
        await update.message.reply_text(
            f"Select a goal to update or delete:\n{goals_text}\nReply with the goal number"
        )
        return UPDATE_GOAL_SELECTION
    else:
        await update.message.reply_text("Invalid choice. Please reply with 1, 2, or 3")
        return UPDATE_PROFILE

async def update_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    new_username = update.message.text.strip()
    user_profiles[user_id]["username"] = new_username
    save_profiles()
    await update.message.reply_text(f"Username updated to {new_username}")
    return ConversationHandler.END

async def update_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    timezone_input = update.message.text.strip()

    try:
        pytz.timezone(timezone_input)
        user_profiles[user_id]["timezone"] = timezone_input
        save_profiles()
        await update.message.reply_text(f"Timezone updated to {timezone_input}")
        return ConversationHandler.END
    except pytz.UnknownTimeZoneError:
        await update.message.reply_text("Invalid timezone. Please try again")
        return UPDATE_TIMEZONE
    
async def set_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Please enter your timezone (e.g., Asia/Seoul, Europe/Berlin, UTC). You can find the list of valid timezones here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
    )
    return SELECT_FIELD
    
async def handle_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    timezone_input = update.message.text.strip()

    try:
        user_timezone = pytz.timezone(timezone_input)

        if user_id not in user_profiles:
            user_profiles[user_id] = {}
        user_profiles[user_id]["timezone"] = timezone_input
        save_profiles()

        await update.message.reply_text(
            f"Your timezone has been set to {timezone_input} successfully!"
        )
        return ConversationHandler.END
    except pytz.UnknownTimeZoneError:
        await update.message.reply_text("Invalid timezone. Please try again")
        return SELECT_FIELD
    
async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    profile = user_profiles.get(user_id)

    if not profile:
        await update.message.reply_text("You don't have a profile yet. Use /register to create one")
        return

    username = profile.get("username", "Not set")
    timezone = profile.get("timezone", "UTC")
    goals = profile.get("goals", [])
    website = profile.get("website", "Not set")

    if goals:
        goals_text = "\n".join(
            [
                f"- {goal['subject']} ({goal['goal_name']}): {goal['logged_hours']} / {goal['target_hours']} hours"
                for goal in goals
            ]
        )
    else:
        goals_text = "No goals set yet"

    message = (
        f"👤 **Profile Details**:\n"
        f"- Username: {username}\n"
        f"- Timezone: {timezone}\n"
        f"- Website: {website}\n\n"
        f"🎯 **Goals**:\n{goals_text}"
    )
    await update.message.reply_text(message, parse_mode="Markdown")
    
registration_handler = ConversationHandler(
    entry_points=[CommandHandler("register", start_registration)],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_username)],
        GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_goals)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)

update_profile_handler = ConversationHandler(
    entry_points=[CommandHandler("update_profile", start_update_profile)],
    states={
        UPDATE_PROFILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_profile_selection)],
        UPDATE_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_username)],
        UPDATE_TIMEZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_timezone)],
        UPDATE_GOAL_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_goal_selection)],
        UPDATE_GOAL_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_goal_action)],
        EDIT_GOAL_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_goal_hours)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)

timezone_handler = ConversationHandler(
    entry_points=[CommandHandler("set_timezone", set_timezone)],
    states={
        SELECT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timezone)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)
