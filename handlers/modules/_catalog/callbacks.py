from aiogram.filters.callback_data import CallbackData

from schemas.callbacks.pagination import PaginationBase


class CatalogCallback(CallbackData, prefix="cat"):
    author_id: str


class ShowSinglePlaylistContentCallback(CallbackData, prefix="s_spc"):
    playlist_id: str


class PaginationSingles1Callback(PaginationBase, prefix="sin1"): ...


class PaginationSingles2Callback(PaginationBase, prefix="sins2"): ...
