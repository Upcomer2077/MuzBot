import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from action_limiter import AL
from bot import bot, dp
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
    print("Бот запущен...")

    dp.include_router(get_handlers_router())
    await AL.start_gc()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)


@dp.startup()
async def on_startup():
    await DM.open_dungeon()


@dp.shutdown()
async def on_shutdown():
    await DM.close_dungeon()


if __name__ == "__main__":
    asyncio.run(main())
