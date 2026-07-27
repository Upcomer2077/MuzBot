import asyncio
import time

from _logger import LOGGER
from config import QUERY_DOWNLOAD_LIMIT_SECS, TRACKS_PER_LIMIT
from type import UserQueryLimit


class LightLimiter:
    """Rate limiter to manage chat action frequencies and track user music download limits."""

    def __init__(
        self,
    ):
        self._ACTIONS_BANK: dict[int, float] = {}
        self._ACTIONS_COOLDOWN = 10

        self._QUERIES_BANK: dict[int, UserQueryLimit] = {}
        self._QUERIES_COOLDOWN_SECS = QUERY_DOWNLOAD_LIMIT_SECS
        self._TRACKS_PER_LIMIT = TRACKS_PER_LIMIT

        self._GARBAGE_COLLECTOR_TASKS: list[asyncio.Task] = []

    def is_allowed_send_action(
        self,
        chat_id: int,
    ):
        """Determine if a Telegram chat status update action can be sent based on cooldown.

        Args:
            chat_id: Unique identifier for the Telegram chat.

        Returns:
            True if the required cooldown interval has passed, False otherwise.
        """
        now = time.time()
        last_sent = self._ACTIONS_BANK.get(chat_id, 0.0)

        if now - last_sent >= self._ACTIONS_COOLDOWN:
            self._ACTIONS_BANK[chat_id] = now
            return True
        return False

    def is_download_allowed(self, user_id: int):
        """Check if a user is within their track download limit for the current time window.

        Args:
            user_id: Unique identifier for the Telegram user.

        Returns:
            True if the download is permitted, False if the limit is exceeded.
        """
        NOW = time.time()
        user = self._QUERIES_BANK.get(user_id)
        if not user or ((NOW - user.get("ts")) > self._QUERIES_COOLDOWN_SECS):
            self._QUERIES_BANK[user_id] = {
                "ts": NOW,
                "semaphore": self._TRACKS_PER_LIMIT - 1,
            }
            return True

        new_semaphore = user.get("semaphore") - 1
        self._QUERIES_BANK[user_id].update(semaphore=new_semaphore)
        if new_semaphore < 0:
            return False
        return True

    # ---- GARBAGE CLEANER
    async def start_gc(self):
        """Start the background asynchronous garbage collector task for cleanups."""
        LOGGER.info("Starting Limiter garbage cleaner")
        self._GARBAGE_COLLECTOR_TASKS = [
            asyncio.create_task(self._garbage_collector()),
        ]

    async def close_gc(self):
        """Cancel and stop all active background garbage collector tasks safely."""
        LOGGER.info("Stopping Limiter garbage cleaner")
        for t in self._GARBAGE_COLLECTOR_TASKS:
            t.cancel()

    async def _garbage_collector(self):
        """Periodically remove expired records from memory banks to prevent memory leaks."""
        try:
            while True:
                await asyncio.sleep(10)
                now = time.time()

                if (len(self._ACTIONS_BANK) < 20) or (len(self._QUERIES_BANK) < 20):
                    continue

                expired_chats = [
                    chat_id
                    for chat_id, last_time in self._ACTIONS_BANK.items()
                    if now - last_time > self._ACTIONS_COOLDOWN
                ]
                expired_limits = [
                    user_id
                    for user_id, info in self._QUERIES_BANK.items()
                    if now - info["ts"] > self._QUERIES_COOLDOWN_SECS
                ]

                for chat_id in expired_chats:
                    self._ACTIONS_BANK.pop(chat_id)
                for chat_id in expired_limits:
                    self._QUERIES_BANK.pop(chat_id)

        except asyncio.CancelledError, KeyboardInterrupt:
            pass
