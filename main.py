import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from action_limiter import AL
from bot import bot, dp
from config import (
    CACHE_ROOT_DIR,
    CPU_COUNT,
    CPU_POOL,
    DATABASE_PATH,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from dungeon import DM
from handlers import get_handlers_router

commands = [
    BotCommand(command="start", description="🚀 Запустить бота"),
    BotCommand(command="help", description="❓ Инструкция по использованию"),
    BotCommand(
        command="force",
        description="⚡ Скачать трек напрямую по ссылке из youtube.music.com",
    ),
]


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


@dp.startup()
async def on_startup():
    await AL.start_gc()
    await DM.open_dungeon()
    print("Бот запущен...")


@dp.shutdown()
async def on_shutdown():
    await DM.close_dungeon()
    await AL.close()
    CPU_POOL.shutdown(cancel_futures=True)


if __name__ == "__main__":
    print("DATABASE_CONTAINER_PATH ", DATABASE_PATH)
    print("TRACKS_PER_LIMIT ", TRACKS_PER_LIMIT)
    print("QUERY_DOWNLOAD_LIMIT_SECS ", QUERY_DOWNLOAD_LIMIT_SECS)
    print("CACHE_ROOT_DIR ", CACHE_ROOT_DIR)
    print("CPU_COUNT ", CPU_COUNT)

    asyncio.run(main())
