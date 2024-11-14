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
        required_kwds_keys = self.operator_fn.required_kwds_keys
        kwds_keys = self.operator_fn.kwds_keys
        for key in required_kwds_keys:
            if key not in self.kwds:
                raise ArgumentError(f"Missing required keyword argument: {key}")
        if self.operator_fn.var_kwds is None:
            for key in self.kwds:
                if key not in kwds_keys:
                    raise ArgumentError(f"Unexpected keyword argument: {key}")

    def verify_arguments(self):
        if len(self.args) < len(self.operator_fn.required_args):
            raise ArgumentError(
                f"Expected at least {len(self.operator_fn.required_args)} positional arguments, got {len(self.args)}"
            )
        if (
            len(self.args) > len(self.operator_fn.args)
            and self.operator_fn.var_args is None
        ):
            raise ArgumentError(
                f"Expected at most {len(self.operator_fn.args)} arguments, got {len(self.args)}"
            )


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
