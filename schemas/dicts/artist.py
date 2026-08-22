from typing import TypedDict


class ArtistsShortInfoDict(TypedDict):
    name: str
    id: str


# =====
class ArtistInfoDict(TypedDict):
    name: str
    albums: ArtistEntityInfoDict | None
    singles: ArtistEntityInfoDict | None


class ArtistEntityInfoDict(TypedDict):
    results: list[ArtistConcreteEntityInfoDict]
    browseId: str


class ArtistConcreteEntityInfoDict(TypedDict):
    title: str
    browseId: str


# =====
