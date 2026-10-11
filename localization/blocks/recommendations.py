from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _RecommendationsBlock:
    rec_error_unknown: Literal["rec_error_unknown"] = "rec_error_unknown"
    rec_limit_rate: Literal["rec_limit_rate"] = "rec_limit_rate"
    rec_searching: Literal["rec_searching"] = "rec_searching"
    rec_error_invalid_file: Literal["rec_error_invalid_file"] = "rec_error_invalid_file"
    rec_error_unrecognized_forward: Literal["rec_error_unrecognized_forward"] = (
        "rec_error_unrecognized_forward"
    )
    rec_error_not_found: Literal["rec_error_not_found"] = "rec_error_not_found"
    rec_results_title: Literal["rec_results_title"] = "rec_results_title"
    rec_results_title_pag: Literal["rec_results_title_pag"] = "rec_results_title_pag"
