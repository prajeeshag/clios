# type: ignore
from typing import Any

import pytest

from clios.exceptions import InvalidFunction
from clios.operator import operator_factory

from .testdata.operator_invalid_fns import failing
from .testdata.operator_valid_fns import passing


@pytest.mark.parametrize("input", failing)
def test_failing(input):
    with pytest.raises(InvalidFunction) as e:
        operator_factory(input.fn)
    assert str(e.value) == str(input.e)
    assert e.value.fn == input.e.fn
    assert e.value.pname == input.e.pname


@pytest.mark.parametrize("input", passing)
def test_passing(input: Any):
    op = operator_factory(input.fn)
    assert op == input
