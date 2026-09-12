from dungeon.models import Subscriptions, TgUsers, YTPerformers
from dungeon.repos.subscriptions import SubscriptionRepository


async def test_set_performer_last_release_upsert():
    """Проверяем update_or_create: создание и обновление профиля артиста при конфликте."""
    repo = SubscriptionRepository()

    # 1. Проверяем вставку (создание новой записи)
    await repo.set_performer_last_release(
        performer_id="artist_777",
        performer_name="Mick Gordon",
        last_album_id="doom_ost",
        last_single_id="bfg_division",
    )

    performer = await YTPerformers.get_or_none(id="artist_777")
    assert performer is not None
    assert performer.name == "Mick Gordon"
    assert performer.last_album_id == "doom_ost"

    # 2. Проверяем апдейт той же записи (конфликт по ID)
    await repo.set_performer_last_release(
        performer_id="artist_777",
        performer_name="Mick Gordon",
        last_album_id="doom_eternal_ost",
        last_single_id=None,
    )

    updated = await YTPerformers.get(id="artist_777")
    assert updated.last_album_id == "doom_eternal_ost"
    assert updated.last_single_id is None


async def test_subscribe_and_drop_operations():
    """Проверяем создание пользователя, оформление подписки и отписку."""
    repo = SubscriptionRepository()

    # ВАЖНО: Сначала создаем артиста, чтобы не упал FOREIGN KEY constraint
    await YTPerformers.create(id="perf_rock", name="Rock Artist")

    # 1. Подписываемся первый раз (должен создаться юзер и подписка, вернет 1)
    status_first = await repo.subscribe_to_performer(
        user_id=42, performer_id="perf_rock"
    )
    assert status_first == 1

    # Проверяем наличие записей
    assert await TgUsers.exists(id=42)
    assert await Subscriptions.filter(tg_user_id=42, performer_id="perf_rock").exists()

    # 2. Повторная подписка (должна проигнорироваться и вернуть 0)
    status_second = await repo.subscribe_to_performer(
        user_id=42, performer_id="perf_rock"
    )
    assert status_second == 0

    # 3. Удаление подписки (drop_sub)
    deleted_rows = await repo.drop_sub(user_id=42, performer_id="perf_rock")
    assert deleted_rows == 1
    assert not await Subscriptions.filter(
        tg_user_id=42, performer_id="perf_rock"
    ).exists()


async def test_get_artists_by_name_prefix_search():
    """Проверяем регистронезависимый поиск по началу имени артиста (__istartswith)."""
    repo = SubscriptionRepository()

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


async def test_get_subscripted_authors_batch_generator():
    """Проверяем асинхронный генератор батчей активных авторов."""
    repo = SubscriptionRepository()

    # Создаем 5 исполнителей
    for i in range(1, 6):
        await YTPerformers.create(id=f"p_{i}", name=f"Performer {i}")

    # Подписываем пользователя
    await TgUsers.create(id=1)
    for i in range(1, 6):
        await Subscriptions.create(
            tg_user_id=1, performer_id=f"p_{i}", is_suspended=False
        )

    # Запускаем генератор с размером батча = 2
    generator = repo.get_subscripted_authors(batch_size=2)

    batches = []
    async for batch in generator:
        batches.append(batch)

    # 5 элементов по 2 в батче должно дать 3 батча (2, 2, 1)
    assert len(batches) == 3
    assert len(batches[0]) == 2
    assert len(batches[1]) == 2
    assert len(batches[2]) == 1

    # Проверяем структуру словарей в первом батче
    first_item = batches[0][0]
    assert "performer_id" in first_item
    assert "name" in first_item


async def test_toggle_user_subscriptions():
    """Проверяем массовое переключение флага заморозки подписок пользователя."""
    repo = SubscriptionRepository()

    await TgUsers.create(id=500)
    await YTPerformers.create(id="perf_1", name="A")
    await YTPerformers.create(id="perf_2", name="B")

    await Subscriptions.create(
        tg_user_id=500, performer_id="perf_1", is_suspended=False
    )
    await Subscriptions.create(
        tg_user_id=500, performer_id="perf_2", is_suspended=False
    )

    # Замораживаем все подписки юзера
    updated_count = await repo.toggle_user_subscriptions(tg_user_id=500, suspend=True)
    assert updated_count == 2

    # Проверяем изменения в базе
    subs = await Subscriptions.filter(tg_user_id=500)
    assert all(s.is_suspended is True for s in subs)
