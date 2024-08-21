# type: ignore
import sys
from dataclasses import dataclass
from typing import Any

from clios.exceptions import InvalidFunction
from tests.operator.testdata.utils import list_functions

from .utils import e_args


@dataclass
class InputFailing:
    fn: Any
    e: InvalidFunction


def ff02(b: bool) -> str:
    """
    Should have a single input parameter of type <str>
    """


def ff05(i: str) -> list[str]:
    """
    type <list[str]> is not supported
    """


def ff06(i: str) -> None:
    """
    Return type cannot be 'None'
    """


def ff13(*b: bool) -> int:
    """
    Should have a single input parameter of type <str>
    """


def ff14(ik: int = 10, *params: str) -> int:
    """
    Should have a single input parameter of type <str>
    """


def ff15(ik: int, input: str, *params: str) -> int:
    """
    Should have a single input parameter of type <str>
    """


def ff16(i: list[str]) -> int:
    """
    Should have a single input parameter of type <str>
    """


def ff24(i) -> Any:
    """
    type <typing.Any> is not supported
    """


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, InvalidFunction(*e_args(fn))) for fn in ff_fns]
