from aiogram import Router

from handlers.modules._subscriptions._unsub import (
    _unsub_cb,
    _unsub_pag_cb,
    _unsubscribe,
)

router = Router(name="Subscriptions/unsub")

router.include_routers(*[x.router for x in [_unsub_cb, _unsub_pag_cb, _unsubscribe]])
