from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _SearchBlock:
    search_limit_rate: Literal["search_limit_rate"] = "search_limit_rate"
    search_searching: Literal["search_searching"] = "search_searching"
    search_not_found: Literal["search_not_found"] = "search_not_found"
    search_results_title: Literal["search_results_title"] = "search_results_title"
    search_results_title_pag: Literal["search_results_title_pag"] = (
        "search_results_title_pag"
    )
    # inline
    inline_track_description: Literal["search_inline_track_description"] = (
        "search_inline_track_description"
    )
    inline_track_message: Literal["search_inline_track_message"] = (
        "search_inline_track_message"
    )
