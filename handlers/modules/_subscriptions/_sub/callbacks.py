from aiogram.filters.callback_data import CallbackData

from schemas.callbacks.pagination import PaginationBase


class SubCallback(CallbackData, prefix="sb"):
    author_id: str


class PaginationSubsArtistsCallback(PaginationBase, prefix="sub"): ...
