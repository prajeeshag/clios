import inspect
from inspect import Parameter as IParameter
from typing import Annotated, Any, Callable, ForwardRef, Generic, get_args, get_origin

from pydantic import PydanticSchemaGenerationError
from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref

from clios.operator.params import Input, Param

from .model import InputType, OperatorFn, Parameter, ParameterKind

_builtin_generic_types = [  # type: ignore
    list,
    dict,
    set,
    tuple,
    frozenset,
]


def _is_generic_type(t: Any) -> bool:
    print("t=", t)
    return issubclass(t, Generic) or t in _builtin_generic_types


def get_operator_fn(func: Callable[..., Any]) -> OperatorFn:
    signature = get_typed_signature(func)
    Parameters: list[Parameter] = []

    var_input_encountered = False
    for param in signature.parameters.values():
        parameter = get_parameter(param)
        if var_input_encountered and parameter.input_type in (
            InputType.INPUT,
            InputType.VAR_INPUT,
        ):
            assert False, "Cannot have more Input parameters after an Input parameter of type `list`"
        if parameter.input_type == InputType.VAR_INPUT:
            var_input_encountered = True
        Parameters.append(parameter)

    return_type = signature.return_annotation

    return OperatorFn(
        parameters=tuple(Parameters),
        return_type=return_type,
        callback=func,
    )


def get_parameter(param: IParameter) -> Parameter:
    assert (
        param.annotation is not inspect.Signature.empty
    ), f"Missing type annotation for parameter `{param.name}`"
    type_ = (
        get_args(param.annotation)[0]
        if get_origin(param.annotation) is Annotated
        else param.annotation
    )
    assert type_ is not Any, f"Input parameter `{param.name}` cannot be of type `Any`"

    try:
        is_generic = _is_generic_type(type_)
    except TypeError:
        raise AssertionError(
            f"Unsupported type annotation for parameter `{param.name}`"
        )
    assert (
        not is_generic
    ), f"Missing type argument for generic class in parameter `{param.name}`"

    parameter_type = get_annotated_parameter_type(param)

    if parameter_type is None:
        if param.kind in (
            IParameter.VAR_POSITIONAL,
            IParameter.VAR_KEYWORD,
        ):
            parameter_type = InputType.PARAMETER
        else:
            if get_origin(type_) is list:
                parameter_type = InputType.VAR_INPUT
            else:
                parameter_type = InputType.INPUT
    elif parameter_type == InputType.INPUT:
        assert param.kind not in (
            IParameter.VAR_POSITIONAL,
            IParameter.VAR_KEYWORD,
        ), f"Input parameter `{param.name}` cannot be of `VARIADIC` kind"
        if get_origin(type_) is list:
            parameter_type = InputType.VAR_INPUT
        else:
            parameter_type = InputType.INPUT

    default = param.default
    if param.default is inspect.Signature.empty:
        default = None

    if parameter_type in [InputType.INPUT, InputType.VAR_INPUT]:
        assert (
            default is None
        ), f"Input parameter `{param.name}` cannot have a default value"

    try:
        parameter = Parameter(
            name=param.name,
            kind=ParameterKind(param.kind),
            input_type=parameter_type,
            annotation=param.annotation,
            default=default,
        )
    except PydanticSchemaGenerationError:
        raise AssertionError(
            f"Unsupported type annotation for parameter `{param.name}`"
        )
    except ValueError as e:
        if str(e) == "Variable tuples can only have one type":
            raise AssertionError(
                f"Unsupported type annotation for parameter `{param.name}`"
            )
        else:
            raise

    return parameter


def get_annotated_parameter_type(param: inspect.Parameter) -> InputType | None:
    if get_origin(param.annotation) is not Annotated:
        return None

    annotated_args = get_args(param.annotation)

    for arg in reversed(annotated_args):
        if isinstance(arg, (Param, Input)):
            if isinstance(arg, Param):
                return InputType.PARAMETER
            return InputType.INPUT


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param.annotation, globalns),
        )
        for param in signature.parameters.values()
    ]
    return_annotation = signature.return_annotation

    if return_annotation is inspect.Signature.empty:
        return_annotation = None

    globalns = getattr(call, "__globals__", {})
    return_annotation = get_typed_annotation(return_annotation, globalns)
    typed_signature = inspect.Signature(
        typed_params, return_annotation=return_annotation
    )
    return typed_signature


def get_typed_annotation(annotation: Any, globalns: dict[str, Any]) -> Any:
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation
