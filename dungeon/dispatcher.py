from peewee_aio import Manager

from config import DATABASE_PATH

DB_DISPATCHER = Manager(f"aiosqlite:///{DATABASE_PATH}")
