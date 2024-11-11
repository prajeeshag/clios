from dataclasses import dataclass
from typing import Any

from pydatic.field import FieldInfo


class ArgumentType:
    POSITIONAL = "positional"
    KEYWORD = "keyword"
    POSITIONAL_OR_KEYWORD = "positional_or_keyword"
    VAR_POSITIONAL = "var_positional"
    VAR_KEYWORD = "var_keyword"


@dataclass(frozen=True)
class Argument:
    name: str
    default: Any
    type_: ArgumentType
    field_info: FieldInfo
