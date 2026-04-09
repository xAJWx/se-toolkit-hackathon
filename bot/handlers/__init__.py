"""Bot handlers package."""

from bot.handlers.start import handle_start, get_start_keyboard
from bot.handlers.help_handler import handle_help, get_help_keyboard
from bot.handlers.remind import handle_remind
from bot.handlers.list_handler import handle_list
from bot.handlers.delete_handler import handle_delete

__all__ = [
    "handle_start",
    "get_start_keyboard",
    "handle_help",
    "get_help_keyboard",
    "handle_remind",
    "handle_list",
    "handle_delete",
]
