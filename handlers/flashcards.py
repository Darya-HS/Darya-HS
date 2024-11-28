
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from utils.data import user_profiles, save_profiles
from states import ADD_QUESTION, ADD_ANSWER, PRACTICE_FLASHCARD, DELETE_FLASHCARD
from handlers.general import cancel_action

async def start_add_flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the process to add a new flashcard."""
    await update.message.reply_text("Enter the question for the flashcard:")
    return ADD_QUESTION

async def add_flashcard_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the flashcard question and ask for the answer."""
    context.user_data["flashcard_question"] = update.message.text
    await update.message.reply_text("Enter the answer for the flashcard:")
    return ADD_ANSWER

async def add_flashcard_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the flashcard answer and save it."""
    user_id = str(update.message.from_user.id)
    question = context.user_data["flashcard_question"]
    answer = update.message.text

    flashcards = user_profiles[user_id].setdefault("flashcards", [])
    flashcards.append({"question": question, "answer": answer})
    save_profiles()

    await update.message.reply_text("Flashcard added successfully!")
    return ConversationHandler.END

async def view_flashcards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the list of flashcards."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id].get("flashcards", [])

    if not flashcards:
        await update.message.reply_text("No flashcards found. Use /add_flashcard to add one.")
        return

    flashcards_text = "\n".join([f"{i + 1}. {fc['question']}" for i, fc in enumerate(flashcards)])
    await update.message.reply_text(f"Your flashcards:\n{flashcards_text}")

async def start_practice_flashcards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start practicing flashcards."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id].get("flashcards", [])

    if not flashcards:
        await update.message.reply_text("No flashcards found. Use /add_flashcard to add one.")
        return ConversationHandler.END

    context.user_data["flashcard_index"] = 0
    # Explicitly call the next step
    await ask_flashcard_question(update, context)
    return PRACTICE_FLASHCARD

async def ask_flashcard_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Present a flashcard question to the user."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id]["flashcards"]
    index = context.user_data["flashcard_index"]

    question = flashcards[index]["question"]
    await update.message.reply_text(f"Question: {question}\n\nType your answer:")
    return PRACTICE_FLASHCARD

async def check_flashcard_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Check the user's answer and move to the next flashcard or finish."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id]["flashcards"]
    index = context.user_data["flashcard_index"]

    # Retrieve the correct answer
    correct_answer = flashcards[index]["answer"]
    user_answer = update.message.text.strip()

    if user_answer.lower() == correct_answer.lower():
        await update.message.reply_text("Correct! 🎉")
    else:
        await update.message.reply_text(f"Wrong. The correct answer is: {correct_answer}")

    # Move to the next flashcard
    context.user_data["flashcard_index"] += 1
    if context.user_data["flashcard_index"] < len(flashcards):
        # Call the next question explicitly
        await ask_flashcard_question(update, context)
        return PRACTICE_FLASHCARD
    else:
        # End the practice session
        await update.message.reply_text("You've completed all your flashcards! 🎓")
        return ConversationHandler.END
    
async def start_delete_flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the process to delete a flashcard."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id].get("flashcards", [])

    if not flashcards:
        await update.message.reply_text("No flashcards found. Use /add_flashcard to add one.")
        return ConversationHandler.END

    flashcards_text = "\n".join([f"{i + 1}. {fc['question']}" for i, fc in enumerate(flashcards)])
    await update.message.reply_text(f"Select a flashcard to delete:\n{flashcards_text}")
    return DELETE_FLASHCARD

async def delete_flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the selected flashcard."""
    user_id = str(update.message.from_user.id)
    flashcards = user_profiles[user_id]["flashcards"]

    try:
        index = int(update.message.text.strip()) - 1
        if not (0 <= index < len(flashcards)):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid input. Please select a valid flashcard number.")
        return DELETE_FLASHCARD

    deleted = flashcards.pop(index)
    save_profiles()
    await update.message.reply_text(f"Deleted flashcard: {deleted['question']}")
    return ConversationHandler.END


flashcard_handler = ConversationHandler(
    entry_points=[CommandHandler("add_flashcard", start_add_flashcard)],
    states={
        ADD_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_flashcard_question)],
        ADD_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_flashcard_answer)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)

practice_flashcard_handler = ConversationHandler(
    entry_points=[CommandHandler("practice_flashcards", start_practice_flashcards)],
    states={
        PRACTICE_FLASHCARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_flashcard_answer)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)

delete_flashcard_handler = ConversationHandler(
    entry_points=[CommandHandler("delete_flashcard", start_delete_flashcard)],
    states={
        DELETE_FLASHCARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_flashcard)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)