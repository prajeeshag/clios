# type: ignore
import pytest

from clios.exceptions import OperatorNotFound
from clios.tokenizer import OperatorToken as Ot


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            [Ot("op1")],
            OperatorNotFound("op1"),
        ],
    ],
)
def test_operator_not_found(mocker, parser, input, expected, operators):
    operators.get.side_effect = KeyError()
    with pytest.raises(OperatorNotFound) as e:
        parser.parse_tokens(input)
    assert e.value.operator == expected.operator
