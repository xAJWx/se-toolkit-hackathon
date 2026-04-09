"""Natural language reminder parser.

Parses human-readable text like:
  "remind me to submit lab 9 at 5pm"
  "buy milk tomorrow at 10:00"
  "meeting in 2 hours"
  "call mom on monday at 3pm"
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import dateparser

# User's timezone (Europe/Moscow = UTC+3)
USER_TZ = timezone(timedelta(hours=3))


def parse_reminder(text: str) -> Optional[dict[str, str | datetime]]:
    """Parse reminder text into (task_text, remind_at).

    Returns dict with 'text' and 'remind_at' keys, or None if parsing fails.
    The returned remind_at is in UTC.
    """
    text = text.strip()

    # Try dateparser on the full text first
    parsed = dateparser.parse(
        text,
        settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
    )

    if parsed is None:
        # Try to extract time and date separately
        # Common patterns
        patterns_to_try = [
            # "tomorrow at 5pm", "today at 10:00"
            r"\b(?:today|tomorrow|on\s+\w+)",
            # "in 2 hours", "in 3 days"
            r"\bin\s+\d+\s+(?:hour|minute|day|week)s?\b",
            # "at 5pm", "at 17:00"
            r"\bat\s+\d{1,2}(:\d{2})?\s*(am|pm)?\b",
        ]

        for pattern in patterns_to_try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                datetime_str = match.group(0)
                parsed = dateparser.parse(
                    datetime_str,
                    settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
                )
                if parsed:
                    break

    if parsed is None:
        return None

    # dateparser returns naive datetime. Store as-is, display as-is.
    # Scheduler compares against NOW() — both in the same timezone.

    # Now extract the task text (everything that's not the datetime part)
    task_text = _extract_task_text(text, parsed)

    if not task_text.strip():
        return None

    return {
        "text": task_text.strip(),
        "remind_at": parsed,
    }


def _extract_task_text(text: str, parsed_dt: datetime) -> str:
    """Extract task description by removing datetime parts from text."""
    result = text

    # Remove common prefix patterns
    prefixes = [
        r"remind\s+me\s+to\s+",
        r"remind\s+me\s+",
        r"set\s+a\s+reminder\s+to\s+",
        r"set\s+a\s+reminder\s+",
        r"don't\s+forget\s+to\s+",
        r"don't\s+forget\s+",
    ]

    for prefix in prefixes:
        result = re.sub(prefix, "", result, count=1, flags=re.IGNORECASE)

    # Remove "at TIME" patterns
    result = re.sub(
        r"\bat\s+\d{1,2}(:\d{2})?\s*(am|pm)?\b",
        "",
        result,
        flags=re.IGNORECASE,
    )

    # Remove date words (today, tomorrow, day names, etc.)
    date_words = [
        r"\btoday\b",
        r"\btomorrow\b",
        r"\byesterday\b",
        r"\b(?:mon|tues|wednes|thurs|fri|satur|sun)day\b",
        r"\bin\s+\d+\s+(?:hour|minute|day|week)s?\b",
    ]

    for word_pattern in date_words:
        result = re.sub(word_pattern, "", result, flags=re.IGNORECASE)

    # Clean up extra spaces
    result = re.sub(r"\s{2,}", " ", result).strip()

    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]

    return result


def _format_time_local(dt: datetime) -> str:
    """Format datetime for display — no conversion, store & show as-is."""
    return dt.strftime("%d %b %Y, %H:%M")


def format_reminder_list(reminders: list[dict]) -> str:
    """Format a list of reminders for display."""
    if not reminders:
        return "📭 You have no pending reminders."

    lines = ["📋 *Your reminders:*\n"]
    for r in reminders:
        remind_at = r["remind_at"]
        if isinstance(remind_at, datetime):
            time_str = _format_time_local(remind_at)
        else:
            time_str = str(remind_at)
        lines.append(f"• #{r['id']} — {r['text']} (_{time_str}_)")

    lines.append("\nUse /delete <id> to remove a reminder.")
    return "\n".join(lines)


def format_reminder_created(reminder_id: int, text: str, remind_at: datetime) -> str:
    """Format confirmation for a newly created reminder."""
    time_str = _format_time_local(remind_at)
    return (
        f"✅ Reminder #{reminder_id} set!\n\n"
        f"📝 {text}\n"
        f"⏰ {time_str}"
    )
