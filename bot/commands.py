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
    LANG = "language"
    FORCE = "force"
    PLAYLIST = "fplist"
    SUBSCRIBE = "sub"
    UNSUBSCRIBE = "usub"
    SUBSCRIPTIONS = "slist"
    CANCEL = "cancel"
    CATALOG = "cat"
    ALBUMS = "albums"


COMMANDS: Final[dict[COMSET, _CommandSchema]] = {
    COMSET.START: {
        "backend": Command(COMSET.START.value),
        "frontend": BotCommand(command=COMSET.START.value, description="🚀 Start bot"),
    },
    COMSET.LANG: {
        "backend": Command(COMSET.LANG.value),
        "frontend": BotCommand(
            command=COMSET.LANG.value, description="🌐 Choose language"
        ),
    },
    COMSET.HELP: {
        "backend": Command(COMSET.HELP.value),
        "frontend": BotCommand(
            command=COMSET.HELP.value, description="❓ Usage instructions"
        ),
    },
    COMSET.FORCE: {
        "backend": Command(COMSET.FORCE.value),
        "frontend": BotCommand(
            command=COMSET.FORCE.value,
            description="⚡ Download via link from youtube.music.com",
        ),
    },
    COMSET.PLAYLIST: {
        "backend": Command(COMSET.PLAYLIST.value),
        "frontend": BotCommand(
            command=COMSET.PLAYLIST.value, description="⚡ Download playlist via link"
        ),
    },
    COMSET.SUBSCRIBE: {
        "backend": Command(COMSET.SUBSCRIBE.value),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIBE.value, description="🔔 Subscribe to the author"
        ),
    },
    COMSET.UNSUBSCRIBE: {
        "backend": Command(COMSET.UNSUBSCRIBE.value),
        "frontend": BotCommand(
            command=COMSET.UNSUBSCRIBE.value,
            description="🔕 Unsubscribe from the author",
        ),
    },
    COMSET.SUBSCRIPTIONS: {
        "backend": Command(COMSET.SUBSCRIPTIONS.value),
        "frontend": BotCommand(
            command=COMSET.SUBSCRIPTIONS.value, description="📜 Subscription list"
        ),
    },
    COMSET.CATALOG: {
        "backend": Command(COMSET.CATALOG.value),
        "frontend": BotCommand(
            command=COMSET.CATALOG.value, description="💿 Artist singles"
        ),
    },
    COMSET.ALBUMS: {
        "backend": Command(COMSET.ALBUMS.value),
        "frontend": BotCommand(
            command=COMSET.ALBUMS.value, description="💿 Artist albums"
        ),
    },
    COMSET.CANCEL: {
        "backend": Command(COMSET.CANCEL.value),
        "frontend": BotCommand(command=COMSET.CANCEL.value, description="❌ Cancel"),
    },
}
