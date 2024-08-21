# type: ignore
from dataclasses import dataclass
from typing import Any

from clios.exceptions import InvalidFunction


@dataclass
class InputFailing:
    fn: Any
    e: Exception


@dataclass
class InputDC:
    fn: Any
    input_type: type
    output_type: type


def dff00(i: int, j: int) -> int: ...
def dff01(i: int = 1) -> str: ...
def dff02(*i: int) -> int: ...
def dcf05() -> str: ...
def dcf06(i: str) -> None: ...
def dcf07(i: str): ...
def dcf08(i) -> int: ...  # type: ignore


dcfailing = [
    InputFailing(
        dff00,
        InvalidFunction(
            "Should take a single input",
            dff00,
        ),
    ),
    InputFailing(
        dff02,
        InvalidFunction(
            "Cannot have variadic inputs",
            dff02,
        ),
    ),
    InputFailing(
        dcf05,
        InvalidFunction(
            "Should take a single input",
            dcf05,
        ),
    ),
    InputFailing(
        dcf06,
        InvalidFunction(
            "Cannot have a return type 'None'",
            dcf06,
        ),
    ),
    InputFailing(
        dcf07,
        InvalidFunction(
            "Cannot have a return type 'None'",
            dcf07,
        ),
    ),
    InputFailing(
        dcf08,
        InvalidFunction(
            "Parameters should have valid type hint",
            dcf08,
        ),
    ),
]


def dcp03(r: float) -> str:
    return 1


dcpassing = [
    InputDC(dcp03, float, str),
]

dcfailingruntime = [
    InputFailing(
        dcp03,
        TypeError(
            "Expected <str> but received <int> from function <dcp03>",
        ),
    ),
]


def dcp04(r: float) -> str:
    return str(r)


dcpassingruntime = [
    (dcp04, str),
]
