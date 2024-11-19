# type: ignore

import pytest

from clios.cli.tokenizer import (
    ColonToken,
    LeftBracketToken,
    OperatorToken,
    RightBracketToken,
    StringToken,
    TokenError,
    TokenType,
    tokenize,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[", TokenType.LEFT_BRACKET],
        ["]", TokenType.RIGHT_BRACKET],
        ["[]", TokenType.STRING],
        ["[s]", TokenType.STRING],
        ["s", TokenType.STRING],
        [":", TokenType.COLON],
        ["-simple,k1=v1=v2", TokenType.OPERATOR],
        ["-simple,k1=v1,k1=v2", TokenType.OPERATOR],
        ["-simple,k2=v1,k1=v2,k2=v2", TokenType.OPERATOR],
        ["-operator,abc=", TokenType.OPERATOR],
        ["-operator,abc=dfg,123", TokenType.OPERATOR],
        ["/some/path/out.nc", TokenType.STRING],
        ["some/path/out.nc", TokenType.STRING],
        ["so-me/path/out.nc", TokenType.STRING],
        ["some path out.nc", TokenType.STRING],
        ["1", TokenType.STRING],
        ["-1", TokenType.STRING],
        ["-100", TokenType.STRING],
    ],
)
def test_TokenType(input: str, expected: TokenType):
    assert TokenType(input) == expected


class Test_tokenize:
    @pytest.mark.parametrize(
        "args,expected",
        [
            (["-operator"], (OperatorToken("-operator"),)),
            (
                ["-operator", "hello"],
                (OperatorToken("-operator"), StringToken("hello")),
            ),
            (
                ["-operator", "hello", ":"],
                (OperatorToken("-operator"), StringToken("hello"), ColonToken()),
            ),
            (
                ["[", ":", "]"],
                (LeftBracketToken(), ColonToken(), RightBracketToken()),
            ),
            (
                ["-100"],
                (StringToken("-100"),),
            ),
            (
                ["-100", "-200"],
                (StringToken("-100"), StringToken("-200")),
            ),
        ],
    )
    def test_valid(self, args, expected):
        assert tokenize(args) == expected

    def test_tokenize_empty_list(self):
        args = []
        expected = ()
        assert tokenize(args) == expected

    def test_invalid(self):
        with pytest.raises(TokenError) as result:
            tokenize(["-inv[sk"])

        assert result.value.token == "-inv[sk"
        assert str(result.value) == "Unknown pattern"
