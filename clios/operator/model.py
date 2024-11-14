# from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from inspect import Parameter as InspectParameter
from typing import Annotated, Any, Callable, get_args, get_origin

from pydantic import Strict, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic.functional_validators import AfterValidator, PlainValidator, WrapValidator

from clios.operator.params import Input, Output, Param, ParamTypes


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


@dataclass
class Parameter:
    name: str
    kind: ParameterKind
    param_type: ParamTypes
    annotation: Any
    default: Any = None

    def __post_init__(self):
        annotation = self.annotation
        if self.param_type.strict:
            if self.is_variadic_input:
                type_ = get_args(self.type_)[0]
                metadata = get_args(annotation)[1:]
                annotation = Annotated[
                    list[Annotated[type_, Strict()]], *metadata, Strict()
                ]
            else:
                annotation = Annotated[annotation, Strict()]

        if self.kind == ParameterKind.VAR_POSITIONAL:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(list[annotation])
        elif self.kind == ParameterKind.VAR_KEYWORD:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(dict[str, annotation])
        else:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(annotation)

    def validate(self, value: Any):
        return self._type_adapter.validate_python(value)

    @property
    def is_input(self):
        return isinstance(self.param_type, Input)

    @property
    def is_param(self):
        return isinstance(self.param_type, Param)

    @property
    def type_(self):
        if get_origin(self.annotation) is Annotated:
            return get_args(self.annotation)[0]
        return self.annotation

    @property
    def is_variadic_input(self):
        return self.is_input and get_origin(self.type_) is list

    @property
    def is_keyword_param(self):
        return self.kind == ParameterKind.KEYWORD_ONLY and not self.is_input

    @property
    def is_positional_param(self):
        return self.kind == ParameterKind.POSITIONAL_ONLY and not self.is_input

    @property
    def is_keyword(self):
        return self.kind == ParameterKind.KEYWORD_ONLY

    @property
    def is_positional(self):
        return self.kind == ParameterKind.POSITIONAL_ONLY


@dataclass
class ReturnType:
    annotation: Any = None
    info: Output = Output()

    def __post_init__(self):
        if self.type_ is None:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(None)
            return

        prohibited_validators = (PlainValidator, WrapValidator, AfterValidator)
        annotation = self.annotation
        if get_origin(self.annotation) is Annotated:
            metadata = [
                arg
                for arg in get_args(self.annotation)[1:]
                if not isinstance(arg, prohibited_validators)
            ]
            type_ = get_args(self.annotation)[0]
            if metadata:
                annotation = Annotated[type_, *metadata]
            else:
                annotation = type_
        annotation = Annotated[annotation, Strict()]
        self._type_adapter: TypeAdapter[Any] = TypeAdapter(annotation)

    def validate(self, value: Any):
        return self._type_adapter.validate_python(value)

    @property
    def type_(self):
        if get_origin(self.annotation) is Annotated:
            return get_args(self.annotation)[0]
        return self.annotation


@dataclass(frozen=True)
class OperatorFn:
    parameters: tuple[Parameter, ...]
    return_type: ReturnType
    callback: Callable[..., Any]

    @cached_property
    def positional_params(self) -> tuple[Parameter, ...]:
        params = [param for param in self.parameters if param.is_positional_param]
        return tuple(params)

    @cached_property
    def var_positional_param(self) -> Parameter | None:
        for param in self.parameters:
            if param.kind == ParameterKind.VAR_POSITIONAL:
                return param
        return None

    @cached_property
    def keyword_params(self) -> tuple[Parameter, ...]:
        params = [param for param in self.parameters if param.is_keyword_param]
        return tuple(params)

    @cached_property
    def var_keyword_param(self) -> Parameter | None:
        for param in self.parameters:
            if param.kind == ParameterKind.VAR_KEYWORD:
                return param
        return None

    @cached_property
    def input_params(self) -> tuple[Parameter, ...]:
        params = [param for param in self.parameters if param.is_input]
        return tuple(params)
