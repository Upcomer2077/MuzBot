from config import MAX_TRACK_DURATION_SECONDS
from dungeon.models import TrackCache
from dungeon.repos.track import TrackRepository
from schemas.dicts import YoutubeSearchResultDict


async def test_enslave_bulk_success(setup_track_db):
    """Проверяем массовую вставку треков и расчет флага is_too_large."""
    repo = TrackRepository()

    test_tracks: list[YoutubeSearchResultDict] = [
        {
            "video_id": "short_id",
            "title": "Short Track",
            "artist": "Artist 1",
            "duration_seconds": MAX_TRACK_DURATION_SECONDS - 10,
            "duration": "0",
        },
        {
            "video_id": "long_id",
            "title": "Long Track",
            "artist": "Artist 2",
            "duration_seconds": MAX_TRACK_DURATION_SECONDS + 10,  # Должен стать True
            "duration": "0",
        },
    ]

    inserted_count = await repo.enslave_bulk(test_tracks)

    assert inserted_count == 2

    short_track = await TrackCache.get_or_none(video_id="short_id")
    assert short_track is not None
    assert short_track.title == "Short Track"
    assert short_track.is_too_large is False

    long_track = await TrackCache.get_or_none(video_id="long_id")
    assert long_track is not None
    assert long_track.is_too_large is True


async def test_summon_slaves_mapping(setup_track_db):
    """Проверяем выборку пачки треков по списку ID и корректность маппинга в словарь."""
    repo = TrackRepository()

    await TrackCache.create(
        video_id="id_1", title="Track 1", artist="A1", track_duration=100
    )
    await TrackCache.create(
        video_id="id_2", title="Track 2", artist="A2", track_duration=120
    )

    result = await repo.summon_slaves(["id_1", "id_2", "missing_id"])

    assert len(result) == 2
    assert "id_1" in result
    assert "id_2" in result
    assert "missing_id" not in result
    assert result["id_1"].title == "Track 1"


async def test_fisting_single_and_bulk_update(setup_track_db):
    """Проверяем обновление полей telegram_file_id и is_too_large (метод fisting)."""
    repo = TrackRepository()

    await TrackCache.create(
        video_id="track_x", title="X", artist="A", track_duration=100
    )
    await TrackCache.create(
        video_id="track_y", title="Y", artist="A", track_duration=100
    )

    single_update = await repo.fisting(
        video_id="track_x", telegram_file_id="tg_file_123"
    )
    assert single_update is True

    updated_x = await TrackCache.get(video_id="track_x")
    assert updated_x.telegram_file_id == "tg_file_123"
    assert (
        updated_x.is_too_large is False
    )  # Не должно измениться, так как передали None

    bulk_update = await repo.fisting(video_id=["track_x", "track_y"], is_too_large=True)
    assert bulk_update is True

    # Проверяем, что оба трека обновились
    assert (await TrackCache.get(video_id="track_x")).is_too_large is True
    assert (await TrackCache.get(video_id="track_y")).is_too_large is True


async def test_next_door_deletion(setup_track_db):
    """Проверяем удаление трека из кэша по ID."""
    repo = TrackRepository()

    await TrackCache.create(
        video_id="target_id", title="To Delete", artist="A", track_duration=100
    )

    deleted = await repo.next_door("target_id")
    assert deleted is True
    assert await TrackCache.get_or_none(video_id="target_id") is None

    delete_missing = await repo.next_door("target_id")
    assert delete_missing is False
