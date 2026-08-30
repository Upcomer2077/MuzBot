from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from action_limiter import AL
from backup import B_SHED
from bot.commands import COMMANDS
from config import BACKUP_EVERY_N_DAYS, BOT_TOKEN
from dungeon import DM
from GC import GC
from handlers import get_handlers_router
from middlewares.handle_errors import BlockedLogMiddleware
from worker import TRACK_PIPELINE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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
    await B_SHED.stop()
    LOGGER.info("Graceful shutdown. Bye!")


dp.errors.outer_middleware(BlockedLogMiddleware())


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=COMMANDS, scope=BotCommandScopeDefault())

    await dp.start_polling(bot)
