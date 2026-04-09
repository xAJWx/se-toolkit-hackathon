"""Tests for the natural language reminder parser."""

from datetime import datetime, timedelta

from bot.services.parser import parse_reminder, format_reminder_list


class TestParseReminder:
    """Test cases for parse_reminder function."""

    def test_remind_me_at_time(self):
        """Test 'remind me to X at HH:MM' pattern."""
        result = parse_reminder("remind me to submit lab 9 at 5pm")
        assert result is not None
        assert "submit lab 9" in result["text"].lower()
        assert result["remind_at"] is not None

    def test_tomorrow_at_time(self):
        """Test 'X tomorrow at HH:MM' pattern."""
        result = parse_reminder("buy milk tomorrow at 10:00")
        assert result is not None
        assert "buy milk" in result["text"].lower()
        assert result["remind_at"] is not None

    def test_in_hours(self):
        """Test 'X in N hours' pattern."""
        result = parse_reminder("meeting in 2 hours")
        assert result is not None
        assert "meeting" in result["text"].lower()
        assert result["remind_at"] is not None

    def test_on_day_at_time(self):
        """Test 'X on DAY at HH:MM' pattern."""
        result = parse_reminder("call mom on monday at 3pm")
        assert result is not None
        assert "call mom" in result["text"].lower()
        assert result["remind_at"] is not None

    def test_no_datetime_returns_none(self):
        """Test that text without datetime returns None."""
        result = parse_reminder("hello world")
        assert result is None

    def test_just_time(self):
        """Test text with only time."""
        result = parse_reminder("reminder at 17:00")
        assert result is not None
        assert result["remind_at"] is not None


class TestFormatReminderList:
    """Test cases for format_reminder_list function."""

    def test_empty_list(self):
        """Test formatting an empty list."""
        result = format_reminder_list([])
        assert "no pending reminders" in result.lower()

    def test_single_reminder(self):
        """Test formatting a single reminder."""
        reminders = [
            {
                "id": 1,
                "text": "Submit lab 9",
                "remind_at": datetime(2026, 4, 15, 17, 0),
            }
        ]
        result = format_reminder_list(reminders)
        assert "#1" in result
        assert "Submit lab 9" in result

    def test_multiple_reminders(self):
        """Test formatting multiple reminders."""
        reminders = [
            {
                "id": 1,
                "text": "Submit lab 9",
                "remind_at": datetime(2026, 4, 15, 17, 0),
            },
            {
                "id": 2,
                "text": "Buy milk",
                "remind_at": datetime(2026, 4, 16, 10, 0),
            },
        ]
        result = format_reminder_list(reminders)
        assert "#1" in result
        assert "#2" in result
        assert "Submit lab 9" in result
        assert "Buy milk" in result
