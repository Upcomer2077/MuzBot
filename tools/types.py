from typing import TypedDict


class YoutubeSearchResultDict(TypedDict):
    """Normalized data structure representing a track item pulled directly from YouTube Music search responses."""

    duration: str | None
    video_id: str
    title: str
    artist: str
    duration_seconds: int


class PlaylistInfoDict(TypedDict):
    id: str
    title: str | None
    author: str | None


class ArtistsShortInfoDict(TypedDict):
    name: str
    id: str


# =====
class ArtistInfoDict(TypedDict):
    name: str
    albums: ArtistEntitiesInfoDict | None
    singles: ArtistEntitiesInfoDict | None


class ArtistEntitiesInfoDict(TypedDict):
    results: list[ArtistConcreteEntityInfoDict]
    browseId: str


class ArtistConcreteEntityInfoDict(TypedDict):
    title: str
    browseId: str


# =====
