from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _SingleBlock:
    download_error_generic: Literal["single_download_error_generic"] = (
        "single_download_error_generic"
    )
    download_processing: Literal["single_download_processing"] = (
        "single_download_processing"
    )
    download_info_not_found: Literal["single_download_info_not_found"] = (
        "single_download_info_not_found"
    )
    download_limit_size_duration: Literal["single_download_limit_size_duration"] = (
        "single_download_limit_size_duration"
    )
    download_limit_rate: Literal["single_download_limit_rate"] = (
        "single_download_limit_rate"
    )
    download_error_failed: Literal["single_download_error_failed"] = (
        "single_download_error_failed"
    )

    # force additions
    force_prompt_link: Literal["single_force_prompt_link"] = "single_force_prompt_link"
    force_invalid_link: Literal["single_force_invalid_link"] = (
        "single_force_invalid_link"
    )
    force_invalid_link_retry: Literal["single_force_invalid_link_retry"] = (
        "single_force_invalid_link_retry"
    )
    force_id_not_recognized: Literal["single_force_id_not_recognized"] = (
        "single_force_id_not_recognized"
    )
