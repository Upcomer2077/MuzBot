from aiogram import Router

from handlers.modules._subscriptions._sub import _sub_cb, _sub_pag_cb, _subscribe

router = Router(name="Subscriptions/sub")

router.include_routers(
    *[
        x.router
        for x in [
            _sub_cb,
            _sub_pag_cb,
            _subscribe,
        ]
    ]
)
