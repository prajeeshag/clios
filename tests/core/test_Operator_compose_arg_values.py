# type: ignore
import pytest

from clios.cli.tokenizer import OperatorToken as Ot
from clios.core.operator import LeafOperator
from clios.core.operator_fn import Parameter


@pytest.fixture
def operator_fn(mocker):
    return mocker.Mock()


@pytest.fixture
def param_mock(mocker):
    def _param_mock():
        return mocker.Mock(spec=Parameter)

    return _param_mock


@pytest.fixture
def op_base(mocker, operator_fn):
    return LeafOperator(operator_fn=operator_fn, token=Ot("test"))


def test__with_no_args_or_inputs(op_base):
    op_base.operator_fn.iter_positional_params.return_value = iter([])
    result = op_base._compose_arg_values([], [])
    assert result == []


def test__with_args_only(op_base, param_mock):
    param1 = param_mock()
    param2 = param_mock()
    param1.is_input = False
    param2.is_input = False
    op_base.operator_fn.iter_positional_params.return_value = iter([param1, param2])
    result = op_base._compose_arg_values([1, 2], [])
    assert result == [1, 2]


def test__with_inputs_only(op_base, param_mock):
    param1 = param_mock()
    param2 = param_mock()
    param1.is_input = True
    param2.is_input = True
    op_base.operator_fn.iter_positional_params.return_value = iter([param1, param2])
    result = op_base._compose_arg_values([], [3, 4])
    assert result == [3, 4]


def test__with_mixed_args_and_inputs(op_base, param_mock):
    param1 = param_mock()
    input1 = param_mock()
    param1.is_input = False
    input1.is_input = True
    op_base.operator_fn.iter_positional_params.return_value = iter([param1, input1])
    result = op_base._compose_arg_values([1], [2])
    assert result == [1, 2]


def test__args_and_inputs_shuffled(op_base, param_mock):
    param_input = param_mock()
    param_input.is_input = True
    param_arg = param_mock()
    param_arg.is_input = False
    op_base.operator_fn.iter_positional_params.return_value = iter(
        [param_arg, param_input, param_arg, param_input]
    )
    result = op_base._compose_arg_values([1, 3], [2, 4])
    assert result == [1, 2, 3, 4]


def test__var_args(op_base, param_mock):
    param_input = param_mock()
    param_input.is_input = True
    param_arg = param_mock()
    param_arg.is_input = False
    op_base.operator_fn.iter_positional_params.return_value = iter(
        [param_arg, param_input, param_arg, param_arg, param_arg, param_arg]
    )
    result = op_base._compose_arg_values([1, 3, 4], [2])
    assert result == [1, 2, 3, 4]
