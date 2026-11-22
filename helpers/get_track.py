from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dungeon.models import TrackCache
    from interfaces.idatabase import IDataBase
    from interfaces.imusictools import IMusicTools


async def get_track(
    video_id: str,
    extract_info_from_ytm: bool = True,
    *,
    MT: IMusicTools,
    DM: IDataBase,
) -> TrackCache | None:
    """Fetch a track from the database cache, optionally querying YouTube Music if missing.

    Args:
        video_id: Unique YouTube Music track identifier.
        extract_info_from_ytm: Flag to fetch missing metadata from YouTube Music. Defaults to True.

    Returns:
        The TrackCache model object instance if available, otherwise None.
    """
    track = await DM.tracks.summon_one(video_id)
    if not track and extract_info_from_ytm:
        res = await MT.extract_track_info(video_id)
        if res:
            await DM.tracks.enslave_bulk([res])
            track = await DM.tracks.summon_one(video_id)
    return track
