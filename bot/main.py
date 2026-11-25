from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from bot.bot import bot
from bot.commands import COMMANDS
from bot.dispatcher import TGDispatcher
from bot.i18n import i18n
from handlers import get_handlers_router
from infra.dungeon.master import DungeonMaster
from infra.overlord import COLD
from infra.worker.new_worker import WorkerPipe
from interfaces.idatabase import IDataBase


async def main():
    DM: IDataBase = DungeonMaster(LOGGER)
    """DungeonMaster instance managing track db-persistence operations."""
    TRACK_PIPELINE = WorkerPipe(LOGGER, DM=DM, COLD=COLD)
    "Instance of worker loop"

    bot_dispatcher = TGDispatcher(
        logger=LOGGER, dungeon_master=DM, track_pipeline=TRACK_PIPELINE
    )
    dp = bot_dispatcher.get_dispatcher()
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        commands=[k["frontend"] for k in COMMANDS.values()],
        scope=BotCommandScopeDefault(),
    )
    i18n.setup(dispatcher=dp)

    await dp.start_polling(bot)
