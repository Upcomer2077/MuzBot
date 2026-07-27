import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import CallbackQuery, Message

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
from tools.send_action import send_action
from type import DownloadCallback, TrackState

router = Router()


@router.callback_query(DownloadCallback.filter())
async def handle_download(callback: CallbackQuery, callback_data: DownloadCallback):
    await callback.answer()  # Reset button timer

    VIDEO_ID = callback_data.video_id
    IDX = callback_data.idx

    if len(VIDEO_ID) == 0:
        LOGGER.error("Video_id param len is 0. Check callback data")
        return callback.answer(
            f"Что-то пошло не так при загрузке трека #{IDX}... Повторите попытку"
        )
    # --------------
    TS = TrackState()

    ANCHOR_MESSAGE = callback.message or await DU.send_anchor_message(
        callback.from_user.id
    )
    ANSWER = await ANCHOR_MESSAGE.answer(f"{TS.base_answer}")
    IS_FROM_INLINE_QUERY = callback.message is None
    CHAT_ID = ANCHOR_MESSAGE.chat.id

    if IS_FROM_INLINE_QUERY and isinstance(ANCHOR_MESSAGE, Message):
        await ANCHOR_MESSAGE.delete()

    track = await DU.get_track(VIDEO_ID)
    if not track:
        return ANCHOR_MESSAGE.answer("Не удалось найти информацию о видео")

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
                LOGGER.warn("Awaiting work_in_progress mutex took 54 seconds or more.")
            break

    if TS.is_too_large:
        return ANSWER.edit_text(
            f"Превышен лимит в {int(MAX_TRACK_DURATION_SECONDS / 60)} минут или вес больше 50МБ. Скачать не выйдет"
        )

    if TS.tg_file_id:
        try:
            TS.sent_audio, TS.is_cache_sent_successfully = await DU.send_cached_audio(
                CHAT_ID, TS.tg_file_id, ANCHOR_MESSAGE
            )
        except Exception as e:
            LOGGER.error(f"Error sending cached audio. tg file id: {TS.tg_file_id}:{e}")
        finally:
            await finalize_download(VIDEO_ID, TS)
    # ----------------
    if not TS.is_cache_sent_successfully:
        if not AL.is_download_allowed(callback.from_user.id):
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
                f"Что-то пошло не так при скачивании трека #{IDX}... Повторите попытку"
            )

        await ANSWER.edit_text(f"{TS.base_answer}Загрузил. Отправляю...")

        (
            audio_file,
            thumb_file,
        ) = prepare_audio_file_to_send(TS.cache_data)

        try:
            LOGGER.info(f"Uploading audio {VIDEO_ID}")
            TS.sent_audio = await DU.send_new_audio(
                ANCHOR_MESSAGE,
                CHAT_ID,
                audio_file,
                thumb_file,
                TS.title,
                TS.artist,
            )
            LOGGER.info(f"Uploaded successfully: {VIDEO_ID}")

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
                f"Что-то пошло не так при выгрузке трека #{IDX}... Повторите попытку"
            )
        finally:
            await finalize_download(VIDEO_ID, TS)

    await ANSWER.delete()
