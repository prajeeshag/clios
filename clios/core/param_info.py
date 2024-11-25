from typing import Any, Callable, Literal

from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class _ParamInfoBase:
    strict: bool = False
    build_phase_validators: tuple[Callable[[Any], Any], ...] = ()
    execute_phase_validators: tuple[Callable[[Any], Any], ...] = ()
    core_validation_phase: Literal["build", "execute"] = "build"


@dataclass(frozen=True)
class Param(_ParamInfoBase):
    pass


@dataclass(frozen=True)
class Input(_ParamInfoBase):
    pass


ParamTypes = Param | Input


@dataclass(frozen=True)
class Output:
    callback: Callable[..., None] | None = None
    num_outputs: NonNegativeInt = 1
