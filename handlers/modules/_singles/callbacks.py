from aiogram.filters.callback_data import CallbackData


class DownloadCallback(CallbackData, prefix="dl"):
    """Callback data schema defining expected inline keyboard button parameters for handling individual audio download requests."""

    video_id: str
    idx: str
