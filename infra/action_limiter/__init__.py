from _logger import LOGGER
from infra.action_limiter.al import LightLimiter

AL = LightLimiter(LOGGER)
"""Global LightLimiter instance used across handlers for rate limiting and download quotas."""
