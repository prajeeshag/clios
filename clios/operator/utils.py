import inspect
from inspect import Parameter as IParameter
from typing import Annotated, Any, Callable, ForwardRef, Generic, get_args, get_origin

from pydantic import PydanticSchemaGenerationError, ValidationError
from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref

from clios.operator.params import Input, Output, Param, ParamTypes

from .model import OperatorFn, Parameter, ParameterKind, ReturnType

_builtin_generic_types = [  # type: ignore
    list,
    dict,
    set,
    tuple,
    frozenset,
]


def _is_generic_type(t: Any) -> bool:
    return issubclass(t, Generic) or t in _builtin_generic_types


def get_operator_fn(func: Callable[..., Any]) -> OperatorFn:
    signature = get_typed_signature(func)
    Parameters: list[Parameter] = []

    for param in signature.parameters.values():
        parameter = get_parameter(param)
        Parameters.append(parameter)

    return_annotation = signature.return_annotation

    output_info = get_output_info(return_annotation)

    return OperatorFn(
        parameters=tuple(Parameters),
        return_type=ReturnType(return_annotation, output_info),
        callback=func,
    )


def get_output_info(return_annotation: Any) -> Output:
    if get_origin(return_annotation) is not Annotated:
        return Output()

    for arg in reversed(get_args(return_annotation)[1:]):
        if isinstance(arg, Output):
            return arg

    return Output()


def get_parameter(param: IParameter) -> Parameter:
    assert (
        param.annotation is not inspect.Signature.empty
    ), f"Missing type annotation for parameter `{param.name}`"
    type_ = (
        get_args(param.annotation)[0]
        if get_origin(param.annotation) is Annotated
        else param.annotation
    )
    assert type_ is not Any, f"Parameter `{param.name}` cannot be of type `Any`"

    try:
        is_generic = _is_generic_type(type_)
    except TypeError:
        raise AssertionError(
            f"Unsupported type annotation for parameter `{param.name}`"
        )
    assert (
        not is_generic
    ), f"Missing type argument for generic class in parameter `{param.name}`"

    default = param.default
    if param.default is inspect.Signature.empty:
        default = None

    param_type = get_parameter_type_annotation(param)

    try:
        parameter = Parameter(
            name=param.name,
            kind=ParameterKind(param.kind),
            param_type=param_type,
            annotation=param.annotation,
            default=default,
        )
    except PydanticSchemaGenerationError:
        raise AssertionError(
            f"Unsupported type annotation for parameter `{param.name}`"
        )
    except ValidationError as e:
        error = e.errors()[0]
        if error["type"] == "assertion_error":
            if "ctx" in error and "error" in error["ctx"]:
                raise error["ctx"]["error"]
            else:
                raise
        else:
            raise
    except ValueError as e:
        if str(e) == "Variable tuples can only have one type":
            raise AssertionError(
                f"Unsupported type annotation for parameter `{param.name}`"
            )
        else:
            raise

    return parameter


def get_parameter_type_annotation(param: inspect.Parameter) -> ParamTypes:
    if get_origin(param.annotation) is Annotated:
        annotated_args = get_args(param.annotation)
        for arg in reversed(annotated_args):
            if isinstance(arg, (Param, Input)):
                return arg
    return Param()


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
