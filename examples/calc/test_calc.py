# type: ignore

import sys

import pytest
from calc import app
from parameters import parameters


@pytest.mark.parametrize("input, output", parameters)
def test(input: list[str], output: str, capsys):
    sys.argv = ["calc", *input]
    app()
    captured = capsys.readouterr()
    assert captured.out == f"{output}\n"
