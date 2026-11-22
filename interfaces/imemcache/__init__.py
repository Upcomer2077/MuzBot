from abc import ABC, abstractmethod

from aiogram.fsm.storage.base import BaseStorage


class IMemoryCache(ABC):
    @abstractmethod
    def open(self, url: str): ...

    @abstractmethod
    async def close(self): ...

    @abstractmethod
    def get_storage(self, url: str) -> BaseStorage: ...

    @abstractmethod
    async def healthcheck(self) -> bool: ...
