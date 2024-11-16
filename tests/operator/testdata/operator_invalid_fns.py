# type: ignore
import sys
from dataclasses import dataclass
from typing import Annotated, Any

from clios.operator.params import Input

from .utils import list_functions


@dataclass
class InputFailing:
    fn: Any
    e: AssertionError


def ff00(i) -> int:
    """Missing type annotation for parameter `i`"""


def ff01(input0) -> int:
    """Missing type annotation for parameter `input0`"""


def ff19(input2: [Any, Input()]) -> int:
    """Unsupported type annotation for parameter `input2`"""


def ff17(**kwds: Annotated[int, Input()]) -> int:
    """Input parameter `kwds` cannot be keyword argument"""


def ff21(input1: list) -> int:
    """Missing type argument for generic class in parameter `input1`"""


def ff22(input1: tuple) -> int:
    """Missing type argument for generic class in parameter `input1`"""


def ff23(input1: Annotated[tuple, Input()]) -> int:
    """Missing type argument for generic class in parameter `input1`"""


def ff24(input1: Annotated[[int, str, ...], Input()]) -> int:
    """Unsupported type annotation for parameter `input1`"""


def ff08(i: Annotated[int, Input()] = 10) -> int:
    """Input parameter `i` cannot have a default value"""


def ff30(*, i: Annotated[int, Input()]) -> int:
    """Input parameter `i` cannot be keyword argument"""


def ff31(**i: Annotated[int, Input()]) -> int:
    """Input parameter `i` cannot be keyword argument"""


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, AssertionError(fn.__doc__)) for fn in ff_fns]
