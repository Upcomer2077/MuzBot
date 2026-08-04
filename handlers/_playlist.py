import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from _logger import LOGGER
from dungeon import DM
from tools.extract_playlist_info import extract_playlist_info
from worker import PLAYLIST_QUEUE

router = Router()
_mutex = asyncio.Semaphore(1)


@router.message(Command("playlist"))
async def playlist1(message: Message, command: CommandObject):
    ANSWER = await message.answer("Загружаю...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")

    user_id = message.from_user.id

    args = command.args
    if not args:
        return ANSWER.edit_text("Отсутствует ссылка на видео")
    link = args
    LOGGER.info("Playlist")
    r = await extract_playlist_info(link)
    if not r:
        return ANSWER.edit_text("Неизвестная ошибка")
    (playlist_info, videos) = r
    # =======DANGER ZONE=========
    await _mutex.acquire()

    await DM.add_playlist_and_tracks(playlist_info, videos)

    position_assigned = await PLAYLIST_QUEUE.enqueue(
        user_id, playlist_id=playlist_info["id"], videos=videos
    )
    _mutex.release()
    # ==========================

    if not position_assigned:
        return ANSWER.edit_text("Достигнуто максимальное количество скачиваний за раз!")
    return ANSWER.edit_text(f"Загружаю...\nВаша позиция в очереди: {position_assigned}")
