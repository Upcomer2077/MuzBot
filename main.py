import asyncio

from aiogram.exceptions import TelegramNotFound
from aiogram.types import BotCommand, BotCommandScopeDefault

from _logger import LOGGER
from action_limiter import AL
from backup import B_SHED
from bot import bot, dp
from config import BACKUP_EVERY_N_DAYS, CPU_POOL, EXPERIMENTAL, SHOW_ON_STARTUP
from dungeon import DM
from GC import GC
from handlers import get_handlers_router
from worker import TRACK_PIPELINE

commands = [
    BotCommand(command="start", description="🚀 Запустить бота"),
    BotCommand(command="help", description="❓ Инструкция по использованию"),
    BotCommand(
        command="force",
        description="⚡ Скачать трек напрямую по ссылке из youtube.music.com",
    ),
    BotCommand(command="playlist", description="⚡ Скачать плейлист по ссылке"),
]


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


@dp.startup()
async def on_startup():

    B_SHED.start(BACKUP_EVERY_N_DAYS)
    AL.start_limiter()
    await GC.start_gc()
    await DM.open_dungeon()
    TRACK_PIPELINE.start()
    LOGGER.info("Bot has been started.")


@dp.shutdown()
async def on_shutdown():
    TRACK_PIPELINE.stop()
    await DM.close_dungeon()
    await GC.close_gc()
    CPU_POOL.shutdown(cancel_futures=True, wait=not EXPERIMENTAL)
    await B_SHED.stop()
    LOGGER.info("Graceful shutdown. Bye!")


if __name__ == "__main__":
    LOGGER.info("Attempting to start bot...")
    for k, v in SHOW_ON_STARTUP.items():
        LOGGER.info(f"{k}: {v}")
    LOGGER.info(f"EXPERIMENTAL: {EXPERIMENTAL}")

    try:
        asyncio.run(main())
    except TelegramNotFound:
        LOGGER.critical("Bot not found. Maybe token is invalid?")
