import inspect
from typing import Any, Callable, ForwardRef

from pydantic._internal._typing_extra import eval_type_lenient as evaluate_forwardref


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
