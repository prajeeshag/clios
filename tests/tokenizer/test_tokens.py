# type: ignore

import pytest

from clios.exceptions import TokenError
from clios.tokenizer.tokens import (
    Colon,
    FilePathToken,
    LeftSquareBracket,
    RightSquareBracket,
)
from clios.tokenizer.tokens import OperatorToken as Optkn


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[", LeftSquareBracket()],
        ["]", None],
        ["[]", None],
        ["[s]", None],
        ["s", None],
    ],
)
def test_LeftSquareBracket(input: str, expected):
    assert LeftSquareBracket.factory(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["[", None],
        ["]", RightSquareBracket()],
        ["[]", None],
        ["[s]", None],
        ["s", None],
    ],
)
def test_RightSquareBracket(input: str, expected: bool):
    assert RightSquareBracket.factory(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        [":", Colon()],
        ["]", None],
        ["[:", None],
        ["[s", None],
    ],
)
def test_Colon(input: str, expected):
    assert Colon.factory(input) == expected


class Test_Optkn:
    parameters = (
        ("-simple,k1=v1=v2", (8, "Invalid parameter")),
        ("-simple,k1=v1,k1=v2", (14, "Parameter already assigned")),
        ("-simple,k2=v1,k1=v2,k2=v2", (20, "Parameter already assigned")),
        ["-operator,abc=", (10, "Invalid parameter")],
        [
            "-operator,abc=dfg,123",
            (18, "Positional parameter after keyword parameter is not allowed"),
        ],
    )

    @pytest.mark.parametrize("string,expected", parameters)
    def test_invalid(self, string: str, expected):
        with pytest.raises(TokenError) as result:
            Optkn.factory(string)

        assert result.value.pos == expected[0]
        assert str(result.value) == expected[1]
        assert result.value.token == string

    @pytest.mark.parametrize(
        "string,expected",
        (
            ["[", None],
            ["]", None],
            [":", None],
            ["-o", None],
            ["-O", None],
            ["-1", None],
            ["--operator", None],
            ["operator", None],
            ["/some/path/out.nc", None],
            ["some/path/out.nc", None],
            ["so-me/path/out.nc", None],
            ["some path out.nc", None],
            (
                "-simple",
                Optkn("simple"),
            ),
            (
                "-singleParam,p1",
                Optkn("singleParam", ("p1",)),
            ),
            (
                "-multiParam,p1,p2,p3",
                Optkn("multiParam", ("p1", "p2", "p3")),
            ),
            (
                "-singleOptionalParam,p1,,p3",
                Optkn("singleOptionalParam", ("p1", "", "p3")),
            ),
            (
                "-multiOptionalParam,,,p3",
                Optkn("multiOptionalParam", ("", "", "p3")),
            ),
            (
                "-endComma1,",
                Optkn("endComma1", ("",)),
            ),
            (
                "-endComma2,,p3,",
                Optkn("endComma2", ("", "p3", "")),
            ),
            (
                "-singleKwParam,k1=v1",
                Optkn("singleKwParam", (), tuple(dict(k1="v1").items())),
            ),
            (
                "-multiKwParam,k1=v1,k2=v2,k3=v3",
                Optkn(
                    "multiKwParam", (), tuple(dict(k1="v1", k2="v2", k3="v3").items())
                ),
            ),
            (
                "-mixed,p1,,,p3,k1=v1,k2=v2,k3=v3",
                Optkn(
                    "mixed",
                    ("p1", "", "", "p3"),
                    tuple(dict(k1="v1", k2="v2", k3="v3").items()),
                ),
            ),
        ),
    )
    def test_valid(self, string: str, expected):
        opArg = Optkn.factory(string)
        assert opArg == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ["-some/path/out.nc", None],
        ["[", None],
        ["]", None],
        [":", None],
        ["/some/path/out.nc", FilePathToken("/some/path/out.nc")],
        ["some/path/out.nc", FilePathToken("some/path/out.nc")],
        ["so-me/path/out.nc", FilePathToken("so-me/path/out.nc")],
        ["some path out.nc", FilePathToken("some path out.nc")],
        ["1", FilePathToken("1")],
        ["-1", FilePathToken("-1")],
    ],
)
def test_FilePathToken(input: str, expected: bool):
    assert FilePathToken.factory(input) == expected
