from _logger import LOGGER
from config import MAX_TRACK_DURATION_SECONDS
from dungeon.models import TrackCache
from schemas.dicts import YoutubeSearchResultDict


class TrackRepository:
    """Handles persistence logic, status updates, and retrieval operations for tracks."""

    async def enslave_bulk(self, tracks: list[YoutubeSearchResultDict]) -> int:
        """Insert multiple tracks into the cache database in a single batch query."""
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
        """Fetch cached tracks mapping them to their corresponding video identifiers."""
        LOGGER.debug(f"Selecting slaves {video_ids}")
        rows = await TrackCache.filter(video_id__in=video_ids)
        LOGGER.debug(f"Selected slaves count: {len(rows)}")
        return {row.video_id: row for row in rows if row.video_id}

    async def summon_one(self, video_id: str) -> TrackCache | None:
        """Retrieve a specific track record by its identifier."""
        LOGGER.debug(f"Selecting one slave {video_id}")
        try:
            return await TrackCache.get_or_none(video_id=video_id)
        except Exception as e:
            LOGGER.error(f"Can't find track {video_id} in database: {e}")
            return None

    async def next_door(self, video_id: str) -> bool:
        """Delete a specific track cache record completely from the database."""
        try:
            LOGGER.debug(f"Removing {video_id}")
            res = await TrackCache.filter(video_id=video_id).delete()
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
        """Update attribute states or Telegram properties on a specific track."""
        LOGGER.debug(f"Updating records: {video_id}")
        update_data = {
            "telegram_file_id": telegram_file_id,
            "is_too_large": is_too_large,
        }
        filtered_update_data = {k: v for k, v in update_data.items() if v is not None}

        if not filtered_update_data:
            return False

        try:
            filter_kwargs = (
                {"video_id__in": video_id}
                if isinstance(video_id, list)
                else {"video_id": video_id}
            )
            rows_updated = await TrackCache.filter(**filter_kwargs).update(
                **filtered_update_data
            )
            LOGGER.debug(f"Updated records count: {rows_updated}. ids: {video_id}")
            return rows_updated != 0
        except Exception as e:
            LOGGER.error(f"Caught error while updating records: {e}")
            return False

    async def get_total_count(self) -> int:
        """Calculate and return the absolute number of track records."""
        return await TrackCache.all().count()
