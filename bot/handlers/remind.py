"""Handler for /remind command and natural language reminder creation."""

from datetime import datetime
from typing import Optional

from bot.services.parser import parse_reminder, format_reminder_created
from bot.services.db import ReminderDB

REMIND_USAGE = (
    "📝 *Set a reminder*\n\n"
    "Usage: /remind <description> <time>\n\n"
    "*Examples:*\n"
    "• `/remind submit lab 9 at 5pm`\n"
    "• `/remind buy milk tomorrow at 10:00`\n"
    "• `/remind meeting in 2 hours`\n\n"
    "You can also just type a reminder naturally "
    "without /remind — I'll try to parse it!"
)


async def handle_remind(
    text: str, user_id: int, db: ReminderDB
) -> str:
    """Parse and create a reminder. Returns response text."""
    if not text.strip():
        return REMIND_USAGE

    result = parse_reminder(text)

    if result is None:
        return (
            "❌ I couldn't understand the date/time from your message.\n\n"
            "Please include a time like:\n"
            "• _at 5pm_\n"
            "• _tomorrow at 10:00_\n"
            "• _in 2 hours_\n"
            "• _on monday at 3pm_"
        )

    task_text = result["text"]
    remind_at = result["remind_at"]

    # Ensure remind_at is timezone-aware or naive consistently
    if remind_at.tzinfo is not None:
        remind_at = remind_at.replace(tzinfo=None)

    reminder_id = await db.create_reminder(user_id, task_text, remind_at)

    return format_reminder_created(reminder_id, task_text, remind_at)
