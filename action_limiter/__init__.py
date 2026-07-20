import asyncio
import time

from aiogram import Bot
from aiogram.enums import ChatAction

import bot


class LightActionLimiter:
    def __init__(self, bot: Bot):
        self.bot = bot
        # Простой плоский словарь {chat_id: timestamp_последней_отправки}
        self._storage: dict[int, float] = {}
        # Запускаем бесконечный фоновый сборщик мусора
        self._task = None
        self._threshold = 10

    async def start_gc(self):
        self._task = asyncio.create_task(self._garbage_collector())

    async def send_action(
        self, chat_id: int, action: ChatAction = ChatAction.UPLOAD_DOCUMENT
    ) -> None:
        """Отправляет статус в ТГ только если интервал в 10 сек истек."""
        now = time.time()
        last_sent = self._storage.get(chat_id, 0.0)

        if now - last_sent >= self._threshold:
            self._storage[chat_id] = now
            try:
                await self.bot.send_chat_action(
                    chat_id=chat_id,
                    action=action,
                )
            except Exception:
                pass  # Глушим ошибки, если юзер заблокировал бота

    async def _garbage_collector(self) -> None:
        """
        Фоновый уборщик памяти.
        Раз в 10 секунд проверяет словарь и полностью удаляет пользователей,
        которые не скачивали ничего за последние 5 секунд.
        """
        try:
            while True:
                await asyncio.sleep(10)  # Спим 10 секунд
                now = time.time()
                expired_chats = [
                    chat_id
                    for chat_id, last_time in self._storage.items()
                    if now - last_time > self._threshold
                ]

                # Удаляем их из памяти
                for chat_id in expired_chats:
                    self._storage.pop(chat_id)
        except asyncio.CancelledError:
            pass

    async def close(self):
        if self._task:
            self._task.cancel()


AL = LightActionLimiter(bot.bot)
