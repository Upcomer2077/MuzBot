import asyncio

from aiogram.enums import ChatAction
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import bot
from dungeon import DM
from dungeon.models import TrackCache
from schemas.callbacks import DownloadCallback, DropCallback
from schemas.callbacks.search_pagination import PaginationCallback
from tools.extract_info import extract_video_info

_ITEMS_PER_PAGE = 9
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
    def get_page_content(search_result: list, page: int):
        """Функция нарезки результатов и сборки клавиатуры"""
        start_idx = page * _ITEMS_PER_PAGE
        end_idx = start_idx + _ITEMS_PER_PAGE
        page_items = search_result[start_idx:end_idx]

        text = f"Найденные варианты (Страница {page + 1}):\n\n"
        builder = InlineKeyboardBuilder()

        for i, video in enumerate(page_items, start=start_idx + 1):
            v_id = video["video_id"]
            title = video["title"]
            duration = video["duration"]
            artist = video["artist"]
            text += f"#{i}. {artist} — {title} [{duration}]\n"

            builder.button(
                text=f"⬇️ {i}",
                callback_data=DownloadCallback(video_id=v_id, idx=str(i)),
            )
        # TODO: search in video category
        # if not (end_idx < len(search_result) and end_idx < _MAX_ITEMS):
        #     text += "\nНе нашли что искали? Попробуйте добавить -v в конце запроса"
        builder.adjust(3, repeat=True)

        nav_builder = InlineKeyboardBuilder()

        # Кнопка «Назад»
        if page > 0:
            nav_builder.button(
                text="⬅️", callback_data=PaginationCallback(page=page - 1).pack()
            )

        if end_idx < len(search_result) and end_idx < _MAX_ITEMS:
            nav_builder.button(
                text="➡️", callback_data=PaginationCallback(page=page + 1).pack()
            )

        nav_builder.button(text="❌", callback_data=DropCallback())

        builder.attach(nav_builder)
        return text, builder.as_markup()
