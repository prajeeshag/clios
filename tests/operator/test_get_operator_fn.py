# type: ignore
import pytest
from pydantic import ValidationError

from clios.operator.utils import get_operator_fn

from .testdata.operator_invalid_fns import failing, failing_parameter_validation
from .testdata.operator_valid_fns import passing


@pytest.mark.parametrize("input", failing)
def test_failing(input):
    with pytest.raises(AssertionError) as e:
        get_operator_fn(input.fn)
    assert str(e.value) == str(input.e)


@pytest.mark.parametrize("input", failing_parameter_validation)
def test_failing_parameter_validation(input):
    with pytest.raises(ValidationError):
        get_operator_fn(input.fn)


@pytest.mark.parametrize("input, Expected", passing)
def test_passing(input, Expected):
    result = get_operator_fn(input, implicit="param")
    assert result == Expected


def test_implicit_invalid():
    def dummy(i: int):
        pass

    with pytest.raises(AssertionError) as e:
        get_operator_fn(dummy, implicit="invalid")

    assert str(e.value) == "Invalid implicit option `invalid`"
