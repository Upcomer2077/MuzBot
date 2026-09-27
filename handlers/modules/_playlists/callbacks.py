from aiogram.filters.callback_data import CallbackData


class DownloadPlaylistCallback(CallbackData, prefix="dlp"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual playlist download requests."""

    playlist_id: str
