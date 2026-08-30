import asyncio

from _logger import LOGGER
from action_limiter import AL
from config import BACKUP_EVERY_N_DAYS
from scheduler import SHED
from scheduler.jobs.backup import job as backup_job
from scheduler.jobs.sub_notifications import job as sub_notification_job
from schemas.dicts.scheduler import JobTrigger


async def setup_jobs():
    j1 = SHED.register_job(
        backup_job,
        "backup_job",
        trigger=JobTrigger.INTERVAL,
        days=BACKUP_EVERY_N_DAYS,
        on_setup=lambda: LOGGER.info(
            f"Backups planned on every {BACKUP_EVERY_N_DAYS} day"
        ),
    )

    j2 = SHED.register_job(
        AL.garbage_collector,
        "AL_GC",
        trigger=JobTrigger.INTERVAL,
        minutes=1,
        on_setup=lambda: LOGGER.debug("Action limiter GC started"),
    )

    j3 = SHED.register_job(
        sub_notification_job,
        "Notifications",
        trigger=JobTrigger.CRON,
        day_of_week="tue,fri",
        hour=3,
        minute=0,
        on_setup=LOGGER.info("Notification job planned on TUE and FRI at 3am."),
    )

    return await asyncio.gather(j1, j2, j3)
