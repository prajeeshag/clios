# type: ignore
import sys
from dataclasses import dataclass
from typing import Any

from clios.exceptions import InvalidFunction

from .utils import e_args, list_functions


@dataclass
class InputFailing:
    fn: Any
    e: InvalidFunction


def ff00(i) -> int:
    """
    Should have valid type annotation
    i
    """


def ff01(ik=1) -> int:
    """
    Should have valid type annotation
    ik
    """


def ff02(b: bool) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    b
    """


def ff03(bk: bool = False) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    bk
    """


def ff04(input: str = "") -> int:
    """
    The name 'input' is reserved for the `input` parameter and cannot used as an optional parameter
    """


def ff05(input: tuple[int, str, ...]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff06(input: list[int, str]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff07(input: tuple[int, ..., str]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff08(input: tuple[..., str]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff09(input: tuple[...]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff10(input: list[int, ...]) -> int:
    """
    Should have valid type annotation
    input
    """


def ff13(*b: bool) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    *b
    """


def ff14(ik: int = 10, *params: str) -> int:
    """
    Variadic positional arguments should be before keyword-arguments
    *params
    """


def ff15(ik: int, input: str, *params: str) -> int:
    """
    If present, the 'input' parameter should be the first parameter
    """


def ff16(i: list[str]) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    i
    """


def ff17(j: int, k: dict[str, str] = {"k": "j"}) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    k
    """


def ff18(j: int, *k: dict[str, str]) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    *k
    """


def ff19(j: int, **k: dict[str, str]) -> int:
    """
    Non-(str,int,float) types should be annotated with a <Reader>
    **k
    """


def ff23() -> list[int]:
    """
    Type <list[int]> is not supported
    """


def ff24() -> Any:
    """
    Type <typing.Any> is not supported
    """


def ff33():
    """
    Return type cannot be 'None'
    """


def ff34() -> None:
    """
    Return type cannot be 'None'
    """


_current_module = sys.modules[__name__]
ff_fns = list_functions(_current_module, "ff")
failing = [InputFailing(fn, InvalidFunction(*e_args(fn))) for fn in ff_fns]
