import logging
from abc import ABC, abstractmethod


class ColoredFormatter(logging.Formatter):
    """Форматтер, который добавляет ANSI-цвета для уровней логирования."""

    # ANSI escape-коды для цветов
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    CRITICAL_EFFECT = "\033[1;30;5;41m"

    def __init__(
        self,
        fmt="[%(asctime)s] %(levelname)-8s [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ):
        super().__init__(fmt, datefmt)

        # Настраиваем цвета для каждого уровня
        self.LEVEL_COLORS = {
            logging.INFO: self.GREEN,
            logging.WARNING: self.YELLOW,
            logging.ERROR: self.RED,
            logging.CRITICAL: self.CRITICAL_EFFECT,
        }

    def format(self, record):
        # Сохраняем оригинальные значения, чтобы не испортить их для других хендлеров (например, Loki)
        orig_levelname = record.levelname
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        orig_name = record.name
        # Красим имя уровня (например, INFO становится зеленым)
        record.levelname = f"{color}{orig_levelname}{self.RESET}"

        # Дополнительно подсвечиваем время серым цветом для эстетики
        # (Опционально, можно убрать, если любите стандартный белый)
        record.asctime = (
            f"{self.GRAY}{self.formatTime(record, self.datefmt)}{self.RESET}"
        )
        record.name = f"{self.CYAN}{orig_name}{self.RESET}"
        # Вызываем базовый форматтер
        if record.levelno == logging.CRITICAL:
            record.msg = f"\033[1;31m{record.msg}{self.RESET}"
        result = super().format(record)

        # Возвращаем всё назад, чтобы не сломать сериализацию
        record.levelname = orig_levelname
        record.name = orig_name
        return result


class ILogger(ABC):
    @abstractmethod
    def info(self, message: str) -> None: ...

    @abstractmethod
    def warn(self, message: str) -> None: ...

    @abstractmethod
    def error(self, message: str) -> None: ...


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
