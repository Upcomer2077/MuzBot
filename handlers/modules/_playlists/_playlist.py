from typing import Final

from aiogram import Router
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from _logger import LOGGER
from bot.commands import COMMANDS, COMSET
from config import MAX_PLAYLIST_TRACKS_REQUEST, PLAYLIST_MAX_TRACKS
from dungeon import DM
from handlers._drop_message.callbacks import DropCallback
from handlers.modules._playlists.callbacks import DownloadPlaylistCallback
from helpers.regexes import YTM_MIX_PLIST_REGEX, YTM_PLIST_REGEX, YTM_USER_PLIST_REGEX
from localization import L10N
from schemas.states import TypedState
from tools.extract_playlist_info import extract_playlist_info

router = Router()


class _PlaylistStates(StatesGroup):
    first_step = State()


@router.message(COMMANDS[COMSET.PLAYLIST]["backend"])
async def playlist(
    message: Message, command: CommandObject, state: FSMContext, i18n: I18nContext
):
    link = command.args
    if not link:
        S: Final = TypedState(state)
        await S.set_state(_PlaylistStates.first_step)
        return await message.answer(
            i18n.get(L10N["playlist"].pl_prompt_link, cancelcommand=COMSET.CANCEL.value)
        )

    await _handler(message, link, i18n)


@router.message(_PlaylistStates.first_step)
async def playlist_step_2(message: Message, state: FSMContext, i18n: I18nContext):
    link = message.text
    if link is None:
        return await message.answer(
            i18n.get(
                L10N["playlist"].pl_error_no_link, cancelcommand=COMSET.CANCEL.value
            )
        )

    await _handler(message, link, i18n)
    await state.clear()


async def _handler(message: Message, link: str, i18n: I18nContext):
    ANSWER = await message.answer(i18n.get(L10N["playlist"].pl_searching))

    _regex_res = (
        YTM_PLIST_REGEX.search(link)
        or YTM_USER_PLIST_REGEX.search(link)
        or YTM_MIX_PLIST_REGEX.search(link)
    )
    if not _regex_res:
        return await ANSWER.edit_text(
            i18n.get(L10N["playlist"].pl_error_invalid_playlist)
        )

    PLAYLIST_ID = _regex_res[0]

    slaves = await DM.playlists.summon_slaves_from_playlist(PLAYLIST_ID)
    playlist = await DM.playlists.get_playlist(PLAYLIST_ID)
    if not slaves or not playlist:
        r = await extract_playlist_info(PLAYLIST_ID)
        if not r:
            return await ANSWER.edit_text(i18n.get(L10N["playlist"].pl_error_not_found))

        (playlist_info, videos) = r
        await DM.playlists.add_playlist_and_tracks(playlist_info, videos)
        slaves = await DM.playlists.summon_slaves_from_playlist(PLAYLIST_ID)
        playlist = await DM.playlists.get_playlist(PLAYLIST_ID)

        if not (slaves and playlist):
            ANSWER.edit_text(i18n.get(L10N["playlist"].pl_error_db_failed))
            LOGGER.error(
                f"Unable to get playlist-slaves from database. pl_id: {PLAYLIST_ID}. Has slaves: {bool(slaves)}. Has playlist {bool(playlist)}"
            )
            raise Exception(
                f"Unable to get playlist-slaves from database. pl_id: {PLAYLIST_ID}"
            )

    builder = InlineKeyboardBuilder()

    if len(slaves) > MAX_PLAYLIST_TRACKS_REQUEST:
        text = (
            i18n.get(
                L10N["playlist"].pl_found_title_limited,
                artist=playlist.artist,
                title=playlist.title,
                limit=MAX_PLAYLIST_TRACKS_REQUEST,
            )
            + "\n\n"
        )
    else:
        text = (
            i18n.get(
                L10N["playlist"].pl_found_title,
                artist=playlist.artist,
                title=playlist.title,
            )
            + "\n\n"
        )

    if PLAYLIST_MAX_TRACKS and len(slaves) > PLAYLIST_MAX_TRACKS:
        text += (
            i18n.get(L10N["playlist"].pl_limit_warning, limit=PLAYLIST_MAX_TRACKS)
            + "\n\n"
        )

    and_more = 0
    for idx, video in enumerate(
        list(slaves.values())[: PLAYLIST_MAX_TRACKS or None], start=1
    ):
        title = video.title
        new_line = f"#{idx}. {title}\n"
        if len(text) + len(new_line) > 4000:
            and_more += 1
            continue
        text += new_line

    if and_more:
        text += i18n.get(L10N["playlist"].pl_and_more, count=and_more) + "\n"

    text += "\n" + i18n.get(L10N["playlist"].pl_download_prompt)

    builder.button(
        text="⬇️",
        callback_data=DownloadPlaylistCallback(playlist_id=playlist.playlist_id),
    ).button(
        text="❌",
        callback_data=DropCallback(),
    ).adjust(2, repeat=True)

    return await ANSWER.edit_text(
        text, reply_markup=builder.as_markup(), parse_mode=None
    )
