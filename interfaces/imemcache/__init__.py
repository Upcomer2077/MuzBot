from abc import ABC, abstractmethod


class IMemoryCache(ABC):
    @abstractmethod
    async def open(self, url: str): ...

    @abstractmethod
    async def close(self): ...

    @abstractmethod
    def get_storage(self, url: str): ...

    @abstractmethod
    async def healthcheck(self) -> bool: ...
