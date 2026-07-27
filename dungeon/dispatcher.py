from peewee_aio import Manager

from config import DATABASE_PATH

DB_DISPATCHER = Manager(f"aiosqlite:///{DATABASE_PATH}")
"""Global asynchronous database manager instance handling Peewee-async connections to SQLite."""
