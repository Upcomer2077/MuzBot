from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _SubscriptionsBlock:
    # list
    list_searching: Literal["subs_searching"] = "subs_searching"
    list_unknown_error: Literal["subs_unknown_error"] = "subs_unknown_error"
    list_not_found_query: Literal["subs_not_found_query"] = "subs_not_found_query"
    list_empty: Literal["subs_empty"] = "subs_empty"
    list_title: Literal["subs_title"] = "subs_title"
    list_title_pag: Literal["subs_title_pag"] = "subs_title_pag"
    # sub
    sub_prompt_performer: Literal["sub_prompt_performer"] = "sub_prompt_performer"
    sub_searching: Literal["sub_searching"] = "sub_searching"
    sub_not_found: Literal["sub_not_found"] = "sub_not_found"
    sub_results_title: Literal["sub_results_title"] = "sub_results_title"
    sub_results_title_pag: Literal["sub_results_title_pag"] = "sub_results_title_pag"
    sub_error_generic: Literal["sub_error_generic"] = "sub_error_generic"
    sub_limit_exceeded: Literal["sub_limit_exceeded"] = "sub_limit_exceeded"
    sub_success: Literal["sub_success"] = "sub_success"
    # usub
    usub_not_found: Literal["usub_not_found"] = "usub_not_found"
    usub_error_generic: Literal["usub_error_generic"] = "usub_error_generic"
    usub_success: Literal["usub_success"] = "usub_success"
