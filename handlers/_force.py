import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from _logger import LOGGER
from action_limiter import AL
from config import (
    MAX_TRACK_DURATION_SECONDS,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from helpers.download_utils import DU
from helpers.finalize_download import finalize_download
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from helpers.regexes import YTM_REGEX, YTM_VID_REGEX
from tools.send_action import send_action
from type import TrackState

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
    TS = TrackState()

    ANSWER = await message.answer(f"{TS.base_answer}")
    VIDEO_ID = VIDEO_ID.group(1)
    CHAT_ID = message.chat.id

    track = await DU.get_track(VIDEO_ID)
    if not track:
        return ANSWER.edit_text("Не удалось найти информацию о видео")

    TS.fill_from(track)

    # --------------
    if TS.is_work_in_progress:
        await ANSWER.edit_text(
            f"{TS.base_answer}Кто-то уже скачивает этот трек... Подождем"
        )
        for i in range(10):
            await asyncio.sleep(6)
            if AL.is_allowed_send_action(CHAT_ID):
                await send_action(CHAT_ID)

            track = await DU.get_track(VIDEO_ID, False)
            if track:
                if track.is_work_in_progress:
                    continue
                TS.fill_from(track)

            if i == 9:
                LOGGER.warn(
                    f"Awaiting work_in_progress mutex took {54} seconds or more."
                )
            break

    # ---------------
    if TS.is_too_large:
        return ANSWER.edit_text(
            f"Превышен лимит в {int(MAX_TRACK_DURATION_SECONDS / 60)} минут или вес больше 50МБ. Скачать не выйдет"
        )
    if TS.tg_file_id:
        try:
            TS.sent_audio, TS.is_cache_sent_successfully = await DU.send_cached_audio(
                CHAT_ID, TS.tg_file_id, ANSWER
            )
        except Exception as e:
            LOGGER.error(
                f"Error sending cached audio. tg file id: {TS.tg_file_id}: {e}"
            )

        finally:
            await finalize_download(VIDEO_ID, TS)

    if not TS.is_cache_sent_successfully:
        if message.from_user and not AL.is_download_allowed(message.from_user.id):
            await ANSWER.edit_text(
                f"Разрешено загружать не более {TRACKS_PER_LIMIT} треков за {QUERY_DOWNLOAD_LIMIT_SECS} сек"
            )
            await asyncio.sleep(5)
            return ANSWER.delete()

        await ANSWER.edit_text(f"{TS.base_answer}В кэше пусто... Загружаю")

        TS.cache_data = await DU.handle_cache_pull(VIDEO_ID, CHAT_ID)

        if not TS.cache_data:
            await finalize_download(VIDEO_ID, TS)
            return ANSWER.edit_text(
                "Что-то пошло не так при скачивании трека... Повторите попытку"
            )

        await ANSWER.edit_text(f"{TS.base_answer}Загрузил. Отправляю...")

        (
            audio_file,
            thumb_file,
        ) = prepare_audio_file_to_send(TS.cache_data)

        try:
            LOGGER.info(f"Uploading audio {VIDEO_ID}")
            TS.sent_audio = await DU.send_new_audio(
                message,
                CHAT_ID,
                audio_file,
                thumb_file,
                TS.title,
                TS.artist,
            )
            LOGGER.info(f"Uploaded successfully {VIDEO_ID}")

        except TelegramNetworkError as e:
            if e.message.find("Request Entity Too Large") != -1:
                TS.is_too_large = True
                await finalize_download(VIDEO_ID, TS)

                return ANSWER.edit_text("Размер файла превышает 50М. Скачать не выйдет")
            LOGGER.error(f"Network error: VID: {VIDEO_ID}: {e}")

            return ANSWER.edit_text("Ошибка сети. Повторите попытку")

        except Exception as e:
            LOGGER.error(f"Error sending audio. VID:{VIDEO_ID}: {e}")
            return ANSWER.edit_text(
                "Что-то пошло не так при выгрузке трека... Повторите попытку"
            )

        finally:
            await finalize_download(VIDEO_ID, TS)

    await ANSWER.delete()
