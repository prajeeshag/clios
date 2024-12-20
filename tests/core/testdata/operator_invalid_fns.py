# type: ignore
import sys
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import AfterValidator

from clios.core.param_info import Input

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


def ff21(input1: list) -> int:
    """Unsupported type annotation for parameter `input1`"""


def ff22(input1: tuple) -> int:
    """Unsupported type annotation for parameter `input1`"""


def ff23(input1: Annotated[tuple, Input()]) -> int:
    """Unsupported type annotation for parameter `input1`"""


def ff24(input1: Annotated[[int, str, ...], Input()]) -> int:
    """Unsupported type annotation for parameter `input1`"""


def ff25(*, input1: Annotated[int, Input()]) -> int:
    """Input parameter `input1` cannot be keyword argument"""


def ff26() -> Annotated[int, AfterValidator(int)]:
    """Only `BeforeValidator` is allowed on return value!"""


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, AssertionError(fn.__doc__)) for fn in ff_fns]


def ffp08(i: Annotated[int, Input()] = 10) -> int:
    """Input parameter `i` cannot have a default value"""


def ffp30(*, i: Annotated[int, Input()]) -> int:
    """Input parameter `i` cannot be keyword argument"""


def ffp31(**i: Annotated[int, Input()]) -> int:
    """Input parameter `i` cannot be keyword argument"""


ff_fns = list_functions(_current_module, "ffp")
failing_parameter_validation = [
    InputFailing(fn, AssertionError(fn.__doc__)) for fn in ff_fns
]
