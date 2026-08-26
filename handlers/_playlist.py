from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from _logger import LOGGER
from config import MAX_PLAYLIST_TRACKS_REQUEST, PLAYLIST_MAX_TRACKS
from dungeon import DM
from helpers.regexes import YTM_MIX_PLIST_REGEX, YTM_PLIST_REGEX, YTM_USER_PLIST_REGEX
from tools.extract_playlist_info import extract_playlist_info

router = Router()


@router.message(Command("plist"))
async def playlist(message: Message, command: CommandObject):
    ANSWER = await message.answer("Ищу...")
    if not message.from_user:
        return ANSWER.edit_text("Неизвестная ошибка")

    link = command.args
    if not link:
        return ANSWER.edit_text("Отсутствует ссылка на видео")

    _regex_res = (
        YTM_PLIST_REGEX.search(link)
        or YTM_USER_PLIST_REGEX.search(link)
        or YTM_MIX_PLIST_REGEX.search(link)
    )
    if not _regex_res:
        return ANSWER.edit_text(
            "Неверный плейлист! Проверьте корректность ссылки! Доступны для скачивания только альбомы с префиксом OLAK5uy_, RD или PL"
        )

    PLAYLIST_ID = _regex_res[0]

    slaves = await DM.summon_slaves_from_playlist(PLAYLIST_ID)
    playlist = await DM.get_playlist(PLAYLIST_ID)
    if not slaves or not playlist:
        r = await extract_playlist_info(PLAYLIST_ID)
        if not r:
            return ANSWER.edit_text("404 🤷")

        (playlist_info, videos) = r
        await DM.add_playlist_and_tracks(playlist_info, videos)
        slaves = await DM.summon_slaves_from_playlist(PLAYLIST_ID)
        playlist = await DM.get_playlist(PLAYLIST_ID)

        if not (slaves and playlist):
            ANSWER.edit_text(
                "Что-то пошло не так при поиске плейлиста. Повторите попытку"
            )
            LOGGER.error(
                f"Unable to get playlist-slaves from database. pl_id: {PLAYLIST_ID}. Has slaves: {bool(slaves)}. Has playlist {bool(playlist)}"
            )
            raise Exception(
                f"Unable to get playlist-slaves from database. pl_id: {PLAYLIST_ID}"
            )

    builder = InlineKeyboardBuilder()
    text = f"Найден плейлист:\n{playlist.artist} — {playlist.title}. {'(Первые ±300 треков)' if len(slaves) > MAX_PLAYLIST_TRACKS_REQUEST else ''}\n\n"
    if PLAYLIST_MAX_TRACKS and len(slaves) > PLAYLIST_MAX_TRACKS:
        text += f"Будут скачаны первые {PLAYLIST_MAX_TRACKS} треков из плейлиста (мы работаем над этим)\n\n"

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
    text += f"И ещё {and_more} треков\n" if and_more else ""
    text += "\nСкачать?"

    builder.button(
        text="⬇️",
        callback_data=f"dlp:{playlist.playlist_id}",
    ).button(
        text="❌",
        callback_data="drop_m",
    ).adjust(2, repeat=True)

    return ANSWER.edit_text(text, reply_markup=builder.as_markup(), parse_mode=None)
