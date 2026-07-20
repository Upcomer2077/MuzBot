from dungeon import DM
from overlord import COLD
from type import TempTrackStatusInfo


async def finalize_download(video_id, tti: TempTrackStatusInfo):
    COLD.annihilate(video_id)
    if tti.sent_message and tti.sent_message.audio and tti.sent_message.audio.file_id:
        tg_audio_id = tti.sent_message.audio.file_id
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
