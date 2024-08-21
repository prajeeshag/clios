# type: ignore

import pytest

from clios.exceptions import TokenError
from clios.tokenizer.tokens import (
    FilePathToken,
    LeftSquareBracket,
    OperatorToken,
    RightSquareBracket,
    Tokenizer,
)

lSqB = LeftSquareBracket()
rSqB = RightSquareBracket()
opToken = OperatorToken("operator")
fileToken = FilePathToken("file.nc")


@pytest.fixture
def tokenizer():
    return Tokenizer(
        [
            LeftSquareBracket,
            RightSquareBracket,
            OperatorToken,
            FilePathToken,
        ]
    )


class Test_tokenize:
    @pytest.mark.parametrize(
        "input,expected",
        [
            ["[", lSqB],
            ["-operator", opToken],
            ["file.nc", fileToken],
            ["1", FilePathToken("1")],
        ],
    )
    def test_valid(self, input: str, expected, tokenizer: Tokenizer):
        assert tokenizer.tokenize(input) == expected

    @pytest.mark.parametrize(
        "input,expected",
        [
            ["-a", TokenError("-a", msg="Unknown pattern")],
            ["-a:sa", TokenError("-a:sa", msg="Unknown pattern")],
            [
                "-abc,x=y=z",
                TokenError("-abc,x=y=z", msg="Invalid parameter", pos=5),
            ],
        ],
    )
    def test_invalid(self, tokenizer: Tokenizer, input, expected):
        with pytest.raises(TokenError) as e:
            tokenizer.tokenize(input)
        assert e.value.pos == expected.pos
        assert str(e.value) == str(expected)
