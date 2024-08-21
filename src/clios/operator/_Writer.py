import inspect
from dataclasses import dataclass
from typing import Callable

from ..exceptions import InvalidFunction
from ._utils import inspect_function

_empty = inspect.Parameter.empty


@dataclass
class Writer:
    fn: Callable[[object, *tuple[str, ...]], None]
    dtype: type
    num_outputs: int = 0

    def __call__(self, input: object, *fpaths: str) -> None:
        self.fn(input, *fpaths)


def writer_factory(fn: Callable[[object, *tuple[str, ...]], None]):
    _, params, _ = inspect_function(fn)
    if len(params) < 1:
        raise InvalidFunction("Should have atleast 1 parameter", fn)

    if params[0][1] is None:
        raise InvalidFunction("Should have valid type annotations", fn, params[0][0])

    for param in params:
        if param[0].startswith("*"):
            raise InvalidFunction("Cannot have variadic parameters", fn, param[0])
        if param[2] is not _empty:
            raise InvalidFunction("Cannot have optional arguments", fn, param[0])

    return Writer(fn, params[0][1], len(params[1:]))
