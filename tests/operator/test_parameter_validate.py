# type: ignore


import pytest
from pydantic import ValidationError

from clios.operator.model import Parameter, ParameterKind
from clios.operator.params import Input, Param


def test_param_strict():
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Param(strict=True),
        annotation=int,
    )
    assert param.validate(1) == 1
    with pytest.raises(ValidationError):
        param.validate("1")


def test_param_nostrict():
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Param(),
        annotation=int,
    )
    assert param.validate(1) == 1
    assert param.validate("1") == 1
    assert param.validate("1.0") == 1


def test_input_nostrict():
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Input(strict=False),
        annotation=int,
    )
    assert param.validate(1) == 1
    assert param.validate("1") == 1
    assert param.validate("1.0") == 1


def test_input_strict():
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Input(),
        annotation=int,
    )
    assert param.validate(1) == 1
    with pytest.raises(ValidationError):
        param.validate("1")
