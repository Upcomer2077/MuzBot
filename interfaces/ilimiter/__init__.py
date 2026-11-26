from abc import ABC, abstractmethod
from typing import Required, TypedDict

from config import (
    CATALOG_COOLDOWN_SECS,
    CATALOG_PER_LIMIT,
    PLAYLIST_DOWNLOAD_COOLDOWN_SECS,
    PLAYLISTS_LIMIT,
    QUERY_DOWNLOAD_LIMIT_SECS,
    SEARCH_COOLDOWN_SECS,
    SEARCH_PER_LIMIT,
    SUBSCRIPTION_COOLDOWN_SECS,
    SUBSCRIPTIONS_PER_LIMIT,
    TRACKS_PER_LIMIT,
)
from interfaces.ilogger import ILogger


class _UserQueryLimitDict(TypedDict):
    """Data blueprint for monitoring a single user's rate limits, tracking remaining downloads and request timestamps."""

    semaphore: Required[int]
    ts: Required[float]


class IActionLimiter(ABC):
    """Rate limiter to manage chat action frequencies and track user music download limits."""

    def __init__(self, logger: ILogger):
        self.__logger = logger
        self._ACTIONS_BANK: dict[int, _UserQueryLimitDict] = {}
        self._ACTIONS_COOLDOWN_SECS = 10
        self._ACTION_PER_LIMIT = 1

        self._QUERIES_BANK: dict[int, _UserQueryLimitDict] = {}
        self._QUERIES_COOLDOWN_SECS = QUERY_DOWNLOAD_LIMIT_SECS
        self._TRACKS_PER_LIMIT = TRACKS_PER_LIMIT

        self._PLAYLIST_BANK: dict[int, _UserQueryLimitDict] = {}
        self._PLAYLIST_COOLDOWN_SECS = PLAYLIST_DOWNLOAD_COOLDOWN_SECS
        self._PLAYLIST_PER_LIMIT = PLAYLISTS_LIMIT

        self._SUBS_BANK: dict[int, _UserQueryLimitDict] = {}
        self._SUBS_COOLDOWN_SECS = SUBSCRIPTION_COOLDOWN_SECS
        self._SUBS_PER_LIMIT = SUBSCRIPTIONS_PER_LIMIT

        self._SEARCH_BANK: dict[int, _UserQueryLimitDict] = {}
        self._SEARCH_COOLDOWN_SECS = SEARCH_COOLDOWN_SECS
        self._SEARCH_PER_LIMIT = SEARCH_PER_LIMIT

        self._CATALOG_BANK: dict[int, _UserQueryLimitDict] = {}
        self._CATALOG_COOLDOWN_SECS = CATALOG_COOLDOWN_SECS
        self._CATALOG_PER_LIMIT = CATALOG_PER_LIMIT

    def is_catalog_action_allowed(
        self,
        chat_id: int,
    ):
        return self._is_allowed(
            chat_id,
            bank=self._CATALOG_BANK,
            cooldown=self._CATALOG_COOLDOWN_SECS,
            per_limit=self._CATALOG_PER_LIMIT,
        )

    @abstractmethod
    def _is_allowed(
        self,
        user_id: int,
        *,
        bank: dict[int, _UserQueryLimitDict],
        cooldown: int,
        per_limit: int,
    ) -> bool: ...
    def is_send_action_allowed(
        self,
        chat_id: int,
    ):
        return self._is_allowed(
            chat_id,
            bank=self._ACTIONS_BANK,
            cooldown=self._ACTIONS_COOLDOWN_SECS,
            per_limit=self._ACTION_PER_LIMIT,
        )

    def is_playlist_download_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._PLAYLIST_BANK,
            cooldown=self._PLAYLIST_COOLDOWN_SECS,
            per_limit=self._PLAYLIST_PER_LIMIT,
        )

    def is_track_download_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._QUERIES_BANK,
            cooldown=self._QUERIES_COOLDOWN_SECS,
            per_limit=self._TRACKS_PER_LIMIT,
        )

    def is_subscription_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._SUBS_BANK,
            cooldown=self._SUBS_COOLDOWN_SECS,
            per_limit=self._SUBS_PER_LIMIT,
        )

    def is_search_allowed(self, user_id: int):
        return self._is_allowed(
            user_id,
            bank=self._SEARCH_BANK,
            cooldown=self._SEARCH_COOLDOWN_SECS,
            per_limit=self._SEARCH_PER_LIMIT,
        )

    @abstractmethod
    def garbage_collector(self, **_): ...
