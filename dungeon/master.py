from dungeon.repos.playlist import PlaylistRepository
from dungeon.repos.subscriptions import SubscriptionRepository
from dungeon.repos.track import TrackRepository
from dungeon.repos.ytperformers import YTPerformersRepository
from dungeon.session import DungeonDBSession
from interfaces.idatabase import IDataBase
from interfaces.ilogger import ILogger


class DungeonMaster(IDataBase):
    def __init__(self, logger: ILogger):
        super().__init__(logger)
        self.tracks = TrackRepository(logger=logger)
        self.playlists = PlaylistRepository(track_repo=self.tracks, logger=logger)
        self.subs = SubscriptionRepository(logger=logger)
        self.performers = YTPerformersRepository(logger=logger)

    async def open_dungeon(self):
        await DungeonDBSession.open_dungeon(logger=self._logger)

    async def close_dungeon(self):
        await DungeonDBSession.close_dungeon(logger=self._logger)
