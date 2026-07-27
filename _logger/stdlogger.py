import logging
import sys

from _logger.baselogger import BaseLogger
from _logger.formatters.colored_formatter import ColoredFormatter


class StdLogger(BaseLogger):
    def _configure_logger(self) -> None:
        stdout_handler = logging.StreamHandler(sys.stdout)

        formatter = ColoredFormatter(
            "[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stdout_handler.setFormatter(formatter)
        self._logger.addHandler(stdout_handler)
