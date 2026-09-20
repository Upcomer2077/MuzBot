# tests/unit/database/test_session.py
from pathlib import Path

import pytest
from tortoise import Tortoise, connections
from tortoise.exceptions import ConfigurationError

from dungeon.session import DungeonDBSession


async def test_dungeon_session_lifecycle(tmp_path: Path):
    test_db_file = tmp_path / "test_dungeon.db"

    assert not test_db_file.exists()

    await DungeonDBSession.open_dungeon(f"sqlite://{test_db_file}")

    assert test_db_file.exists(), f"Файл базы данных не найден по пути: {test_db_file}"
    assert test_db_file.stat().st_size > 0
    assert "models" in Tortoise.apps

    connection = connections.get("default")
    _, journal_mode_rows = await connection.execute_query("PRAGMA journal_mode;")
    journal_mode = journal_mode_rows[0][0]
    assert journal_mode.upper() == "WAL"

    _, synchronous_rows = await connection.execute_query("PRAGMA synchronous;")
    assert synchronous_rows[0][0] == 1

    _, foreign_keys_rows = await connection.execute_query("PRAGMA foreign_keys;")
    assert foreign_keys_rows[0][0] == 1

    await DungeonDBSession.close_dungeon()

    with pytest.raises(ConfigurationError):
        connections.get("default")
