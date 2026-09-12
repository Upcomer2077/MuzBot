from tortoise import Tortoise, connections

from _logger import LOGGER
from config import DATABASE_PATH


class DungeonDBSession:
    """Manages the connection lifecycle and settings of the underlying database engine."""

    @staticmethod
    async def open_dungeon(db_url: str = f"sqlite://{DATABASE_PATH}"):
        """Open database connection, initialize tables, and set PRAGMA optimizations."""
        await Tortoise.init(db_url=db_url, modules={"models": ["dungeon.models"]})
        await Tortoise.generate_schemas()

        try:
            connection = connections.get("default")
            pragma_script = """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA foreign_keys=ON;
            PRAGMA auto_vacuum=INCREMENTAL;
            """
            await connection.execute_script(pragma_script)
            LOGGER.debug("Database pragma set. Connection success")
        except Exception as e:
            LOGGER.critical(f"Caught error while opening the dungeon: {e}")

    @staticmethod
    async def close_dungeon():
        """Disconnect safely from the storage engine."""
        await Tortoise.close_connections()
        LOGGER.debug("Database connection closed")
