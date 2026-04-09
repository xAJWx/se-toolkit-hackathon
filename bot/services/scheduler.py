"""Reminder scheduler — periodically checks for due reminders and sends them."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from bot.services.db import ReminderDB

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 30  # seconds

# User's timezone (UTC+3)
USER_TZ = timezone(timedelta(hours=3))


def format_time_for_user(dt: datetime) -> str:
    """Format datetime for display — naive timestamp, show as-is."""
    return dt.strftime("%d %b %Y, %H:%M")


def get_reminder_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for a reminder notification."""
    keyboard = [
        [
            InlineKeyboardButton("📋 My Reminders", callback_data="list"),
            InlineKeyboardButton("➕ Add Another", callback_data="add_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


class ReminderScheduler:
    """Background task that checks for due reminders and sends notifications."""

    def __init__(self, bot: Bot, db: ReminderDB):
        self._bot = bot
        self._db = db
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the scheduler background task."""
        self._task = asyncio.create_task(self._loop())
        logger.info("Reminder scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("Reminder scheduler stopped")

    async def _loop(self) -> None:
        """Main scheduler loop."""
        while True:
            try:
                await self._check_and_send()
            except Exception:
                logger.exception("Error in reminder scheduler loop")
            await asyncio.sleep(CHECK_INTERVAL)

    async def _check_and_send(self) -> None:
        """Check for due reminders and send them."""
        due = await self._db.get_due_reminders()

        if due:
            logger.info(f"Found {len(due)} due reminders: {[r['id'] for r in due]}")

        for reminder in due:
            try:
                user_id = reminder["user_id"]
                text = reminder["text"]
                remind_at = reminder["remind_at"]

                # Convert UTC from DB to user's local time
                time_str = format_time_for_user(remind_at)

                message = f"🔔 *Reminder*\n\n📝 {text}\n⏰ {time_str}"
                keyboard = get_reminder_keyboard(reminder["id"])

                await self._bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )

                await self._db.mark_sent(reminder["id"])
                logger.info(f"Sent reminder #{reminder['id']} to user {user_id}")

            except Exception:
                logger.exception(
                    f"Failed to send reminder #{reminder['id']}"
                )
