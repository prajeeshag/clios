# type: ignore

import pytest
from calculator import app
from parameters import parameters

from clios.ast_builder import ASTBuilder
from clios.tokenizer import tokenize


@pytest.mark.parametrize("input, output", parameters)
def test(input: list[str], output: str):
    parser = ASTBuilder(app._operators)
    tokens = tokenize(input)
    op = parser.parse_tokens(tokens, return_value=True)
    assert op.execute() == output
