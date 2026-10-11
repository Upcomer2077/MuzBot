from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _AlbumsBlock:
    alb_limit_rate: Literal["alb_limit_rate"] = "alb_limit_rate"
    alb_prompt_performer: Literal["alb_prompt_performer"] = "alb_prompt_performer"
    alb_searching: Literal["alb_searching"] = "alb_searching"
    alb_not_found: Literal["alb_not_found"] = "alb_not_found"
    alb_results_title: Literal["alb_results_title"] = "alb_results_title"
    alb_results_title_pag: Literal["alb_results_title_pag"] = "alb_results_title_pag"
    # callback additions
    alb_action_limit_rate: Literal["alb_action_limit_rate"] = "alb_action_limit_rate"
    alb_searching_generic: Literal["alb_searching_generic"] = "alb_searching_generic"
    alb_error_failed: Literal["alb_error_failed"] = "alb_error_failed"
    alb_no_albums: Literal["alb_no_albums"] = "alb_no_albums"
    alb_albums_title: Literal["alb_albums_title"] = "alb_albums_title"
    alb_albums_title_pag: Literal["alb_albums_title_pag"] = "alb_albums_title_pag"
    alb_pl_error_db_failed: Literal["alb_pl_error_db_failed"] = "alb_pl_error_db_failed"
