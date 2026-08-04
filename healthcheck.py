import asyncio
import sys

import requests
from aiogram.enums import ChatMemberStatus

import bot
from _logger import LOGGER
from config import CHANNEL_STORAGE_ID, DATABASE_PATH, LOKI_URL
from dungeon import DM
from type import YoutubeSearchResultDict


async def _check_loki():
    LOGGER.debug("---LOKI---")
    if LOKI_URL is None:
        LOGGER.debug("LOKI_URL is None")
    else:
        LOGGER.debug(f"LOKI_URL is {LOKI_URL}")
        ready_url = LOKI_URL.replace("/loki/api/v1/push", "/ready")
        response = await asyncio.to_thread(requests.get, ready_url, timeout=3)
        response.raise_for_status()
        if not response.text.strip() == "ready":
            raise (Exception("LOKI_URL is specified but LOKI not ready"))
    return LOGGER.debug("Loki check: pass")


async def _check_database():
    LOGGER.debug("---DATABASE---")
    LOGGER.debug(f"DB_CONTAINER_PATH: {DATABASE_PATH}")
    await DM.open_dungeon()
    res = await DM._get_slaves_count()
    LOGGER.debug(f"Slaves in dungeon count: {res}")

    count_enslaved = await DM.enslave_bulk(
        [
            YoutubeSearchResultDict(
                video_id="0",
                title="0",
                artist="0",
                duration="0",
                duration_seconds=0,
            )
        ]
    )

    if count_enslaved > 0:
        LOGGER.debug("Database check: passed")
        await DM.next_door(video_id="0")
    else:
        await DM.next_door(video_id="0")
        raise Exception("Database check: failed. I/O error. Check your dungeon!")


async def _check_channel():
    me = await bot.bot.get_me()

    member = await bot.bot.get_chat_member(chat_id=CHANNEL_STORAGE_ID, user_id=me.id)

    if member.status != ChatMemberStatus.ADMINISTRATOR:
        raise Exception(f"Bot is not administrator i {CHANNEL_STORAGE_ID} channel")

    if not member.can_post_messages:
        raise Exception(f"Bot can't post messages in {CHANNEL_STORAGE_ID} channel")


async def _check():
    try:
        LOGGER.debug("-----HEALTH CHECK-----")
        await _check_database()
        await _check_loki()
        await _check_channel()
    except Exception as e:
        LOGGER.critical(f"{e}")
        sys.exit(1)
    finally:
        await DM.next_door(video_id="0")
        await DM.close_dungeon()
        LOGGER.debug("-----HEALTH CHECK END-----")


if __name__ == "__main__":
    asyncio.run(_check())
