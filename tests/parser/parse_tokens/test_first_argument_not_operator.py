# type: ignore
import pytest

from clio.exceptions import OperatorNotFound
from clio.tokenizer import FilePathToken as Ft
from clio.tokenizer import OperatorToken as Ot


@pytest.mark.parametrize(
    "input,expected",
    [
        [[Ft("f2"), Ot("op2")], OperatorNotFound("f2")],
    ],
)
def test_first_argument_not_operator(mocker, parser, input, expected):
    with pytest.raises(OperatorNotFound) as e:
        parser.parse_tokens(input)
    assert e.value.operator == expected.operator
