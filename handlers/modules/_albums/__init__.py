from aiogram import Router

from handlers.modules._albums.stages._1 import _artists, _artists_pag_cb
from handlers.modules._albums.stages._2 import _albums, _albums_pag_cb
from handlers.modules._albums.stages._3 import _content

router = Router(name="Albums router")

router.include_routers(
    *[x.router for x in [_artists, _artists_pag_cb, _albums, _albums_pag_cb, _content]]
)
