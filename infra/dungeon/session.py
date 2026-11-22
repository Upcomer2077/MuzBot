from tortoise import Tortoise, connections

from config import DATABASE_PATH
from interfaces.ilogger import ILogger


class DungeonDBSession:
    """Manages the connection lifecycle and settings of the underlying database engine."""

    @staticmethod
    async def open_dungeon(
        db_url: str = f"sqlite://{DATABASE_PATH}", *, logger: ILogger
    ):
        """Open database connection, initialize tables, and set PRAGMA optimizations."""
        await Tortoise.init(
            db_url=db_url,
            modules={"models": ["infra.dungeon.models"]},
            _enable_global_fallback=True,
        )
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
            logger.debug("Database pragma set. Connection success")
        except Exception as e:
            logger.critical(f"Caught error while opening the dungeon: {e}")

    @staticmethod
    async def close_dungeon(*, logger: ILogger):
        """Disconnect safely from the storage engine."""
        await Tortoise.close_connections()
        logger.debug("Database connection closed")
