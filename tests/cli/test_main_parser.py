# type: ignore
import typing as t

import pytest
from pydantic import ValidationError

from clios.cli.main_parser import CliParser, ParserError
from clios.cli.param_parser import CliParamParser, ParamParserError
from clios.cli.tokenizer import CliTokenizer
from clios.core.operator import RootOperator
from clios.core.operator_fn import OperatorFn
from clios.core.param_info import Input, Output, Param
from clios.core.registry import OperatorRegistry

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


ops = {
    "op_": op_,
    "op_1o": op_1o,
    "op_1i": op_1i,
    "op_1I": op_1I,
    "op_2i": op_2i,
    "op_vi": op_vi,
    "op_1k": op_1k,
    "op_1p1k": op_1p1k,
    "op_1p": op_1p,
    "op_1K": op_1K,
    "op_1P": op_1P,
    "op_1p1o": op_1p1o,
    "op_1i1k": op_1i1k,
    "op_1i1p": op_1i1p,
    "op_1i1o": op_1i1o,
    "op_1i1p1o": op_1i1p1o,
    "op_1i1k1o": op_1i1k1o,
    "op_1o_noroot": op_1o_noroot,
}
operator_fns = OperatorRegistry()
param_parser = CliParamParser()
for name, op in ops.items():
    operator_fns.add(name, OperatorFn.validate(op, arg_parser=param_parser))


invalids = [
    [
        ["f2", "-op_1i"],
        ParserError("Operator `f2` not found!", ctx={"token_index": 0}),
    ],
    [
        ["-op_1i", "-op_not_found"],
        ParserError("Operator `op_not_found` not found!", ctx={"token_index": 1}),
    ],
    [
        ["-op_1i", "["],
        ParserError("This syntax is not supported yet!", ctx={"token_index": 1}),
    ],
    [
        ["-op_not_found"],
        ParserError("Operator `op_not_found` not found!", ctx={"token_index": 0}),
    ],
    [
        ["-op_1o_noroot"],
        ParserError(
            "Operator `op_1o_noroot` cannot be used as root operator!",
            ctx={"token_index": 0},
        ),
    ],
    [
        ["-op_vi", "-op_1o", "-op_1o", "-op_1o", "-op_"],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 4},
        ),
    ],
    [
        ["op_2i", "-op_1o", "-op_1i1o", "-op_"],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 2, "unchainable_token_index": 3},
        ),
    ],
    [
        ["op_2i", "-op_1o", "-op_"],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 2},
        ),
    ],
    [
        [
            "op_2i",
            "-op_1i1o",
            "-op_1i1o",
            "-op_1i1o",
            "-op_1o",
            "-op_",
        ],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 5},
        ),
    ],
    [
        ["-op_1i1o"],
        ParserError("Missing output(s)!", ctx={"token_index": 0}),
    ],
    [
        ["-op_1i1o", "-op_1o", "-op_1o"],
        ParserError("Output file path must be a string", ctx={"token_index": 2}),
    ],
    [
        ["op_1i", "-op_1o", "-op_1o"],
        ParserError(
            "Got too many inputs!", ctx={"token_index": 2, "num_extra_tokens": 1}
        ),
    ],
    [
        ["op_vi"],
        ParserError("Missing inputs for operator op_vi!", ctx={"token_index": 0}),
    ],
    [
        ["op_1i"],
        ParserError("Missing inputs for operator op_1i!", ctx={"token_index": 0}),
    ],
    [
        [],
        ParserError("Input is empty!"),
    ],
]

validation_errors = [
    [
        ["op_1i", "op_1o"],
        ParserError("Data validation failed for input op_1o!", ctx={"token_index": 1}),
        ValidationError,
    ],
    [
        [
            "op_1p",
        ],
        ParserError(
            "Failed to parse arguments for operator `op_1p`!", ctx={"token_index": 0}
        ),
        ParamParserError,
    ],
]


@pytest.mark.parametrize("tokens, expected", invalids)
def test_get_operator_invalid(tokens, expected):
    tokenizer = CliTokenizer()
    parser = CliParser(
        operator_fns=operator_fns,
        tokenizer=tokenizer,
    )
    with pytest.raises(ParserError) as e:
        parser.get_operator(tokens)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("tokens, expected, error", validation_errors)
def test_get_operator_validation_error(tokens, expected, error):
    tokenizer = CliTokenizer()
    parser = CliParser(
        operator_fns=operator_fns,
        tokenizer=tokenizer,
    )
    with pytest.raises(ParserError) as e:
        parser.get_operator(tokens)
    assert str(e.value) == str(expected)
    assert e.value.ctx["token_index"] == expected.ctx["token_index"]
    assert isinstance(e.value.ctx["error"], error)


def test_get_synopsis():
    tokenizer = CliTokenizer()
    parser = CliParser(
        operator_fns=operator_fns,
        tokenizer=tokenizer,
    )
    assert parser.get_synopsis("op_1i1p1o") == "op_1i1p1o,ip i output"


def test_get_synopsis_fail():
    tokenizer = CliTokenizer()
    parser = CliParser(
        operator_fns=operator_fns,
        tokenizer=tokenizer,
    )
    with pytest.raises(ParserError):
        parser.get_synopsis("f2")


def test_get_operator_passing():
    tokenizer = CliTokenizer()
    parser = CliParser(
        operator_fns=operator_fns,
        tokenizer=tokenizer,
    )
    operator = parser.get_operator(["-op_1i1p1o,1", "1", "output"])
    assert isinstance(operator, RootOperator)
