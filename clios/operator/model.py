from dataclasses import dataclass
from enum import Enum
from inspect import Parameter as InspectParameter
from typing import Annotated, Any, Callable

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo


class ParameterKind(Enum):
    POSSITIONAL_ONLY = InspectParameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = InspectParameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = InspectParameter.VAR_POSITIONAL
    KEYWORD_ONLY = InspectParameter.KEYWORD_ONLY
    VAR_KEYWORD = InspectParameter.VAR_KEYWORD


class Parameter:
    name: str
    kind: ParameterKind
    field_info: FieldInfo

    def __post_init__(self):
        self._type_adapter: TypeAdapter[Any] = TypeAdapter(
            Annotated[self.field_info.annotation, self.field_info]
        )


@dataclass(frozen=True)
class OperatorFn:
    arguments: tuple[Parameter, ...]
    return_type: Any
    callback: Callable[..., Any]
