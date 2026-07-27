import asyncio
import time

from aiogram import Bot
from aiogram.enums import ChatAction

import bot
from _logger import LOGGER
from config import QUERY_DOWNLOAD_LIMIT_SECS, TRACKS_PER_LIMIT
from type import UserQueryLimit


class LightLimiter:
    def __init__(self, bot: Bot):
        self.bot = bot
        # Простой плоский словарь {chat_id: timestamp_последней_отправки}
        self._actions_bank: dict[int, float] = {}
        self._ACTIONS_COOLDOWN = 10

        self._queries_bank: dict[int, UserQueryLimit] = {}
        self._QUERIES_COOLDOWN_SECS = QUERY_DOWNLOAD_LIMIT_SECS
        self._TRACKS_PER_LIMIT = TRACKS_PER_LIMIT
        # Запускаем бесконечный фоновый сборщик мусора
        self._garbage_collector_tasks: list[asyncio.Task] = []

    async def start_gc(self):
        LOGGER.info("Starting Limiter garbage cleaner")
        self._garbage_collector_tasks = [
            asyncio.create_task(self._garbage_collector()),
        ]

    async def send_action(
        self, chat_id: int, action: ChatAction = ChatAction.UPLOAD_DOCUMENT
    ) -> None:
        """Отправляет статус в ТГ только если интервал в 10 сек истек."""
        now = time.time()
        last_sent = self._actions_bank.get(chat_id, 0.0)

        if now - last_sent >= self._ACTIONS_COOLDOWN:
            self._actions_bank[chat_id] = now
            try:
                await self.bot.send_chat_action(
                    chat_id=chat_id,
                    action=action,
                )
            except Exception:
                pass  # Глушим ошибки, если юзер заблокировал бота

    def is_download_allowed(self, user_id: int):
        now = time.time()
        user = self._queries_bank.get(user_id)
        if not user or ((now - user.get("ts")) > self._QUERIES_COOLDOWN_SECS):
            self._queries_bank[user_id] = {
                "ts": now,
                "semaphore": self._TRACKS_PER_LIMIT - 1,
            }
            return True

        new_semaphore = user.get("semaphore") - 1
        self._queries_bank[user_id].update(semaphore=new_semaphore)
        if new_semaphore < 0:
            return False
        return True

    async def close(self):
        for t in self._garbage_collector_tasks:
            t.cancel()

    async def _garbage_collector(self):
        try:
            while True:
                await asyncio.sleep(10)  # Спим 10 секунд
                now = time.time()

                if (len(self._actions_bank) < 20) or (len(self._queries_bank) < 20):
                    continue

                expired_chats = [
                    chat_id
                    for chat_id, last_time in self._actions_bank.items()
                    if now - last_time > self._ACTIONS_COOLDOWN
                ]
                expired_limits = [
                    user_id
                    for user_id, info in self._queries_bank.items()
                    if now - info["ts"] > self._QUERIES_COOLDOWN_SECS
                ]

                # Удаляем их из памяти
                for chat_id in expired_chats:
                    self._actions_bank.pop(chat_id)
                for chat_id in expired_limits:
                    self._queries_bank.pop(chat_id)
        except asyncio.CancelledError, KeyboardInterrupt:
            pass


AL = LightLimiter(bot.bot)
