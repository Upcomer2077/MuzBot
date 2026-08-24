import os
import tarfile
from datetime import datetime

from aiogram.types import FSInputFile

import bot
from _logger import LOGGER
from config import CACHE_ROOT_DIR, CHANNEL_STORAGE_ID, DATABASE_PATH, TZ


def _make_backup():
    """Create a compressed tar.xz archive of the database file.

    Returns:
        tuple[bool, str | None]: Status of the backup and path to the archive file.
    """
    backup_dir = f"{CACHE_ROOT_DIR}/backups"
    if not os.path.exists(DATABASE_PATH):
        LOGGER.critical(f"BACKUP: file {DATABASE_PATH} not found.")
        return (False, None)

    os.makedirs(backup_dir, exist_ok=True)

    date_str = datetime.now(TZ).strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"{date_str}_backup.tar.xz"
    archive_path = os.path.join(backup_dir, archive_name)

    try:
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(DATABASE_PATH, arcname=os.path.basename(DATABASE_PATH))
        LOGGER.debug(f"Backup created: {archive_path}")
        return (True, archive_path)
    except Exception as e:
        LOGGER.error(f"Error while making backup tar: {e}")
        return (False, None)


async def _send_to_channel(archive_path):
    """Upload the generated backup archive to the configured Telegram channel.

    Args:
        archive_path (str): File path of the backup archive to be sent.
    """
    bot_info = await bot.bot.get_me()
    caption = f"📦 **#Backup** for @{bot_info.username or 'bot'}\n📅 {datetime.now(TZ).strftime('%d.%m.%Y %H:%M')}"
    document = FSInputFile(archive_path)
    try:
        await bot.bot.send_document(
            chat_id=CHANNEL_STORAGE_ID,
            document=document,
            caption=caption,
            parse_mode="Markdown",
            disable_notification=True,
        )
        LOGGER.info("Backup file was send to channel")
    except Exception as e:
        LOGGER.error(f"Backup send failed: {e}")


async def job():
    """Execute the full workflow: create backup, send to channel, and remove local archive."""
    (success, archive_path) = _make_backup()
    if success and archive_path:
        await _send_to_channel(archive_path)
        if os.path.exists(archive_path):
            os.remove(archive_path)
