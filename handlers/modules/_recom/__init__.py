from aiogram import Router

from handlers.modules._recom import _rec, _rec_pag_cb

router = Router(name="Recommendations router")

router.include_routers(*[x.router for x in [_rec, _rec_pag_cb]])
