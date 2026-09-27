from typing import ClassVar

from tortoise import Model, fields
from tortoise.indexes import PartialIndex


class TrackCache(Model):
    video_id = fields.CharField(primary_key=True, max_length=255)
    title = fields.CharField(255)
    artist = fields.CharField(255)
    telegram_file_id = fields.CharField(max_length=255, null=True)
    track_duration = fields.IntegerField(default=0)
    is_too_large = fields.BooleanField(default=False, null=True)
    created_at = fields.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        table = "tracks"


class PlaylistCache(Model):
    playlist_id = fields.CharField(255, primary_key=True)
    title = fields.CharField(255, default="UNKNOWN")
    artist: fields.CharField[str] = fields.CharField(255, default="unknown")

    class Meta:
        table = "playlists"


class TrackPlaylist(Model):
    """Junction database model linking tracks and playlists (Many-to-Many relationship)."""

    id = fields.IntField(primary_key=True)

    # Свойство называется video, а колонка в базе данных — video_id
    video: fields.ForeignKeyRelation[TrackCache] = fields.ForeignKeyField(
        "models.TrackCache",
        related_name="playlists",
        on_delete=fields.CASCADE,
        source_field="video_id",
    )

    # Свойство называется playlist, а колонка в базе данных — playlist_id
    playlist: fields.ForeignKeyRelation[PlaylistCache] = fields.ForeignKeyField(
        "models.PlaylistCache",
        related_name="tracks",
        on_delete=fields.CASCADE,
        source_field="playlist_id",
    )
    track_order = fields.IntField(default=0)

    class Meta:
        table = "tracks_playlists"
        unique_together: ClassVar[tuple[str, str, str]] = (
            "playlist",
            "track_order",
            "video",
        )


# ============


class TgUsers(Model):
    id = fields.BigIntField(primary_key=True, generated=False)

    class Meta:
        table = "telegram_users"


class YTPerformers(Model):
    id = fields.CharField(primary_key=True, max_length=255, generated=False)
    name = fields.CharField(max_length=255, null=False)
    # TODO: make mig with new table? [updated_at]
    last_single_id = fields.CharField(max_length=255, null=True)
    last_album_id = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "yt_performers"


class Subscriptions(Model):
    """Junction database model linking performers and users (Many-to-Many relationship)."""

    id = fields.IntField(primary_key=True)

    tg_user: fields.ForeignKeyRelation[TgUsers] = fields.ForeignKeyField(
        "models.TgUsers",
        related_name="yt_performers",
        on_delete=fields.CASCADE,
        source_field="tg_user_id",
    )

    performer: fields.ForeignKeyRelation[YTPerformers] = fields.ForeignKeyField(
        "models.YTPerformers",
        related_name="telegram_users",
        on_delete=fields.CASCADE,
        source_field="performer_id",
    )
    is_suspended = fields.BooleanField(default=False, null=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True)

    class Meta:
        table = "subscriptions"
        unique_together = (("performer", "tg_user"),)
        indexes: ClassVar[list[PartialIndex]] = [
            PartialIndex(
                fields=["performer"],
                condition={"is_suspended": False},
            )
        ]


class Singles(Model):
    playlist: fields.ForeignKeyRelation[PlaylistCache] = fields.ForeignKeyField(
        "models.PlaylistCache",
        related_name="singles",
        on_delete=fields.CASCADE,
        source_field="playlist_id",
    )
    performer: fields.ForeignKeyRelation[YTPerformers] = fields.ForeignKeyField(
        "models.YTPerformers",
        related_name="single_entries",
        on_delete=fields.CASCADE,
        source_field="performer_id",
    )
    browse_id = fields.CharField(255, null=False)
    order = fields.SmallIntegerField(null=False)

    class Meta:
        table = "singles"
        unique_together: ClassVar[tuple[str, str]] = ("performer", "playlist")


class Albums(Model):
    playlist: fields.ForeignKeyRelation[PlaylistCache] = fields.ForeignKeyField(
        "models.PlaylistCache",
        related_name="albums",
        on_delete=fields.CASCADE,
        source_field="playlist_id",
    )
    performer: fields.ForeignKeyRelation[YTPerformers] = fields.ForeignKeyField(
        "models.YTPerformers",
        related_name="album_entries",
        on_delete=fields.CASCADE,
        source_field="performer_id",
    )
    browse_id = fields.CharField(255, null=False)
    order: fields.SmallIntField = fields.SmallIntegerField(null=False)

    class Meta:
        table = "albums"
        unique_together: ClassVar[tuple[str, str]] = ("performer", "playlist")
