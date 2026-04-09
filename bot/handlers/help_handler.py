"""Handler for /help command."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

HELP_TEXT = (
    "📖 *RemindMe Bot — Help*\n\n"
    "*Commands:*\n"
    "/start — Welcome message\n"
    "/help — Show this help\n"
    "/remind <text> — Set a reminder\n"
    "/list — List your pending reminders\n"
    "/delete <id> — Delete a reminder by ID\n\n"
    "*Natural language examples:*\n"
    "• _remind me to submit lab 9 at 5pm_\n"
    "• _buy milk tomorrow at 10:00_\n"
    "• _meeting in 2 hours_\n"
    "• _call mom on monday at 3pm_\n\n"
    "You can also just type a reminder naturally "
    "without any command — I'll try to parse it!"
)


def get_help_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📋 My Reminders", callback_data="list")],
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_help() -> str:
    return HELP_TEXT
