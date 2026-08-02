import asyncio

from aiogram.exceptions import TelegramNotFound
from aiogram.types import BotCommand, BotCommandScopeDefault

from _logger import LOGGER
from action_limiter import AL
from bot import bot, dp
from config import (
    CACHE_ROOT_DIR,
    CPU_COUNT,
    CPU_POOL,
    DATABASE_PATH,
    EXPERIMENTAL,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from dungeon import DM
from GC import GC
from handlers import get_handlers_router

commands = [
    BotCommand(command="start", description="🚀 Запустить бота"),
    BotCommand(command="help", description="❓ Инструкция по использованию"),
    BotCommand(
        command="force",
        description="⚡ Скачать трек напрямую по ссылке из youtube.music.com",
    ),
    *(
        [BotCommand(command="playlist", description="Скачать плейлист")]
        if EXPERIMENTAL
        else []
    ),
]


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


@dp.startup()
async def on_startup():
    AL.start_limiter()
    await GC.start_gc()
    await DM.open_dungeon()
    LOGGER.info("Bot has been started.")


@dp.shutdown()
async def on_shutdown():
    await DM.close_dungeon()
    await GC.close_gc()
    CPU_POOL.shutdown(cancel_futures=True)
    LOGGER.info("Graceful shutdown. Bye!")


if __name__ == "__main__":
    LOGGER.info("Attempting to start bot...")
    LOGGER.info(f"DATABASE_CONTAINER_PATH: {DATABASE_PATH}")
    LOGGER.info(f"TRACKS_PER_LIMIT: {TRACKS_PER_LIMIT}")
    LOGGER.info(f"QUERY_DOWNLOAD_LIMIT_SECS: {QUERY_DOWNLOAD_LIMIT_SECS}")
    LOGGER.info(f"CACHE_ROOT_DIR: {CACHE_ROOT_DIR}")
    LOGGER.info(f"CPU_COUNT: {CPU_COUNT}")
    LOGGER.info(f"EXPERIMENTAL: {EXPERIMENTAL}")
    try:
        asyncio.run(main())
    except TelegramNotFound:
        LOGGER.critical("Bot not found. Maybe token is invalid?")
