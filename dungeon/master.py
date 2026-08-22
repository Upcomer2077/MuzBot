from datetime import datetime
from zoneinfo import ZoneInfo

from peewee_aio import Manager
from peewee_aio.model import AIOModelSelect

from _logger import LOGGER
from config import MAX_TRACK_DURATION_SECONDS, TZ
from dungeon.dispatcher import DB_DISPATCHER
from dungeon.models import (
    PlaylistCache,
    Subscriptions,
    TgUsers,
    TrackCache,
    TrackPlaylist,
    YTPerformers,
)
from schemas.dicts import PlaylistInfoDict, YoutubeSearchResultDict


class DungeonMaster:
    """Database controller managing TrackCache operations, schema initializations, and bulk entries."""

    def __init__(self, db_path: str, db_dispatcher: Manager):
        """Initialize database credentials and assign the peewee-async manager instance.

        Args:
            db_path: Filesystem path to the SQLite database.
            db_dispatcher: Asynchronous database connection manager.
        """

        self._db_path = db_path
        self._db_dispatcher = db_dispatcher

    async def open_dungeon(
        self,
    ):
        """Open database connection, initialize tables, set PRAGMA optimizations, and reset temporary states."""

        try:
            async with self._db_dispatcher, self._db_dispatcher.connection():
                await TrackCache.create_table(safe=True)
                await PlaylistCache.create_table(safe=True)
                await TrackPlaylist.create_table(safe=True)
                await YTPerformers.create_table(safe=True)
                await TgUsers.create_table(safe=True)
                await Subscriptions.create_table(safe=True)
                await self._db_dispatcher.execute("PRAGMA journal_mode=WAL;")
                await self._db_dispatcher.execute("PRAGMA synchronous=NORMAL;")
                await self._db_dispatcher.execute("PRAGMA foreign_keys=ON;")
                await self._db_dispatcher.execute("PRAGMA auto_vacuum = INCREMENTAL;")
            LOGGER.debug("Database pragma set. Connection success")
        except Exception as e:
            LOGGER.critical(f"Caught error while opening the dungeon: {e}")

    async def close_dungeon(self):
        """Reset operational database states and disconnect safely from the storage engine."""
        await self._db_dispatcher.disconnect()
        LOGGER.debug("Database connection closed")

    async def enslave_bulk(self, tracks: list[YoutubeSearchResultDict]) -> int:
        """Insert multiple tracks into the cache database in a single batch query.

        Args:
            tracks: Collection of dictionaries containing YouTube Music search result data.

        Returns:
            The total number of successfully inserted database rows.
        """

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
            LOGGER.debug(f"Inserting tracks (bulk). {len(tracks)}")
            query = TrackCache.insert_many(data_to_insert)

            inserted_rows: int = await self._db_dispatcher.execute(query)
            LOGGER.debug(f"Inserting complete. Total: {inserted_rows}")
            return inserted_rows

        except Exception as e:
            LOGGER.error(f"Bulk saving error: {e}")
            return 0

    async def summon_slaves(self, video_ids: list[str]) -> dict[str, TrackCache]:
        """Fetch cached Telegram file identifiers mapping them to their corresponding video identifiers.

        Args:
            video_ids: List of YouTube track video identifiers to query.

        Returns:
            A dictionary mapping matching video IDs to available Telegram file IDs.
        """
        LOGGER.debug(f"Selecting slaves {video_ids}")
        query = TrackCache.select().where(TrackCache.video_id.in_(video_ids))

        rows = await query
        LOGGER.debug(f"Selected slaves count: {len(rows)}")
        res: dict[str, TrackCache] = {}
        for i in rows:
            if i.video_id:
                res[i.video_id] = i
        return res

    async def summon_one(self, video_id: str):
        """Retrieve a specific track record and update its recent usage timestamp indicator.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            The TrackCache model object instance if found, otherwise None.
        """
        LOGGER.debug(f"Selecting one slave {video_id}")

        try:
            track = await TrackCache.get_or_none(TrackCache.video_id == video_id)
            if track:
                track.last_used_at = datetime.now(ZoneInfo(TZ))
                await track.save()

                LOGGER.debug("Selected one slave")
                return track

            LOGGER.debug("Slave not found")
            return None

        except Exception as e:
            LOGGER.error(f"Can't find track {video_id} in database: {e}")
            return None

    async def next_door(self, video_id: str) -> bool:
        """Delete a specific track cache record completely from the database using its identifier.

        Args:
            video_id: Target YouTube track identifier to purge.

        Returns:
            True if the target row was deleted successfully, False if not found or failed.
        """
        try:
            LOGGER.debug(f"Removing {video_id}")
            query = TrackCache.delete().where(TrackCache.video_id == video_id)
            deleted_count = await self._db_dispatcher.execute(query)
            LOGGER.debug(f"Removed {video_id}")
            return deleted_count > 0
        except Exception as e:
            LOGGER.error(f"Can't delete track {video_id}: {e}")
            return False

    async def fisting(
        self,
        video_id: str | list[str],
        telegram_file_id: str | None = None,
        is_too_large: bool | None = None,
    ) -> bool:
        """Update attribute states, processing status flags, or Telegram properties on a specific track.

        Args:
            video_id: Target YouTube track identifier.
            telegram_file_id: Unique Telegram cloud storage file reference. Defaults to None.
            is_too_large: Constraint flag indicating file size exceeded limits. Defaults to None.

        Returns:
            True if any database records were modified, False otherwise.
        """
        LOGGER.debug(f"Updating records: {video_id}")
        update_data = {
            TrackCache.telegram_file_id: telegram_file_id,
            TrackCache.is_too_large: is_too_large,
        }
        filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
        try:
            query = TrackCache.update(filtered_update_data).where(
                TrackCache.video_id.in_(video_id)
                if isinstance(video_id, list)
                else TrackCache.video_id == video_id
            )

            rows_updated: int = await self._db_dispatcher.execute(query)
            LOGGER.debug(f"Updated records count: {rows_updated}. ids: {video_id}")
            return rows_updated != 0

        except Exception as e:
            LOGGER.error(f"Caught error while updating records: {e}")
            return False

    async def _get_slaves_count(self):
        """Calculate and return the absolute number of track records currently present in the table.

        Returns:
            Total row count integer from the tracks table.
        """
        res = await TrackCache.select(TrackCache.video_id).count()
        return res

    async def get_playlist(self, pl_id: str):
        LOGGER.debug(f"Collecting info about playlist {pl_id}")
        r = await PlaylistCache.get_or_none(PlaylistCache.playlist_id == pl_id)
        LOGGER.debug(f"Collecting {pl_id} done")
        return r

    async def add_playlist_and_tracks(
        self, playlist_info: PlaylistInfoDict, tracks: list[YoutubeSearchResultDict]
    ):
        LOGGER.debug("Adding playlist and tracks")
        LOGGER.debug("Enslaving tracks: ")
        count = await self.enslave_bulk(tracks)
        LOGGER.debug(f"Tracks enslaved: {count}")

        q1 = PlaylistCache.insert(
            playlist_id=playlist_info["id"],
            title=playlist_info["title"],
            artist=playlist_info["artist"],
        )
        LOGGER.debug(f"Enslaving playlist info: {playlist_info['id']} ")
        _ = await DB_DISPATCHER.execute(q1)
        LOGGER.debug(f"Enslaved playlist: {playlist_info['id']} ")

        relations_data = [
            {
                "video_id": v["video_id"],
                "playlist_id": playlist_info["id"],
                "track_order": idx,
            }
            for (idx, v) in enumerate(tracks)
        ]
        LOGGER.debug(f"Enslaving intermediate table: {len(relations_data)} ")
        q2 = TrackPlaylist.insert_many(relations_data).on_conflict_ignore()
        r: int = await DB_DISPATCHER.execute(q2)
        LOGGER.debug(f"Enslaving intermediate table done: {r} ")

        return r

    async def summon_slaves_from_playlist(
        self, playlist_id: str
    ) -> dict[str, TrackCache] | None:
        """Fetch cached Telegram file identifiers mapping them to their corresponding video identifiers.

        Args:
            playlist_id: ytm playlist identifier to query.

        Returns:
            A dictionary mapping matching video IDs to available Telegram file IDs.
        """
        LOGGER.debug(f"Getting slaves from playlist: {playlist_id} ")
        query = (
            TrackCache.select()
            .join(TrackPlaylist, on=(TrackCache.video_id == TrackPlaylist.video_id))
            .where(TrackPlaylist.playlist_id == playlist_id)
            .order_by(TrackPlaylist.track_order)
        )
        rows = await query
        LOGGER.debug(f"Getting slaves from playlist done: {len(rows)} ")

        res: dict[str, TrackCache] = {}
        if not len(rows):
            return None
        for i in rows:
            if i.video_id:
                res[i.video_id] = i
        return res

    async def set_performer_last_release(
        self,
        performer_id: str,
        *,
        performer_name: str,
        last_album_id: str | None,
        last_single_id: str | None,
    ):
        query = YTPerformers.insert(
            id=performer_id,
            name=performer_name,
            last_single_id=last_single_id,
            last_album_id=last_album_id,
        )

        await DB_DISPATCHER.execute(query)

    async def subscribe_to_performer(self, user_id: int, performer_id: str):
        query = TgUsers.insert(id=user_id)
        await DB_DISPATCHER.execute(query)

        query = Subscriptions.insert(
            tg_user_id=user_id, performer_id=performer_id
        ).on_conflict("IGNORE")

        r = await DB_DISPATCHER.execute(query)

        return r

    async def get_performer_info(self, performer_id: str):
        return await YTPerformers.get_or_none(id=performer_id)

    async def drop_sub(self, performer_id: str, user_id: int):
        query = Subscriptions.delete().where(
            (Subscriptions.tg_user_id == user_id)
            & (Subscriptions.performer_id == performer_id)
        )

        await DB_DISPATCHER.execute(query)

    async def get_artists_by_name(self, user_id: int, s_query: str):
        like_pattern = f"{s_query}%"
        query: AIOModelSelect[YTPerformers] = (
            YTPerformers.select(YTPerformers.id, YTPerformers.name)
            .join(Subscriptions, on=(Subscriptions.performer_id == YTPerformers.id))
            .where(
                (Subscriptions.tg_user_id == user_id)
                & (YTPerformers.name.ilike(like_pattern))
            )
        )

        r = await query
        return list(r)
