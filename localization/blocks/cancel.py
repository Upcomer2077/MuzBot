from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _CancelBlock:
    cancel_nothing: Literal["cancel_nothing"] = "cancel_nothing"
    cancel_success: Literal["cancel_success"] = "cancel_success"
