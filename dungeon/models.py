from tortoise import Model, fields


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
    video = fields.ForeignKeyField(
        "models.TrackCache",
        related_name="playlists",
        on_delete=fields.CASCADE,
        source_field="video_id",
    )

    # Свойство называется playlist, а колонка в базе данных — playlist_id
    playlist = fields.ForeignKeyField(
        "models.PlaylistCache",
        related_name="tracks",
        on_delete=fields.CASCADE,
        source_field="playlist_id",
    )
    track_order = fields.IntField(default=0)

    class Meta:
        table = "tracks_playlists"
        unique_together = (("video", "playlist"),)


# ============


class TgUsers(Model):
    id = fields.BigIntField(pk=True, generated=False)

    class Meta:
        table = "telegram_users"


class YTPerformers(Model):
    id = fields.CharField(pk=True, max_length=255, generated=False)
    name = fields.CharField(max_length=255, null=False)
    last_single_id = fields.CharField(max_length=255, null=True)
    last_album_id = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "yt_performers"


class Subscriptions(Model):
    """Junction database model linking performers and users (Many-to-Many relationship)."""

    id = fields.IntField(primary_key=True)

    # Переименовываем свойство в tg_user, а колонку в БД задаем через source_field
    tg_user = fields.ForeignKeyField(
        "models.TgUsers",
        related_name="yt_performers",
        on_delete=fields.CASCADE,
        source_field="tg_user_id",
    )

    # Переименовываем свойство в performer, а колонку в БД задаем через source_field
    performer = fields.ForeignKeyField(
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
