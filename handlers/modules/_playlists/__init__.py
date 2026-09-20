from aiogram import Router

from handlers.modules._playlists import _download_cb, _playlist

router = Router(name="Playlists router")

router.include_routers(*[x.router for x in [_download_cb, _playlist]])
