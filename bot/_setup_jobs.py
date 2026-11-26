import asyncio

from config import BACKUP_EVERY_N_DAYS
from infra.scheduler.jobs.backup import job as backup_job
from infra.scheduler.jobs.sub_notifications import job as sub_notification_job
from interfaces.idatabase import IDataBase
from interfaces.ilimiter import IActionLimiter
from interfaces.ilogger import ILogger
from interfaces.imusictools import IMusicTools
from interfaces.ischeduler import IScheduler
from interfaces.ischeduler.triggers import JobTrigger
from interfaces.iworkerpipe import IWorkerPipeline


async def setup_jobs(
    *,
    logger: ILogger,
    DM: IDataBase,
    TRACK_PIPELINE: IWorkerPipeline,
    AL: IActionLimiter,
    SHED: IScheduler,
    MT: IMusicTools,
) -> tuple[None, None, None]:
    j1 = SHED.register_job(
        backup_job,
        "backup_job",
        trigger=JobTrigger.INTERVAL,
        func_kwargs={"logger": logger},
        days=BACKUP_EVERY_N_DAYS,
        on_setup=lambda _logger: _logger.info(
            f"Backups planned on every {BACKUP_EVERY_N_DAYS} day"
        ),
    )

    j2 = SHED.register_job(
        AL.garbage_collector,
        "AL_GC",
        trigger=JobTrigger.INTERVAL,
        minutes=1,
        func_kwargs={"logger": logger},
        on_setup=lambda _logger: _logger.debug("Action limiter GC started"),
    )

    j3 = SHED.register_job(
        sub_notification_job,
        "Notifications",
        trigger=JobTrigger.CRON,
        day_of_week="tue,fri",
        hour="3,11,20",
        minute=0,
        func_kwargs={
            "logger": logger,
            "DM": DM,
            "TRACK_PIPELINE": TRACK_PIPELINE,
            "MT": MT,
        },
        on_setup=lambda _logger: _logger.info(
            "Notification job planned on TUE and FRI at 3am, 11am and 8pm."
        ),
    )

    return await asyncio.gather(j1, j2, j3)
