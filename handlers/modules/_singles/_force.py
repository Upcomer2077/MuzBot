from typing import Final

from aiogram import Router
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_i18n import I18nContext

import bot
from _logger import LOGGER
from action_limiter import AL
from bot.commands import COMMANDS, COMSET
from config import (
    MAX_TRACK_DURATION_SECONDS,
    QUERY_DOWNLOAD_LIMIT_SECS,
    TRACKS_PER_LIMIT,
)
from helpers.regexes import YTM_REGEX, YTM_VID_REGEX
from helpers.utils import U
from localization import L10N
from schemas.states import TypedState
from worker import TRACK_PIPELINE
from worker.priorities import DownloadTaskPriorities

router = Router()


class _ForceState(StatesGroup):
    first_enter_link = State()


@router.message(COMMANDS[COMSET.FORCE]["backend"])
async def force(
    message: Message, command: CommandObject, state: FSMContext, i18n: I18nContext
):
    if not command.args:
        S: Final = TypedState(state)
        await S.set_state(_ForceState.first_enter_link)
        return await message.answer(
            i18n.get(
                L10N["single"].force_prompt_link, cancelcommand=COMSET.CANCEL.value
            )
        )

    YTM_LINK = command.args

    if YTM_REGEX.match(YTM_LINK) is None:
        return await message.answer(i18n.get(L10N["single"].force_invalid_link))

    return await _handler(message, YTM_LINK, i18n)


@router.message(_ForceState.first_enter_link)
async def force_step_2(message: Message, state: FSMContext, i18n: I18nContext):
    YTM_LINK = message.text

    if YTM_LINK is None or YTM_REGEX.match(YTM_LINK) is None:
        return await message.answer(
            i18n.get(
                L10N["single"].force_invalid_link_retry,
                cancelcommand=COMSET.CANCEL.value,
            )
        )

    await _handler(message, YTM_LINK, i18n)
    return await state.clear()


# ======================================================================


async def _handler(message: Message, ytm_link: str, i18n: I18nContext):
    VIDEO_ID = YTM_VID_REGEX.search(ytm_link)
    if not VIDEO_ID:
        LOGGER.warning(f"Video id not recognized: {ytm_link}")
        return await message.answer(i18n.get(L10N["single"].force_id_not_recognized))
    ANSWER = await message.answer(i18n.get(L10N["single"].download_processing))
    VIDEO_ID = VIDEO_ID.group(1)
    CHAT_ID = message.chat.id

    track = await U.get_track(VIDEO_ID)
    if not track:
        return await ANSWER.edit_text(i18n.get(L10N["single"].download_info_not_found))

    if track.is_too_large:
        return await ANSWER.edit_text(
            i18n.get(
                L10N["single"].download_limit_size_duration,
                limit_min=int(MAX_TRACK_DURATION_SECONDS / 60),
            )
        )

    if not AL.is_track_download_allowed(CHAT_ID):
        return await ANSWER.edit_text(
            i18n.get(
                L10N["single"].download_limit_rate,
                limit_tracks=TRACKS_PER_LIMIT,
                limit_secs=QUERY_DOWNLOAD_LIMIT_SECS,
            )
        )

    if AL.is_send_action_allowed(CHAT_ID):
        await U.send_action(CHAT_ID)

    if not track.telegram_file_id:
        _, cache = await TRACK_PIPELINE.submit(
            VIDEO_ID,
            track_title=track.title,
            artist=track.artist,
            priority=DownloadTaskPriorities.SINGLE,
        )
        if cache.file_id or cache.is_too_large:
            if cache.is_too_large:
                return await ANSWER.edit_text(
                    i18n.get(
                        L10N["single"].download_limit_size_duration,
                        limit_min=int(MAX_TRACK_DURATION_SECONDS / 60),
                    )
                )
            track = await U.get_track(VIDEO_ID, extract_info_from_ytm=False)
            if not (track and track.telegram_file_id):
                return await ANSWER.edit_text(
                    i18n.get(L10N["single"].download_info_not_found)
                )

        else:
            return await ANSWER.edit_text(
                i18n.get(
                    L10N["single"].download_error_failed,
                    artist=track.artist,
                    title=track.title,
                )
            )

    await bot.bot.send_audio(CHAT_ID, track.telegram_file_id)
    return await ANSWER.delete()
