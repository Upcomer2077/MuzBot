from aiogram import Router

from handlers.modules._search import _inline, _search, _search_cb

router = Router(name="Search router")

router.include_routers(
    *[
        x.router
        for x in [
            _inline,
            _search_cb,
            # MUST BE THE LAST
            _search,
        ]
    ]
)
