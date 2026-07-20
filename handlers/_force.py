import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from action_limiter import AL
from config import MAX_TRACK_DURATION_SECONDS, YTM_REGEX, YTM_VID_REGEX
from dungeon import DM
from helpers.finalize_download import finalize_download
from helpers.prepare_audio_file_to_send import prepare_audio_file_to_send
from helpers.pull_data_from_cache import pull_data_from_cache
from overlord import COLD
from tools.download import download
from tools.extract_info import extract_info
from tools.send_audio import answer_audio, answer_audio_cached
from type import TempTrackStatusInfo

router = Router()


@router.message(Command("force"))
async def force(message: Message, command: CommandObject):
    if not command.args:
        return message.answer("Отсутствует ссылка на видео")
    link = command.args

    if YTM_REGEX.match(link) is None:
        return message.answer("Некорректная ссылка")

    video_id = YTM_VID_REGEX.search(link)
    if not video_id:
        return message.answer("Не удалось распознать идентификатор видео")
    # ---------------------------------
    TTI = TempTrackStatusInfo()
    answer = await message.answer(f"{TTI.base_answer}")
    video_id = video_id.group(1)
    track = await DM.summon_one(video_id)

    if track:
        TTI.title = track.title
        TTI.artist = track.artist
        TTI.tg_file_id = track.telegram_file_id
        TTI.track_duration = track.track_duration
        TTI.is_too_large = track.is_too_large
        TTI.is_work_in_progress = track.is_work_in_progress

        # --------------
    if TTI.is_work_in_progress:
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

            break

    # ---------------
    if TTI.is_too_large:
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
            print(e)
        finally:
            await finalize_download(video_id, TTI)

    if not TTI.cache_sent_successfully:
        await AL.send_action(message.chat.id)

        res = await extract_info(video_id)

        if not res:
            return message.answer("Не удалось найти информацию о видео")

        TTI.title, TTI.artist, TTI.track_duration = (
            res["title"],
            res["artist"],
            res["duration_seconds"],
        )

        await DM.enslave_bulk([res])

        if TTI.track_duration > MAX_TRACK_DURATION_SECONDS:
            await DM.fisting(video_id, is_too_large=True)
            return answer.edit_text(
                f"Длительность видео превышает {int(MAX_TRACK_DURATION_SECONDS / 60)} минут. Скачать не выйдет"
            )

        await answer.edit_text(f"{TTI.base_answer}В кэше пусто... Загружаю")
        await DM.fisting(video_id, is_work_in_progress=True)
        TTI.cache_data = await pull_data_from_cache(video_id, download)

        if not TTI.cache_data:
            await finalize_download(video_id, TTI)
            return answer.edit_text(
                "Что-то пошло не так при скачивании трека... Повторите попытку"
            )

        await answer.edit_text(f"{TTI.base_answer}Загрузил. Отправляю...")

        (
            audio_file,
            thumb_file,
        ) = prepare_audio_file_to_send(TTI.cache_data)

        await AL.send_action(message.chat.id)
        try:
            TTI.sent_message = await answer_audio(
                message,
                audio_file=audio_file,
                thumb_file=thumb_file,
                title=TTI.title,
                artist=TTI.artist,
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

                return answer.edit_text("Размер файла превышает 50М. Скачать не выйдет")
            return answer.edit_text("Ошибка сети. Повторите попытку")

        except Exception as e:
            print(e)
            return answer.edit_text(
                "Что-то пошло не так при выгрузке трека... Повторите попытку"
            )

        finally:
            await finalize_download(video_id, TTI)

    await answer.delete()
