# type: ignore

import sys

import pytest
from calc import operators
from parameters import parameters

from clios import Clios


@pytest.mark.parametrize("input, output", parameters)
def test(input: list[str], output: str, capsys):
    sys.argv = ["calc", *input]
    Clios(operators)()
    captured = capsys.readouterr()
    assert captured.out == f"{output}\n"
