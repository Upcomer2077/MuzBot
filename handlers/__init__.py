from aiogram import Router

from handlers import _inline
from handlers.callbacks.pagination import _search_pag_cb

from . import _drop_message, _force, _help, _playlist, _search, _start
from .callbacks import _download_cb, _download_playlist_cb


def get_handlers_router():
    """Initialize and aggregate all modular message and callback routers into a single root handlers router dispatcher.

    Returns:
        The consolidated main Router object instance populated with ordered sub-routers.
    """
    main_router = Router()
    main_router.include_routers(
        _download_cb.router,
        _drop_message.router,
        _start.router,
        _help.router,
        _force.router,
        _inline.router,
        _playlist.router,
        _download_playlist_cb.router,
        _search_pag_cb.router,
        # MUST BE THE LAST
        _search.router,
    )

    return main_router
