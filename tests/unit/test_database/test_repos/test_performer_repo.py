from dungeon.models import Albums, Singles, Subscriptions, TgUsers, YTPerformers
from dungeon.repos.ytperformers import YTPerformersRepository
from tools.types import ArtistConcreteEntityInfoDict


async def test_set_performer_last_release_upsert():
    """Проверяем update_or_create: создание и обновление профиля артиста при конфликте."""
    repo = YTPerformersRepository()

    # 1. Проверяем вставку (создание новой записи)
    await repo.set_performer_releases_v2(
        performer_id="artist_777",
        info={
            "name": "Mick Gordon",
            "albums": [
                ArtistConcreteEntityInfoDict(
                    title="doom_ost", browseId="1", order=1, audioPlaylistId="5"
                )
            ],
            "singles": None,
        },
    )

    album = await Albums.get(performer_id="artist_777").prefetch_related("performer")
    single = await Singles.get_or_none(performer_id="artist_777").prefetch_related(
        "performer"
    )
    assert album.performer.name is not None
    assert album.performer.name == "Mick Gordon"
    assert album.browse_id == "1"
    assert single == None


async def test_get_artists_by_name_prefix_search():
    """Проверяем регистронезависимый поиск по началу имени артиста (__istartswith)."""
    repo = YTPerformersRepository()

    # Создаем артистов
    await YTPerformers.create(id="1", name="Linkin Park")
    await YTPerformers.create(id="2", name="Limp Bizkit")
    await YTPerformers.create(id="3", name="The Prodigy")

    # Создаем пользователя
    await TgUsers.create(id=100)

    # Создаем подписки. Используем tg_user_id и performer_id (имя свойства в модели + _id)
    await Subscriptions.create(tg_user_id=100, performer_id="1")
    await Subscriptions.create(tg_user_id=100, performer_id="2")
    await Subscriptions.create(tg_user_id=100, performer_id="3")

    # Тестируем поиск
    results = await repo.get_artists_by_name(user_id=100, s_query="LI")

    assert len(results) == 2
    names = [r.name for r in results]
    assert "Linkin Park" in names
    assert "Limp Bizkit" in names
    assert "The Prodigy" not in names
