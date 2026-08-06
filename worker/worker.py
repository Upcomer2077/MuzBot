import asyncio

from config import PLAYLISTS_LIMIT
from type import PlaylistTask


class PlaylistQueueManager:
    def __init__(self):
        self._queue: asyncio.Queue[PlaylistTask] = asyncio.Queue()
        self._registry: list[PlaylistTask] = []
        self._cooldowns: dict[int, float] = {}
        self._current_task_info: PlaylistTask | None
        self._LIMIT = PLAYLISTS_LIMIT

    async def __aenter__(self):
        self._current_task_info = await self._next_task()
        return self._current_task_info

    async def __aexit__(self, *_):
        if self._current_task_info:
            await self._task_done(self._current_task_info)
            self._current_task_info = None

    def _set_cooldown(self, user_id: int):
        if self._cooldowns.get(user_id, self._LIMIT) <= 0:
            return False
        self._cooldowns[user_id] = self._cooldowns.get(user_id, self._LIMIT) - 1
        return True

    def _unset_c_down(self, user_id: int):
        c_down = self._cooldowns.get(user_id)

        self._cooldowns[user_id] = c_down + 1 if c_down else self._LIMIT

        return self._cooldowns[user_id]

    async def enqueue(self, user_id: int, playlist_id: str) -> int:
        if self._set_cooldown(user_id):
            task = PlaylistTask(
                user_id=user_id,
                playlist_id=playlist_id,
            )
            self._registry.append(task)
            await self._queue.put(task)
            return len(self._registry)

        return 0

    async def _task_done(self, task: PlaylistTask):
        self._unset_c_down(task.user_id)
        if task in self._registry:
            self._registry.remove(task)

    async def _next_task(self) -> PlaylistTask:
        return await self._queue.get()
