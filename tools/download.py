import os
from typing import TYPE_CHECKING

import yt_dlp

from _logger import LOGGER
from config import CACHE_ROOT_DIR
from helpers.get_ytm_video_link import get_ytm_video_link

if TYPE_CHECKING:
    from yt_dlp import _Params


def download_from_ytm(video_id: str):
    try:
        # Replace with the YouTube URL of the music video/track
        youtube_url = get_ytm_video_link(video_id)

        ydl_opts: "_Params" = {
            "format": "bestaudio/best",  # Select the best audio quality available
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",  # Convert to MP3
                    "preferredquality": "192",  # Audio bitrate (192 kbps)
                },
            ],
            "postprocessor_args": [
                "-threads",
                "2",  # Разрешаем использовать до 2 потоков на один процесс кодирования
                "-vn",  # Вырезаем видео/картинки во время кодирования (обложку мы шлем отдельно)
                "-sn",  # Отключаем субтитры
                "-dn",  # Отключаем мусорные потоки данных
            ],
            "no_warnings": True,
            "outtmpl": f"{CACHE_ROOT_DIR}/{video_id}/%(title)s.%(ext)s",  # Name the file based on the YouTube video title
            "sleep_interval": 5,
            "max_sleep_interval": 15,
            "quiet": True,
            "retries": 3,
        }
        LOGGER.info(f"Dl-PID for {video_id}: {os.getpid()}")
        LOGGER.info(f"Attempting to download video {video_id}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        LOGGER.info(f"Downloaded successfully: {video_id}")
    except Exception as e:
        LOGGER.error(f"Error while downloading video {e}")
        return False

    return True
