# type: ignore
import pytest

from clios.exceptions import ArgumentError
from clios.operator.operator import _OpBase  # type: ignore


# mock OperatorFn
@pytest.fixture
def mock_operator_fn(mocker):
    operator_fn = mocker.patch("clios.operator.operator.OperatorFn", autospec=True)
    operator_fn.required_args = []
    operator_fn.args = []
    operator_fn.var_args = None
    operator_fn.required_kwds_keys = []
    operator_fn.var_kwds = None
    return operator_fn


def test_arg_less_than_required(mock_operator_fn):
    mock_operator_fn.required_args = ["a", "b"]
    with pytest.raises(ArgumentError):
        _OpBase(operator_fn=mock_operator_fn, args=(), kwds={})


def test_arg_gt_positional_no_var_arg(mock_operator_fn):
    mock_operator_fn.required_args = ["a", "b"]
    mock_operator_fn.args = ["a", "b", 1]
    mock_operator_fn.var_args = None
    with pytest.raises(ArgumentError):
        _OpBase(operator_fn=mock_operator_fn, args=(1, 2, 3, 4), kwds={})


def test_arg_gt_positional_with_var_arg(mock_operator_fn):
    mock_operator_fn.required_args = ["a", "b"]
    mock_operator_fn.args = ["a", "b", 1]
    mock_operator_fn.var_args = "var_args"
    _OpBase(operator_fn=mock_operator_fn, args=(1, 2, 3, 4), kwds={})


def test_required_kwd_missing(mock_operator_fn):
    mock_operator_fn.required_kwds_keys = ["a"]
    with pytest.raises(ArgumentError):
        _OpBase(operator_fn=mock_operator_fn, args=(), kwds={})


def test_more_kwds(mock_operator_fn):
    mock_operator_fn.kwds_keys = ["a"]
    with pytest.raises(ArgumentError):
        _OpBase(operator_fn=mock_operator_fn, args=(), kwds={"a": 1, "b": 2})


def test_more_kwds_with_varkwds(mock_operator_fn):
    mock_operator_fn.kwds_keys = ["a"]
    mock_operator_fn.var_kwds = "var_kwds"
    _OpBase(operator_fn=mock_operator_fn, args=(), kwds={"a": 1, "b": 2})
