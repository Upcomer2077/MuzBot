from typing import NamedTuple

from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import PAGINATION_ITEMS_PER_PAGE
from handlers._drop_message.callbacks import DropCallback
from schemas.callbacks.pagination import PaginationBase


class _PageContentResult[T](NamedTuple):
    content: list[T]
    nav_builder: InlineKeyboardBuilder
    drop_builder: InlineKeyboardBuilder
    start_idx: int


_MAX_ITEMS = 27 * 2


def get_page_content[T](
    search_result: list[T],
    page: int,
    pag_cb_type: type[PaginationBase],
    max: int = _MAX_ITEMS,
) -> _PageContentResult[T]:
    """Функция нарезки результатов и nav сборки клавиатуры"""
    start_idx = page * PAGINATION_ITEMS_PER_PAGE
    end_idx = start_idx + PAGINATION_ITEMS_PER_PAGE
    content = search_result[start_idx:end_idx]

    nav_builder = InlineKeyboardBuilder()
    drop_builder = InlineKeyboardBuilder()

    if page > 0:
        nav_builder.button(text="⬅️", callback_data=pag_cb_type(page=page - 1).pack())

    if end_idx < len(search_result) and (end_idx < max if max else True):
        nav_builder.button(text="➡️", callback_data=pag_cb_type(page=page + 1).pack())

    drop_builder.button(text="❌", callback_data=DropCallback())

    return _PageContentResult(content, nav_builder, drop_builder, start_idx)
