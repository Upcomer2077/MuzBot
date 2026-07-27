from abc import ABC, abstractmethod


class ILogger(ABC):
    @abstractmethod
    def info(self, message: str) -> None: ...

    @abstractmethod
    def warn(self, message: str) -> None: ...

    @abstractmethod
    def error(self, message: str) -> None: ...
