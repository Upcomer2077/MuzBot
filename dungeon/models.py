from peewee import SQL, BooleanField, CharField, IntegerField
from peewee_aio import AIOModel

from dungeon.dispatcher import DB_DISPATCHER


@DB_DISPATCHER.register
class TrackCache(AIOModel):
    video_id = CharField(
        primary_key=True, max_length=20, constraints=[SQL("ON CONFLICT IGNORE")]
    )
    title = CharField(max_length=255)
    artist = CharField(max_length=255)
    telegram_file_id = CharField(max_length=255, null=True)
    track_duration = IntegerField(default=0)
    is_too_large = BooleanField(default=False, null=True)
    is_work_in_progress = BooleanField(default=False, null=True)

    class Meta:
        table_name = "tracks"
