import os

from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

from _logger.baselogger import BaseLogger


class LokiLogger(BaseLogger):
    def __init__(self, name: str, url: str, level: str = "INFO"):
        self.url: str = url
        super().__init__(name, level)

    def _configure_logger(self) -> None:
        loki_url = self.url

        loki_handler = LokiLoggerHandler(
            url=loki_url,
            labels={
                "application": self.name,
                "environment": os.getenv("ENV_TYPE", "production"),
            },
            timeout=10,
        )
        self._logger.addHandler(loki_handler)
