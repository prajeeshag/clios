from dataclasses import dataclass
from typing import Callable

from clio.operator._utils import inspect_function

from ..exceptions import InvalidFunction
from ._utils import type2str


@dataclass(frozen=True)
class Reader:
    fn: Callable[[str], object]
    dtype: type

    def __call__(self, input: str) -> object:
        output = self.fn(input)
        if not isinstance(output, self.dtype):
            raise TypeError(
                f"Expected <{type2str(self.dtype)}> but received <{type2str(type(output))}> from function",
                self.fn,
            )
        return output


def reader_factory(fn: Callable[[str], object]) -> Reader:
    _, params, output_type = inspect_function(fn)

    if output_type is None or output_type is type(None):
        raise InvalidFunction("Return type cannot be 'None'", fn)

    try:
        isinstance("", output_type)
    except Exception:
        raise InvalidFunction(f"type <{output_type}> is not supported", fn)

    if len(params) != 1:
        raise InvalidFunction("Should have a single input parameter of type <str>", fn)

    if params[0][1] is not str:
        raise InvalidFunction("Should have a single input parameter of type <str>", fn)

    return Reader(fn, output_type)
