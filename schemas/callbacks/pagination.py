from abc import ABC

from aiogram.filters.callback_data import CallbackData


class PaginationBase(ABC, CallbackData, prefix="p"):
    page: int
