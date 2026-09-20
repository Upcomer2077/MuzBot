from typing import Final

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.types import Message

import bot
from bot.commands import COMMANDS, COMSET

router = Router()


@router.message(COMMANDS[COMSET.HELP]["backend"])
async def help(message: Message, command: CommandObject):
    ARGS: Final = command.args
    if not ARGS:
        bot_info = await bot.Bot.get_me(bot.bot)
        text = (
            ""
            "Введите запрос для поиска трека.\n"
            "Если трек не найден - попробуйте ввести более точный запрос.\n"
            "Поиск идет по базе music.youtube.com (и только)"
            f"\nДоступен inline-режим. Напишите в любом чате @{bot_info.username or 'username_бота'} *<трек>*"
            "\n\nДоступна возможность подписаться на исполнителя. При подписке бот будет автоматически отправлять новые релизы в чат."
            "\nНекоторые команды могут вводиться как с аргументами, так и самостоятельно."
            f"\nЧтобы узнать подробнее о работе команд напишите:\n/{COMSET.HELP.value} *<команда>*"
        )

        return message.answer(text, parse_mode=ParseMode.MARKDOWN)

    if ARGS.strip().find(COMSET.START.value) != -1:
        return message.answer(
            f"*{COMSET.START.value}*: базовая команда для запуска бота. Если бот был заблокирован, при повторном запуске размораживает подписки.\nВ ручном вызове нет необходимости",
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.HELP.value) != -1:
        return message.answer("А что не ясно?")

    if ARGS.strip().find(COMSET.FORCE.value) != -1:
        return message.answer(
            f"*{COMSET.FORCE.value}*: команда для непосредственного скачивания трека по ссылке из music.youtube.com.\n"
            f"Пример: /{COMSET.FORCE.value} https://music.youtube.com/watch?v=YCi7qXeA\\_vM.\nТак же можно написать команду и отправить ссылку отдельно. \n"
            "Удобно, если трек уже включен в ютуб музыке или по каким-либо причинам не может быть найден через интерфейс бота."
            "\n*Важно!*: треки скачиваются только с ресурса music.youtube.com. Другие ссылки будут отклонены.",
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.PLAYLIST.value) != -1:
        return message.answer(
            f"*{COMSET.PLAYLIST.value}*: команда для скачивания плейлиста по ссылке. Аналогична команде /{COMSET.FORCE.value}, но для плейлистов. Так же можно написать команду и отправить ссылку отдельно.\n"
            f"Пример: /{COMSET.PLAYLIST.value} music.youtube.com/playlist?list=OLAK5uy\\_kodfrWJRKHZNTPRTIx8NWqcvYhNeZnqnA ",
            parse_mode=ParseMode.MARKDOWN,
        )

    # MUST BE EARLIER THAN SUB
    if ARGS.strip().find(COMSET.UNSUBSCRIBE.value) != -1:
        return message.answer(
            f"*{COMSET.UNSUBSCRIBE.value}*: удаляет подписку на исполнителя. Так же можно написать команду и отправить исполнителя отдельно.\n"
            f"Пример: /{COMSET.UNSUBSCRIBE.value} instasasalka",
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.SUBSCRIBE.value) != -1:
        return message.answer(
            f"*{COMSET.SUBSCRIBE.value}*: позволяет подписаться на исполнителя. Так же можно написать команду и отправить исполнителя отдельно.\nКаждые несколько дней бот проверяет релизы исполнителей и при появлении новых отправляет их в чат\n"
            f"Пример: /{COMSET.SUBSCRIBE.value} [OXVGEN](https://music.youtube.com/@oxvgen9)",
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.SUBSCRIPTIONS.value) != -1:
        return message.answer(
            f"*{COMSET.SUBSCRIPTIONS.value}*: показывает все ваши подписки. Может использоваться как самостоятельная команда.\n"
            f"Пример: /{COMSET.SUBSCRIPTIONS.value} arc (покажет все подписки, которые включают слово 'arc')",
            parse_mode=ParseMode.MARKDOWN,
        )

    if ARGS.strip().find(COMSET.CANCEL.value) != -1:
        return message.answer(
            f"*{COMSET.CANCEL.value}*: отменяет действия. Используется там, где команды вводятся в несколько этапов",
            parse_mode=ParseMode.MARKDOWN,
        )

    return message.answer(f"Неизвестный аргумент: {ARGS}")
