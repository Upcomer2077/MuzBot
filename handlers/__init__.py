from aiogram import Router

from config import EXPERIMENTAL
from handlers import _inline

from . import _download, _drop_message, _force, _help, _playlist, _search, _start


def get_handlers_router():
    """Initialize and aggregate all modular message and callback routers into a single root handlers router dispatcher.

    Returns:
        The consolidated main Router object instance populated with ordered sub-routers.
    """
    main_router = Router()
    main_router.include_routers(
        _download.router,
        _drop_message.router,
        _start.router,
        _help.router,
        _force.router,
        _inline.router,
        *([_playlist.router] if EXPERIMENTAL else []),
        # MUST BE THE LAST
        _search.router,
    )

    return main_router
