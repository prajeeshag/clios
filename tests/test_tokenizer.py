# type: ignore

import pytest

from clios.exceptions import TokenError
from clios.tokenizer import (
    ColonToken,
    LeftBracketToken,
    OperatorToken,
    RightBracketToken,
    StringToken,
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
        ["-s:ssd", TokenType.INVALID],
    ],
)
def test_TokenType(input: str, expected: TokenType):
    assert TokenType(input) == expected


class Test_OperatorToken:
    parameters_invalid = (
        ("-simple,k1=v1=v2", (8, "Invalid parameter")),
        ("-simple,k1=v1,k1=v2", (14, "Parameter already assigned")),
        ("-simple,k2=v1,k1=v2,k2=v2", (20, "Parameter already assigned")),
        ["-operator,abc=", (10, "Invalid parameter")],
        [
            "-operator,abc=dfg,123",
            (18, "Positional parameter after keyword parameter is not allowed"),
        ],
    )
    parameters_valid = (
        (
            "-simple",
            ("simple", (), ()),
        ),
        (
            "-singleParam,p1",
            ("singleParam", ("p1",), ()),
        ),
        (
            "-multiParam,p1,p2,p3",
            ("multiParam", ("p1", "p2", "p3"), ()),
        ),
        (
            "-singleOptionalParam,p1,,p3",
            ("singleOptionalParam", ("p1", "", "p3"), ()),
        ),
        (
            "-multiOptionalParam,,,p3",
            ("multiOptionalParam", ("", "", "p3"), ()),
        ),
        (
            "-endComma1,",
            ("endComma1", ("",), ()),
        ),
        (
            "-endComma2,,p3,",
            ("endComma2", ("", "p3", ""), ()),
        ),
        (
            "-singleKwParam,k1=v1",
            ("singleKwParam", (), (("k1", "v1"),)),
        ),
        (
            "-multiKwParam,k1=v1,k2=v2,k3=v3",
            ("multiKwParam", (), tuple(dict(k1="v1", k2="v2", k3="v3").items())),
        ),
        (
            "-mixed,p1,,,p3,k1=v1,k2=v2,k3=v3",
            (
                "mixed",
                ("p1", "", "", "p3"),
                tuple(dict(k1="v1", k2="v2", k3="v3").items()),
            ),
        ),
    )

    @pytest.mark.parametrize("string,expected", parameters_invalid)
    def test_invalid(self, string: str, expected):
        with pytest.raises(TokenError) as result:
            OperatorToken(string)

        assert result.value.pos == expected[0]
        assert str(result.value) == expected[1]
        assert result.value.token == string

    @pytest.mark.parametrize("string,expected", parameters_valid)
    def test_valid(self, string: str, expected):
        opArg = OperatorToken(string)
        assert (opArg.name, opArg.args, opArg.kwds) == expected


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
