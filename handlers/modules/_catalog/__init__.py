from aiogram import Router

from handlers.modules._catalog.stages._1 import _artists, _artists_pag_cb
from handlers.modules._catalog.stages._2 import _singles, _singles_pag_cb
from handlers.modules._catalog.stages._3 import _content

router = Router(name="Catalog router")

router.include_routers(
    *[
        x.router
        for x in [_artists, _artists_pag_cb, _singles, _singles_pag_cb, _content]
    ]
)
