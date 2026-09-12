from collections.abc import AsyncGenerator
from typing import Any

from dungeon.models import Subscriptions, TgUsers, YTPerformers


class SubscriptionRepository:
    """Manages users subscriptions, artists caching profiles, and bulk queries mappings."""

    async def set_performer_last_release(
        self,
        performer_id: str,
        *,
        performer_name: str,
        last_album_id: str | None,
        last_single_id: str | None,
    ) -> None:
        """Create or update performer status releases configuration profile."""
        await YTPerformers.update_or_create(
            id=performer_id,
            defaults={
                "name": performer_name,
                "last_single_id": last_single_id,
                "last_album_id": last_album_id,
            },
        )

    async def subscribe_to_performer(self, user_id: int, performer_id: str) -> int:
        """Establish unique binding link between TG user profile node and artist identity."""
        await TgUsers.get_or_create(id=user_id, defaults={})
        _, created = await Subscriptions.get_or_create(
            tg_user_id=user_id, performer_id=performer_id
        )
        return 1 if created else 0

    async def get_performer_info(self, performer_id: str) -> YTPerformers | None:
        """Look up unique artist properties cached in the node store."""
        return await YTPerformers.get_or_none(id=performer_id)

    async def drop_sub(self, performer_id: str, user_id: int) -> int:
        """Unsubscribe user identity completely from designated target artist events stream."""
        return await Subscriptions.filter(
            tg_user_id=user_id, performer_id=performer_id
        ).delete()

    async def get_artists_by_name(
        self, user_id: int, s_query: str
    ) -> list[YTPerformers]:
        """Perform fuzzy prefix query filter lookup scanning for user specific active artists bindings."""
        r = await YTPerformers.filter(
            telegram_users__tg_user_id=user_id, name__istartswith=s_query
        ).only("id", "name")
        return list(r)

    async def get_subscripted_authors(
        self, batch_size: int = 100
    ) -> AsyncGenerator[list[dict[str, Any]]]:
        """Iteratively load distinct rows bundles grouping active profiles that carry active metrics."""
        base_query = (
            YTPerformers.filter(telegram_users__is_suspended=False)
            .distinct()
            .order_by("id")
        )
        offset = 0
        while True:
            results = (
                await base_query.limit(batch_size)
                .offset(offset)
                .values(
                    performer_id="id",
                    name="name",
                    last_album_id="last_album_id",
                    last_single_id="last_single_id",
                )
            )
            if not results:
                break
            yield results
            offset += batch_size

    async def get_tg_users_with_subs(
        self, performers_ids: list
    ) -> list[dict[str, Any]]:
        """Fetch relation structures between performers and active user targets mapped arrays."""
        if not performers_ids:
            return []
        return (
            await Subscriptions.filter(performer_id__in=performers_ids)
            .order_by("performer_id")
            .values(performer_id="performer_id", tg_user_id="tg_user_id")
        )

    async def toggle_user_subscriptions(self, tg_user_id: int, suspend: bool) -> int:
        """Mass toggle activation flags variables for specific profiles records bundle."""
        return await Subscriptions.filter(tg_user_id=tg_user_id).update(
            is_suspended=suspend
        )
