from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from bot.bot import bot
from bot.commands import COMMANDS
from bot.dispatcher import TGDispatcher
from bot.i18n import i18n
from config import CACHE_ROOT_DIR
from handlers import get_handlers_router
from infra.action_limiter.al import LightLimiter
from infra.dungeon.master import DungeonMaster
from infra.overlord.overlord import CacheOverlord
from infra.red.redis_cache import RedisCache
from infra.scheduler.core import Scheduler
from infra.tools.MusicTools.ytmusic_tools import YTMusicTools
from infra.worker.new_worker import WorkerPipe
from interfaces.icache import ICache
from interfaces.idatabase import IDataBase
from interfaces.ilimiter import IActionLimiter
from interfaces.imemcache import IMemoryCache
from interfaces.imusictools import IMusicTools
from interfaces.ischeduler import IScheduler


async def main():
    DM: IDataBase = DungeonMaster(LOGGER)
    """DungeonMaster instance managing track db-persistence operations."""
    COLD: ICache = CacheOverlord(CACHE_ROOT_DIR, LOGGER)
    """Global CacheOverlord instance handling local filesystem interactions for media storage files."""
    MT: IMusicTools = YTMusicTools(logger=LOGGER)
    TRACK_PIPELINE = WorkerPipe(LOGGER, DM=DM, COLD=COLD, MT=MT)
    "Instance of worker loop"
    RED: IMemoryCache = RedisCache(LOGGER)
    AL: IActionLimiter = LightLimiter(LOGGER)
    """Global LightLimiter instance used across handlers for rate limiting and download quotas."""
    SHED: IScheduler = Scheduler(logger=LOGGER)

    bot_dispatcher = TGDispatcher(
        logger=LOGGER,
        dungeon_master=DM,
        track_pipeline=TRACK_PIPELINE,
        memcache=RED,
        limiter=AL,
        scheduler=SHED,
        music_tools=MT,
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
