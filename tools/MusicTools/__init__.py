from _logger import LOGGER
from interfaces.imusictools import IMusicTools
from tools.MusicTools.ytmusic_tools import YTMusicTools

MT: IMusicTools = YTMusicTools(logger=LOGGER)
