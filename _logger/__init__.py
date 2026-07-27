from _logger.multilogger import MultiLogger
from config import LOKI_URL

LOGGER = MultiLogger("LG1", LOKI_URL)
"""Global MultiLogger instance configured with standard output and Loki integration."""
