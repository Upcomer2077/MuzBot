import asyncio
import time

from _logger import LOGGER
from config import (
    PLAYLIST_DOWNLOAD_COOLDOWN_SECS,
    PLAYLISTS_LIMIT,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from GC import GC
from type import UserQueryLimit


class LightLimiter:
    """Rate limiter to manage chat action frequencies and track user music download limits."""

    def __init__(
        self,
    ):
        self._ACTIONS_BANK: dict[int, UserQueryLimit] = {}
        self._ACTIONS_COOLDOWN_SECS = 10
        self._ACTION_PER_LIMIT = 1

        self._QUERIES_BANK: dict[int, UserQueryLimit] = {}
        self._QUERIES_COOLDOWN_SECS = QUERY_DOWNLOAD_LIMIT_SECS
        self._TRACKS_PER_LIMIT = TRACKS_PER_LIMIT

        self._PLAYLIST_BANK: dict[int, UserQueryLimit] = {}
        self._PLAYLIST_COOLDOWN_SECS = PLAYLIST_DOWNLOAD_COOLDOWN_SECS
        self._PLAYLIST_PER_LIMIT = PLAYLISTS_LIMIT

    def start_limiter(self):
        GC.register_task(asyncio.create_task(self._garbage_collector()))
        LOGGER.debug("Action limiter started")

    def is_send_action_allowed(
        self,
        chat_id: int,
    ):
        return self._is_allowed(
            chat_id,
            bank=self._ACTIONS_BANK,
            cooldown=self._ACTIONS_COOLDOWN_SECS,
            per_limit=self._ACTION_PER_LIMIT,
        )

    def is_playlist_download_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._PLAYLIST_BANK,
            cooldown=self._PLAYLIST_COOLDOWN_SECS,
            per_limit=self._PLAYLIST_PER_LIMIT,
        )

    def is_track_download_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._QUERIES_BANK,
            cooldown=self._QUERIES_COOLDOWN_SECS,
            per_limit=self._TRACKS_PER_LIMIT,
        )

    def _is_allowed(
        self,
        user_id: int,
        *,
        bank: dict[int, UserQueryLimit],
        cooldown: int,
        per_limit: int,
    ):
        """Check if a user is within their download limit for the current time window.

        Args:
            user_id: Unique identifier for the Telegram user.

        Returns:
            True if the download is permitted, False if the limit is exceeded.
        """
        NOW = time.time()

        user = bank.get(user_id)
        if not user or ((NOW - user.get("ts")) > cooldown):
            bank[user_id] = {
                "ts": NOW,
                "semaphore": per_limit - 1,
            }
            return True

        new_semaphore = user.get("semaphore") - 1
        bank[user_id].update(semaphore=new_semaphore)
        if new_semaphore < 0:
            return False
        return True

    async def _garbage_collector(self):
        """Periodically remove expired records from memory banks to prevent memory leaks."""
        try:
            while True:
                await asyncio.sleep(10)
                now = time.time()
                total_garbage_len = (
                    len(self._ACTIONS_BANK)
                    + len(self._QUERIES_BANK)
                    + len(self._PLAYLIST_BANK)
                )
                if (total_garbage_len) < 30:
                    continue

                LOGGER.debug(f"Collecting garbage. Total bank: {total_garbage_len}")
                total_removed = 0
                for item in [
                    (self._ACTIONS_COOLDOWN_SECS, self._ACTIONS_BANK),
                    (self._QUERIES_COOLDOWN_SECS, self._QUERIES_BANK),
                    (self._PLAYLIST_COOLDOWN_SECS, self._PLAYLIST_BANK),
                ]:
                    cooldown, bank = item
                    for key, info in bank.copy().items():
                        if now - info["ts"] > cooldown:
                            bank.pop(key)
                            total_removed += 1

                LOGGER.debug(f"Collecting garbage done. Removed: {total_removed}")

        except asyncio.CancelledError, KeyboardInterrupt:
            pass
