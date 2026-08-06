import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery

import bot
from _logger import LOGGER
from type import DownloadPlaylistCallback
from worker import PLAYLIST_QUEUE

router = Router()
_mutex = asyncio.Semaphore(1)


@router.callback_query(DownloadPlaylistCallback.filter())
async def handle_playlist_download(
    callback: CallbackQuery, callback_data: DownloadPlaylistCallback
):
    await callback.answer("Загружаю... Это займет время.")

    USER_ID = callback.from_user.id
    PLAYLIST_ID = callback_data.playlist_id

    if len(PLAYLIST_ID) == 0:
        LOGGER.error("Video_id param len is 0. Check callback data")
        return callback.answer(
            "Что-то пошло не так при загрузке плейлиста... Повторите попытку"
        )
    # =======DANGER ZONE=========

    await _mutex.acquire()

    position_assigned = await PLAYLIST_QUEUE.enqueue(USER_ID, playlist_id=PLAYLIST_ID)
    _mutex.release()
    # ==========================

    if not position_assigned:
        m = await bot.bot.send_message(
            USER_ID, "Достигнуто максимальное количество скачиваний за раз!"
        )
        await asyncio.sleep(5)
        return m.delete()
    m = await bot.bot.send_message(
        USER_ID, f"Загружаю...\nВаша позиция в очереди: {position_assigned}"
    )
    await asyncio.sleep(120)
    return m.delete()
