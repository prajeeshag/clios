import inspect
import typing as t
from inspect import Parameter as IParameter

from pydantic import PydanticSchemaGenerationError
from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref

from .operator_fn import OperatorFn
from .param_info import Input, Output, Param, ParamTypes
from .parameter import Parameter, ParameterKind, ReturnType

_builtin_generic_types = [  # type: ignore
    list,
    dict,
    set,
    tuple,
    frozenset,
]


def _is_generic_type(t: t.Any) -> bool:
    return issubclass(t, t.Generic) or t in _builtin_generic_types


Implicit = t.Literal["input", "param"]


def get_operator_fn(
    func: t.Callable[..., t.Any],
    implicit: Implicit = "input",
) -> OperatorFn:
    signature = get_typed_signature(func)
    Parameters: list[Parameter] = []

    for param in signature.parameters.values():
        parameter = get_parameter(param, implicit)
        Parameters.append(parameter)

    return_annotation = signature.return_annotation

    output_info = get_output_info(return_annotation)

    return OperatorFn(
        parameters=tuple(Parameters),
        output=ReturnType(return_annotation, output_info),
        callback=func,
    )


def get_output_info(return_annotation: t.Any) -> Output:
    if t.get_origin(return_annotation) is not t.Annotated:
        return Output()

    for arg in reversed(t.get_args(return_annotation)[1:]):
        if isinstance(arg, Output):
            return arg
    return Output()


def get_parameter(param: IParameter, implicit: Implicit) -> Parameter:
    assert (
        param.annotation is not inspect.Signature.empty
    ), f"Missing type annotation for parameter `{param.name}`"
    type_ = (
        t.get_args(param.annotation)[0]
        if t.get_origin(param.annotation) is t.Annotated
        else param.annotation
    )

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
        default = Parameter.empty

    param_type = get_parameter_type_annotation(param)
    if param_type is None:
        if implicit == "input":
            param_type = Input()
        elif implicit == "param":
            param_type = Param()
        else:
            raise AssertionError(f"Invalid implicit option `{implicit}`")

    try:
        return Parameter(
            name=param.name,
            kind=ParameterKind(param.kind),
            info=param_type,
            annotation=param.annotation,
            default=default,
        )
    except PydanticSchemaGenerationError:
        raise AssertionError(
            f"Unsupported type annotation for parameter `{param.name}`"
        )


def get_parameter_type_annotation(param: inspect.Parameter) -> ParamTypes | None:
    if t.get_origin(param.annotation) is t.Annotated:
        annotated_args = t.get_args(param.annotation)
        for arg in reversed(annotated_args):
            if isinstance(arg, (Param, Input)):
                return arg
    return None


def get_typed_signature(call: t.Callable[..., t.Any]) -> inspect.Signature:
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


def get_typed_annotation(annotation: t.Any, globalns: dict[str, t.Any]) -> t.Any:
    if isinstance(annotation, str):
        annotation = t.ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation
