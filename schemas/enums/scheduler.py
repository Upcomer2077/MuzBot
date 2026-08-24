from enum import Enum


class JobTrigger(Enum):
    INTERVAL = "interval"
    CRON = "cron"
    ONCE = "date"
