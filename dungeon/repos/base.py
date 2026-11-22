from abc import ABC

from interfaces.ilogger import ILogger


class BaseRepo(ABC):
    def __init__(self, logger: ILogger):
        self._logger = logger
