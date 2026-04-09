"""Handler for /delete command — removes a reminder by ID."""

from bot.services.db import ReminderDB

DELETE_USAGE = "🗑 *Delete a reminder*\n\nUsage: /delete <id>\n\nExample: `/delete 1`"


async def handle_delete(
    args: str, user_id: int, db: ReminderDB
) -> str:
    """Delete a reminder by ID. Returns response text."""
    if not args.strip():
        return DELETE_USAGE

    try:
        reminder_id = int(args.strip())
    except ValueError:
        return "❌ Please provide a valid reminder ID (a number)."

    deleted = await db.delete_reminder(user_id, reminder_id)

    if deleted:
        return f"✅ Reminder #{reminder_id} has been deleted."
    else:
        return (
            f"❌ Reminder #{reminder_id} not found or doesn't belong to you.\n"
            "Use /list to see your reminders."
        )
