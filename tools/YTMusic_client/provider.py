from asyncio import Lock

from ytmusicapi import YTMusic


class YTMusicProvider(YTMusic):
    def __init__(self):
        super().__init__()
        self.playlist_lock = Lock()
        self.search_lock = Lock()
        self.track_lock = Lock()
