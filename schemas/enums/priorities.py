from enum import Enum


class DownloadTaskPriorities(float, Enum):
    SINGLE = 1.0
    "For single found by search"
    ALBUM = 2.0
    "For playlists"
    NOTIFICATION = 2.5
    "For tracks pulled by notification job"
