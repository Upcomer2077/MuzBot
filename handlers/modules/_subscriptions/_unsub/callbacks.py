from aiogram.filters.callback_data import CallbackData

from schemas.callbacks.pagination import PaginationBase


class UnSubCallback(CallbackData, prefix="usb"):
    author_id: str


class PaginationUSubsArtistsCallback(PaginationBase, prefix="usub"): ...
