from aiogram.filters.callback_data import CallbackData

from schemas.callbacks.pagination import PaginationBase


class PaginationAlbums1Callback(PaginationBase, prefix="albs1"): ...


class PaginationAlbums2Callback(PaginationBase, prefix="albs2"): ...


class AlbumsCallback(CallbackData, prefix="alb"):
    author_id: str


class ShowAlbumPlaylistContentCallback(CallbackData, prefix="spc"):
    playlist_id: str
