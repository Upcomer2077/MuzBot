from _logger import LOGGER
from dungeon.master import DungeonMaster
from interfaces.idatabase import IDataBase

DM: IDataBase = DungeonMaster(LOGGER)
"""Global DungeonMaster instance managing track db-persistence operations."""
