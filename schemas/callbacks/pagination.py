from abc import ABC

from aiogram.filters.callback_data import CallbackData


class PaginationBase(ABC, CallbackData, prefix="p"):
    page: int


class PaginationSearchCallback(PaginationBase, prefix="page"): ...


class PaginationSubsListCallback(PaginationBase, prefix="slits"): ...


class PaginationSubsArtistsCallback(PaginationBase, prefix="sub"): ...


class PaginationUSubsArtistsCallback(PaginationBase, prefix="usub"): ...
