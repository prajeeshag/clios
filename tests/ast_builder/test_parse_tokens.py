# type: ignore
import pytest
from pydantic import ValidationError

from clios import ParserError
from clios.ast_builder import ErrorType
from clios.tokenizer import OperatorToken as Ot
from clios.tokenizer import StringToken as Ft

invalids = [
    [
        [Ft("f2"), Ot("op_not_found")],
        ParserError(ErrorType.OPERATOR_NOT_FOUND, ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i"), Ot("op_not_found")],
        ParserError(ErrorType.OPERATOR_NOT_FOUND, ctx={"token_index": 1}),
    ],
    [
        [Ot("op_1o_noroot")],
        ParserError(ErrorType.UNSUPPORTED_ROOT_OPERATOR, ctx={"token_index": 0}),
    ],
    [
        [
            Ot("op_1i,1"),
        ],
        ParserError(
            ErrorType.TOO_MANY_ARGS, ctx={"token_index": 0, "expected_num_args": 0}
        ),
    ],
    [
        [
            Ot("op_1i,a=1"),
        ],
        ParserError(ErrorType.UNEXPECTED_KWD, ctx={"token_index": 0, "arg_key": "a"}),
    ],
    [
        [
            Ot("op_1i1k,ip=1,a=1"),
        ],
        ParserError(ErrorType.UNEXPECTED_KWD, ctx={"token_index": 0, "arg_key": "a"}),
    ],
    [
        [
            Ot("op_1i1k"),
        ],
        ParserError(
            ErrorType.MISSING_REQUIRED_KWD, ctx={"token_index": 0, "arg_key": "ip"}
        ),
    ],
    [
        [
            Ot("op_1i1p"),
        ],
        ParserError(
            ErrorType.TOO_FEW_ARGS, ctx={"token_index": 0, "expected_num_args": 1}
        ),
    ],
    [
        [
            Ot("op_1i1p,1,2"),
        ],
        ParserError(
            ErrorType.TOO_MANY_ARGS, ctx={"token_index": 0, "expected_num_args": 1}
        ),
    ],
    [
        [Ot("op_vi"), Ot("op_1o"), Ot("op_1o"), Ot("op_1o"), Ot("op_")],
        ParserError(
            ErrorType.CHAIN_TYPE_ERROR,
            ctx={"token_index": 0, "unchainable_token_index": 4},
        ),
    ],
    [
        [Ot("op_2i"), Ot("op_1o"), Ot("op_1i1o"), Ot("op_")],
        ParserError(
            ErrorType.CHAIN_TYPE_ERROR,
            ctx={"token_index": 2, "unchainable_token_index": 3},
        ),
    ],
    [
        [Ot("op_2i"), Ot("op_1o"), Ot("op_")],
        ParserError(
            ErrorType.CHAIN_TYPE_ERROR,
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
            ErrorType.CHAIN_TYPE_ERROR,
            ctx={"token_index": 0, "unchainable_token_index": 5},
        ),
    ],
    [
        [Ot("op_1i1o")],
        ParserError(ErrorType.MISSING_OUTPUT, ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i1o"), Ot("op_1o"), Ot("op_1o")],
        ParserError(ErrorType.MISSING_OUTPUT_FILE, ctx={"token_index": 2}),
    ],
    [
        [Ot("op_1i"), Ot("op_1o"), Ot("op_1o")],
        ParserError(ErrorType.TOO_MANY_INPUTS, ctx={"token_index": 2}),
    ],
    [
        [Ot("op_vi")],
        ParserError(ErrorType.TOO_FEW_INPUTS, ctx={"token_index": 0}),
    ],
    [
        [Ot("op_1i")],
        ParserError(ErrorType.MISSING_INPUTS, ctx={"token_index": 0}),
    ],
]

arg_validation_error = [
    [
        [Ot("op_1p,a")],
        {
            "error_type": ErrorType.ARG_VALIDATION_ERROR,
            "token_index": 0,
            "arg_index": 0,
        },
    ],
    [
        [Ot("op_1k,ip=a")],
        {
            "error_type": ErrorType.ARG_VALIDATION_ERROR,
            "token_index": 0,
            "arg_key": "ip",
        },
    ],
]


@pytest.mark.parametrize("input,expected", invalids)
def test_invalid(parser, input, expected):
    with pytest.raises(ParserError) as e:
        parser.parse_tokens(input)
    assert str(e.value) == str(expected)
    assert e.value.ctx == expected.ctx


@pytest.mark.parametrize("input,expected", arg_validation_error)
def test_validation_error(parser, input, expected):
    with pytest.raises(ParserError) as e:
        parser.parse_tokens(input)
    assert str(e.value) == expected["error_type"].value
    assert e.value.ctx["token_index"] == expected["token_index"]
    assert isinstance(e.value.ctx["validation_error"], ValidationError)
    if "arg_index" in expected:
        assert e.value.ctx["arg_index"] == expected["arg_index"]
    else:
        assert e.value.ctx["arg_key"] == expected["arg_key"]
