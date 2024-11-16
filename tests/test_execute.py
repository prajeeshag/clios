# type: ignore
import pytest
from pydantic import ValidationError

from clios.operator.operator import ErrorType, OperatorError, RootOperator
from clios.tokenizer import OperatorToken as Ot
from clios.tokenizer import StringToken as Ft

execute_validation_error = [
    [
        [Ot("op_1P,a")],
        {
            "error_type": ErrorType.ARG_VALIDATION_ERROR,
            "token": Ot("op_1P,a"),
            "arg_index": 0,
        },
    ],
    [
        [Ot("op_1K,ip=a")],
        {
            "error_type": ErrorType.ARG_VALIDATION_ERROR,
            "token": Ot("op_1K,ip=a"),
            "arg_key": "ip",
        },
    ],
    [
        [Ot("op_1I"), Ft("input")],
        {
            "error_type": ErrorType.INPUT_VALIDATION_ERROR,
            "token": Ft("input"),
        },
    ],
]


@pytest.mark.parametrize("input,expected", execute_validation_error)
def test_validation_error(parser, input, expected):
    op = parser.parse_tokens(input)
    with pytest.raises(OperatorError) as e:
        op.execute()
    assert str(e.value) == expected["error_type"].value
    assert e.value.ctx["token"] == expected["token"]
    assert isinstance(e.value.ctx["validation_error"], ValidationError)
    if "arg_index" in expected:
        assert e.value.ctx["arg_index"] == expected["arg_index"]
    elif "arg_key" in expected:
        assert e.value.ctx["arg_key"] == expected["arg_key"]


valid = [
    [[Ot("op_")], "op_"],
    [[Ot("op_1i"), Ot("op_1p1o,1")], "op_1i [ op_1p1o,1 ]"],
    [
        [Ot("op_1i1o"), Ot("op_1p1o,1"), Ft("output")],
        "output [ op_1i1o [ op_1p1o,1 ] ]",
    ],
    [[Ot("op_1i"), Ft("100")], "op_1i [ 100 ]"],
]


@pytest.mark.parametrize("input,expected_draw", valid)
def test_valid(parser, input, expected_draw):
    op = parser.parse_tokens(input)
    assert isinstance(op, RootOperator)
    assert op.draw() == expected_draw
    op.execute()
