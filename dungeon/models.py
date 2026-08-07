from datetime import datetime

from peewee import (
    SQL,
    BooleanField,
    CharField,
    CompositeKey,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
)
from peewee_aio import AIOModel

from dungeon.dispatcher import DB_DISPATCHER


@DB_DISPATCHER.register
class TrackCache(AIOModel):
    """Database model for caching downloaded YouTube Music tracks metadata and Telegram file references."""

    video_id = CharField(
        primary_key=True, max_length=20, constraints=[SQL("ON CONFLICT IGNORE")]
    )
    title = CharField(max_length=255)
    artist = CharField(max_length=255)
    telegram_file_id = CharField(max_length=255, null=True)
    track_duration = IntegerField(default=0)
    is_too_large = BooleanField(default=False, null=True)
    created_at = DateTimeField(default=datetime.now, null=True)

    class Meta:
        table_name = "tracks"


@DB_DISPATCHER.register
class PlaylistCache(AIOModel):
    """Database model for caching downloaded YouTube Music playlists metadata."""

    playlist_id = CharField(
        primary_key=True, max_length=255, constraints=[SQL("ON CONFLICT IGNORE")]
    )
    title = CharField(max_length=255, default="UNKNOWN")
    artist = CharField(max_length=255, default="unknown")

    class Meta:
        table_name = "playlists"


@DB_DISPATCHER.register
class TrackPlaylist(AIOModel):
    """Junction database model linking tracks and playlists (Many-to-Many relationship)."""

    video_id = ForeignKeyField(
        TrackCache,
        backref="playlists",
        on_delete="CASCADE",
    )

    playlist_id = ForeignKeyField(
        PlaylistCache,
        backref="tracks",
        on_delete="CASCADE",
    )
    track_order = IntegerField(default=0)

    class Meta:
        table_name = "tracks_playlists"
        primary_key = CompositeKey("video_id", "playlist_id")
