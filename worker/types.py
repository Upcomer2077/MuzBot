from typing import NamedTuple


class DownloadResult(NamedTuple):
    file_id: str | None
    is_too_large: bool
    is_error: bool
