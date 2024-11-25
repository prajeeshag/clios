# from dataclasses import dataclass
import inspect as i
import typing as t
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from pydantic import BeforeValidator, ConfigDict, PydanticUserError, Strict, TypeAdapter
from pydantic.functional_validators import AfterValidator, PlainValidator, WrapValidator
from typing_extensions import Doc

from .param_info import Input, Output, Param, ParamTypes
from .utils import get_parameter_type_annotation


def _get_type(annotation: t.Any):
    if t.get_origin(annotation) is t.Annotated:
        return t.get_args(annotation)[0]
    return annotation


def _init_validator(
    info: ParamTypes,
    annotation: t.Any,
    phase_validators: tuple[t.Callable[[t.Any], t.Any], ...],
    phase: str,
) -> TypeAdapter[t.Any]:
    validators = [BeforeValidator(validator) for validator in phase_validators]
    if info.core_validation_phase != phase:
        annotation = t.Any

    if validators:
        annotation = t.Annotated[annotation, *validators]  # type: ignore

    if info.strict and _get_type(annotation) is not t.Any:
        annotation = t.Annotated[annotation, Strict()]

    try:
        return TypeAdapter(annotation, config=ConfigDict(arbitrary_types_allowed=True))
    except PydanticUserError as e:
        if e.code == "type-adapter-config-unused":
            return TypeAdapter(annotation)
        raise


def _get_description(annotation: t.Any) -> str:
    if t.get_origin(annotation) is t.Annotated:
        for arg in t.get_args(annotation)[::-1]:
            if isinstance(arg, Doc):
                return arg.documentation
    return ""


class ParameterKind(Enum):
    # POSITIONAL_OR_KEYWORD is as POSITIONAL_ONLY
    POSITIONAL_ONLY = i.Parameter.POSITIONAL_ONLY
    VAR_POSITIONAL = i.Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = i.Parameter.KEYWORD_ONLY
    VAR_KEYWORD = i.Parameter.VAR_KEYWORD

    @classmethod
    def _missing_(cls, value: object) -> "ParameterKind":
        if value == i.Parameter.POSITIONAL_OR_KEYWORD:
            return cls.POSITIONAL_ONLY
        return super()._missing_(value)


@dataclass(frozen=True)
class _Empty:
    pass


@dataclass
class ParamVal:
    val: t.Any
    key: str = ""


@dataclass(frozen=True)
class Parameter:
    """A dataclass to represent a parameter of an operator function"""

    empty: t.ClassVar[_Empty] = _Empty()
    name: str
    kind: ParameterKind
    info: ParamTypes
    annotation: t.Any
    build_phase_validator: TypeAdapter[t.Any]
    execute_phase_validator: TypeAdapter[t.Any]
    description: str
    default: t.Any

    @classmethod
    def validate(cls, param: i.Parameter, implicit: str) -> "Parameter":
        assert (
            param.annotation is not i.Signature.empty
        ), f"Missing type annotation for parameter `{param.name}`"
        type_ = (
            t.get_args(param.annotation)[0]
            if t.get_origin(param.annotation) is t.Annotated
            else param.annotation
        )

        assert not _is_not_supported(
            type_
        ), f"Unsupported type annotation for parameter `{param.name}`"

        default = param.default
        if param.default is i.Signature.empty:
            default = Parameter.empty

        param_type = get_parameter_type_annotation(param)
        if param_type is None:
            if implicit == "input":
                param_type = Input()
            elif implicit == "param":
                param_type = Param()
            else:
                raise AssertionError(f"Invalid implicit option `{implicit}`")
        kind = ParameterKind(param.kind)

        if isinstance(param_type, Input):
            assert kind not in (
                ParameterKind.VAR_KEYWORD,
                ParameterKind.KEYWORD_ONLY,
            ), f"Input parameter `{param.name}` cannot be keyword argument"

            assert (
                default is Parameter.empty
            ), f"Input parameter `{param.name}` cannot have a default value"

        build_phase_validator = _init_validator(
            param_type,
            param.annotation,
            param_type.build_phase_validators,
            "build",
        )
        execute_phase_validator = _init_validator(
            param_type,
            param.annotation,
            param_type.execute_phase_validators,
            "execute",
        )

        description = _get_description(param.annotation)
        return cls(
            name=param.name,
            kind=kind,
            info=param_type,
            annotation=param.annotation,
            build_phase_validator=build_phase_validator,
            execute_phase_validator=execute_phase_validator,
            description=description,
            default=default,
        )

    @property
    def is_input(self):
        """Check if the parameter is an input"""
        return isinstance(self.info, Input)

    @property
    def is_param(self):
        """Check if the parameter is a parameter"""
        return isinstance(self.info, Param)

    @property
    def type_(self):
        """Get the data type of the parameter"""
        return _get_type(self.annotation)

    @property
    def is_var_keyword(self):
        """Check if the parameter is a variable keyword"""
        return self.kind == ParameterKind.VAR_KEYWORD

    @property
    def is_var_input(self):
        """Check if the parameter is a variable input"""
        return self.is_input and self.kind == ParameterKind.VAR_POSITIONAL

    @property
    def is_var_param(self):
        """Check if the parameter is a variable parameter"""
        return self.is_param and self.kind == ParameterKind.VAR_POSITIONAL

    @property
    def is_keyword_param(self):
        """Check if the parameter is a keyword parameter"""
        return self.kind == ParameterKind.KEYWORD_ONLY and not self.is_input

    @property
    def is_positional_param(self):
        """Check if the parameter is a positional parameter"""
        return self.kind == ParameterKind.POSITIONAL_ONLY and not self.is_input

    @property
    def is_required(self):
        """Check if the parameter is required"""
        if self.is_input:
            return True

        if self.is_var_param or self.is_var_keyword:
            return False

        return self.default is Parameter.empty


@dataclass(frozen=True)
class ReturnValue:
    """A dataclass to represent the return type of an operator function"""

    validator: TypeAdapter[t.Any]
    annotation: t.Any
    info: Output

    @classmethod
    def validate(cls, annotation: t.Any, info: Output) -> "ReturnValue":
        prohibited_validators = (PlainValidator, WrapValidator, AfterValidator)
        type_adapter: TypeAdapter[t.Any]
        if _get_type(annotation) is None:
            type_adapter = TypeAdapter(None)
            info = Output(info.callback, num_outputs=0)
        else:
            if t.get_origin(annotation) is t.Annotated:
                if any(
                    isinstance(arg, prohibited_validators)
                    for arg in t.get_args(annotation)[1:]
                ):
                    raise AssertionError(
                        "Only `BeforeValidator` is allowed on return value!"
                    )
            annotation = t.Annotated[annotation, Strict()]
            type_adapter = TypeAdapter(
                annotation, config=ConfigDict(arbitrary_types_allowed=True)
            )
        return cls(type_adapter, annotation, info)

    @property
    def type_(self):
        return _get_type(self.annotation)


class Parameters(tuple[Parameter, ...]):
    @cached_property
    def required_keywords(self) -> dict[str, Parameter]:
        """Get a dictionary of required keyword arguments"""
        return {
            param.name: param
            for param in self
            if param.is_keyword_param and param.is_required
        }

    def iter_positional_arguments(self) -> t.Generator[Parameter, None, None]:
        """Iterate over positional arguments"""
        for param in self:
            if param.is_positional_param:
                yield param
        while self.var_argument is not None:
            yield self.var_argument

    def iter_inputs(self) -> t.Generator[Parameter, None, None]:
        """Iterate over input arguments"""
        for param in self:
            if param.is_input and not param.is_var_input:
                yield param
        while self.var_input is not None:
            yield self.var_input

    def iter_positional(self) -> t.Generator[Parameter, None, None]:
        """Iterate over positional (i.e. both input and arguments)"""
        var_param = None
        for param in self:
            if param.is_var_param or param.is_var_input:
                var_param = param
                break
            if param.is_keyword_param or param.is_var_keyword:
                break
            yield param

        while var_param is not None:
            yield var_param

    def get_keyword_argument(self, key: str) -> Parameter:
        """Get the keyword argument by key"""
        for param in self:
            if param.is_keyword_param:
                if param.name == key:
                    return param
        if self.var_keyword is not None:
            return self.var_keyword
        raise KeyError(f"Unknown keyword argument: {key}")

    @cached_property
    def var_argument(self) -> Parameter | None:
        """Get the variable positional argument, if any"""
        for param in self:
            if param.is_var_param:
                return param
        return None

    @cached_property
    def var_keyword(self) -> Parameter | None:
        """Get the variable keyword argument, if any"""
        for param in self:
            if param.is_var_keyword:
                return param
        return None

    @cached_property
    def num_minimum_inputs(self) -> int:
        """Get the number of minimum required input parameters"""
        return len([param for param in self if param.is_input])

    @cached_property
    def input_present(self) -> int:
        """Check if there is any input parameter"""
        for param in self:
            if param.is_input:
                return True
        return False

    @cached_property
    def var_input(self) -> Parameter | None:
        """Get the variable input parameter, if any"""
        for param in self:
            if param.is_var_input:
                return param
        return None

    @cached_property
    def num_required_args(self) -> int:
        """Get the number of required positional arguments"""
        params = [
            param for param in self if param.is_required and param.is_positional_param
        ]
        return len(params)


def _is_not_supported(type_: t.Any) -> bool:
    _builtin_generic_types = [  # type: ignore
        list,
        dict,
        set,
        tuple,
        frozenset,
    ]

    return not isinstance(type_, type) or type_ in _builtin_generic_types
