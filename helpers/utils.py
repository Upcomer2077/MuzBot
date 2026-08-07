import asyncio
from typing import Optional

from aiogram.enums import ChatAction
from aiogram.types import Message

import bot
from dungeon import DM
from dungeon.models import TrackCache
from tools.extract_info import extract_video_info


class U:
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

    @staticmethod
    async def send_action(
        chat_id: int, action: ChatAction = ChatAction.UPLOAD_DOCUMENT
    ):
        """Asynchronously send a specific chat status action to a Telegram user.

        Args:
            chat_id: Unique identifier for the target Telegram chat.
            action: The type of Telegram ChatAction activity to display. Defaults to ChatAction.UPLOAD_DOCUMENT.
        """
        await bot.bot.send_chat_action(
            chat_id=chat_id,
            action=action,
        )

    # TODO: remove?
    @staticmethod
    async def delete_markup_after_delay(msg: Message, delay: int = 60) -> None:
        await asyncio.sleep(delay)
        try:
            await msg.edit_reply_markup(reply_markup=None)
        except Exception:
            pass  # Ignore errors if the message was already deleted by the user
