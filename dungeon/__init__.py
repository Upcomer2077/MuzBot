import os
from datetime import datetime

from peewee_aio import Manager

from config import DATABASE_DIR, DATABASE_FILENAME, MAX_TRACK_DURATION_SECONDS
from dungeon.dispatcher import DB_DISPATCHER
from dungeon.models import TrackCache
from type import YoutubeSearchResultDict


class DungeonMaster:
    def __init__(self, db_dir: str, db_name: str, db_dispatcher: Manager):
        self._db_dir = db_dir
        self._db_name = db_name
        self._db_dispatcher = db_dispatcher

    async def open_dungeon(
        self,
    ):
        """Создает таблицу в базе данных, если её нет."""
        os.makedirs(self._db_dir, exist_ok=True)

        async with self._db_dispatcher:
            async with self._db_dispatcher.connection():
                await TrackCache.create_table(safe=True)
                await self._db_dispatcher.execute("PRAGMA journal_mode=WAL;")
                await self._db_dispatcher.execute("PRAGMA synchronous=NORMAL;")
                await self._db_dispatcher.execute("PRAGMA foreign_keys=ON;")
                await self._db_dispatcher.execute("PRAGMA auto_vacuum = INCREMENTAL;")
        await self._finalize()

    async def close_dungeon(self):
        await self._finalize()
        await self._db_dispatcher.disconnect()

    async def enslave_bulk(self, tracks: list[YoutubeSearchResultDict]) -> int:
        if not tracks:
            return 0

        try:
            data_to_insert = []

            for track in tracks:
                data_to_insert.append(
                    {
                        TrackCache.video_id: track["video_id"],
                        TrackCache.title: track["title"],
                        TrackCache.artist: track["artist"],
                        TrackCache.track_duration: int(track["duration_seconds"]),
                        TrackCache.is_too_large: int(
                            (track["duration_seconds"] or 0)
                            > MAX_TRACK_DURATION_SECONDS
                        ),
                    }
                )

            # Формируем массовый запрос
            query = TrackCache.insert_many(data_to_insert)

            inserted_rows = await self._db_dispatcher.execute(query)
            return inserted_rows

        except Exception as e:
            print(f"Ошибка при массовом сохранении треков: {e}")
            return 0

    async def summon_one(self, video_id: str):
        """Ищет трек по его video_id и возвращает в виде словаря."""
        try:
            track = await TrackCache.get_or_none(TrackCache.video_id == video_id)
            if track:
                track.last_used_at = datetime.now()
                await track.save()

                return track
            return None
        except Exception as e:
            print(f"Ошибка при поиске трека: {e}")
            return None

    async def next_door(self, video_id: str) -> bool:
        """Удаляет строку с указанным video_id из базы данных."""
        try:
            query = TrackCache.delete().where(TrackCache.video_id == video_id)
            deleted_count = await self._db_dispatcher.execute(query)
            return deleted_count > 0
        except Exception as e:
            print(f"Ошибка при удалении трека: {e}")
            return False

    async def fisting(
        self,
        video_id: str,
        telegram_file_id: str | None = None,
        is_too_large: bool | None = None,
        is_work_in_progress: bool | None = None,
    ) -> bool:

        update_data = {
            TrackCache.telegram_file_id: telegram_file_id,
            TrackCache.is_too_large: is_too_large,
            TrackCache.is_work_in_progress: is_work_in_progress,
        }
        filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
        try:
            query = TrackCache.update(filtered_update_data).where(
                TrackCache.video_id == video_id
            )

            rows_updated: int = await self._db_dispatcher.execute(query)
            return rows_updated != 0

        except Exception as e:
            print(e)
            return False

    async def _finalize(self):
        query = TrackCache.update(is_work_in_progress=False).where(
            TrackCache.is_work_in_progress == True  # noqa: E712
        )
        try:
            await DB_DISPATCHER.execute(query)
        except Exception as e:
            print(f"❌ Не удалось обновить базу данных при выключении: {e}")


DM = DungeonMaster(DATABASE_DIR, DATABASE_FILENAME, DB_DISPATCHER)
