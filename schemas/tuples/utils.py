from typing import NamedTuple

from aiogram.utils.keyboard import InlineKeyboardBuilder


class PageContentResult[T](NamedTuple):
    content: list[T]
    nav_builder: InlineKeyboardBuilder
    drop_builder: InlineKeyboardBuilder
    start_idx: int
