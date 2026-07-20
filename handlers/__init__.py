from aiogram import Router

from handlers import _inline

from . import _download, _drop_message, _force, _help, _search, _start


def get_handlers_router():
    main_router = Router()
    main_router.include_routers(
        _download.router,
        _drop_message.router,
        _start.router,
        _help.router,
        _force.router,
        _inline.router,
        # MUST BE THE LAST
        _search.router,
    )

    return main_router
