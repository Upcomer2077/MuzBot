from aiogram import Router

from handlers.modules._singles import _download_cb, _force

router = Router(name="Singles router")

router.include_routers(*[x.router for x in [_download_cb, _force]])
