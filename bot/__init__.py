from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault
from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers import FSMManager
from aiogram_i18n.middleware import I18nMiddleware

from _logger import LOGGER
from bot._setup_jobs import setup_jobs
from bot.bot import bot
from bot.commands import COMMANDS
from config import REDIS_CACHE_URL
from handlers import get_handlers_router
from infra.dungeon import DM
from infra.red import RED
from infra.scheduler import SHED
from infra.worker import TRACK_PIPELINE
from middlewares.handle_errors import BlockedLogMiddleware

dp = Dispatcher(storage=RED.get_storage(REDIS_CACHE_URL))
dp["logger"] = LOGGER


@dp.startup()
async def _on_startup():

    RED.open(REDIS_CACHE_URL)
    await RED.healthcheck()

    await setup_jobs(logger=LOGGER)
    await SHED.start()
    await DM.open_dungeon()
    TRACK_PIPELINE.start()
    LOGGER.info("Bot has been started.")


@dp.shutdown()
async def _on_shutdown():
    await RED.close()
    TRACK_PIPELINE.stop()
    await DM.close_dungeon()
    await SHED.stop()
    LOGGER.info("Graceful shutdown. Bye!")


dp.errors.outer_middleware(BlockedLogMiddleware())

i18n = I18nMiddleware(
    core=FluentCompileCore(path="localization/locales/{locale}/"),
    default_locale="en",
    manager=FSMManager(),
)
i18n.setup(dispatcher=dp)


async def main():
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        commands=[k["frontend"] for k in COMMANDS.values()],
        scope=BotCommandScopeDefault(),
    )

    await dp.start_polling(bot)
