import asyncio
import time

from interfaces.ilimiter import IActionLimiter, _UserQueryLimitDict


class LightLimiter(IActionLimiter):
    def _is_allowed(
        self,
        user_id: int,
        *,
        bank: dict[int, _UserQueryLimitDict],
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
        return not new_semaphore < 0

    def garbage_collector(self, **_):
        """Remove expired records from memory banks to prevent memory leaks. Should be called periodically"""
        try:
            now = time.time()
            total_garbage_len = (
                len(self._ACTIONS_BANK)
                + len(self._QUERIES_BANK)
                + len(self._PLAYLIST_BANK)
                + len(self._SUBS_BANK)
                + len(self._SEARCH_BANK)
                + len(self._CATALOG_BANK)
            )
            if total_garbage_len < 50:
                return

            self.__logger.debug(f"Collecting garbage. Total bank: {total_garbage_len}")
            total_removed = 0
            for item in [
                (self._ACTIONS_COOLDOWN_SECS, self._ACTIONS_BANK),
                (self._QUERIES_COOLDOWN_SECS, self._QUERIES_BANK),
                (self._PLAYLIST_COOLDOWN_SECS, self._PLAYLIST_BANK),
                (self._SUBS_COOLDOWN_SECS, self._SUBS_BANK),
                (self._SEARCH_COOLDOWN_SECS, self._SEARCH_BANK),
                (self._CATALOG_COOLDOWN_SECS, self._CATALOG_BANK),
            ]:
                cooldown, bank = item
                for key, info in bank.copy().items():
                    if now - info["ts"] > cooldown:
                        bank.pop(key)
                        total_removed += 1

            self.__logger.debug(f"Collecting garbage done. Removed: {total_removed}")

        except asyncio.CancelledError, KeyboardInterrupt:
            pass
