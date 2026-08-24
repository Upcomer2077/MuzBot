from aiogram import Router

import handlers.callbacks as c_backs
import handlers.subscriptions as subs
from handlers import _inline

from . import _force, _help, _playlist, _search, _start


def get_handlers_router():
    """Initialize and aggregate all modular message and callback routers into a single root handlers router dispatcher.

    Returns:
        The consolidated main Router object instance populated with ordered sub-routers.
    """
    main_router = Router()

    main_router.include_routers(
        _start.router,
        _help.router,
        _force.router,
        _inline.router,
        _playlist.router,
        subs.router,
        c_backs.router,
        # MUST BE THE LAST
        _search.router,
    )

    return main_router
