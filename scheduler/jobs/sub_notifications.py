import asyncio
from collections.abc import Coroutine, Sequence
from random import uniform
from typing import Any

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import LinkPreviewOptions
from aiogram.utils.media_group import MediaGroupBuilder, MediaType

import bot
from _logger import LOGGER
from dungeon import DM
from schemas.dicts.artist import ArtistInfoDict
from schemas.enums.priorities import DownloadTaskPriorities
from schemas.tuples.worker import DownloadResult
from tools.extract_artist_discography import extract_artist_discography
from tools.extract_playlist_info import extract_playlist_info
from tools.YTMusic_client import YT
from worker import TRACK_PIPELINE


def _get_last(new_info: ArtistInfoDict):
    albums = None if not new_info["albums"] else new_info["albums"]["results"]
    singles = None if not new_info["singles"] else new_info["singles"]["results"]

    last_single_id = None if not singles else singles[0]["browseId"]
    last_album_id = None if not albums else albums[0]["browseId"]
    return last_single_id, last_album_id


async def job():
    LOGGER.info("Starting notification/subs job")
    async for batch in DM.get_subscripted_authors():
        for author in batch:
            total_media_groups: list[Sequence[MediaType]] = []
            new_info = await extract_artist_discography(author["performer_id"])

            await asyncio.sleep(uniform(1.0, 3.0))
            
            fresh_single_browse_id, fresh_album_browse_id = _get_last(new_info)

            if (not fresh_album_browse_id) and (not fresh_single_browse_id):
                continue

            local_performer_info = await DM.get_performer_info(author["performer_id"])
            if not local_performer_info:
                LOGGER.error(f"No info about performer {author['performer_id']}")
                continue

            if (
                fresh_album_browse_id == local_performer_info.last_album_id
                and fresh_single_browse_id == local_performer_info.last_single_id
            ):
                continue

            if (
                fresh_album_browse_id
                and fresh_album_browse_id != local_performer_info.last_album_id
            ):
                status = await _set_tasks(fresh_album_browse_id)
                if status:
                    tasks, album_id = status
                    _ = await asyncio.gather(*tasks, return_exceptions=False)
                    media_groups = await _form_media_groups(album_id)
                    if media_groups:
                        total_media_groups.extend(media_groups)
            # =========

            if (
                fresh_single_browse_id
                and fresh_single_browse_id != local_performer_info.last_single_id
            ):
                status = await _set_tasks(fresh_single_browse_id)
                if status:
                    tasks, album_id = status
                    _ = await asyncio.gather(*tasks, return_exceptions=False)
                    media_groups = await _form_media_groups(album_id)
                    if media_groups:
                        total_media_groups.extend(media_groups)

            res = await DM.get_tg_users_with_subs([author["performer_id"]])

            subscribers: list[int] = []

            for rr in res:
                subscribers.append(rr["tg_user_id"])

            if not len(subscribers) or not len(total_media_groups):
                continue

            await DM.set_performer_last_release(
                author["performer_id"],
                performer_name=new_info["name"],
                last_single_id=fresh_single_browse_id,
                last_album_id=fresh_album_browse_id,
            )

            for u in subscribers:
                try:
                    await asyncio.sleep(uniform(1.0, 3.0))
                    await bot.bot.send_message(
                        u,
                        f'Новинка у <a href="https://music.youtube.com/browse/{author["performer_id"]}">{new_info["name"]}</a>!',
                        parse_mode=ParseMode.HTML,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
                    for mg in total_media_groups:
                        await bot.bot.send_media_group(u, list(mg))
                        await asyncio.sleep(1)
                except TelegramForbiddenError:
                    await DM.toggle_user_subscriptions(u, True)
                    LOGGER.debug("Bot blocked by user")
                    continue

    LOGGER.info("Notification/subs job: done")




async def _form_media_groups(album_id: str):
    tracks_info = await DM.summon_slaves_from_playlist(album_id)

    if not tracks_info:
        LOGGER.error(f"Can not find info about playlist {album_id}.")
        return None

    v_ids: list[str] = []

    mg_builder = MediaGroupBuilder()
    media_group_cached: list[Sequence[MediaType]] = []

    group_count = 0
    for tc in tracks_info.values():
        if tc.is_too_large:
            continue
        if tc.telegram_file_id:
            mg_builder.add_audio(media=tc.telegram_file_id)
            group_count += 1

            v_ids.append(tc.telegram_file_id)

        if group_count >= 10:
            media_group_cached.append(mg_builder.build())
            mg_builder = MediaGroupBuilder()
            group_count = 0
    media_group_cached.append(mg_builder.build())

    return media_group_cached


async def _set_tasks(fresh_id: str):
    _tasks: list[Coroutine[Any, Any, tuple[str, DownloadResult]]] = []
    album_info = await asyncio.to_thread(YT.get_album, fresh_id)
    album_id: str = album_info["audioPlaylistId"]
    res = await extract_playlist_info(album_id)
    if not res:
        LOGGER.error(f"No info about playlist {album_id}")
        return None

    (playlist_info, videos) = res
    await DM.add_playlist_and_tracks(playlist_info, videos)
    tracks_info = await DM.summon_slaves_from_playlist(album_id)
    if not tracks_info:
        LOGGER.error(f"Summoning slaves failed on album {album_id}")
        return None

    for v in list(tracks_info.values()):
        if v.telegram_file_id is None and not v.is_too_large:
            t = TRACK_PIPELINE.submit(
                v.video_id,
                track_title=v.title,
                artist=v.artist,
                priority=DownloadTaskPriorities.NOTIFICATION,
            )
            _tasks.append(t)
    return (_tasks, album_id)
