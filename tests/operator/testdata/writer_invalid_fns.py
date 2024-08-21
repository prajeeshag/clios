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


def ff00():
    """
    Should have atleast 1 parameter
    """


def ff01(i, c):
    """
    Should have valid type annotations
    i
    """


def ff02(i: int, *c) -> int:
    """
    Cannot have variadic parameters
    *c
    """


def ff03(i: int, **c) -> int:
    """
    Cannot have variadic parameters
    **c
    """


def ff04(i: int, c="s") -> int:
    """
    Cannot have optional arguments
    c
    """


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, InvalidFunction(*e_args(fn))) for fn in ff_fns]
