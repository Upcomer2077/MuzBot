from aiogram import Router

from handlers import _drop_message, _help, _start
from handlers.modules import _playlists, _search, _singles, _subscriptions


def get_handlers_router():
    """Initialize and aggregate all modular message and callback routers into a single root handlers router dispatcher.

    Returns:
        The consolidated main Router object instance populated with ordered sub-routers.
    """
    main_router = Router()

    main_router.include_routers(
        *[
            x.router
            for x in [
                _start,
                _help,
                _drop_message,
                _singles,
                _playlists,
                _subscriptions,
                # MUST BE THE LAST
                _search,
            ]
        ]
    )

    return main_router
