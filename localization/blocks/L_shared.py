from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _SharedBlock:
    too_old_result: Literal["too_old_result"] = "too_old_result"
