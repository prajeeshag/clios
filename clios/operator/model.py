from dataclasses import dataclass
from enum import Enum
from inspect import Parameter as InspectParameter
from typing import Any, Callable, Type

from pydantic import TypeAdapter


class ParameterKind(Enum):
    # POSITIONAL_OR_KEYWORD is as POSITIONAL_ONLY
    POSITIONAL_ONLY = InspectParameter.POSITIONAL_ONLY
    VAR_POSITIONAL = InspectParameter.VAR_POSITIONAL
    KEYWORD_ONLY = InspectParameter.KEYWORD_ONLY
    VAR_KEYWORD = InspectParameter.VAR_KEYWORD

    @classmethod
    def _missing_(cls, value: object) -> "ParameterKind":
        if value == InspectParameter.POSITIONAL_OR_KEYWORD:
            return cls.POSITIONAL_ONLY
        return super()._missing_(value)


class InputType(Enum):
    INPUT = "input"
    VAR_INPUT = "var_input"
    PARAMETER = "parameter"


@dataclass
class Parameter:
    name: str
    kind: ParameterKind
    input_type: InputType
    annotation: Any
    default: Any = None

    def __post_init__(self):
        if self.kind == ParameterKind.VAR_POSITIONAL:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(list[self.annotation])
        elif self.kind == ParameterKind.VAR_KEYWORD:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(
                dict[str, self.annotation]
            )
        else:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(self.annotation)

    def validate(self, value: Any):
        return self._type_adapter.validate_python(value)


@dataclass(frozen=True)
class OperatorFn:
    parameters: tuple[Parameter, ...]
    return_type: Type[Any]
    callback: Callable[..., Any]
