import asyncio

from aiogram.enums import ChatAction
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import bot
from config import PAGINATION_ITEMS_PER_PAGE
from dungeon import DM
from dungeon.models import TrackCache
from schemas.callbacks import DropCallback
from schemas.callbacks.pagination import PaginationBase
from schemas.tuples.utils import PageContentResult
from tools.extract_info import extract_video_info

_MAX_ITEMS = 27


class U:
    """Utility class providing static helper operations for track extraction, caching, and media transmissions."""

    @staticmethod
    async def get_track(
        video_id: str, extract_info_from_ytm: bool = True
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
            res = await extract_video_info(video_id)
            if res:
                await DM.tracks.enslave_bulk([res])
                track = await DM.tracks.summon_one(video_id)
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
            return  # Ignore errors if the message was already deleted by the user

    @staticmethod
    def get_page_content[T](
        search_result: list[T],
        page: int,
        pag_cb_type: type[PaginationBase],
        max: int = _MAX_ITEMS,
    ) -> PageContentResult[T]:
        """Функция нарезки результатов и nav сборки клавиатуры"""
        start_idx = page * PAGINATION_ITEMS_PER_PAGE
        end_idx = start_idx + PAGINATION_ITEMS_PER_PAGE
        content = search_result[start_idx:end_idx]

        nav_builder = InlineKeyboardBuilder()
        drop_builder = InlineKeyboardBuilder()

        if page > 0:
            nav_builder.button(
                text="⬅️", callback_data=pag_cb_type(page=page - 1).pack()
            )

        if end_idx < len(search_result) and (end_idx < max if max else True):
            nav_builder.button(
                text="➡️", callback_data=pag_cb_type(page=page + 1).pack()
            )

        drop_builder.button(text="❌", callback_data=DropCallback())

        return PageContentResult(content, nav_builder, drop_builder, start_idx)
