from enum import Enum
from typing import Final, TypedDict

from aiogram.filters import Command
from aiogram.types import BotCommand


class _CommandSchema(TypedDict):
    backend: Command
    frontend: BotCommand


class COMSET(Enum):
    START = "start"
    HELP = "help"
    FORCE = "force"
    PLAYLIST = "plist"
    SUBSCRIBE = "sub"
    UNSUBSCRIBE = "usub"
    SUBSCRIPTIONS = "slist"
    CANCEL = "cancel"


COMMANDS: Final[dict[COMSET, _CommandSchema]] = {
    COMSET.START: {
        "backend": Command(COMSET.START.value),
        "frontend": BotCommand(
            command=COMSET.START.value, description="🚀 Запустить бота"
        ),
    },
    COMSET.HELP: {
        "backend": Command(COMSET.HELP.value),
        "frontend": BotCommand(
            command=COMSET.HELP.value, description="❓ Инструкция по использованию"
        ),
    },
    COMSET.FORCE: {
        "backend": Command(COMSET.FORCE.value),
        "frontend": BotCommand(
            command=COMSET.FORCE.value,
            description="⚡ Скачать по ссылке из youtube.music.com",
        ),
    },
    COMSET.PLAYLIST: {
        "backend": Command(COMSET.PLAYLIST.value),
        "frontend": BotCommand(
            command=COMSET.PLAYLIST.value, description="⚡ Скачать плейлист по ссылке"
        ),
    },
    COMSET.SUBSCRIBE: {
        "backend": Command(COMSET.SUBSCRIBE.value),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIBE.value, description="🔔 Подписаться на автора"
        ),
    },
    COMSET.UNSUBSCRIBE: {
        "backend": Command(COMSET.UNSUBSCRIBE.value),
        "frontend": BotCommand(
            command=COMSET.UNSUBSCRIBE.value, description="🔕 Отписаться от автора"
        ),
    },
    COMSET.SUBSCRIPTIONS: {
        "backend": Command(COMSET.SUBSCRIPTIONS.value),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIPTIONS.value, description="📜 Список подписок"
        ),
    },
    COMSET.CANCEL: {
        "backend": Command(COMSET.CANCEL.value),
        "frontend": BotCommand(command=COMSET.CANCEL.value, description="❌ Отменить"),
    },
}
