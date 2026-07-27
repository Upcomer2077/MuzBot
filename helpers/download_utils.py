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
    """Utility class providing static helper operations for track extraction, caching, and media transmissions."""

    @staticmethod
    async def get_track(
        video_id: str, extract_info_from_ytm: bool = True
    ) -> Optional[TrackCache]:
        """Fetch a track from the database cache, optionally querying YouTube Music if missing.

        Args:
            video_id: Unique YouTube Music track identifier.
            extract_info_from_ytm: Flag to fetch missing metadata from YouTube Music. Defaults to True.

        Returns:
            The TrackCache model object instance if available, otherwise None.
        """
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
        """Transmit a cached track file directly to the user using Telegram's unique file reference.

        Args:
            chat_id: Unique identifier for the destination Telegram chat.
            tg_file_id: Cached Telegram cloud storage file identification string.
            anchor: Target Telegram message object used to trigger the text reply interface.

        Returns:
            A tuple containing the dispatched Telegram message instance and a success confirmation flag.
        """
        if AL.is_allowed_send_action(chat_id):
            await send_action(chat_id)

        sent_audio = await answer_audio_cached(anchor, audio_file=tg_file_id)
        cache_sent_successfully = True
        return sent_audio, cache_sent_successfully

    @staticmethod
    async def handle_cache_pull(video_id: str, chat_id: int):
        """Lock the track status for processing and invoke data retrieval operation.

        Args:
            video_id: Target YouTube Music track video identifier.
            chat_id: Unique identifier for the active Telegram chat conversation context.

        Returns:
            The output containing track data pulled from the storage blocks cache layer.
        """
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
        """Transmit a newly downloaded and converted media file stream to the user alongside metadata descriptors.

        Args:
            anchor_message: Target Telegram message object acting as an anchor.
            chat_id: Unique identifier for the destination Telegram chat interface.
            audio_f: Local file wrapper pointing directly to the converted target track format.
            thumb_f: Optional visual asset descriptor referencing album artwork structures.
            title: Song name header attribute for Telegram player displays.
            artist: Musician names or band details mapping metadata identifiers.

        Returns:
            The uploaded Telegram media message object instance.
        """

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
        """Send a stealth placeholder separator text sequence to serve as a target chat reference point.

        Args:
            chat_id: Target conversation path tracking index block identifier.

        Returns:
            The newly created structural chat marker entry message token wrapper.
        """
        return await bot.bot.send_message(
            chat_id,
            "||\\.||",
            parse_mode="MarkdownV2",
        )
