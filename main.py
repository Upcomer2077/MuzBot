import asyncio

from aiogram.exceptions import TelegramNotFound

from _logger import LOGGER
from bot import main
from config import DEBUG, EXPERIMENTAL, SHOW_ON_STARTUP

if __name__ == "__main__":
    LOGGER.info("Attempting to start bot...")
    if DEBUG:
        for k, v in SHOW_ON_STARTUP.items():
            LOGGER.info(f"{k}: {v}")
    LOGGER.info(f"EXPERIMENTAL: {EXPERIMENTAL}")

    try:
        asyncio.run(main())
    except TelegramNotFound:
        LOGGER.critical("Bot not found. Maybe token is invalid?")
    except Exception as e:
        LOGGER.critical(f"Unknown error: {e}")
