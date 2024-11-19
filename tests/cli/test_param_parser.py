# type: ignore
import typing as t

import pytest
from pydantic import ValidationError

from clios.cli.param_parser import CliParamParser
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
            "op_1i,1",
            op_1i,
        ],
        ParserError(
            "Too many arguments: expected 0 argument(s)!", "op_1i,1", spos=6, epos=7
        ),
    ],
    [
        [
            "op_1i,a=1",
            op_1i,
        ],
        ParserError("Unknown keyword argument `a`!", "op_1i,a=1", spos=6, epos=9),
    ],
    [
        [
            "op_1i1k,ip=1,a=1",
            op_1i1k,
        ],
        ParserError(
            "Unknown keyword argument `a`!", "op_1i1k,ip=1,a=1", spos=13, epos=16
        ),
    ],
    [
        [
            "op_1i1k,ip=1,ip=1",
            op_1i1k,
        ],
        ParserError(
            "Duplicate keyword argument `ip`!", "op_1i1k,ip=1,ip=1", spos=13, epos=17
        ),
    ],
    [
        [
            "op_1i1k,ip=1,1",
            op_1i1k,
        ],
        ParserError(
            "Positional argument after keyword argument is not allowed!",
            "op_1i1k,ip=1,1",
            spos=13,
            epos=14,
        ),
    ],
    [
        [
            "op_1i1k",
            op_1i1k,
        ],
        ParserError(
            "Missing required keyword argument `ip`!", "op_1i1k", spos=0, epos=7
        ),
    ],
    [
        [
            "op_1i1p",
            op_1i1p,
        ],
        ParserError(
            "Missing arguments: expected atleast 1, got 0 argument(s)!",
            spos=0,
            epos=7,
        ),
    ],
    [
        [
            "op_1i1p,1,2",
            op_1i1p,
        ],
        ParserError(
            "Too many arguments: expected 1 argument(s)!",
            spos=10,
            epos=11,
        ),
    ],
]

build_validation_error = [
    [
        ["op_1p,a", op_1p],
        ParserError("Data validation failed for argument!", spos=6, epos=7),
    ],
    [
        ["op_1k,ip=a", op_1k],
        ParserError("Data validation failed for argument `ip`!", spos=6, epos=10),
    ],
]


@pytest.mark.parametrize("input,expected", invalid_operators)
def test_parse_arguments(input, expected):
    parser = CliParamParser()
    parameters = OperatorFn.validate(input[1], parser).parameters

    with pytest.raises(ParserError) as e:
        parser.parse_arguments(input[0], parameters)
    assert str(e.value) == str(expected)
    assert e.value.spos == expected.spos
    assert e.value.epos == expected.epos


@pytest.mark.parametrize("input,expected", build_validation_error)
def test_parse_arguments_build_validation_error(input, expected):
    parser = CliParamParser()
    parameters = OperatorFn.validate(input[1], parser).parameters

    with pytest.raises(ParserError) as e:
        parser.parse_arguments(input[0], parameters)

    assert str(e.value) == str(expected)
    assert e.value.spos == expected.spos
    assert e.value.epos == expected.epos
    assert isinstance(e.value.ctx["validation_error"], ValidationError)


def test_get_name():
    parser = CliParamParser()
    assert parser.get_name("op_1i1p,1,2") == "op_1i1p"


def test_valid():
    parser = CliParamParser()
    parameters = OperatorFn.validate(op_1p1k, parser, implicit="param").parameters
    param_values = parser.parse_arguments("op_1p1k,1,ik=1", parameters)
    assert param_values[0].val == 1
    assert param_values[0].key == ""
    assert param_values[1].val == 1
    assert param_values[1].key == "ik"


def test_get_synopsis():
    parser = CliParamParser()

    def fn(
        input: int,
        p1: intParam,
        p2: intParam = 10,
        *args: intParam,
        k1: intParam,
        k2: intParam = 10,
        **kwds: intParam,
    ) -> int:
        pass

    expected = ",p1[,p2,*args],k1=<val>[,k2=<val>,**kwds]"
    parameters = OperatorFn.validate(fn, parser).parameters
    assert parser.get_synopsis(parameters, "") == expected


# def test_return_empty(parser):
#     op = parser.parse_tokens([])
#     assert isinstance(op, _Empty)
