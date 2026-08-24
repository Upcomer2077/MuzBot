from collections.abc import Callable
from datetime import datetime
from typing import Required, TypedDict

from schemas.enums.scheduler import JobTrigger


class BaseJob(TypedDict):
    trigger: JobTrigger
    func: Required[Callable]
    id: str
    on_setup: Callable | None


class IntervalConfig(TypedDict, total=False):
    days: int | None
    hours: int | None
    minutes: int


class CronConfig(TypedDict, total=False):
    day: str | int
    hour: str | int
    minute: str | int


class OneTimeConfig(TypedDict, total=False):
    run_date: datetime


class IntervalJob(BaseJob, IntervalConfig): ...


class CronJob(BaseJob, CronConfig): ...


class OneTimeJob(BaseJob, OneTimeConfig): ...
