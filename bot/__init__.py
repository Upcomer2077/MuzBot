from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from bot._setup_jobs import setup_jobs
from bot.commands import COMMANDS
from config import BOT_TOKEN
from dungeon import DM
from handlers import get_handlers_router
from middlewares.handle_errors import BlockedLogMiddleware
from scheduler import SHED
from worker import TRACK_PIPELINE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.startup()
async def _on_startup():
    await setup_jobs()
    await SHED.start()
    await DM.open_dungeon()
    TRACK_PIPELINE.start()
    LOGGER.info("Bot has been started.")


@dp.shutdown()
async def _on_shutdown():
    TRACK_PIPELINE.stop()
    await DM.close_dungeon()
    await SHED.stop()
    LOGGER.info("Graceful shutdown. Bye!")


dp.errors.outer_middleware(BlockedLogMiddleware())


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=COMMANDS, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)
