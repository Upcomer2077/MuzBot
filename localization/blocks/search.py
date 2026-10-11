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
