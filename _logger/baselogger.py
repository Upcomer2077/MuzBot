import logging
from abc import ABC, abstractmethod

from _logger.ILogger import ILogger


class BaseLogger(ILogger, ABC):
    """Базовый абстрактный класс для логирования."""

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self._logger = logging.getLogger(f"{name}_{self.__class__.__name__}")
        self._logger.setLevel(level.upper())
        # Инициализируем стандартный логгер Python
        if self._logger.hasHandlers():
            self._logger.handlers.clear()

        # Вызываем абстрактный метод конфигурации
        self._configure_logger()

    @abstractmethod
    def _configure_logger(self) -> None:
        """Метод для специфичной настройки хендлеров в дочерних классах."""
        pass

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warn(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def critical(self, message: str) -> None:
        self._logger.critical(message)
