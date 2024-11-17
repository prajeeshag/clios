# type: ignore
import pytest

from clios.core.arg_parser import OprArgParserAbc
from clios.core.operator_fn import OperatorFn
from clios.core.parameter import Parameters, ParamVal

from .testdata.operator_invalid_fns import failing, failing_parameter_validation
from .testdata.operator_valid_fns import passing


@pytest.fixture
def mock_arg_parser():
    class MockArgParser(OprArgParserAbc):
        def parse(self, string: str, parameters: Parameters) -> tuple[ParamVal, ...]:
            pass

        def synopsis(self, parameters: Parameters) -> str:
            pass

    return MockArgParser()


@pytest.mark.parametrize("input", failing)
def test_failing(input, mock_arg_parser):
    with pytest.raises(AssertionError) as e:
        OperatorFn.validate(input.fn, arg_parser=mock_arg_parser)
    assert str(e.value) == str(input.e)


@pytest.mark.parametrize("input", failing_parameter_validation)
def test_failing_parameter_validation(input, mock_arg_parser):
    with pytest.raises(AssertionError) as e:
        OperatorFn.validate(input.fn, arg_parser=mock_arg_parser)
    assert str(e.value) == str(input.e)


@pytest.mark.parametrize("input, Expected", passing)
def test_passing(input, Expected, mock_arg_parser):
    result = OperatorFn.validate(input, implicit="param", arg_parser=mock_arg_parser)
    assert result == Expected


def test_implicit_invalid(mock_arg_parser):
    def dummy(i: int):
        pass

    with pytest.raises(AssertionError) as e:
        OperatorFn.validate(dummy, implicit="invalid", arg_parser=mock_arg_parser)

    assert str(e.value) == "Invalid implicit option `invalid`"
