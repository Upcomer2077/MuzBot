from _logger import LOGGER
from infra.tools.MusicTools.ytmusic_tools import YTMusicTools
from interfaces.imusictools import IMusicTools

MT: IMusicTools = YTMusicTools(logger=LOGGER)
