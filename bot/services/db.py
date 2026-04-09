"""Database service for PostgreSQL operations."""

import asyncpg
from datetime import datetime
from typing import Optional

from bot.config import get_dsn


class ReminderDB:
    """Database operations for reminders."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self) -> None:
        """Initialize connection pool."""
        self._pool = await asyncpg.create_pool(dsn=self._dsn)

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()

    async def create_reminder(
        self, user_id: int, text: str, remind_at: datetime
    ) -> int:
        """Create a new reminder. Returns reminder ID."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO reminders (user_id, text, remind_at)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                user_id,
                text,
                remind_at,
            )
            return row["id"]

    async def list_reminders(self, user_id: int) -> list[dict]:
        """List all pending reminders for a user."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, text, remind_at, created_at
                FROM reminders
                WHERE user_id = $1 AND is_sent = FALSE
                ORDER BY remind_at ASC
                """,
                user_id,
            )
            return [dict(r) for r in rows]

    async def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Delete a reminder. Returns True if deleted."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM reminders
                WHERE id = $1 AND user_id = $2
                """,
                reminder_id,
                user_id,
            )
            return result == "DELETE 1"

    async def get_due_reminders(self) -> list[dict]:
        """Get all reminders that are due (remind_at <= now and not sent)."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, text, remind_at
                FROM reminders
                WHERE is_sent = FALSE AND remind_at <= (NOW() + INTERVAL '3 hours')
                ORDER BY remind_at ASC
                """
            )
            return [dict(r) for r in rows]

    async def mark_sent(self, reminder_id: int) -> None:
        """Mark a reminder as sent."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE reminders SET is_sent = TRUE WHERE id = $1
                """,
                reminder_id,
            )
