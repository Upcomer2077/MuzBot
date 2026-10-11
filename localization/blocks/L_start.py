from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _StartBlock:
    start: Literal["start"] = "start"
