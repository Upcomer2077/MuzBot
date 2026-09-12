from collections.abc import AsyncGenerator
from typing import Any

from tortoise import Tortoise, connections
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from _logger import LOGGER
from config import (
    DATABASE_PATH,
    MAX_PLAYLIST_TRACKS_REQUEST,
    MAX_TRACK_DURATION_SECONDS,
)
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

    async def open_dungeon(self):
        """Open database connection, initialize tables, set PRAGMA optimizations, and reset temporary states."""

        await Tortoise.init(
            db_url=f"sqlite://{DATABASE_PATH}", modules={"models": ["dungeon.models"]}
        )
        await Tortoise.generate_schemas()

        try:
            connection = connections.get("default")

            pragma_script = """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA foreign_keys=ON;
            PRAGMA auto_vacuum=INCREMENTAL;
            """
            await connection.execute_script(pragma_script)

            LOGGER.debug("Database pragma set. Connection success")

        except Exception as e:
            LOGGER.critical(f"Caught error while opening the dungeon: {e}")

    async def close_dungeon(self):
        """Reset operational database states and disconnect safely from the storage engine."""
        await Tortoise.close_connections()
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
            instances_to_insert = []
            for track in tracks:
                duration = (
                    int(track["duration_seconds"])
                    if track.get("duration_seconds")
                    else 0
                )

                instances_to_insert.append(
                    TrackCache(
                        video_id=track["video_id"],
                        title=track["title"],
                        artist=track["artist"],
                        track_duration=duration,
                        is_too_large=duration > MAX_TRACK_DURATION_SECONDS,
                    )
                )

            LOGGER.debug(f"Inserting tracks (bulk). Total count: {len(tracks)}")

            await TrackCache.bulk_create(instances_to_insert)

            LOGGER.debug("Inserting complete")
            return len(tracks)

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
        rows = await TrackCache.filter(video_id__in=video_ids)

        LOGGER.debug(f"Selected slaves count: {len(rows)}")

        return {row.video_id: row for row in rows if row.video_id}

    async def summon_one(self, video_id: str):
        """Retrieve a specific track record and update its recent usage timestamp indicator.

        Args:
            video_id: Target YouTube track identifier.

        Returns:
            The TrackCache model object instance if found, otherwise None.
        """
        LOGGER.debug(f"Selecting one slave {video_id}")

        try:
            track = await TrackCache.get_or_none(video_id=video_id)
            return track

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
            res: int = await TrackCache.filter(video_id=video_id).delete()

            LOGGER.debug(f"Removed {video_id}")
            return res > 0
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
            video_id: Target YouTube track identifier (or list of identifiers).
            telegram_file_id: Unique Telegram cloud storage file reference. Defaults to None.
            is_too_large: Constraint flag indicating file size exceeded limits. Defaults to None.

        Returns:
            True if any database records were modified, False otherwise.
        """
        LOGGER.debug(f"Updating records: {video_id}")

        update_data = {
            "telegram_file_id": telegram_file_id,
            "is_too_large": is_too_large,
        }
        filtered_update_data = {k: v for k, v in update_data.items() if v is not None}

        if not filtered_update_data:
            return False

        try:
            if isinstance(video_id, list):
                filter_kwargs = {"video_id__in": video_id}
            else:
                filter_kwargs = {"video_id": video_id}

            rows_updated: int = await TrackCache.filter(**filter_kwargs).update(
                **filtered_update_data
            )

            LOGGER.debug(f"Updated records count: {rows_updated}. ids: {video_id}")
            return rows_updated != 0

        except Exception as e:
            LOGGER.error(f"Caught error while updating records: {e}")
            return False

    async def _get_slaves_count(self) -> int:
        """Calculate and return the absolute number of track records currently present in the table.

        Returns:
            Total row count integer from the tracks table.
        """
        return await TrackCache.all().count()

    async def get_playlist(self, pl_id: str):
        LOGGER.debug(f"Collecting info about playlist {pl_id}")
        r = await PlaylistCache.get_or_none(playlist_id=pl_id)
        LOGGER.debug(f"Collecting {pl_id} done")
        return r

    async def add_playlist_and_tracks(
        self, playlist_info: PlaylistInfoDict, tracks: list[YoutubeSearchResultDict]
    ) -> int:
        LOGGER.debug("Adding playlist and tracks")
        LOGGER.debug("Enslaving tracks: ")
        count = await self.enslave_bulk(tracks)
        LOGGER.debug(f"Tracks enslaved: {count}")

        async with in_transaction():
            LOGGER.debug(f"Enslaving playlist info: {playlist_info['id']} ")

            _, created = await PlaylistCache.get_or_create(
                playlist_id=playlist_info["id"],
                defaults={
                    "title": playlist_info["title"],
                    "artist": playlist_info["author"],
                },
            )
            LOGGER.debug(
                f"Enslaved playlist: {playlist_info['id']} (Created: {created})"
            )

            relations_instances = [
                TrackPlaylist(
                    video_id=v["video_id"],
                    playlist_id=playlist_info["id"],
                    track_order=idx,
                )
                for (idx, v) in enumerate(tracks)
            ]

            LOGGER.debug(f"Enslaving intermediate table: {len(relations_instances)}")
            try:
                await TrackPlaylist.bulk_create(
                    relations_instances, ignore_conflicts=True
                )
                r = len(relations_instances)
            except IntegrityError as e:
                LOGGER.warning(
                    f"Some relations already existed or constraint failed: {e}"
                )
                r = 0

            LOGGER.debug(f"Enslaving intermediate table done: {r}")
            return r

    async def summon_slaves_from_playlist(
        self, playlist_id: str, limit: int | None = MAX_PLAYLIST_TRACKS_REQUEST + 1
    ) -> dict[str, TrackCache] | None:
        """Fetch cached Telegram file identifiers mapping them to their corresponding video identifiers.

        Args:
            playlist_id: ytm playlist identifier to query.

        Returns:
            A dictionary mapping matching video IDs to available Telegram file IDs.
        """
        LOGGER.debug(f"Getting slaves from playlist: {playlist_id} ")

        query = TrackCache.filter(playlists__playlist_id=playlist_id).order_by(
            "playlists__track_order"
        )

        if limit is not None:
            query = query.limit(limit)

        rows = await query
        LOGGER.debug(f"Getting slaves from playlist done: {len(rows)} ")

        if not rows:
            return None

        return {row.video_id: row for row in rows if row.video_id}

    async def set_performer_last_release(
        self,
        performer_id: str,
        *,
        performer_name: str,
        last_album_id: str | None,
        last_single_id: str | None,
    ):
        await YTPerformers.update_or_create(
            id=performer_id,
            defaults={
                "name": performer_name,
                "last_single_id": last_single_id,
                "last_album_id": last_album_id,
            },
        )

    async def subscribe_to_performer(self, user_id: int, performer_id: str):
        await TgUsers.get_or_create(id=user_id, defaults={})

        _, created = await Subscriptions.get_or_create(
            tg_user_id=user_id, performer_id=performer_id
        )

        return 1 if created else 0

    async def get_performer_info(self, performer_id: str):
        return await YTPerformers.get_or_none(id=performer_id)

    async def drop_sub(self, performer_id: str, user_id: int) -> int:
        rows_deleted = await Subscriptions.filter(
            tg_user_id=user_id, performer_id=performer_id
        ).delete()

        return rows_deleted

    async def get_artists_by_name(
        self, user_id: int, s_query: str
    ) -> list[YTPerformers]:
        r = await YTPerformers.filter(
            telegram_users__tg_user_id=user_id, name__istartswith=s_query
        ).only("id", "name")

        return list(r)

    async def get_subscripted_authors(
        self, batch_size: int = 100
    ) -> AsyncGenerator[list[dict[str, Any]]]:
        """Yield batches of active performers that have at least one active subscription."""
        base_query = (
            YTPerformers.filter(telegram_users__is_suspended=False)
            .distinct()
            .order_by("id")
        )

        offset = 0
        while True:
            results = (
                await base_query.limit(batch_size)
                .offset(offset)
                .values(
                    performer_id="id",
                    name="name",
                    last_album_id="last_album_id",
                    last_single_id="last_single_id",
                )
            )

            if not results:
                break

            yield results

            offset += batch_size

    async def get_tg_users_with_subs(
        self, performers_ids: list
    ) -> list[dict[str, Any]]:
        """Fetch relations between performers and Telegram users as dictionaries."""
        if not performers_ids:
            return []
        return (
            await Subscriptions.filter(performer_id__in=performers_ids)
            .order_by("performer_id")
            .values(performer_id="performer_id", tg_user_id="tg_user_id")
        )

    async def toggle_user_subscriptions(self, tg_user_id: int, suspend: bool) -> int:
        """Update the suspension status for all subscriptions belonging to a specific user."""
        rows_updated = await Subscriptions.filter(tg_user_id=tg_user_id).update(
            is_suspended=suspend
        )

        return rows_updated
