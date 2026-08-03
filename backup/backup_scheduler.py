import os
import tarfile
from datetime import datetime

from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import bot
from _logger import LOGGER
from config import CACHE_ROOT_DIR, CHANNEL_STORAGE_ID, DATABASE_PATH


class BackupScheduler:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()

    def start(self, every_n_days: int):
        """Configure the backup job interval and start the scheduler.

        Args:
            every_n_days (int): Interval in days between consecutive backups.
        """
        self._setup_job(every_n_days)
        self._scheduler.start()
        LOGGER.info("Scheduler has been started")

    def stop(self):
        self._scheduler.shutdown()
        LOGGER.info("Scheduler has been stopped")

    def _make_backup(self):
        """Create a compressed tar.xz archive of the database file.

        Returns:
            tuple[bool, str | None]: Status of the backup and path to the archive file.
        """
        backup_dir = f"{CACHE_ROOT_DIR}/backups"
        if not os.path.exists(DATABASE_PATH):
            LOGGER.error(f"BACKUP: file {DATABASE_PATH} not found.")
            return (False, None)

        os.makedirs(backup_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_name = f"{date_str}_backup.tar.xz"
        archive_path = os.path.join(backup_dir, archive_name)

        try:
            with tarfile.open(archive_path, "w:xz") as tar:
                tar.add(DATABASE_PATH, arcname=os.path.basename(DATABASE_PATH))
            return (True, archive_path)
        except Exception as e:
            LOGGER.error(f"Error while making backup tar: {e}")
            return (False, None)

    async def _send_to_channel(self, archive_path):
        """Upload the generated backup archive to the configured Telegram channel.

        Args:
            archive_path (str): File path of the backup archive to be sent.
        """
        caption = f"📦 **Backup**\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        document = FSInputFile(archive_path)
        try:
            await bot.bot.send_document(
                chat_id=CHANNEL_STORAGE_ID,
                document=document,
                caption=caption,
                parse_mode="Markdown",
                disable_notification=True,
            )
        except Exception as e:
            LOGGER.error(f"Backup send failed: {e}")

    async def _job(self):
        """Execute the full workflow: create backup, send to channel, and remove local archive."""
        (success, archive_path) = self._make_backup()
        if success and archive_path:
            await self._send_to_channel(archive_path)
            if os.path.exists(archive_path):
                os.remove(archive_path)

    def _setup_job(self, every_n_days: int):
        """Add or update the periodic backup task in the scheduler.

        Args:
            every_n_days (int): Frequency of the backup job in days.
        """
        self._scheduler.add_job(
            self._job,
            trigger="interval",
            days=every_n_days,
            id="weekly_db_backup",
            replace_existing=True,
        )

        LOGGER.info(f"Backups planned on every {every_n_days} day")
