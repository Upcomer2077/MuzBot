from aiogram import Dispatcher

from bot._setup_jobs import setup_jobs
from config import REDIS_CACHE_URL
from infra.red import RED
from infra.scheduler import SHED
from interfaces.idatabase import IDataBase
from interfaces.ilogger import ILogger
from interfaces.iworkerpipe import IWorkerPipeline
from middlewares.handle_errors import BlockedLogMiddleware


class TGDispatcher:
    def __init__(
        self,
        *,
        logger: ILogger,
        dungeon_master: IDataBase,
        track_pipeline: IWorkerPipeline,
    ):
        self._logger = logger
        self._dungeon_master = dungeon_master
        self._t_pipe = track_pipeline

    def get_dispatcher(self):
        dp = Dispatcher(storage=RED.get_storage(REDIS_CACHE_URL))
        dp["logger"] = self._logger
        dp["DM"] = self._dungeon_master
        dp["TRACK_PIPELINE"] = self._t_pipe

        @dp.startup()
        async def _on_startup():

            RED.open(REDIS_CACHE_URL)
            await RED.healthcheck()

            await setup_jobs(
                logger=self._logger,
                DM=self._dungeon_master,
                TRACK_PIPELINE=self._t_pipe,
            )
            await SHED.start()
            await self._dungeon_master.open_dungeon()
            self._t_pipe.start()
            self._logger.info("Bot has been started.")

        @dp.shutdown()
        async def _on_shutdown():
            await RED.close()
            self._t_pipe.stop()
            await self._dungeon_master.close_dungeon()
            await SHED.stop()
            self._logger.info("Graceful shutdown. Bye!")

        dp.errors.outer_middleware(BlockedLogMiddleware())

        return dp
