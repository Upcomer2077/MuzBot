import asyncio

from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedAudio,
    InputTextMessageContent,
    LinkPreviewOptions,
)

from dungeon import DM
from helpers.prettify_incoming_query import prettify_incoming_query
from schemas.dicts import YoutubeSearchResultDict
from tools.search import search_in_ytm

router = Router()


@router.inline_query()
async def inline(q: InlineQuery):
    if not q.query:
        return q.answer([])

    query = prettify_incoming_query(q.query)
    search_result: list[YoutubeSearchResultDict] = await asyncio.shield(
        asyncio.to_thread(search_in_ytm, query.strip(), 9)
    )

    if len(search_result) == 0:
        return
    await DM.enslave_bulk(search_result)

    entities = await DM.summon_slaves([one["video_id"] for one in search_result])

    inline_results = []
    for idx, video in enumerate(search_result, start=1):
        v_id = video["video_id"]
        title = video["title"]
        duration = video["duration"]
        artist = video["artist"]

        if not v_id:
            continue
        entity = entities.get(v_id)

        tg_audio_id = (
            entity.telegram_file_id if entity and entity.telegram_file_id else None
        )

        card = (
            InlineQueryResultArticle(
                id=v_id,
                title=f"{artist} — {title}",
                description=f"⏱ Длительность: {duration}",
                hide_url=True,
                input_message_content=InputTextMessageContent(
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                    message_text=f"{artist} — {title} [{duration}]",
                    disable_web_page_preview=True,
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⬇️", callback_data=f"dl:{v_id}:{idx}"
                            )
                        ]
                    ]
                ),
            )
            if not tg_audio_id
            else InlineQueryResultCachedAudio(id=v_id, audio_file_id=tg_audio_id)
        )
        inline_results.append(card)
    await q.answer(
        results=inline_results,
        cache_time=60,
        is_personal=False,
    )
