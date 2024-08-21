# type: ignore
import sys
from dataclasses import dataclass
from typing import Any

from clio.exceptions import InvalidFunction

from .utils import e_args, list_functions


@dataclass
class InputFailing:
    fn: Any
    e: InvalidFunction


def ff00():
    """
    Must take a single 'input'
    """


def ff01(s: str) -> None:
    """
    Must take a single 'input'
    """


def ff02(input: tuple[int, ...]):
    """
    Must take a single 'input'
    """


def ff03(input: int, i: str, c: int) -> None:
    """
    Cannot have more than two arguments, including 'input'
    """


def ff04(input: int, i: str = "s"):
    """
    Cannot have keyword arguments
    """


def ff05(input: int, **i: int) -> None:
    """
    Cannot have variadic arguments
    """


def ff06(input: int, s: int) -> None:
    """
    The second argument must be of type <str>
    """


def ff07(input: int) -> int:
    """
    Should return 'None'
    """


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, InvalidFunction(*e_args(fn))) for fn in ff_fns]


@dataclass
class InputPassing:
    fn: Any
    data_type: type
    requires_file_path: bool


def fp00(input: float) -> None: ...
def fp02(input: int, c: str) -> None: ...


passing = [
    InputPassing(fp00, float, False),
    InputPassing(fp02, int, True),
]
