from _logger.multilogger import MultiLogger
from config import DEBUG, LOKI_URL

LOGGER = MultiLogger("LG1", LOKI_URL, level="DEBUG" if DEBUG else "INFO")
"""Global MultiLogger instance configured with standard output and Loki integration."""
