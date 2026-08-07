from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import bot
from _logger import LOGGER
from action_limiter import AL
from config import (
    MAX_TRACK_DURATION_SECONDS,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from helpers.regexes import YTM_REGEX, YTM_VID_REGEX
from helpers.utils import U
from worker import TRACK_PIPELINE

router = Router()


@router.message(Command("force"))
async def force(message: Message, command: CommandObject):
    if not command.args:
        return message.answer("Отсутствует ссылка на видео")
    YTM_LINK = command.args

    if YTM_REGEX.match(YTM_LINK) is None:
        return message.answer("Некорректная ссылка")

    VIDEO_ID = YTM_VID_REGEX.search(YTM_LINK)
    if not VIDEO_ID:
        LOGGER.warn(f"Video id not recognized: {YTM_LINK}")
        return message.answer("Не удалось распознать идентификатор видео")
    # ---------------------------------

    ANSWER = await message.answer(
        "⏳ Обрабатываю запрос (это займет несколько секунд)\n"
    )
    VIDEO_ID = VIDEO_ID.group(1)
    CHAT_ID = message.chat.id

    track = await U.get_track(VIDEO_ID)
    if not track:
        return ANSWER.edit_text("Не удалось найти информацию о видео")

    if track.is_too_large:
        return ANSWER.edit_text(
            f"Превышен лимит в {int(MAX_TRACK_DURATION_SECONDS / 60)} минут или вес больше 50МБ. Скачать не выйдет"
        )

    if not AL.is_track_download_allowed(CHAT_ID):
        await ANSWER.edit_text(
            f"Разрешено загружать не более {TRACKS_PER_LIMIT} треков за {QUERY_DOWNLOAD_LIMIT_SECS} сек"
        )

    if AL.is_send_action_allowed(CHAT_ID):
        await U.send_action(CHAT_ID)

    if not track.telegram_file_id:
        _, cache = await TRACK_PIPELINE.submit(
            VIDEO_ID, track_title=track.title, artist=track.artist
        )
        if cache.file_id or cache.is_too_large:
            if cache.is_too_large:
                return ANSWER.edit_text(
                    f"Превышен лимит в {int(MAX_TRACK_DURATION_SECONDS / 60)} минут или вес больше 50МБ. Скачать не выйдет"
                )
            track = await U.get_track(VIDEO_ID, extract_info_from_ytm=False)
            if not (track and track.telegram_file_id):
                return ANSWER.edit_text("Не удалось найти информацию о видео")

        else:
            return ANSWER.edit_text(
                f"Произошла ошибка при скачивании трека {track.artist} - {track.title}"
            )

    await bot.bot.send_audio(CHAT_ID, track.telegram_file_id)
    return ANSWER.delete()
