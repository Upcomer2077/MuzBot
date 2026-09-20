from enum import Enum
from typing import Final, TypedDict

from aiogram.filters import Command
from aiogram.types import BotCommand


class _CommandSchema(TypedDict):
    backend: Command
    frontend: BotCommand


class COMSET(Enum):
    START = 0
    HELP = 1
    FORCE = 2
    PLAYLIST = 3
    SUBSCRIBE = 4
    UNSUBSCRIBE = 5
    SUBSCRIPTIONS = 6


COMMANDS: Final[dict[COMSET, _CommandSchema]] = {
    COMSET.START: {
        "backend": Command("start"),
        "frontend": BotCommand(command="start", description="🚀 Запустить бота"),
    },
    COMSET.HELP: {
        "backend": Command("help"),
        "frontend": BotCommand(
            command="help", description="❓ Инструкция по использованию"
        ),
    },
    COMSET.FORCE: {
        "backend": Command("force"),
        "frontend": BotCommand(
            command="force",
            description="⚡ Скачать по ссылке из youtube.music.com",
        ),
    },
    COMSET.PLAYLIST: {
        "backend": Command("plist"),
        "frontend": BotCommand(
            command="plist", description="⚡ Скачать плейлист по ссылке"
        ),
    },
    COMSET.SUBSCRIBE: {
        "backend": Command("sub"),
        "frontend": BotCommand(command="sub", description="🔔 Подписаться на автора"),
    },
    COMSET.UNSUBSCRIBE: {
        "backend": Command("usub"),
        "frontend": BotCommand(command="usub", description="🔕 Отписаться от автора"),
    },
    COMSET.SUBSCRIPTIONS: {
        "backend": Command("slist"),
        "frontend": BotCommand(command="slist", description="📜 Список подписок"),
    },
}
