from typing import Any, Callable, Protocol

from pydantic.dataclasses import dataclass

from .model import OperatorFn


class OperatorProtocol(Protocol):
    def execute(self) -> Any: ...


@dataclass(frozen=True)
class _OpBase:
    operator_fn: OperatorFn
    args: tuple[str, ...] = ()
    kwds: dict[str, str] = {}

    def __post_init__(self):
        pass


@dataclass(frozen=True)
class Operator(_OpBase):
    operator_fn: OperatorFn
    args: tuple[str, ...] = ()
    kwds: dict[str, str] = {}
    inputs: tuple[OperatorProtocol, ...] = ()

    def execute(self) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class LeafOperator(_OpBase):
    operator_fn: OperatorFn
    args: tuple[str, ...] = ()
    kwds: dict[str, str] = {}

    def execute(self) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Parser:
    fn: Callable[[str], Any]
    arg: str

    def execute(self) -> Any:
        return self.fn(self.arg)
