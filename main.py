import asyncio
import tomllib  # Доступно в Python 3.11+. Для Python < 3.11 используйте: import tomli as tomllib
from pathlib import Path

from aiogram.exceptions import TelegramNotFound

from _logger import LOGGER
from bot import main
from config import EXPERIMENTAL, SHOW_ON_STARTUP


def get_project_info():
    pyproject_path = Path(__file__).resolve().parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    p_version: str = data.get("project", {}).get("version")
    p_name: str = data.get("project", {}).get("name")
    return (p_name, p_version) if p_name and p_version else None


if __name__ == "__main__":
    info = get_project_info()
    if info:
        LOGGER.info(f"Starting {info[0]} V{info[1]}")
    else:
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
