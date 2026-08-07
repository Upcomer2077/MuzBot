import asyncio

from aiogram.exceptions import TelegramNotFound

from _logger import LOGGER
from bot import main
from config import EXPERIMENTAL, SHOW_ON_STARTUP

if __name__ == "__main__":
    LOGGER.info("Starting bot...")
    for k, v in SHOW_ON_STARTUP.items():
        LOGGER.debug(f"{k}: {v}")
    LOGGER.info(f"EXPERIMENTAL: {EXPERIMENTAL}")

    try:
        asyncio.run(main())
    except TelegramNotFound:
        LOGGER.critical("Bot not found. Maybe token is invalid?")
    except Exception as e:
        LOGGER.critical(f"Unknown error: {e}")
