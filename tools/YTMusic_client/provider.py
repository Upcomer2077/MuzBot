from asyncio import Semaphore

from ytmusicapi import YTMusic


class YTMusicProvider(YTMusic):
    def __init__(self):
        super().__init__()
        self.playlist_lock = Semaphore(2)
        self.search_lock = Semaphore(4)
        self.track_lock = Semaphore(2)
