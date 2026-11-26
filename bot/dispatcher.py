from aiogram import Dispatcher

from bot._setup_jobs import setup_jobs
from config import REDIS_CACHE_URL
from interfaces.idatabase import IDataBase
from interfaces.ilimiter import IActionLimiter
from interfaces.ilogger import ILogger
from interfaces.imemcache import IMemoryCache
from interfaces.ischeduler import IScheduler
from interfaces.iworkerpipe import IWorkerPipeline
from middlewares.handle_errors import BlockedLogMiddleware


class TGDispatcher:
    def __init__(
        self,
        *,
        logger: ILogger,
        dungeon_master: IDataBase,
        track_pipeline: IWorkerPipeline,
        memcache: IMemoryCache,
        limiter: IActionLimiter,
        scheduler: IScheduler,
    ):
        self._logger = logger
        self._dungeon_master = dungeon_master
        self._t_pipe = track_pipeline
        self._red = memcache
        self._action_limiter = limiter
        self._scheduler = scheduler

    def get_dispatcher(self):
        dp = Dispatcher(storage=self._red.get_storage(REDIS_CACHE_URL))
        dp["logger"] = self._logger
        dp["DM"] = self._dungeon_master
        dp["TRACK_PIPELINE"] = self._t_pipe
        dp["AL"] = self._action_limiter

        @dp.startup()
        async def _on_startup():

            self._red.open(REDIS_CACHE_URL)
            await self._red.healthcheck()

            await setup_jobs(
                logger=self._logger,
                DM=self._dungeon_master,
                TRACK_PIPELINE=self._t_pipe,
                AL=self._action_limiter,
                SHED=self._scheduler,
            )
            await self._scheduler.start()
            await self._dungeon_master.open_dungeon()
            self._t_pipe.start()
            self._logger.info("Bot has been started.")

        @dp.shutdown()
        async def _on_shutdown():
            await self._red.close()
            self._t_pipe.stop()
            await self._dungeon_master.close_dungeon()
            await self._scheduler.stop()
            self._logger.info("Graceful shutdown. Bye!")

        dp.errors.outer_middleware(BlockedLogMiddleware())

        return dp
