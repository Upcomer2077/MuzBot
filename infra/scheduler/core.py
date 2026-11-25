import asyncio
import inspect

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from interfaces.ilogger import ILogger
from interfaces.ischeduler import IScheduler


class Scheduler(IScheduler):
    def __init__(self, logger: ILogger) -> None:
        super().__init__(logger)
        self._scheduler = AsyncIOScheduler()
        self._setup_task: asyncio.Task | None = None

    async def start(self):
        try:
            self._scheduler.start()
            self._setup_task = asyncio.create_task(self._setup_loop())
            self._logger.debug("Backup scheduler has been started.")
        except Exception as e:
            self._logger.error(f"Backup scheduler has NOT been started!!! {e}")

    async def stop(self):
        try:
            if self._setup_task:
                self._setup_task.cancel()
            self._scheduler.shutdown()
            self._logger.debug("Backup scheduler has been stopped")
        except Exception as e:
            self._logger.error(f"Error while stopping backup scheduler! {e}")

    async def _setup_loop(self):
        try:
            while True:
                j = await self._planned.get()

                func = j["func"]
                func_kwargs = j["func_kwargs"]
                id = j["id"]
                on_setup = j["on_setup"]
                clean_params = {
                    k: v
                    for k, v in j.items()
                    if k not in ("func", "on_setup", "id", "trigger", "func_kwargs")
                    and v is not None
                }

                self._scheduler.add_job(
                    func,
                    kwargs=func_kwargs,
                    trigger=j["trigger"].value,
                    id=id,
                    replace_existing=True,
                    **clean_params,  # pyright: ignore[reportArgumentType]
                )
                if on_setup:
                    if inspect.iscoroutinefunction(on_setup):
                        await on_setup(_logger=self._logger)
                    else:
                        on_setup(_logger=self._logger)
                await asyncio.sleep(0.1)
                self._planned.task_done()

        except Exception as e:
            self._logger.error(f"Error in scheduler loop (id:{j['id']}): {e}")
