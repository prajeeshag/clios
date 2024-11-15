# from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from inspect import Parameter as InspectParameter
from typing import Annotated, Any, Callable, get_args, get_origin

from pydantic import BeforeValidator, Strict, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic.functional_validators import AfterValidator, PlainValidator, WrapValidator

from clios.operator.params import Input, Output, Param, ParamTypes


def _get_type(annotation: Any):
    if get_origin(annotation) is Annotated:
        return get_args(annotation)[0]
    return annotation


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
        self._validate_input_param()
        self._init_build_phase_validator()
        self._init_execute_phase_validator()

    def _validate_input_param(self):
        if not self.is_input:
            return
        assert self.kind not in (
            ParameterKind.VAR_KEYWORD,
            ParameterKind.KEYWORD_ONLY,
        ), f"Input parameter `{self.name}` cannot be keyword argument"

        assert (
            self.default is None
        ), f"Input parameter `{self.name}` cannot have a default value"

    def _init_build_phase_validator(self):
        self._build_phase_validator: TypeAdapter[Any] = self._init_validator(
            self.param_type.build_phase_validators, "build"
        )

    def _init_execute_phase_validator(self):
        self._execute_phase_validator: TypeAdapter[Any] = self._init_validator(
            self.param_type.execute_phase_validators, "execute"
        )

    def _init_validator(
        self,
        phase_validators: tuple[Callable[[Any], Any], ...],
        phase: str,
    ) -> TypeAdapter[Any]:
        validators = [BeforeValidator(validator) for validator in phase_validators]
        annotation = Any
        if self.param_type.core_validation_phase == phase:
            annotation = self.annotation

        if validators:
            annotation = Annotated[annotation, *validators]

        if self.param_type.strict and _get_type(annotation) is not Any:
            annotation = Annotated[annotation, Strict()]

        return TypeAdapter(annotation)

    def validate_build(self, value: Any) -> Any:
        return self._build_phase_validator.validate_python(value)

    def validate_execute(self, value: Any) -> Any:
        return self._execute_phase_validator.validate_python(value)

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
    def is_var_keyword(self):
        return self.kind == ParameterKind.VAR_KEYWORD

    @property
    def is_var_input(self):
        return self.is_input and self.kind == ParameterKind.VAR_POSITIONAL

    @property
    def is_var_param(self):
        return self.is_param and self.kind == ParameterKind.VAR_POSITIONAL

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

    @property
    def is_var_positional(self):
        return self.kind == ParameterKind.VAR_POSITIONAL

    @property
    def required(self):
        return self.default is None


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
    def args(self) -> tuple[Parameter, ...]:
        params = [param for param in self.parameters if param.is_positional_param]
        return tuple(params)

    @cached_property
    def var_args(self) -> Parameter | None:
        for param in self.parameters:
            if param.is_var_param:
                return param
        return None

    @cached_property
    def kwds(self) -> dict[str, Parameter]:
        return {
            param.name: param for param in self.parameters if param.is_keyword_param
        }

    @cached_property
    def var_kwds(self) -> Parameter | None:
        for param in self.parameters:
            if param.is_var_keyword:
                return param
        return None

    @cached_property
    def inputs(self) -> tuple[Parameter, ...]:
        params = [
            param
            for param in self.parameters
            if param.is_input and not param.is_var_input
        ]
        return tuple(params)

    @cached_property
    def num_inputs(self) -> int:
        if self.var_input is not None:
            return -1
        return len(self.inputs)

    @cached_property
    def input_present(self) -> int:
        return not self.num_inputs == 0

    @cached_property
    def var_input(self) -> Parameter | None:
        for param in self.parameters:
            if param.is_var_input:
                return param
        return None

    @cached_property
    def required_args(self) -> tuple[Parameter, ...]:
        params = [
            param
            for param in self.parameters
            if param.is_positional_param and param.required
        ]
        return tuple(params)

    @cached_property
    def required_kwds(self) -> dict[str, Parameter]:
        return {
            param.name: param
            for param in self.parameters
            if param.is_keyword_param and param.required
        }

    def iter_args(self):
        for param in self.args:
            yield param
        while self.var_args is not None:
            yield self.var_args

    def iter_inputs(self):
        for param in self.inputs:
            yield param
        while self.var_input is not None:
            yield self.var_input

    def iter_positional_params(self):
        var_param = None
        for param in self.parameters:
            if param.is_var_positional:
                var_param = param
                break
            if param.is_keyword or param.is_var_keyword:
                break
            yield param

        while var_param is not None:
            yield var_param

    def get_kwd(self, key: str) -> Parameter:
        if key in self.kwds:
            return self.kwds[key]
        if self.var_kwds is not None:
            return self.var_kwds
        raise KeyError(f"Unexpected keyword argument: {key}")
