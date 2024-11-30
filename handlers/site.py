
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from utils.data import user_profiles, save_profiles
from handlers.general import cancel_action
from states import SET_SITE_URL


async def start_set_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt the user to input a website URL"""
    await update.message.reply_text("Please enter the website URL (e.g., https://example.com):")
    return SET_SITE_URL

async def save_site_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the user's website URL"""
    user_id = str(update.message.from_user.id)
    url = update.message.text.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await update.message.reply_text("Invalid URL. Please make sure it starts with http:// or https://")
        return SET_SITE_URL

    # Save the URL in the user's profile
    if user_id not in user_profiles:
        user_profiles[user_id] = {"username": "Unknown", "goals": [], "website": url}
    else:
        user_profiles[user_id]["website"] = url

    save_profiles()  # Save the profile to disk
    await update.message.reply_text(f"Website saved! Use /site to access {url}")
    return ConversationHandler.END

async def open_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a button to open the user's saved site"""
    user_id = str(update.message.from_user.id)

    if user_id not in user_profiles or "website" not in user_profiles[user_id]:
        await update.message.reply_text("No website saved. Use /set_site to set one first")
        return

    website_url = user_profiles[user_id]["website"]

    # Create an inline button with the link
    keyboard = [
        [InlineKeyboardButton("Open Site 🌐", url=website_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Click the button below to visit your saved site ({website_url}):",
        reply_markup=reply_markup
    )

async def clear_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in user_profiles and "website" in user_profiles[user_id]:
        del user_profiles[user_id]["website"]
        save_profiles()
        await update.message.reply_text("Your saved website has been cleared")
    else:
        await update.message.reply_text("No website to clear")

set_site_handler = ConversationHandler(
    entry_points=[CommandHandler("set_site", start_set_site)],
    states={
        SET_SITE_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_site_url)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)