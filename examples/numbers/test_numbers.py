# type: ignore
import subprocess

import pytest
from parameters import parameters


@pytest.mark.parametrize("input, output", parameters)
def test(input: list[str], output: str, capsys):
    result = subprocess.run(
        ["python", "examples/numbers/numbers.py", *input],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == output
