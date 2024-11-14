# type: ignore
from typing import Annotated

from clios.operator.model import InputType as PT
from clios.operator.model import OperatorFn as OpFn
from clios.operator.model import Parameter as P
from clios.operator.model import ParameterKind as PK
from clios.operator.params import Param

passing = []


def fp00() -> int: ...


passing += [(fp00, OpFn((), int, fp00))]


def fp02(input: int) -> int: ...


pfp02 = (P("input", PK.POSITIONAL_ONLY, PT.INPUT, int),)
passing += [(fp02, OpFn(pfp02, int, fp02))]


def fp03(input: tuple[int]) -> int: ...


pfp03 = (P("input", PK.POSITIONAL_ONLY, PT.INPUT, tuple[int]),)
passing += [(fp03, OpFn(pfp03, int, fp03))]


def fp04(input: list[int]) -> int: ...


pfp04 = (P("input", PK.POSITIONAL_ONLY, PT.VAR_INPUT, list[int]),)
passing += [(fp04, OpFn(pfp04, int, fp04))]


def fp06(input: Annotated[tuple[int, ...], Param()]) -> int: ...


passing += [
    (
        fp06,
        OpFn(
            (
                P(
                    "input",
                    PK.POSITIONAL_ONLY,
                    PT.PARAMETER,
                    Annotated[tuple[int, ...], Param()],
                ),
            ),
            int,
            fp06,
        ),
    )
]


def fp07(*params: int) -> int: ...


passing += [
    (
        fp07,
        OpFn(
            (P("params", PK.VAR_POSITIONAL, PT.PARAMETER, int),),
            int,
            fp07,
        ),
    )
]


def fp08(i: Annotated[int, Param()] = 10) -> int: ...


passing += [
    (
        fp08,
        OpFn(
            (P("i", PK.POSITIONAL_ONLY, PT.PARAMETER, Annotated[int, Param()], 10),),
            int,
            fp08,
        ),
    )
]


def fp09(*, i: Annotated[int, Param()] = 10) -> int: ...


passing += [
    (
        fp09,
        OpFn(
            (P("i", PK.KEYWORD_ONLY, PT.PARAMETER, Annotated[int, Param()], 10),),
            int,
            fp09,
        ),
    )
]


# def fp10(ik: int = 1) -> int: ...


# passing += [Ge(fp10, int, optional_kwargs=(P("ik", int, dR[int], 1),))]


# def fp11(ik: int = 1, **kwds: str) -> int: ...


# passing += [
#     Ge(
#         fp11,
#         int,
#         optional_kwargs=(P("ik", int, dR[int], 1),),
#         var_kwarg=P("**kwds", str, dR[str]),
#     )
# ]


# def fp12(
#     input: tuple[int, str],
#     i: int,
#     j: str,
#     *params: str,
#     ik: int = 10,
#     sk: str = "hi",
#     **kwargs: int,
# ) -> int: ...


# passing += [
#     Op(
#         fp12,
#         int,
#         (P("i", int, dR[int]), P("j", str, dR[str])),
#         P("*params", str, dR[str]),
#         (),
#         (
#             P("ik", int, dR[int], 10),
#             P("sk", str, dR[str], "hi"),
#         ),
#         P("**kwargs", int, dR[int]),
#         input=I((int, str)),
#     )
# ]


# def fp13(input: list[bool]) -> int: ...


# passing += [Op(fp13, int, input=I((bool,), var_list=True))]


# def fp14(input: tuple[bool, ...]) -> int: ...


# passing += [Op(fp14, int, input=I((bool,), var_tuple=True))]


# def fp15(input: tuple[bool, int]) -> int: ...


# passing += [Op(fp15, int, input=I((bool, int)))]


# def fp16(i: Annotated[bool, _toBoolReader]) -> int: ...


# passing += [Ge(fp16, int, (P("i", bool, _toBoolReader),))]


# def fp17(input: int, i: int, j: int, *args: int, k: int, m: int) -> int: ...


# passing += [
#     Op(
#         fp17,
#         int,
#         (P("i", int, dR[int]), P("j", int, dR[int])),
#         P("*args", int, dR[int]),
#         (P("k", int, dR[int]), P("m", int, dR[int])),
#         input=I((int,)),
#     )
# ]


# def fp18(input: int, i: int, j: int, *args: int, k: int, m: int, n: int = 1) -> int: ...


# passing += [
#     Op(
#         fp18,
#         int,
#         args=(P("i", int, dR[int]), P("j", int, dR[int])),
#         required_kwargs=(P("k", int, dR[int]), P("m", int, dR[int])),
#         optional_kwargs=(P("n", int, dR[int], 1),),
#         var_arg=P("*args", int, dR[int]),
#         input=I((int,)),
#     ),
# ]


# def fp19(input: Callable[str, str]) -> int: ...


# passing += [
#     Op(
#         fp19,
#         int,
#         input=I((Callable[str, str],)),
#     ),
# ]


# def fp20(input: tuple[list[str]]) -> int: ...


# passing += [
#     Op(
#         fp20,
#         int,
#         input=I((list[str],)),
#     )
# ]


# def fp21(input: list[tuple[str, ...]]) -> int: ...


# passing += [
#     Op(
#         fp21,
#         int,
#         input=I((tuple[str, ...],), var_list=True),
#     )
# ]
