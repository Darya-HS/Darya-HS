
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from utils.data import user_profiles, save_profiles
from math import floor
from handlers.general import cancel_action
from states import SET_GOAL_SUBJECT, SET_GOAL_NAME, SET_GOAL_HOURS, UPDATE_GOAL_SELECTION, UPDATE_GOAL_ACTION, EDIT_GOAL_HOURS, LOG_TIME_SELECTION, LOG_TIME_HOURS

async def start_set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    if user_id not in user_profiles:
        await update.message.reply_text("You don't have a profile yet. Use /register to create one")
        return ConversationHandler.END

    await update.message.reply_text("What is the subject of the goal?")
    return SET_GOAL_SUBJECT

async def set_goal_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["subject"] = update.message.text
    await update.message.reply_text("What is the goal name? (e.g., midterm, project)")
    return SET_GOAL_NAME

async def set_goal_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["goal_name"] = update.message.text
    await update.message.reply_text("How many target hours do you want to allocate to this goal?")
    return SET_GOAL_HOURS

async def set_goal_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    subject = context.user_data["subject"]
    goal_name = context.user_data["goal_name"]

    try:
        target_hours = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Target hours must be a number. Please start over with /set_goal")
        return ConversationHandler.END

    goals = user_profiles[user_id].setdefault("goals", [])
    goals.append({
        "subject": subject,
        "goal_name": goal_name,
        "target_hours": target_hours,
        "logged_hours": 0,
    })
    save_profiles()

    await update.message.reply_text(
        f"Goal set: {subject} - {goal_name} ({target_hours} hours target) 🎯"
    )
    return ConversationHandler.END

async def collect_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)

    user_profiles[user_id] = {
        "username": context.user_data["username"],
        "goals": [],
        "timezone": "UTC",
    }

    save_profiles()

    await update.message.reply_text(
        f"Profile created! Welcome, {context.user_data['username']} 🎉\n"
        "You can now set study goals using /set_goal"
    )
    return ConversationHandler.END

async def update_goal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    try:
        goal_index = int(update.message.text.strip()) - 1
    except ValueError:
        await update.message.reply_text("Invalid input. Please reply with the number of the goal")
        return UPDATE_GOAL_SELECTION

    goals = user_profiles[user_id].get("goals", [])
    if not (0 <= goal_index < len(goals)):
        await update.message.reply_text("Invalid choice. Please select a valid goal number")
        return UPDATE_GOAL_SELECTION

    context.user_data["goal_index"] = goal_index

    await update.message.reply_text("Reply with 'edit' to modify this goal or 'delete' to remove it")
    return UPDATE_GOAL_ACTION

async def update_goal_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    action = update.message.text.strip().lower()
    user_id = str(update.message.from_user.id)
    goal_index = context.user_data["goal_index"]

    if action == "edit":
        await update.message.reply_text("Enter the new target hours for this goal:")
        return EDIT_GOAL_HOURS
    elif action == "delete":
        goals = user_profiles[user_id]["goals"]
        deleted_goal = goals.pop(goal_index)
        save_profiles()
        await update.message.reply_text(f"Deleted goal: {deleted_goal['subject']} ({deleted_goal['goal_name']}).")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Invalid action. Reply with 'edit' or 'delete'")
        return UPDATE_GOAL_ACTION
    
async def edit_goal_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    goal_index = context.user_data["goal_index"]

    try:
        new_target_hours = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid number for target hours")
        return EDIT_GOAL_HOURS

    goals = user_profiles[user_id]["goals"]
    goals[goal_index]["target_hours"] = new_target_hours
    save_profiles()

    await update.message.reply_text(
        f"Goal updated successfully! 🎉\n"
        f"Updated Goal: {goals[goal_index]['subject']} ({goals[goal_index]['goal_name']})\n"
        f"New Target Hours: {new_target_hours}"
    )
    return ConversationHandler.END

async def start_log_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    goals = user_profiles[user_id].get("goals", [])

    if not goals:
        await update.message.reply_text("You don't have any goals yet. Use /set_goal to add one")
        return ConversationHandler.END

    goals_text = "\n".join(
        [f"{i + 1}. {goal['subject']} ({goal['goal_name']}) - {goal['logged_hours']}/{goal['target_hours']} hours"
         for i, goal in enumerate(goals)]
    )
    await update.message.reply_text(
        f"Select a goal to log time for:\n{goals_text}\nReply with the goal number"
    )
    return LOG_TIME_SELECTION

async def log_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    goals = user_profiles[user_id].get("goals", [])

    try:
        goal_index = int(update.message.text.strip()) - 1
        if not (0 <= goal_index < len(goals)):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid input. Please reply with a valid goal number")
        return LOG_TIME_SELECTION

    context.user_data["goal_index"] = goal_index
    await update.message.reply_text("How many hours would you like to log?")
    return LOG_TIME_HOURS

async def log_time_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    goal_index = context.user_data["goal_index"]

    try:
        logged_hours = float(update.message.text.strip())
        if logged_hours <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a valid positive number for hours")
        return LOG_TIME_HOURS

    goal = user_profiles[user_id]["goals"][goal_index]
    goal["logged_hours"] += logged_hours
    save_profiles()

    progress = floor((goal["logged_hours"] / goal["target_hours"]) * 100)
    progress = min(progress, 100)  # Cap progress at 100%

    await update.message.reply_text(
        f"Successfully logged {logged_hours} hours for {goal['subject']} ({goal['goal_name']}).\n"
        f"Progress: {goal['logged_hours']}/{goal['target_hours']} hours ({progress}%)"
    )
    return ConversationHandler.END

async def view_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    goals = user_profiles[user_id].get("goals", [])

    if not goals:
        await update.message.reply_text("You don't have any goals yet. Use /set_goal to add one.")
        return

    progress_text = "\n".join(
        [f"{goal['subject']} ({goal['goal_name']}): {goal['logged_hours']}/{goal['target_hours']} hours "
         f"({floor((goal['logged_hours'] / goal['target_hours']) * 100)}%)"
         for goal in goals]
    )
    await update.message.reply_text(f"Your progress:\n{progress_text}")

set_goal_handler = ConversationHandler(
    entry_points=[CommandHandler("set_goal", start_set_goal)],
    states={
        SET_GOAL_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_goal_subject)],
        SET_GOAL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_goal_name)],
        SET_GOAL_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_goal_hours)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)

log_time_handler = ConversationHandler(
    entry_points=[CommandHandler("log_time", start_log_time)],
    states={
        LOG_TIME_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_time_selection)],
        LOG_TIME_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_time_hours)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)