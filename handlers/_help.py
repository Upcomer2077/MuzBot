from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram_i18n import I18nContext

import bot
from bot.commands import COMMANDS, COMSET
from localization import L10N

router = Router()


@router.message(COMMANDS[COMSET.HELP]["backend"])
async def help(message: Message, command: CommandObject, i18n: I18nContext):
    ARGS: Final = command.args
    if not ARGS:
        bot_info = await bot.Bot.get_me(bot.bot)
        text = i18n.get(
            L10N["help"].help_full,
            botname=bot_info.username or "bot_username",
            helpcommand=COMSET.HELP.value,
        )

        return message.answer(text, parse_mode=ParseMode.MARKDOWN)

    if ARGS.strip().find(COMSET.START.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_start, com=COMSET.START.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.HELP.value) != -1:
        return message.answer(i18n.get(L10N["help"].help_help))

    if ARGS.strip().find(COMSET.FORCE.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_force, com=COMSET.FORCE.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.PLAYLIST.value) != -1:
        return message.answer(
            i18n.get(
                L10N["help"].help_playlist,
                com=COMSET.PLAYLIST.value,
                comForce=COMSET.FORCE.value,
            ),
            parse_mode=ParseMode.MARKDOWN,
        )

    # MUST BE EARLIER THAN SUB
    if ARGS.strip().find(COMSET.UNSUBSCRIBE.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_unsubscribe, com=COMSET.UNSUBSCRIBE.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.SUBSCRIBE.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_subscribe, com=COMSET.SUBSCRIBE.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.SUBSCRIPTIONS.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_subscriptions, com=COMSET.SUBSCRIPTIONS.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.ALBUMS.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_albums, com=COMSET.ALBUMS.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.CATALOG.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_catalog, com=COMSET.CATALOG.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.CANCEL.value) != -1:
        return message.answer(
            i18n.get(L10N["help"].help_cancel, com=COMSET.CANCEL.value),
            parse_mode=ParseMode.MARKDOWN,
        )

    return message.answer(i18n.get(L10N["help"].help_unknown_arg, args=ARGS))
