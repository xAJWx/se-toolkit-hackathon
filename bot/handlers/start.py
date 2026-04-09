"""Handler for /start command."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


WELCOME_TEXT = (
    "🔔 *Welcome to RemindMe!*\n\n"
    "I help you set reminders using natural language.\n"
    "Just tell me what to remind you and when!\n\n"
    "*Examples:*\n"
    "• _remind me to submit lab 9 at 5pm_\n"
    "• _buy milk tomorrow at 10:00_\n"
    "• _meeting in 2 hours_\n"
    "• _call mom on monday at 3pm_\n\n"
    "Use /help to see all available commands."
)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Return inline keyboard for /start."""
    keyboard = [
        [
            InlineKeyboardButton("📋 My Reminders", callback_data="list"),
            InlineKeyboardButton("➕ Add Reminder", callback_data="add_help"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_start() -> str:
    """Return welcome message."""
    return WELCOME_TEXT
