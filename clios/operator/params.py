from typing import Any, Callable

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class _ParamBase:
    strict: bool = False


@dataclass(frozen=True)
class Param(_ParamBase):
    pass


@dataclass(frozen=True)
class Input(_ParamBase):
    strict: bool = True
    parser: Callable[[str], Any] | None = str


ParamTypes = Param | Input


@dataclass(frozen=True)
class Output:
    file_saver: Callable[[Any, str], None] | None = None
