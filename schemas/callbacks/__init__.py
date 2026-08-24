from aiogram.filters.callback_data import CallbackData


class DropCallback(CallbackData, prefix="drop_m"): ...


class DownloadCallback(CallbackData, prefix="dl"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual audio download requests."""

    video_id: str
    idx: str


class DownloadPlaylistCallback(CallbackData, prefix="dlp"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual playlist download requests."""

    playlist_id: str


class SubCallback(CallbackData, prefix="sb"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual playlist download requests."""

    author_id: str


class UnSubCallback(CallbackData, prefix="usb"):
    author_id: str
