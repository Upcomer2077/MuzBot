import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import CallbackQuery, Message

import bot
from action_limiter import AL
from config import (
    LOGGER,
    MAX_TRACK_DURATION_SECONDS,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from dungeon import DM
from helpers.finalize_download import finalize_download
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from helpers.pull_data_from_cache import pull_data_from_cache
from tools.download import download
from tools.send_audio import answer_audio, answer_audio_cached
from type import TempTrackStatusInfo

router = Router()


@router.callback_query(F.data.startswith("dl:"))
async def handle_download(callback: CallbackQuery):
    IS_FROM_INLINE_QUERY = callback.message is None

    if not callback.data:
        LOGGER.critical("Callback data not found!!!")
        return callback.answer("Что-то пошло не так... Повторите попытку")
    await callback.answer()

    cbd = callback.data

    video_id = cbd.split(":")[1]
    idx = cbd.split(":")[2]

    if len(video_id) == 0:
        LOGGER.error("Video_id param len is 0")
        return callback.answer(
            f"Что-то пошло не так при загрузке трека #{idx}... Повторите попытку"
        )
    # --------------
    TTI = TempTrackStatusInfo()

    message = callback.message or await bot.bot.send_message(
        callback.from_user.id,
        "||Это системное сообщение, оно исчезнет после загрузки||",
        parse_mode="MarkdownV2",
    )
    answer = await message.answer(f"{TTI.base_answer}")
    track = await DM.summon_one(video_id)

    if track:
        TTI.fill_from(track)

    # --------------
    if TTI.is_work_in_progress:
        await answer.edit_text(
            f"{TTI.base_answer}Кто-то уже скачивает этот трек... Подождем"
        )
        for i in range(10):
            await asyncio.sleep(6)
            await AL.send_action(message.chat.id)

            track = await DM.summon_one(video_id)
            if track:
                if track.is_work_in_progress:
                    continue
                TTI.is_work_in_progress = track.is_work_in_progress
                TTI.is_too_large = track.is_too_large
                TTI.tg_file_id = track.telegram_file_id
            if i == 9:
                LOGGER.warn(
                    f"Awaiting work_in_progress mutex took {54} seconds or more."
                )
            break

    if TTI.is_too_large:
        if IS_FROM_INLINE_QUERY and isinstance(message, Message):
            await message.delete()
        return answer.edit_text(
            f"Длительность видео превышает {int(MAX_TRACK_DURATION_SECONDS / 60)} минут. Скачать не выйдет"
        )

    if TTI.tg_file_id:
        try:
            await answer.edit_text(f"{TTI.base_answer}Попадание в кэш! Отправляю...")
            await AL.send_action(message.chat.id)

            TTI.sent_message = await answer_audio_cached(
                message, audio_file=TTI.tg_file_id
            )
            TTI.cache_sent_successfully = True
        except Exception as e:
            LOGGER.error(
                f"Error sending cached audio. tg file id: {TTI.tg_file_id}:{e}"
            )
        finally:
            if IS_FROM_INLINE_QUERY and isinstance(message, Message):
                await message.delete()
            await finalize_download(video_id, TTI)
    # ----------------
    if not TTI.cache_sent_successfully:
        if not AL.is_download_allowed(callback.from_user.id):
            await answer.edit_text(
                f"Разрешено загружать не более {TRACKS_PER_LIMIT} треков за {QUERY_DOWNLOAD_LIMIT_SECS} сек"
            )
            await asyncio.sleep(5)
            return answer.delete()

        await answer.edit_text(f"{TTI.base_answer}В кэше пусто... Загружаю")
        await DM.fisting(video_id, is_work_in_progress=True)
        await AL.send_action(message.chat.id)

        TTI.cache_data = await pull_data_from_cache(video_id, download)

        if not TTI.cache_data:
            await finalize_download(video_id, TTI)
            if IS_FROM_INLINE_QUERY and isinstance(message, Message):
                await message.delete()
            return answer.edit_text(
                f"Что-то пошло не так при скачивании трека #{idx}... Повторите попытку"
            )

        await answer.edit_text(f"{TTI.base_answer}Загрузил. Отправляю...")

        (
            audio_file,
            thumb_file,
        ) = prepare_audio_file_to_send(TTI.cache_data)
        await AL.send_action(message.chat.id)
        try:
            LOGGER.info(f"Uploading audio {video_id}")
            TTI.sent_message = await answer_audio(
                message,
                audio_file=audio_file,
                thumb_file=thumb_file,
                title=TTI.title,
                artist=TTI.artist,
            )
            LOGGER.info(f"Uploaded successfully {video_id}")

        except TelegramNetworkError as e:
            if e.message.find("Request Entity Too Large") != -1:
                TTI.is_too_large = True
                await finalize_download(video_id, TTI)

                return answer.edit_text("Размер файла превышает 50М. Скачать не выйдет")
            LOGGER.error(f"Network error: VID: {video_id}: {e}")

            return answer.edit_text("Ошибка сети. Повторите попытку")

        except Exception as e:
            LOGGER.error(f"Error sending audio. VID:{video_id}: {e}")
            return answer.edit_text(
                f"Что-то пошло не так при выгрузке трека #{idx}... Повторите попытку"
            )
        finally:
            if IS_FROM_INLINE_QUERY and isinstance(message, Message):
                await message.delete()
            await finalize_download(video_id, TTI)

    await answer.delete()
