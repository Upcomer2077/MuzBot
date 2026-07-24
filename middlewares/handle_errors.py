from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import ErrorEvent

from config import LOGGER


class BlockedLogMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: ErrorEvent, data):
        if isinstance(event.exception, TelegramForbiddenError):
            return LOGGER.info("Bot blocked by user. Error handled well")

        return await handler(event, data)
