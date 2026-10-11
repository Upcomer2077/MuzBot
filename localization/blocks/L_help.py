from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _HelpBlock:
    help_full: Literal["help_full"] = "help_full"
    help_start: Literal["help_start"] = "help_start"
    help_help: Literal["help_help"] = "help_help"
    help_force: Literal["help_force"] = "help_force"
    help_playlist: Literal["help_playlist"] = "help_playlist"
    help_unsubscribe: Literal["help_unsubscribe"] = "help_unsubscribe"
    help_subscribe: Literal["help_subscribe"] = "help_subscribe"
    help_subscriptions: Literal["help_subscriptions"] = "help_subscriptions"
    help_albums: Literal["help_albums"] = "help_albums"
    help_catalog: Literal["help_catalog"] = "help_catalog"
    help_cancel: Literal["help_cancel"] = "help_cancel"
    help_unknown_arg: Literal["help_unknown_arg"] = "help_unknown_arg"
