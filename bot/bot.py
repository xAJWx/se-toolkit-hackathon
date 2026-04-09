#!/usr/bin/env python3
"""RemindMe Telegram Bot — Smart reminders in natural language.

Supports two modes:
1. Test mode: `uv run bot.py --test "remind me to submit lab 9 at 5pm"` — prints response to stdout
2. Telegram mode: Connects to Telegram API and handles messages
"""

import sys
import argparse
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from bot.config import load_config, get_dsn
from bot.handlers import (
    handle_start,
    handle_help,
    handle_remind,
    handle_list,
    handle_delete,
    get_start_keyboard,
)
from bot.services import ReminderDB, ReminderScheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Global DB and scheduler instances
db: ReminderDB | None = None
scheduler: ReminderScheduler | None = None


async def handle_start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /start command."""
    response = handle_start()
    keyboard = get_start_keyboard()
    await update.message.reply_text(response, reply_markup=keyboard, parse_mode="Markdown")


async def handle_help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /help command."""
    await update.message.reply_text(handle_help(), parse_mode="Markdown")


async def handle_remind_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /remind command."""
    assert db is not None
    text = " ".join(context.args) if context.args else ""
    user_id = update.effective_user.id
    response = await handle_remind(text, user_id, db)
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_list_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /list command."""
    assert db is not None
    user_id = update.effective_user.id
    response = await handle_list(user_id, db)
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_delete_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /delete command."""
    assert db is not None
    args = " ".join(context.args) if context.args else ""
    user_id = update.effective_user.id
    response = await handle_delete(args, user_id, db)
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle natural language reminders (any text that's not a command)."""
    assert db is not None
    text = update.message.text
    if text:
        user_id = update.effective_user.id
        response = await handle_remind(text, user_id, db)
        await update.message.reply_text(response, parse_mode="Markdown")


async def handle_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle inline keyboard button clicks."""
    assert db is not None
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    data = query.data

    if data == "list":
        user_id = query.from_user.id
        response = await handle_list(user_id, db)
        await query.edit_message_text(response, parse_mode="Markdown")
    elif data == "add_help":
        await query.edit_message_text(
            "➕ *Add a reminder*\n\n"
            "Just type your reminder naturally, for example:\n"
            "• _remind me to submit lab 9 at 5pm_\n"
            "• _buy milk tomorrow at 10:00_\n"
            "• _meeting in 2 hours_",
            parse_mode="Markdown",
        )
    elif data == "help":
        await query.edit_message_text(handle_help(), parse_mode="Markdown")
    else:
        await query.edit_message_text("Unknown action.")


def run_test_mode(command_text: str) -> None:
    """Run in test mode — parse reminder and print response (no DB/Telegram).

    Args:
        command_text: The text to test (e.g., "/remind buy milk at 5pm")
    """
    from bot.services.parser import parse_reminder, format_reminder_created

    text = command_text
    if text.startswith("/remind "):
        text = text[len("/remind "):]
    elif text.startswith("/start"):
        print(handle_start())
        sys.exit(0)
    elif text.startswith("/help"):
        print(handle_help())
        sys.exit(0)

    result = parse_reminder(text)

    if result is None:
        print(
            "❌ I couldn't understand the date/time from your message.\n\n"
            "Please include a time like:\n"
            "• _at 5pm_\n"
            "• _tomorrow at 10:00_\n"
            "• _in 2 hours_"
        )
    else:
        task_text = result["text"]
        remind_at = result["remind_at"]
        print(format_reminder_created(0, task_text, remind_at))

    sys.exit(0)


async def run_telegram_mode(config: dict) -> None:
    """Run the bot in Telegram mode.

    Args:
        config: Configuration dictionary with BOT_TOKEN and DB settings
    """
    global db, scheduler

    bot_token = config.get("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN not found in configuration")
        sys.exit(1)

    logger.info("Starting RemindMe Telegram bot...")

    # Initialize DB
    dsn = get_dsn(config)
    db = ReminderDB(dsn)
    await db.init()
    logger.info("Database connection established")

    # Build application
    application = Application.builder().token(bot_token).build()

    # Initialize scheduler
    scheduler = ReminderScheduler(application.bot, db)
    await scheduler.start()
    logger.info("Reminder scheduler started")

    # Add command handlers
    application.add_handler(CommandHandler("start", handle_start_command))
    application.add_handler(CommandHandler("help", handle_help_command))
    application.add_handler(CommandHandler("remind", handle_remind_command))
    application.add_handler(CommandHandler("list", handle_list_command))
    application.add_handler(CommandHandler("delete", handle_delete_command))

    # Add message handler for natural language reminders
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Run with graceful shutdown
    try:
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        if scheduler:
            await scheduler.stop()
        if db:
            await db.close()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RemindMe Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the specified command (no Telegram connection)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    if args.test:
        # Test mode - no Telegram connection needed
        run_test_mode(args.test)
    else:
        # Telegram mode
        asyncio.run(run_telegram_mode(config))


if __name__ == "__main__":
    main()
