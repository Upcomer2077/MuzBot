from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from action_limiter import AL
from bot.commands import COMMANDS
from config import BACKUP_EVERY_N_DAYS, BOT_TOKEN
from dungeon import DM
from handlers import get_handlers_router
from middlewares.handle_errors import BlockedLogMiddleware
from scheduler import SHED
from scheduler.jobs.backup import job as backup_job
from schemas.dicts.scheduler import JobTrigger
from worker import TRACK_PIPELINE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.startup()
async def on_startup():
    await setup_jobs()
    await SHED.start()
    await DM.open_dungeon()
    TRACK_PIPELINE.start()
    LOGGER.info("Bot has been started.")


@dp.shutdown()
async def on_shutdown():
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


async def setup_jobs():
    await SHED.register_job(
        backup_job,
        "backup_job",
        trigger=JobTrigger.INTERVAL,
        days=BACKUP_EVERY_N_DAYS,
        on_setup=lambda: LOGGER.info(
            f"Backups planned on every {BACKUP_EVERY_N_DAYS} day"
        ),
    )

    await SHED.register_job(
        AL.garbage_collector,
        "AL_GC",
        trigger=JobTrigger.INTERVAL,
        minutes=1,
        on_setup=lambda: LOGGER.debug("Action limiter GC started"),
    )
