import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dungeon import DM
from helpers.prettify_incoming_query import prettify_incoming_query
from tools.search import search_in_ytm
from type import YoutubeSearchResultDict

router = Router()


@router.message()
async def get_list(message: Message):
    query = message.text
    if query is None:
        return None
    clean_text = prettify_incoming_query(query)
    if len(clean_text) == 0:
        return None
    status_msg = await message.answer("🔍 Ищу варианты...")
    search_result: list[YoutubeSearchResultDict] = await asyncio.shield(
        asyncio.to_thread(search_in_ytm, query.strip(), 9)
    )

    if len(search_result) == 0:
        return await status_msg.edit_text("404 🤷")

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
            callback_data=f"dl:{v_id}:{idx}",
        )
    builder.button(
        text="❌",
        callback_data="drop_m",
    ).adjust(3, repeat=True)

    await DM.enslave_bulk(search_result)

    await status_msg.edit_text(text, reply_markup=builder.as_markup(), parse_mode=None)
