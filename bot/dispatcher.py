from aiogram import Dispatcher

from bot._setup_jobs import setup_jobs
from config import REDIS_CACHE_URL
from infra.dungeon import DM
from infra.red import RED
from infra.scheduler import SHED
from infra.worker import TRACK_PIPELINE
from interfaces.ilogger import ILogger
from middlewares.handle_errors import BlockedLogMiddleware


class TGDispatcher:
    def __init__(self, *, logger: ILogger):
        self._logger = logger

    def get_dispatcher(self):
        dp = Dispatcher(storage=RED.get_storage(REDIS_CACHE_URL))
        dp["logger"] = self._logger

        @dp.startup()
        async def _on_startup():

            RED.open(REDIS_CACHE_URL)
            await RED.healthcheck()

            await setup_jobs(logger=self._logger)
            await SHED.start()
            await DM.open_dungeon()
            TRACK_PIPELINE.start()
            self._logger.info("Bot has been started.")

        @dp.shutdown()
        async def _on_shutdown():
            await RED.close()
            TRACK_PIPELINE.stop()
            await DM.close_dungeon()
            await SHED.stop()
            self._logger.info("Graceful shutdown. Bye!")

        dp.errors.outer_middleware(BlockedLogMiddleware())

        return dp
