import asyncio
import time

from _logger import LOGGER
from config import QUERY_DOWNLOAD_LIMIT_SECS, TRACKS_PER_LIMIT
from type import UserQueryLimit


class LightLimiter:
    def __init__(
        self,
    ):
        # Простой плоский словарь {chat_id: timestamp_последней_отправки}
        self._ACTIONS_BANK: dict[int, float] = {}
        self._ACTIONS_COOLDOWN = 10

        self._QUERIES_BANK: dict[int, UserQueryLimit] = {}
        self._QUERIES_COOLDOWN_SECS = QUERY_DOWNLOAD_LIMIT_SECS
        self._TRACKS_PER_LIMIT = TRACKS_PER_LIMIT
        # Запускаем бесконечный фоновый сборщик мусора
        self._GARBAGE_COLLECTOR_TASKS: list[asyncio.Task] = []

    def is_allowed_send_action(
        self,
        chat_id: int,
    ):
        """Отправляет статус в ТГ только если интервал в 10 сек истек."""
        now = time.time()
        last_sent = self._ACTIONS_BANK.get(chat_id, 0.0)

        if now - last_sent >= self._ACTIONS_COOLDOWN:
            self._ACTIONS_BANK[chat_id] = now
            return True
        return False

    def is_download_allowed(self, user_id: int):
        now = time.time()
        user = self._QUERIES_BANK.get(user_id)
        if not user or ((now - user.get("ts")) > self._QUERIES_COOLDOWN_SECS):
            self._QUERIES_BANK[user_id] = {
                "ts": now,
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
        LOGGER.info("Starting Limiter garbage cleaner")
        self._GARBAGE_COLLECTOR_TASKS = [
            asyncio.create_task(self._garbage_collector()),
        ]

    async def close_gc(self):
        LOGGER.info("Stopping Limiter garbage cleaner")
        for t in self._GARBAGE_COLLECTOR_TASKS:
            t.cancel()

    async def _garbage_collector(self):
        try:
            while True:
                await asyncio.sleep(10)  # Спим 10 секунд
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

                # Удаляем их из памяти
                for chat_id in expired_chats:
                    self._ACTIONS_BANK.pop(chat_id)
                for chat_id in expired_limits:
                    self._QUERIES_BANK.pop(chat_id)

        except asyncio.CancelledError, KeyboardInterrupt:
            pass
