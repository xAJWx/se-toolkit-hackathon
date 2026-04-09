"""Handler for /list command — shows user's pending reminders."""

from bot.services.db import ReminderDB
from bot.services.parser import format_reminder_list


async def handle_list(user_id: int, db: ReminderDB) -> str:
    """List all pending reminders for a user."""
    reminders = await db.list_reminders(user_id)
    return format_reminder_list(reminders)
