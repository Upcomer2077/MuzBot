from _logger.ILogger import ILogger
from _logger.lokilogger import LokiLogger
from _logger.stdlogger import StdLogger


class MultiLogger(ILogger):
    """Composite logger that duplicates logs to standard output and optionally to Grafana Loki."""

    def __init__(self, name: str, loki_url: str | None = None):
        """Initialize standard logger and conditionally set up Loki logging.

        Args:
            name: The name of the logger instance.
            loki_url: The URL endpoint for Grafana Loki api. Defaults to None.
        """
        self.name = name
        self._loki_url = loki_url
        self.std_logger = StdLogger(name)
        self.loki_logger = None

        if self._loki_url:
            self._activate_loki(self._loki_url)

    def _activate_loki(self, url: str):
        self.loki_logger = LokiLogger(self.name, url)

    def info(self, message: str):
        self.std_logger.info(message)
        if self.loki_logger:
            self.loki_logger.info(message)

    def error(self, message: str):
        self.std_logger.error(message)
        if self.loki_logger:
            self.loki_logger.error(message)

    def warn(self, message: str):
        self.std_logger.warn(message)
        if self.loki_logger:
            self.loki_logger.warn(message)

    def critical(self, message: str):
        self.std_logger.critical(message)
        if self.loki_logger:
            self.loki_logger.critical(message)
