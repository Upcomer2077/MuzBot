import pytest
from tortoise import Tortoise


@pytest.fixture(
    autouse=True,
)
async def setup_track_db():
    await Tortoise.init(
        db_url="sqlite://:memory:", modules={"models": ["dungeon.models"]}
    )
    await Tortoise.generate_schemas()

    yield  # Здесь выполняются сами тесты

    # Зачистка после каждого теста
    if hasattr(Tortoise, "_inited") and Tortoise._inited:
        try:
            await Tortoise.close_connections()
        except Exception:
            ...
        await Tortoise._reset_apps()
