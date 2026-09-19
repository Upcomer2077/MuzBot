from aiogram import Router

from handlers.callbacks.subscriptions import (
    _list_cb,
    _sub_cb,
    _sub_pag_cb,
    _unsub_cb,
    _usub_pag_cb,
)

router = Router(name="Subscriptions cb")

router.include_routers(
    *[x.router for x in [_sub_cb, _unsub_cb, _list_cb, _sub_pag_cb, _usub_pag_cb]]
)
