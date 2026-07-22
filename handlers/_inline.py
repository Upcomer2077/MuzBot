import asyncio
from uuid import uuid4

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedAudio,
    InputTextMessageContent,
)
from ytmusicapi.exceptions import YTMusicServerError

import bot
from config import INLINE_STOP_WORD
from dungeon import DM
from helpers.finalize_download import finalize_download
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from helpers.prettify_incoming_query import prettify_incoming_query
from helpers.pull_data_from_cache import pull_data_from_cache
from overlord import COLD
from tools.download import download
from tools.search import search
from type import TempTrackStatusInfo, YoutubeSearchResultDict

router = Router()


@router.inline_query()
async def inline(q: InlineQuery):
    if not q.query or not q.query.endswith(INLINE_STOP_WORD):
        return q.answer([])

    query = prettify_incoming_query(q.query)
    print(q.query, query)
    try:
        search_result: list[YoutubeSearchResultDict] = await asyncio.shield(
            asyncio.to_thread(search, query.strip(), 1)
        )
    except YTMusicServerError as e:
        print(f"Caught YTMusicServerError: {e}")
        print(f"Query: {q.query}")
        return

    if len(search_result) == 0:
        return

    await DM.enslave_bulk(search_result)

    track = search_result[0]
    video_id = track["video_id"]
    track_from_db = await DM.summon_one(video_id)

    if not track_from_db:
        print("Critical error")
        return

    TTI = TempTrackStatusInfo(
        tg_file_id=track_from_db.telegram_file_id,
        is_too_large=track_from_db.is_too_large,
        is_work_in_progress=track_from_db.is_work_in_progress,
    )

    if TTI.tg_file_id:
        return q.answer(
            [
                InlineQueryResultCachedAudio(
                    id=query,
                    audio_file_id=TTI.tg_file_id,
                )
            ],
            cache_time=60,
        )
    if TTI.is_too_large:
        return q.answer(
            results=[
                InlineQueryResultArticle(
                    id=video_id,
                    title=f"[{track['duration']}]{track_from_db.artist} - {track_from_db.title}",
                    hide_url=True,
                    description="❌ Ошибка: Слишком большой для скачивания",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f"❌ Трек *{track_from_db.artist} — {track_from_db.title}* слишком большой для скачивания"
                        ),
                        parse_mode="Markdown",
                    ),
                )
            ],
            cache_time=5,
        )
    await q.answer(
        results=[
            InlineQueryResultArticle(
                id=video_id,
                title=f"[{track['duration']}]{track_from_db.artist} - {track_from_db.title}",
                hide_url=True,
                description=f'Не найден в кэше, уже загружаем. Повторите через 10-15 секунд (сотрите "{INLINE_STOP_WORD}" и напишите снова)',
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"Трек *{track_from_db.artist} — {track_from_db.title}* сейчас скачивается на сервер.\n"
                        f"Пожалуйста, подождите немного и нажмите кнопку ниже для повторного поиска."
                    ),
                    parse_mode="Markdown",
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔄 Обновить поиск",
                                switch_inline_query_current_chat=f"{q.query}",
                            ),
                        ]
                    ]
                ),
            ),
        ],
        cache_time=5,
    )
    if TTI.is_work_in_progress:
        return

    TTI.cache_data = await pull_data_from_cache(track["video_id"], download)
    if not TTI.cache_data:
        return
    (
        audio_file,
        thumb_file,
    ) = prepare_audio_file_to_send(TTI.cache_data)

    try:
        TTI.sent_message = await bot.bot.send_audio(
            "-1004341515592",
            audio=audio_file,
            thumbnail=thumb_file,
            title=track["title"],
            performer=track["artist"],
            disable_notification=True,
        )
    except TelegramNetworkError as e:
        print(e)
        if e.message.find("Request Entity Too Large") != -1:
            print("Request Entity Too Large")
            COLD.annihilate(video_id)
            await DM.fisting(
                video_id,
                None,
                True,
                is_work_in_progress=False,
            )

    except Exception as e:
        print(e)

    finally:
        await finalize_download(video_id, TTI)

    # inline_results = []
    # for idx, video in enumerate(search_result, start=1):
    #     v_id = video["video_id"]
    #     title = video["title"]
    #     duration = video["duration"]
    #     artist = video["artist"]

    #     if not v_id:
    #         continue

    #     card = InlineQueryResultArticle(
    #         id=v_id,
    #         title=f"{artist} — {title}",
    #         description=f"⏱ Длительность: {duration}",
    #         hide_url=True,
    #         # Текст, который отправится в чат, когда пользователь кликнет на трек
    #         input_message_content=InputTextMessageContent(
    #             link_preview_options=LinkPreviewOptions(is_disabled=True),
    #             message_text=f"{artist} — {title} [{duration}]",
    #             disable_web_page_preview=True,
    #         ),
    #         reply_markup=InlineKeyboardMarkup(
    #             inline_keyboard=[
    #                 [InlineKeyboardButton(text="⬇️", callback_data=f"dl:{v_id}:{idx}")]
    #             ]
    #         ),
    #     )
    #     inline_results.append(card)
    # await q.answer(
    #     results=inline_results,
    #     cache_time=60,
    #     is_personal=False,
    # )
