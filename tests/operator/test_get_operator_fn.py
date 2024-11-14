# type: ignore


import pytest

from clios.operator.utils import get_operator_fn

from .testdata.operator_invalid_fns import failing
from .testdata.operator_valid_fns import passing


@pytest.mark.parametrize("input", failing)
def test_failing(input):
    with pytest.raises(AssertionError) as e:
        get_operator_fn(input.fn)
    assert str(e.value) == str(input.e)


@pytest.mark.parametrize("input, Expected", passing)
def test_passing(input, Expected):
    result = get_operator_fn(input)
    assert result == Expected
