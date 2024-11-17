# type: ignore
import pytest

from clios.core.operator_fn import Parameter, ParameterKind
from clios.core.param_info import Input, Param


@pytest.fixture
def param_input():
    return Parameter(
        name="test_input",
        kind=ParameterKind.POSITIONAL_ONLY,
        info=Input(strict=True),
        annotation=int,
    )


@pytest.fixture
def param_kwds():
    return Parameter(
        name="test_param",
        kind=ParameterKind.KEYWORD_ONLY,
        info=Param(strict=False),
        annotation=str,
    )


@pytest.fixture
def param_positional():
    return Parameter(
        name="test_param",
        kind=ParameterKind.POSITIONAL_ONLY,
        info=Param(strict=False),
        annotation=str,
    )


def test_is_input(param_input, param_kwds):
    assert param_input.is_input is True
    assert param_kwds.is_input is False


def test_is_param(param_input, param_kwds):
    assert param_input.is_param is False
    assert param_kwds.is_param is True


def test_type_(param_input, param_kwds):
    assert param_input.type_ is int
    assert param_kwds.type_ is str


def test_is_variadic_input(param_input, param_kwds):
    assert param_input.is_var_input is False
    assert param_kwds.is_var_input is False


def test_is_keyword_param(param_input, param_kwds):
    assert param_input.is_keyword_param is False
    assert param_kwds.is_keyword_param is True


def test_is_positional_param(param_input, param_positional):
    assert param_input.is_positional_param is False
    assert param_positional.is_positional_param is True


def test_is_keyword(param_input, param_kwds):
    assert param_input.is_keyword_param is False
    assert param_kwds.is_keyword_param is True


def test_is_positional(param_input, param_kwds):
    assert param_input.is_positional is True
    assert param_kwds.is_positional is False
