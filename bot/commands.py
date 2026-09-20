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


COMMANDS: Final[dict[COMSET, _CommandSchema]] = {
    COMSET.START: {
        "backend": Command("start"),
        "frontend": BotCommand(
            command=COMSET.START.value, description="🚀 Запустить бота"
        ),
    },
    COMSET.HELP: {
        "backend": Command("help"),
        "frontend": BotCommand(
            command=COMSET.HELP.value, description="❓ Инструкция по использованию"
        ),
    },
    COMSET.FORCE: {
        "backend": Command("force"),
        "frontend": BotCommand(
            command=COMSET.FORCE.value,
            description="⚡ Скачать по ссылке из youtube.music.com",
        ),
    },
    COMSET.PLAYLIST: {
        "backend": Command("plist"),
        "frontend": BotCommand(
            command=COMSET.PLAYLIST.value, description="⚡ Скачать плейлист по ссылке"
        ),
    },
    COMSET.SUBSCRIBE: {
        "backend": Command("sub"),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIBE.value, description="🔔 Подписаться на автора"
        ),
    },
    COMSET.UNSUBSCRIBE: {
        "backend": Command("usub"),
        "frontend": BotCommand(
            command=COMSET.UNSUBSCRIBE.value, description="🔕 Отписаться от автора"
        ),
    },
    COMSET.SUBSCRIPTIONS: {
        "backend": Command("slist"),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIPTIONS.value, description="📜 Список подписок"
        ),
    },
}
