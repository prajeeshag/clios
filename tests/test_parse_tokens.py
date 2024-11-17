# type: ignore
import pytest
from pydantic import ValidationError

from clios.cli.ast_builder import _Empty
from clios.cli.tokenizer import LeftBracketToken
from clios.cli.tokenizer import OperatorToken as Ot
from clios.cli.tokenizer import StringToken as Ft
from clios.exceptions import ParserError

invalids = [
    [
        [Ft("f2"), Ot("op_not_found")],
        ParserError("Operator `f2` not found!", ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i"), Ot("op_not_found")],
        ParserError("Operator `op_not_found` not found!", ctx={"token_index": 1}),
    ],
    [
        [Ot("op_1i"), LeftBracketToken()],
        ParserError("This syntax is not supported yet!", ctx={"token_index": 1}),
    ],
    [
        [Ot("op_not_found")],
        ParserError("Operator `op_not_found` not found!", ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1o_noroot")],
        ParserError(
            "Operator `op_1o_noroot` cannot be used as root operator!",
            ctx={"token_index": 0},
        ),
    ],
    [
        [
            Ot("op_1i,1"),
        ],
        ParserError(
            "Too many arguments: expected 0, got 1",
            ctx={"token_index": 0},
        ),
    ],
    [
        [
            Ot("op_1i,a=1"),
        ],
        ParserError(
            "Unexpected keyword argument: `a`!", ctx={"token_index": 0, "arg_key": "a"}
        ),
    ],
    [
        [
            Ot("op_1i1k,ip=1,a=1"),
        ],
        ParserError(
            "Unexpected keyword argument: `a`!", ctx={"token_index": 0, "arg_key": "a"}
        ),
    ],
    [
        [
            Ot("op_1i1k"),
        ],
        ParserError(
            "Missing required keyword argument: `ip`!",
            ctx={"token_index": 0, "arg_key": "ip"},
        ),
    ],
    [
        [
            Ot("op_1i1p"),
        ],
        ParserError(
            "Missing arguments: expected atleast 1, got 0",
            ctx={"token_index": 0},
        ),
    ],
    [
        [
            Ot("op_1i1p,1,2"),
        ],
        ParserError(
            "Too many arguments: expected 1, got 2",
            ctx={"token_index": 0},
        ),
    ],
    [
        [Ot("op_vi"), Ot("op_1o"), Ot("op_1o"), Ot("op_1o"), Ot("op_")],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 4},
        ),
    ],
    [
        [Ot("op_2i"), Ot("op_1o"), Ot("op_1i1o"), Ot("op_")],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 2, "unchainable_token_index": 3},
        ),
    ],
    [
        [Ot("op_2i"), Ot("op_1o"), Ot("op_")],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 2},
        ),
    ],
    [
        [
            Ot("op_2i"),
            Ot("op_1i1o"),
            Ot("op_1i1o"),
            Ot("op_1i1o"),
            Ot("op_1o"),
            Ot("op_"),
        ],
        ParserError(
            "These operators cannot be chained together!",
            ctx={"token_index": 0, "unchainable_token_index": 5},
        ),
    ],
    [
        [Ot("op_1i1o")],
        ParserError("Missing output(s)!", ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i1o"), Ot("op_1o"), Ot("op_1o")],
        ParserError("Output file path must be a string", ctx={"token_index": 2}),
    ],
    [
        [Ot("op_1i"), Ot("op_1o"), Ot("op_1o")],
        ParserError("Got too many inputs!", ctx={"token_index": 2}),
    ],
    [
        [Ot("op_vi")],
        ParserError("Missing inputs!", ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i")],
        ParserError("Missing inputs!", ctx={"token_index": 0}),
    ],
]

build_validation_error = [
    [
        [Ot("op_1p,a")],
        {
            "error_type": "Data validation error!",
            "token_index": 0,
            "arg_index": 0,
        },
    ],
    [
        [Ot("op_1k,ip=a")],
        {
            "error_type": "Data validation error!",
            "token_index": 0,
            "arg_key": "ip",
        },
    ],
    [
        [Ot("op_1i"), Ft("input")],
        {
            "error_type": "Data validation error!",
            "token_index": 1,
        },
    ],
]


@pytest.mark.parametrize("input,expected", invalids)
def test_invalid(parser, input, expected):
    with pytest.raises(ParserError) as e:
        parser.parse_tokens(input)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("input,expected", build_validation_error)
def test_validation_error(parser, input, expected):
    with pytest.raises(ParserError) as e:
        parser.parse_tokens(input)
    assert str(e.value) == expected["error_type"]
    assert e.value.ctx["token_index"] == expected["token_index"]
    assert isinstance(e.value.ctx["validation_error"], ValidationError)
    if "arg_index" in expected:
        assert e.value.ctx["arg_index"] == expected["arg_index"]
    elif "arg_key" in expected:
        assert e.value.ctx["arg_key"] == expected["arg_key"]


def test_return_empty(parser):
    op = parser.parse_tokens([])
    assert isinstance(op, _Empty)
