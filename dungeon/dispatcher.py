from peewee_aio import Manager

from config import DATABASE_DIR, DATABASE_FILENAME

DB_DISPATCHER = Manager(f"aiosqlite:///{DATABASE_DIR}/{DATABASE_FILENAME}")
