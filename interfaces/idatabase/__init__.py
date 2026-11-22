from abc import ABC, abstractmethod

from dungeon.repos.playlist import PlaylistRepository
from dungeon.repos.subscriptions import SubscriptionRepository
from dungeon.repos.track import TrackRepository
from dungeon.repos.ytperformers import YTPerformersRepository
from interfaces.ilogger import ILogger


class IDataBase(ABC):
    """Unified Facade managing connection states and direct routing endpoints to segmented repositories."""

    def __init__(self, logger: ILogger):
        self._logger = logger
        self.tracks: TrackRepository
        self.playlists: PlaylistRepository
        self.subs: SubscriptionRepository
        self.performers: YTPerformersRepository

    @abstractmethod
    async def open_dungeon(self): ...

    @abstractmethod
    async def close_dungeon(self): ...
