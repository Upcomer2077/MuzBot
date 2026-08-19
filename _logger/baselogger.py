import logging
from abc import ABC, abstractmethod

from _logger.ILogger import ILogger


class BaseLogger(ILogger, ABC):
    """Abstract base class for custom loggers with predefined logging levels and handlers management."""

    def __init__(self, name: str, level: str = "DEBUG"):
        """Initialize the logger instance, set the log level, and clear existing handlers.

        Args:
            name: The base name for the logger instance.
            level: The logging level string (e.g., 'INFO', 'DEBUG'). Defaults to 'INFO'.
        """
        self.name = name
        self._logger = logging.getLogger(f"{name}_{self.__class__.__name__}")
        self._logger.setLevel(level.upper())

        if self._logger.hasHandlers():
            self._logger.handlers.clear()

        self._configure_logger()

    @abstractmethod
    def _configure_logger(self) -> None:
        """Abstract method to implement specific logger configuration and handlers.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def critical(self, message: str) -> None:
        self._logger.critical(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)
