from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class _LanguageBlock:
    lang_changed: Literal["lang_changed"] = "lang_changed"
    lang_select_text: Literal["lang_select_text"] = "lang_select_text"
