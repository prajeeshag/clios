# from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from inspect import Parameter as InspectParameter
from typing import Annotated, Any, Callable, ClassVar, NamedTuple, get_args, get_origin

from docstring_parser import parse as parse_docstring  # type: ignore
from pydantic import BeforeValidator, Strict, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic.functional_validators import AfterValidator, PlainValidator, WrapValidator
from typing_extensions import Doc

from .params import Input, Output, Param, ParamTypes


def _get_type(annotation: Any):
    if get_origin(annotation) is Annotated:
        return get_args(annotation)[0]
    return annotation


type_to_str = {
    int: "int",
    float: "float",
    str: "text",
    bool: "bool",
}


class ParamDoc(NamedTuple):
    """A named tuple to represent the documentation of a parameter"""

    repr: str
    type_: str = "text"
    default: str = ""
    description: str = ""


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


@dataclass(frozen=True)
class _Empty:
    def __str__(self) -> str:
        return ""


@dataclass
class Parameter:
    """A dataclass to represent a parameter of an operator function"""

    empty: ClassVar[_Empty] = _Empty()
    name: str
    kind: ParameterKind
    param_type: ParamTypes
    annotation: Any
    default: Any = empty

    def __post_init__(self):
        self._validate_input_param()
        self._init_build_phase_validator()
        self._init_execute_phase_validator()
        self._init_doc()

    def _init_doc(self):
        self._description = ""
        if get_origin(self.annotation) is Annotated:
            for arg in get_args(self.annotation)[::-1]:
                if isinstance(arg, Doc):
                    self._description = arg.documentation
                    break
        self._type_doc = "text"
        if _get_type(self.type_) in type_to_str:
            self._type_doc = type_to_str[_get_type(self.type_)]

        self._default_doc = str(self.default)
        if self.default == "":
            self._default_doc = "''"

    def _validate_input_param(self):
        if not self.is_input:
            return
        assert self.kind not in (
            ParameterKind.VAR_KEYWORD,
            ParameterKind.KEYWORD_ONLY,
        ), f"Input parameter `{self.name}` cannot be keyword argument"

        assert (
            self.default is Parameter.empty
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

    def get_doc(self) -> ParamDoc:
        return ParamDoc(
            repr=self.repr,
            type_=self._type_doc,
            default=self._default_doc,
            description=self._description,
        )

    # TODO: Add capability for custom representation in function signature
    @property
    def repr(self):
        res = self.name
        if self.is_keyword:
            res = f"{res}=<val>"
        if self.is_var_keyword:
            res = "<key>=<val>"
        return res

    @property
    def is_input(self):
        """Check if the parameter is an input"""
        return isinstance(self.param_type, Input)

    @property
    def is_param(self):
        """Check if the parameter is a parameter"""
        return isinstance(self.param_type, Param)

    @property
    def type_(self):
        """Get the data type of the parameter"""
        if get_origin(self.annotation) is Annotated:
            return get_args(self.annotation)[0]
        return self.annotation

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
    def is_keyword(self):
        """Check if the parameter is a keyword"""
        return self.kind == ParameterKind.KEYWORD_ONLY

    @property
    def is_positional(self):
        """Check if the parameter is a positional"""
        return self.kind == ParameterKind.POSITIONAL_ONLY

    @property
    def is_var_positional(self):
        """Check if the parameter is a variable positional"""
        return self.kind == ParameterKind.VAR_POSITIONAL

    @property
    def required(self):
        """Check if the parameter is required"""
        return self.default is Parameter.empty


@dataclass
class ReturnType:
    """A dataclass to represent the return type of an operator function"""

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
    """A dataclass to represent an operator function"""

    parameters: tuple[Parameter, ...]
    return_type: ReturnType
    callback: Callable[..., Any]

    @property
    def short_description(self):
        """Get the short description of the operator"""
        if not self.callback.__doc__:
            return ""
        return parse_docstring(self.callback.__doc__).short_description

    @property
    def long_description(self):
        """Get the long description of the operator"""
        if not self.callback.__doc__:
            return ""
        return parse_docstring(self.callback.__doc__).long_description

    def get_args_doc(self) -> list[ParamDoc]:
        """Get the documentation of the arguments"""
        docs = [param.get_doc() for param in self.args]
        if self.var_args is not None:
            docs.append(self.var_args.get_doc())
        return docs

    def get_kwds_doc(self) -> list[ParamDoc]:
        """Get the documentation of the keyword arguments"""
        docs = [param.get_doc() for param in self.kwds.values()]
        if self.var_kwds is not None:
            docs.append(self.var_kwds.get_doc())
        return docs

    def get_synopsis(self, name: str) -> str:
        """get the synopsis of the operator"""
        required_args = ",".join(param.repr for param in self.required_args)
        optional_args = ",".join(
            param.repr for param in self.args if not param.required
        )
        if self.var_args is not None:
            optional_args += "," + self.var_args.repr

        if optional_args:
            optional_args = f"[{optional_args},]"

        required_kwds = ",".join(param.repr for param in self.required_kwds.values())
        optional_kwds = ",".join(
            param.repr for param in self.kwds.values() if not param.required
        )
        if self.var_kwds is not None:
            optional_kwds += "," + self.var_kwds.repr

        if optional_kwds:
            optional_kwds = f"[{optional_kwds},]"

        inputs = " ".join(param.repr for param in self.inputs)

        if self.var_input is not None:
            inputs += " " + self.var_input.repr

        if self.return_type.info.num_outputs == 1:
            output = "output"
        else:
            output = " ".join(
                [f"output{i+1}" for i in range(self.return_type.info.num_outputs)]
            )

        synopsis = name
        if required_args:
            synopsis += f",{required_args}"
        if optional_args:
            synopsis += f",{optional_args}"
        if required_kwds:
            synopsis += f",{required_kwds}"
        if optional_kwds:
            synopsis += f",{optional_kwds}"
        if inputs:
            synopsis += f" {inputs}"
        if output:
            synopsis += f" {output}"

        return synopsis

    @cached_property
    def args(self) -> tuple[Parameter, ...]:
        """Get a tuple of positional arguments"""
        params = [param for param in self.parameters if param.is_positional_param]
        return tuple(params)

    @cached_property
    def var_args(self) -> Parameter | None:
        """Get the variable positional argument, if any"""
        for param in self.parameters:
            if param.is_var_param:
                return param
        return None

    @cached_property
    def kwds(self) -> dict[str, Parameter]:
        """Get a dictionary of keyword arguments"""
        return {
            param.name: param for param in self.parameters if param.is_keyword_param
        }

    @cached_property
    def var_kwds(self) -> Parameter | None:
        """Get the variable keyword argument, if any"""
        for param in self.parameters:
            if param.is_var_keyword:
                return param
        return None

    @cached_property
    def inputs(self) -> tuple[Parameter, ...]:
        """Get a tuple of input parameters"""
        params = [
            param
            for param in self.parameters
            if param.is_input and not param.is_var_input
        ]
        return tuple(params)

    @cached_property
    def num_inputs(self) -> int:
        """Get the number of input parameters"""
        if self.var_input is not None:
            return -1
        return len(self.inputs)

    @cached_property
    def input_present(self) -> int:
        """Check if there is any input parameter"""
        return not self.num_inputs == 0

    @cached_property
    def var_input(self) -> Parameter | None:
        """Get the variable input parameter, if any"""
        for param in self.parameters:
            if param.is_var_input:
                return param
        return None

    @cached_property
    def required_args(self) -> tuple[Parameter, ...]:
        """Get a tuple of required positional arguments"""
        params = [
            param
            for param in self.parameters
            if param.is_positional_param and param.required
        ]
        return tuple(params)

    @cached_property
    def required_kwds(self) -> dict[str, Parameter]:
        """Get a dictionary of required keyword arguments"""
        return {
            param.name: param
            for param in self.parameters
            if param.is_keyword_param and param.required
        }

    def iter_args(self):
        """Iterate over positional arguments"""
        for param in self.args:
            yield param
        while self.var_args is not None:
            yield self.var_args

    def iter_inputs(self):
        """Iterate over input parameters"""
        for param in self.inputs:
            yield param
        while self.var_input is not None:
            yield self.var_input

    def iter_positional_params(self):
        """Iterate over positional parameters (i.e. both input and arguments)"""
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
        """Get the keyword argument by key"""
        if key in self.kwds:
            return self.kwds[key]
        if self.var_kwds is not None:
            return self.var_kwds
        raise KeyError(f"Unexpected keyword argument: {key}")
