from aiogram import Router

from handlers.callbacks.download import _download_cb, _download_playlist_cb

router = Router(name="Download cb router")

router.include_routers(_download_cb.router, _download_playlist_cb.router)
