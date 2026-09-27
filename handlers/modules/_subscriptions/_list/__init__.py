from aiogram import Router

from handlers.modules._subscriptions._list import _list, _list_pag_cb

router = Router(name="Subscriptions/list")

router.include_routers(
    *[
        x.router
        for x in [
            _list,
            _list_pag_cb,
        ]
    ]
)
