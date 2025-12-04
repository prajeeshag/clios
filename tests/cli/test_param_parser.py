# type: ignore
import typing as t

import pytest
from pydantic import ValidationError

from clios.cli.param_parser import StandardParamParser
from clios.core.operator_fn import OperatorFn
from clios.core.param_info import Input, Output, Param
from clios.core.param_parser import ParamParserError as ParserError

intOut = t.Annotated[int, Output(callback=print)]
intParam = t.Annotated[int, Param()]
intIn = t.Annotated[int, Input()]
IntParam = t.Annotated[int, Param(core_validation_phase="execute")]
IntIn = t.Annotated[int, Input(core_validation_phase="execute")]


def op_():
    pass


def op_1o_noroot() -> int:
    pass


def op_1i(i: intIn):
    "op_1i i"
    pass


def op_1I(i: IntIn):
    "op_1I i"
    pass


def op_2i(i: intIn, j: intIn):
    pass


def op_1o() -> intOut:
    return 1


def op_vi(*i: intIn):
    pass


def op_1k(*, ip: intParam):
    pass


def op_1p1k(ip: intParam, *, ik: intParam):
    pass


def op_1p(ip: intParam):
    pass


def selvar(name: t.Annotated[str, Param()]):
    pass


def op_1K(*, ip: IntParam):
    pass


def op_1P(ip: IntParam):
    pass


def op_1p1o(ip: intParam) -> intOut:
    return 1


def op_1i1k(i: intIn, *, ip: intParam):
    pass


def op_1i1p(i: intIn, ip: intParam):
    pass


def op_1i1o(i: intIn) -> intOut:
    return 1


def op_1i1p1o(i: intIn, ip: intParam) -> intOut:
    return 1


def op_1i1k1o(i: intIn, *, ip: intParam) -> intOut:
    return 1


invalid_operators = [
    [
        [
            "1",
            op_1i,
        ],
        ParserError(
            "Too many arguments: expected 0 argument(s)!", ctx={"spos": 0, "epos": 1}
        ),
    ],
    [
        [
            "a=1",
            op_1i,
        ],
        ParserError("Unknown keyword argument `a`!", ctx={"spos": 0, "epos": 3}),
    ],
    [
        [
            "i&p=1",
            op_1i1k,
        ],
        ParserError("Invalid keyword argument name `i&p`!", ctx={"spos": 0, "epos": 5}),
    ],
    [
        [
            "ip=1,ip=1",
            op_1i1k,
        ],
        ParserError("Duplicate keyword argument `ip`!", ctx={"spos": 5, "epos": 9}),
    ],
    [
        [
            "ip=1,1",
            op_1i1k,
        ],
        ParserError(
            "Positional argument after keyword argument is not allowed!",
            ctx={"spos": 5, "epos": 6},
        ),
    ],
    [
        [
            "",
            op_1i1k,
        ],
        ParserError(
            "Missing required keyword argument `ip`!", ctx={"spos": 0, "epos": 0}
        ),
    ],
    [
        [
            "",
            op_1i1p,
        ],
        ParserError(
            "Missing arguments: expected atleast 1, got 0 argument(s)!",
            ctx={"spos": 0, "epos": 0},
        ),
    ],
    [
        [
            "1,2",
            op_1i1p,
        ],
        ParserError(
            "Too many arguments: expected 1 argument(s)!",
            ctx={"spos": 2, "epos": 3},
        ),
    ],
]

build_error = [
    [
        ["a", op_1p],
        ParserError("Data validation failed for argument!", ctx={"spos": 0, "epos": 1}),
    ],
    [
        ["ip=a", op_1k],
        ParserError(
            "Data validation failed for argument `ip`!", ctx={"spos": 0, "epos": 4}
        ),
    ],
]


@pytest.mark.parametrize("input,expected", invalid_operators)
def test_parse_arguments(input, expected):
    parser = StandardParamParser()
    parameters = OperatorFn.from_def(input[1], parser, implicit="input").parameters

    with pytest.raises(ParserError) as e:
        parser.parse_arguments(input[0], parameters)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("input,expected", build_error)
def test_parse_arguments_build_error(input, expected):
    parser = StandardParamParser()
    parameters = OperatorFn.from_def(input[1], parser, implicit="input").parameters

    with pytest.raises(ParserError) as e:
        parser.parse_arguments(input[0], parameters)

    assert e.value.message == expected.message
    assert e.value.ctx["spos"] == expected.ctx["spos"]
    assert e.value.ctx["epos"] == expected.ctx["epos"]
    assert isinstance(e.value.ctx["error"], ValidationError)
    assert str(e.value)


@pytest.mark.parametrize(
    "fn,input,expected",
    [
        [op_1p, "100", [(100,), ()]],
        [selvar, "name", [("name",), ()]],
        [op_1p1k, "1,ik=1", [(1,), (("ik", 1),)]],
    ],
)
def test_valid(fn, input, expected):
    parser = StandardParamParser()
    parameters = OperatorFn.from_def(fn, parser, implicit="param").parameters
    param_values = parser.parse_arguments(input, parameters)
    assert param_values[0] == expected[0]
    assert param_values[1] == expected[1]


def test_valid_single():
    parser = StandardParamParser()
    parameters = OperatorFn.from_def(op_1i1p1o, parser, implicit="input").parameters
    param_values = parser.parse_arguments("1", parameters)
    assert param_values[0] == (1,)


def get_synopsis_input():
    parser = StandardParamParser()
    res = []

    def fn1(
        input: int,
        p1: intParam,
        p2: intParam = 10,
        *args: intParam,
        k1: intParam,
        k2: intParam = 10,
        **kwds: intParam,
    ) -> int:
        pass

    res.append(
        [
            parser,
            OperatorFn.from_def(fn1, parser, implicit="input").parameters,
            ",p1[,p2,*args],k1=<val>[,k2=<val>,**kwds]",
        ]
    )

    def fn2(
        p2: intParam = 10,
    ) -> int:
        pass

    res.append(
        [parser, OperatorFn.from_def(fn2, parser, implicit="input").parameters, "[,p2]"]
    )

    return res


@pytest.mark.parametrize("parser, parameters, expected", get_synopsis_input())
def test_get_synopsis(parser, parameters, expected):
    assert parser.get_synopsis(parameters, lsep=",") == expected
