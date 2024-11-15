from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from clios.exceptions import ArgumentError

from .model import OperatorFn


class OperatorProtocol(Protocol):
    def execute(self) -> Any: ...


@dataclass(frozen=True)
class _OpBase:
    operator_fn: OperatorFn
    args: tuple[str, ...] = ()
    kwds: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.verify_arguments()
        self.verify_keywords()

    def verify_keywords(self):
        required_kwds_keys = self.operator_fn.required_kwds.keys()
        kwds_keys = self.operator_fn.kwds.keys()
        for key in required_kwds_keys:
            if key not in self.kwds:
                raise ArgumentError(f"Missing required keyword argument: {key}")
        if self.operator_fn.var_kwds is None:
            for key in self.kwds:
                if key not in kwds_keys:
                    raise ArgumentError(f"Unexpected keyword argument: {key}")

    def verify_arguments(self):
        len_required_args = len(self.operator_fn.required_args)
        if len(self.args) < len_required_args:
            raise ArgumentError(
                f"Expected at least {len_required_args} positional arguments, got {len(self.args)}"
            )
        if (
            len(self.args) > len(self.operator_fn.args)
            and self.operator_fn.var_args is None
        ):
            raise ArgumentError(
                f"Expected at most {len(self.operator_fn.args)} arguments, got {len(self.args)}"
            )

    def validate_arguments(self) -> tuple[Any, ...]:
        arg_values: list[Any] = []
        iter_args = self.operator_fn.iter_args()
        for val in self.args:
            param = next(iter_args)
            arg_values.append(param.validate(val))
        return tuple(arg_values)

    def validate_keywords(self) -> dict[str, Any]:
        arg_values: dict[str, Any] = {}
        for key, val in self.kwds.items():
            param = self.operator_fn.get_kwd(key)
            arg_values[key] = param.validate(val)
        return arg_values


@dataclass(frozen=True)
class Operator(_OpBase):
    inputs: tuple[OperatorProtocol, ...] = ()

    def execute(self) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class LeafOperator(_OpBase):
    def execute(self) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Parser:
    fn: Callable[[str], Any]
    arg: str

    def execute(self) -> Any:
        return self.fn(self.arg)
