from config import DATABASE_PATH
from dungeon.dispatcher import DB_DISPATCHER
from dungeon.master import DungeonMaster

DM = DungeonMaster(DATABASE_PATH, DB_DISPATCHER)
"""Global DungeonMaster instance managing track db-persistence operations."""
