from dungeon import DM
from overlord import COLD
from type import TrackState


async def finalize_download(video_id, tti: TrackState) -> bool:
    """Clean up local temporary media cache files and update the track's status and file IDs in the database.

    Args:
        video_id: Unique YouTube Music track identifier.
        tti: TrackState container holding the transmission results and file size flags.

    Returns:
        True if the database record updates successfully, False otherwise.
    """
    COLD.annihilate(video_id)
    if tti.sent_audio and tti.sent_audio.audio and tti.sent_audio.audio.file_id:
        tg_audio_id = tti.sent_audio.audio.file_id
        return await DM.fisting(
            video_id,
            tg_audio_id,
            tti.is_too_large,
            is_work_in_progress=False,
        )
    return await DM.fisting(
        video_id,
        is_work_in_progress=False,
    )
