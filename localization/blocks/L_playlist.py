from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _PlaylistBlock:
    pl_prompt_link: Literal["pl_prompt_link"] = "pl_prompt_link"
    pl_error_no_link: Literal["pl_error_no_link"] = "pl_error_no_link"
    pl_searching: Literal["pl_searching"] = "pl_searching"
    pl_error_invalid_playlist: Literal["pl_error_invalid_playlist"] = (
        "pl_error_invalid_playlist"
    )
    pl_error_not_found: Literal["pl_error_not_found"] = "pl_error_not_found"
    pl_error_db_failed: Literal["pl_error_db_failed"] = "pl_error_db_failed"
    pl_found_title: Literal["pl_found_title"] = "pl_found_title"
    pl_found_title_limited: Literal["pl_found_title_limited"] = "pl_found_title_limited"
    pl_limit_warning: Literal["pl_limit_warning"] = "pl_limit_warning"
    pl_and_more: Literal["pl_and_more"] = "pl_and_more"
    pl_download_prompt: Literal["pl_download_prompt"] = "pl_download_prompt"

    # playlist download additions
    pl_downloading: Literal["pl_downloading"] = "pl_downloading"
    pl_download_error_generic: Literal["pl_download_error_generic"] = (
        "pl_download_error_generic"
    )
    pl_download_limit_rate: Literal["pl_download_limit_rate"] = "pl_download_limit_rate"
    pl_download_error_unknown: Literal["pl_download_error_unknown"] = (
        "pl_download_error_unknown"
    )
    pl_download_failed_title: Literal["pl_download_failed_title"] = (
        "pl_download_failed_title"
    )
    pl_download_failed_too_large: Literal["pl_download_failed_too_large"] = (
        "pl_download_failed_too_large"
    )
