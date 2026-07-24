import logging
import sys

from _logger import BaseLogger, ColoredFormatter


class StdLogger(BaseLogger):
    """Реализация логирования в стандартный вывод (stdout)."""

    def _configure_logger(self) -> None:
        stdout_handler = logging.StreamHandler(sys.stdout)

        # Задаем читаемый формат для консоли
        formatter = ColoredFormatter(
            "[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stdout_handler.setFormatter(formatter)
        self._logger.addHandler(stdout_handler)
