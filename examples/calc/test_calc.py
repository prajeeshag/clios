# type: ignore

import pytest
from parameters import parameters

from clios.cli.ast_builder import ASTBuilder
from clios.cli.tokenizer import tokenize
from examples.calc.calc import app


@pytest.mark.parametrize("input, output", parameters)
def test(input: list[str], output: str):
    parser = ASTBuilder(app.operators_db)
    tokens = tokenize(input)
    op = parser.parse_tokens(tokens, return_value=True)
    assert op.execute() == output
