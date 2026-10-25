from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _CatalogBlock:
    cat_limit_rate: Literal["cat_limit_rate"] = "cat_limit_rate"
    cat_prompt_performer: Literal["cat_prompt_performer"] = "cat_prompt_performer"
    cat_searching: Literal["cat_searching"] = "cat_searching"
    cat_not_found: Literal["cat_not_found"] = "cat_not_found"
    cat_results_title: Literal["cat_results_title"] = "cat_results_title"
    cat_results_title_pag: Literal["cat_results_title_pag"] = "cat_results_title_pag"
    # catalog callback additions
    cat_action_limit_rate: Literal["cat_action_limit_rate"] = "cat_action_limit_rate"
    cat_searching_generic: Literal["cat_searching_generic"] = "cat_searching_generic"
    cat_error_failed: Literal["cat_error_failed"] = "cat_error_failed"
    cat_no_releases: Literal["cat_no_releases"] = "cat_no_releases"
    cat_releases_title: Literal["cat_releases_title"] = "cat_releases_title"
    cat_releases_title_pag: Literal["cat_releases_title_pag"] = "cat_releases_title_pag"
    cat_pl_error_db_failed: Literal["cat_pl_error_db_failed"] = "cat_pl_error_db_failed"
    cat_pl_has_no_singles: Literal["cat_pl_has_no_singles"] = "cat_pl_has_no_singles"
