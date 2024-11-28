from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Help")],  # Add the "Help" button
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
