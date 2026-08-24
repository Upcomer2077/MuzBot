import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dungeon import DM
from helpers.prettify_incoming_query import prettify_incoming_query
from schemas.callbacks import DownloadCallback, DropCallback
from schemas.dicts import YoutubeSearchResultDict
from tools.search import search_in_ytm

router = Router()


@router.message()
async def get_list(message: Message):
    QUERY = message.text
    if QUERY is None:
        return None
    clean_text = prettify_incoming_query(QUERY)
    if len(clean_text) == 0:
        return None
    STATUS_MESSAGE = await message.answer("🔍 Ищу варианты...")
    search_result: list[YoutubeSearchResultDict] = await asyncio.shield(
        asyncio.to_thread(search_in_ytm, QUERY.strip(), 9)
    )

    if len(search_result) == 0:
        return STATUS_MESSAGE.edit_text("404 🤷")

    builder = InlineKeyboardBuilder()
    text = "Найденные варианты:\n\n"

    for idx, video in enumerate(search_result, start=1):
        v_id = video["video_id"]
        title = video["title"]
        duration = video["duration"]
        artist = video["artist"]
        text += f"#{idx}. {artist} — {title} [{duration}]\n"

        builder.button(
            text=f"⬇️{idx}",
            callback_data=DownloadCallback(video_id=v_id, idx=str(idx)),
        )
    builder.button(
        text="❌",
        callback_data=DropCallback(),
    ).adjust(3, repeat=True)

    await DM.enslave_bulk(search_result)

    await STATUS_MESSAGE.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=None
    )
