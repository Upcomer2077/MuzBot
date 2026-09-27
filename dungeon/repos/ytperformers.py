from typing import Final

from tortoise.transactions import in_transaction

from _logger import LOGGER
from dungeon.models import Albums, PlaylistCache, Singles, YTPerformers
from tools.types import ArtistInfoDict


class YTPerformersRepository:
    async def set_performer_releases_v2(
        self, performer_id: str, *, info: ArtistInfoDict
    ):
        """Create or update performer status releases configuration profile."""
        try:
            async with in_transaction():
                await YTPerformers.get_or_create(
                    id=performer_id,
                    defaults={
                        "name": info["name"],
                    },
                )

                _albums: Final = info["albums"] or []
                _singles: Final = info["singles"] or []
                # ====
                db_playlists = [
                    PlaylistCache(
                        playlist_id=p["audioPlaylistId"],
                        title=p["title"],
                        artist=info["name"],
                    )
                    for p in _albums + _singles
                ]

                db_singles = [
                    Singles(
                        playlist_id=s["audioPlaylistId"],
                        performer_id=performer_id,
                        browse_id=s["browseId"],
                        order=s["order"],
                    )
                    for s in _singles
                ]
                db_albums = [
                    Albums(
                        playlist_id=a["audioPlaylistId"],
                        performer_id=performer_id,
                        browse_id=a["browseId"],
                        order=a["order"],
                    )
                    for a in _albums
                ]

                await PlaylistCache.bulk_create(db_playlists, ignore_conflicts=True)
                await Singles.bulk_create(db_singles, ignore_conflicts=True)
                await Albums.bulk_create(db_albums, ignore_conflicts=True)
                return True
        except Exception as e:
            LOGGER.error(str(e))
            return False

    async def get_performer_info(self, performer_id: str) -> YTPerformers | None:
        """Look up unique artist properties cached in the node store."""
        return await YTPerformers.get_or_none(id=performer_id)

    async def get_artists_by_name(
        self, user_id: int, s_query: str
    ) -> list[YTPerformers]:
        """Perform fuzzy prefix query filter lookup scanning for user specific active artists bindings."""
        r = await YTPerformers.filter(
            telegram_users__tg_user_id=user_id, name__icontains=s_query
        ).only("id", "name")
        return list(r)

    async def get_artist_releases(
        self, performer_id: str, *, fetch_singles=True, fetch_albums=True
    ):
        performer = await YTPerformers.get_or_none(id=performer_id)
        if not performer:
            return None
        albums = singles = None
        if fetch_albums:
            albums = (
                await Albums.filter(performer_id=performer_id)
                .prefetch_related("playlist")
                .order_by("-order")
            )
            if not len(albums):
                albums = None
        if fetch_singles:
            singles = (
                await Singles.filter(performer_id=performer_id)
                .prefetch_related("playlist")
                .order_by("-order")
            )
            if not len(singles):
                singles = None
        if (fetch_singles and not singles) and (fetch_albums and not albums):
            return None
        return (albums, singles)

    async def get_artist_last_release(
        self, performer_id: str, *, fetch_singles=True, fetch_albums=True
    ):
        performer = await YTPerformers.get_or_none(id=performer_id)
        if not performer:
            return None
        albums = singles = None
        if fetch_albums:
            albums = (
                await Albums.filter(performer_id=performer_id)
                .prefetch_related("playlist")
                .order_by("-order")
                .first()
            )

        if fetch_singles:
            singles = (
                await Singles.filter(performer_id=performer_id)
                .prefetch_related("playlist")
                .order_by("-order")
                .first()
            )

        return (albums, singles)
