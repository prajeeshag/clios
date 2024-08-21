# type: ignore
from typing import Annotated, Callable

from clios.operator import Generator as Ge
from clios.operator import Operator as Op
from clios.operator import Reader
from clios.operator._Operator import _BASE_DATA_READERS as dR
from clios.operator._Operator import _Input as I
from clios.operator._Operator import _Param as P


def _toBool(s: str) -> bool:
    return int(s) != 0


_toBoolReader = Reader(_toBool, bool)

passing = []


def fp00() -> int: ...


passing += [Ge(fp00, int)]


def fp02(input: int) -> int: ...


passing += [Op(fp02, int, input=I((int,)))]


def fp03(input: tuple[int]) -> int: ...


passing += [Op(fp03, int, input=I((int,)))]


def fp04(input: tuple[int, float, str]) -> int: ...


passing += [Op(fp04, int, input=I((int, float, str)))]


def fp05(input: list[int]) -> int: ...


passing += [Op(fp05, int, input=I((int,), var_list=True))]


def fp06(input: tuple[int, ...]) -> int: ...


passing += [Op(fp06, int, input=I((int,), var_tuple=True))]


def fp07(*params: int) -> int: ...


passing += [Ge(fp07, int, var_arg=P("*params", int, dR[int]))]


def fp08(i: int) -> int: ...


passing += [Ge(fp08, int, args=(P("i", int, dR[int]),))]


def fp09(input: tuple[int, str], i: int, j: str, *params: str) -> int: ...


passing += [
    Op(
        fp09,
        int,
        args=(
            P("i", int, dR[int]),
            P("j", str, dR[str]),
        ),
        var_arg=P("*params", str, dR[str]),
        input=I((int, str)),
    )
]


def fp10(ik: int = 1) -> int: ...


passing += [Ge(fp10, int, optional_kwargs=(P("ik", int, dR[int], 1),))]


def fp11(ik: int = 1, **kwds: str) -> int: ...


passing += [
    Ge(
        fp11,
        int,
        optional_kwargs=(P("ik", int, dR[int], 1),),
        var_kwarg=P("**kwds", str, dR[str]),
    )
]


def fp12(
    input: tuple[int, str],
    i: int,
    j: str,
    *params: str,
    ik: int = 10,
    sk: str = "hi",
    **kwargs: int,
) -> int: ...


passing += [
    Op(
        fp12,
        int,
        (P("i", int, dR[int]), P("j", str, dR[str])),
        P("*params", str, dR[str]),
        (),
        (
            P("ik", int, dR[int], 10),
            P("sk", str, dR[str], "hi"),
        ),
        P("**kwargs", int, dR[int]),
        input=I((int, str)),
    )
]


def fp13(input: list[bool]) -> int: ...


passing += [Op(fp13, int, input=I((bool,), var_list=True))]


def fp14(input: tuple[bool, ...]) -> int: ...


passing += [Op(fp14, int, input=I((bool,), var_tuple=True))]


def fp15(input: tuple[bool, int]) -> int: ...


passing += [Op(fp15, int, input=I((bool, int)))]


def fp16(i: Annotated[bool, _toBoolReader]) -> int: ...


passing += [Ge(fp16, int, (P("i", bool, _toBoolReader),))]


def fp17(input: int, i: int, j: int, *args: int, k: int, m: int) -> int: ...


passing += [
    Op(
        fp17,
        int,
        (P("i", int, dR[int]), P("j", int, dR[int])),
        P("*args", int, dR[int]),
        (P("k", int, dR[int]), P("m", int, dR[int])),
        input=I((int,)),
    )
]


def fp18(input: int, i: int, j: int, *args: int, k: int, m: int, n: int = 1) -> int: ...


passing += [
    Op(
        fp18,
        int,
        args=(P("i", int, dR[int]), P("j", int, dR[int])),
        required_kwargs=(P("k", int, dR[int]), P("m", int, dR[int])),
        optional_kwargs=(P("n", int, dR[int], 1),),
        var_arg=P("*args", int, dR[int]),
        input=I((int,)),
    ),
]


def fp19(input: Callable[str, str]) -> int: ...


passing += [
    Op(
        fp19,
        int,
        input=I((Callable[str, str],)),
    ),
]


def fp20(input: tuple[list[str]]) -> int: ...


passing += [
    Op(
        fp20,
        int,
        input=I((list[str],)),
    )
]


def fp21(input: list[tuple[str, ...]]) -> int: ...


passing += [
    Op(
        fp21,
        int,
        input=I((tuple[str, ...],), var_list=True),
    )
]
