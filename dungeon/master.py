from dungeon.repos.playlist import PlaylistRepository
from dungeon.repos.subscriptions import SubscriptionRepository
from dungeon.repos.track import TrackRepository
from dungeon.session import DungeonDBSession


class DungeonMaster:
    """Unified Facade managing connection states and direct routing endpoints to segmented repositories."""

    def __init__(self):
        # Инициализируем изолированные компоненты
        self.tracks = TrackRepository()
        self.playlists = PlaylistRepository(track_repo=self.tracks)
        self.subs = SubscriptionRepository()

    # Ссылки для обратной совместимости инициализации
    async def open_dungeon(self):
        await DungeonDBSession.open_dungeon()

    async def close_dungeon(self):
        await DungeonDBSession.close_dungeon()
