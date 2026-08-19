from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramForbiddenError, TelegramNetworkError
from aiogram.types import ErrorEvent

from _logger import LOGGER


class BlockedLogMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: ErrorEvent, data):
        if isinstance(event.exception, TelegramForbiddenError):
            return LOGGER.info("Bot blocked by user. Error handled well")
        if isinstance(event.exception, TelegramNetworkError):
            return LOGGER.warning("Request timeout.")
        return await handler(event, data)
