from typing import TypedDict

from dungeon.models import TrackCache


class _T(TypedDict):
    cached: list[TrackCache]
    missing: list[TrackCache]


def split_by_cache(acc: _T, track: TrackCache):
    acc["missing" if track.telegram_file_id is None else "cached"].append(track)
    return acc
