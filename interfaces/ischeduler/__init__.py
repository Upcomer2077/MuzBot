import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Literal, Unpack, cast, overload

from interfaces.ilogger import ILogger
from interfaces.ischeduler.types import (
    CronConfig,
    CronJob,
    IntervalConfig,
    IntervalJob,
    JobTrigger,
    OneTimeConfig,
    OneTimeJob,
)

Job = IntervalJob | CronJob | OneTimeJob


class IScheduler(ABC):
    def __init__(self, logger: ILogger) -> None:
        self._planned: asyncio.Queue[Job] = asyncio.Queue()
        self._logger = logger

    @abstractmethod
    async def start(self): ...
    @abstractmethod
    async def stop(self): ...

    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        func_kwargs: Any | None,
        trigger: Literal[JobTrigger.INTERVAL],
        on_setup: Callable | None = None,
        **kwargs: Unpack[IntervalConfig],
    ) -> None: ...

    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        func_kwargs: Any | None,
        trigger: Literal[JobTrigger.CRON],
        on_setup: Callable | None = None,
        **kwargs: Unpack[CronConfig],
    ) -> None: ...
    @overload
    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        func_kwargs: Any | None,
        trigger: Literal[JobTrigger.ONCE],
        on_setup: Callable | None = None,
        **kwargs: Unpack[OneTimeConfig],
    ) -> None: ...

    async def register_job(
        self,
        func: Callable,
        id: str,
        *,
        func_kwargs: Any | None,
        trigger: JobTrigger,
        on_setup: Callable | None = None,
        **kwargs,
    ) -> None:
        job_dict: Job = cast(
            Job,
            {
                "func": func,
                "func_kwargs": func_kwargs,
                "trigger": trigger,
                "id": id,
                "on_setup": on_setup,
                **kwargs,
            },
        )
        await self._planned.put(job_dict)
