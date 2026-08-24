import asyncio
import inspect
from collections.abc import Callable
from typing import Literal, Unpack, cast, overload

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from _logger import LOGGER
from schemas.dicts.scheduler import (
    CronConfig,
    CronJob,
    IntervalConfig,
    IntervalJob,
    OneTimeConfig,
    OneTimeJob,
)
from schemas.enums.scheduler import JobTrigger

Job = IntervalJob | CronJob | OneTimeJob


class Scheduler:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()
        self._planned: asyncio.Queue[Job] = asyncio.Queue()
        self._setup_task: asyncio.Task | None = None

    async def start(self):
        try:
            self._scheduler.start()
            self._setup_task = asyncio.create_task(self._setup_loop())
            LOGGER.debug("Backup scheduler has been started.")
        except Exception as e:
            LOGGER.error(f"Backup scheduler has NOT been started!!! {e}")

    async def stop(self):
        try:
            if self._setup_task:
                self._setup_task.cancel()
            self._scheduler.shutdown()
            LOGGER.debug("Backup scheduler has been stopped")
        except Exception as e:
            LOGGER.error(f"Error while stopping backup scheduler! {e}")

    async def _setup_loop(self):
        try:
            while True:
                j = await self._planned.get()

                func = j["func"]
                id = j["id"]
                on_setup = j["on_setup"]
                clean_params = {
                    k: v
                    for k, v in j.items()
                    if k not in ("func", "on_setup", "id", "trigger") and v is not None
                }

                self._scheduler.add_job(
                    func,
                    trigger=j["trigger"].value,
                    id=id,
                    replace_existing=True,
                    **clean_params,  # pyright: ignore[reportArgumentType]
                )
                if on_setup:
                    if inspect.iscoroutinefunction(on_setup):
                        await on_setup()
                    else:
                        on_setup()
                await asyncio.sleep(0.1)
                self._planned.task_done()

        except Exception as e:
            LOGGER.error(f"Error in scheduler loop (id:{j['id']}): {e}")

    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        trigger: Literal[JobTrigger.INTERVAL],
        on_setup: Callable | None,
        **kwargs: Unpack[IntervalConfig],
    ) -> None: ...

    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        trigger: Literal[JobTrigger.CRON],
        on_setup: Callable | None,
        **kwargs: Unpack[CronConfig],
    ) -> None: ...
    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        trigger: Literal[JobTrigger.ONCE],
        on_setup: Callable | None,
        **kwargs: Unpack[OneTimeConfig],
    ) -> None: ...

    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        trigger: JobTrigger,
        on_setup: Callable | None,
        **kwargs,
    ) -> None:
        job_dict: Job = cast(
            Job,
            {
                "func": func,
                "trigger": trigger,
                "id": id,
                "on_setup": on_setup,
                **kwargs,
            },
        )
        await self._planned.put(job_dict)
