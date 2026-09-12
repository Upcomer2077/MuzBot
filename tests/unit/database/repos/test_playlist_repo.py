from dungeon.models import PlaylistCache, TrackCache, TrackPlaylist
from dungeon.repos.playlist import PlaylistRepository
from dungeon.repos.track import TrackRepository
from schemas.dicts import PlaylistInfoDict, YoutubeSearchResultDict


async def test_get_playlist_returns_correct_data():
    """Проверяем базовое получение мета-информации о плейлисте по ID."""
    repo = PlaylistRepository()

    # Предзаполняем таблицу плейлистов напрямую через модель
    await PlaylistCache.create(
        playlist_id="pl_123", title="Synthwave Chill", artist="Various Artists"
    )

    # Тестируем получение существующего
    playlist = await repo.get_playlist("pl_123")
    assert playlist is not None
    assert playlist.title == "Synthwave Chill"
    assert playlist.artist == "Various Artists"

    # Тестируем получение несуществующего
    missing = await repo.get_playlist("missing_pl")
    assert missing is None


async def test_add_playlist_and_tracks_creates_records_atomically():
    """Проверяем атомарное создание плейлиста, кэширование треков и генерацию m2m связей."""
    # Передаем явно TrackRepository, чтобы все слои работали в одной memory-сессии
    track_repo = TrackRepository()
    repo = PlaylistRepository(track_repo=track_repo)

    playlist_info: PlaylistInfoDict = {
        "id": "pl_rock",
        "title": "Classic Rock",
        "author": "John Doe",
    }

    test_tracks: list[YoutubeSearchResultDict] = [
        {
            "video_id": "rock_1",
            "title": "Track One",
            "artist": "Band A",
            "duration_seconds": 200,
            "duration": "0",
        },
        {
            "video_id": "rock_2",
            "title": "Track Two",
            "artist": "Band B",
            "duration_seconds": 250,
            "duration": "0",
        },
    ]

    # Вызываем метод репозитория
    relations_count = await repo.add_playlist_and_tracks(playlist_info, test_tracks)

    # Должно вернуться количество созданных промежуточных связей
    assert relations_count == 2

    # 1. Проверяем, что плейлист создался
    playlist = await PlaylistCache.get_or_none(playlist_id="pl_rock")
    assert playlist is not None
    assert playlist.title == "Classic Rock"

    # 2. Проверяем, что треки попали в кэш треков
    track1 = await TrackCache.get_or_none(video_id="rock_1")
    assert track1 is not None
    assert track1.title == "Track One"

    # 3. Проверяем, что m2m связи физически записались в промежуточную таблицу
    relations = (
        await TrackPlaylist.filter(playlist_id="pl_rock")
        .order_by("track_order")
        .values("video_id", "track_order")
    )
    assert len(relations) == 2

    assert relations[0]["video_id"] == "rock_1"
    assert relations[0]["track_order"] == 0

    assert relations[1]["video_id"] == "rock_2"
    assert relations[1]["track_order"] == 1


async def test_add_playlist_and_tracks_handles_conflicts():
    """Проверяем, что повторное добавление тех же треков в тот же плейлист

    не падает по IntegrityError благодаря ignore_conflicts=True.
    """
    repo = PlaylistRepository()

    playlist_info: PlaylistInfoDict = {
        "id": "pl_dup",
        "title": "Duplicate Test",
        "author": "Tester",
    }
    test_tracks: list[YoutubeSearchResultDict] = [
        {
            "video_id": "track_dup",
            "title": "Unique Title",
            "artist": "Art",
            "duration_seconds": 120,
            "duration": "0",
        }
    ]

    # Первый запуск — чистое создание
    first_run = await repo.add_playlist_and_tracks(playlist_info, test_tracks)
    assert first_run == 1

    # Второи запуск с теми же данными — не должен вызывать краш базы данных
    second_run = await repo.add_playlist_and_tracks(playlist_info, test_tracks)

    # В зависимости от СУБД вернется либо 1 (проигнорировано), либо 0, главное — отсутствие Exception
    assert second_run in (0, 1)


async def test_summon_slaves_from_playlist_sorting_and_limit():
    """Проверяем, что выборка треков из плейлиста строго соблюдает track_order и лимиты."""
    repo = PlaylistRepository()

    # Вручную создаем структуру в памяти
    await PlaylistCache.create(playlist_id="pl_sort", title="Sorted", artist="Dev")

    # Создаем треки
    await TrackCache.create(
        video_id="v_first", title="First", artist="A", track_duration=100
    )
    await TrackCache.create(
        video_id="v_second", title="Second", artist="A", track_duration=100
    )
    await TrackCache.create(
        video_id="v_third", title="Third", artist="A", track_duration=100
    )

    # Создаем связи Many-to-Many с разным порядком (track_order)
    # Намеренно пишем их хаотично, чтобы проверить сортировку на стороне SQL
    await TrackPlaylist.create(
        playlist_id="pl_sort", video_id="v_second", track_order=1
    )
    await TrackPlaylist.create(playlist_id="pl_sort", video_id="v_third", track_order=2)
    await TrackPlaylist.create(playlist_id="pl_sort", video_id="v_first", track_order=0)

    # 1. Проверяем сортировку: метод должен вернуть словарь, где ключи идут в порядке track_order
    ordered_result = await repo.summon_slaves_from_playlist("pl_sort")
    assert ordered_result is not None
    assert len(ordered_result) == 3

    # Превращаем ключи словаря в список, чтобы проверить их последовательность
    keys_sequence = list(ordered_result.keys())
    assert keys_sequence == ["v_first", "v_second", "v_third"]

    # 2. Проверяем работу лимита
    limited_result = await repo.summon_slaves_from_playlist("pl_sort", limit=2)
    assert limited_result is not None
    assert len(limited_result) == 2
    assert list(limited_result.keys()) == ["v_first", "v_second"]

    # 3. Проверяем пустой плейлист
    empty_result = await repo.summon_slaves_from_playlist("missing_pl")
    assert empty_result is None
