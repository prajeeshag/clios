# type: ignore
import typing as t

import pytest
from pydantic import ValidationError

from clios.cli.main_parser import CliParser, ParserError
from clios.cli.param_parser import ParamParserError, StandardParamParser
from clios.cli.tokenizer import CliTokenizer
from clios.core.operator import RootOperator
from clios.core.operator_fn import OperatorFn, OperatorFns
from clios.core.param_info import Input, Output, Param

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


def op_2o() -> t.Annotated[int, Output(callback=print, num_outputs=2)]:
    return 1


def selvar(name: t.Annotated[str, Param()]):
    pass


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
    "op_2o": op_2o,
    "selvar": selvar,
}
operator_fns = OperatorFns()
param_parser = StandardParamParser()
for name, op in ops.items():
    operator_fns[name] = OperatorFn.from_def(op, param_parser=param_parser)


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
        ["-op_1i.py"],
        ParserError("Module `op_1i.py` not found!", ctx={"token_index": 0}),
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

invalids_inline_operator = [
    [
        ["-inline_empty.py"],
        ["inline_empty.py"],
        ParserError(
            "No OperatorFn found in module `inline_empty.py`!", ctx={"token_index": 0}
        ),
    ],
    [
        ["-inline_multiple.py"],
        ["inline_multiple.py"],
        ParserError(
            "Multiple OperatorFn found in module `inline_multiple.py`!",
            ctx={"token_index": 0},
        ),
    ],
]


@pytest.mark.parametrize("tokens, expected", invalids)
def test_get_operator_invalid(tokens, expected):
    tokenizer = CliTokenizer()
    parser = CliParser(
        tokenizer=tokenizer,
    )
    with pytest.raises(ParserError) as e:
        parser.get_operator(operator_fns, tokens)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("tokens, files_to_copy, expected", invalids_inline_operator)
def test_get_operator_invalid_inline_operator(
    tokens, files_to_copy, expected, copy_file
):
    tokenizer = CliTokenizer()
    parser = CliParser(
        tokenizer=tokenizer,
    )
    for file in files_to_copy:
        copy_file(file)

    with pytest.raises(ParserError) as e:
        parser.get_operator(operator_fns, tokens)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("tokens, expected, error", validation_errors)
def test_get_operator_validation_error(tokens, expected, error):
    tokenizer = CliTokenizer()
    parser = CliParser(
        tokenizer=tokenizer,
    )
    with pytest.raises(ParserError) as e:
        parser.get_operator(operator_fns, tokens)
    assert e.value.message == expected.message
    assert e.value.ctx["token_index"] == expected.ctx["token_index"]
    assert isinstance(e.value.ctx["error"], error)
    assert expected.message in str(e.value)


def test_get_synopsis():
    tokenizer = CliTokenizer()
    parser = CliParser(
        tokenizer=tokenizer,
    )
    op_fn = operator_fns.get("op_1i1p1o")
    assert parser.get_synopsis(op_fn, "operator") == " -operator,ip i output"

    op_fn = operator_fns.get("op_2o")
    assert parser.get_synopsis(op_fn, "operator") == " -operator output1 output2"

    op_fn = operator_fns.get("op_1i")
    assert parser.get_synopsis(op_fn, "operator") == " -operator i"


@pytest.mark.parametrize(
    "input",
    [
        ["-op_1i1p1o,1", "1", "output"],
        ["-selvar,precip"],
    ],
)
def test_get_operator_passing(input):
    tokenizer = CliTokenizer()
    parser = CliParser(
        tokenizer=tokenizer,
    )

    operator = parser.get_operator(operator_fns, input)
    assert isinstance(operator, RootOperator)
