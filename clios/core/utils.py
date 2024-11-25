import inspect
import typing as t

from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref

from .param_info import Input, Output, Param, ParamTypes


def get_output_info(return_annotation: t.Any) -> Output:
    if t.get_origin(return_annotation) is not t.Annotated:
        return Output()

    for arg in reversed(t.get_args(return_annotation)[1:]):
        if isinstance(arg, Output):
            return arg
    return Output()


def get_parameter_type_annotation(param: inspect.Parameter) -> ParamTypes | None:
    if t.get_origin(param.annotation) is t.Annotated:
        annotated_args = t.get_args(param.annotation)
        for arg in reversed(annotated_args[1:]):
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
