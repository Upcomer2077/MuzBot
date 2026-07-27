from typing import Literal, Optional

from aiogram.types import FSInputFile, MaybeInaccessibleMessageUnion, Message

import bot
from action_limiter import AL
from dungeon import DM
from dungeon.models import TrackCache
from helpers.pull_data_from_cache import pull_data_from_cache
from tools.extract_info import extract_video_info
from tools.send_action import send_action
from tools.send_audio import answer_audio, answer_audio_cached


class DU:
    @staticmethod
    async def get_track(
        video_id: str, extract_info_from_ytm: bool = True
    ) -> Optional[TrackCache]:
        track = await DM.summon_one(video_id)
        if not track and extract_info_from_ytm:
            res = await extract_video_info(video_id)
            if res:
                await DM.enslave_bulk([res])
                track = await DM.summon_one(video_id)
        return track

    @staticmethod
    async def send_cached_audio(
        chat_id: int, tg_file_id: str, anchor: MaybeInaccessibleMessageUnion
    ) -> tuple[Message, Literal[True]]:
        if AL.is_allowed_send_action(chat_id):
            await send_action(chat_id)

        sent_audio = await answer_audio_cached(anchor, audio_file=tg_file_id)
        cache_sent_successfully = True
        return sent_audio, cache_sent_successfully

    @staticmethod
    async def handle_cache_pull(video_id: str, chat_id: int):
        await DM.fisting(video_id, is_work_in_progress=True)
        if AL.is_allowed_send_action(chat_id):
            await send_action(chat_id)

        return await pull_data_from_cache(video_id)

    @staticmethod
    async def send_new_audio(
        anchor_message: MaybeInaccessibleMessageUnion,
        chat_id: int,
        audio_f: FSInputFile,
        thumb_f: FSInputFile | None,
        title: str,
        artist: str,
    ) -> Message:
        if AL.is_allowed_send_action(chat_id):
            await send_action(chat_id)
        sent_audio = await answer_audio(
            anchor_message,
            audio_file=audio_f,
            thumb_file=thumb_f,
            title=title,
            artist=artist,
        )
        return sent_audio

    @staticmethod
    async def send_anchor_message(chat_id: int):
        return await bot.bot.send_message(
            chat_id,
            "||\\.||",
            parse_mode="MarkdownV2",
        )
