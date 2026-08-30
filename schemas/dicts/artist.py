from typing import TypedDict


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
