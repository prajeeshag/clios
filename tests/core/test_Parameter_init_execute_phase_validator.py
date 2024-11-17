# type: ignore
from typing import Annotated, Any

import pytest
from pydantic import BeforeValidator, Strict

from clios.core.operator_fn import Parameter, ParameterKind
from clios.core.param_info import Param


@pytest.fixture
def parameter(mocker):
    mocker.patch("clios.operator.model.Parameter.__post_init__", return_value=None)

    def _parameter(param):
        return Parameter(
            name="test_param",
            kind=ParameterKind.POSITIONAL_ONLY,
            info=param,
            annotation=int,
        )

    return _parameter


@pytest.fixture
def type_adapter_mock(mocker):
    type_adapter_mock = mocker.patch("clios.operator.model.TypeAdapter")
    type_adapter_mock.return_value = "TypeAdapter"
    return type_adapter_mock


def test_with_build_phase_strict(parameter, type_adapter_mock):
    param_type = Param(
        execute_phase_validators=[int, str], core_validation_phase="build", strict=True
    )
    parameter_mock = parameter(param_type)
    parameter_mock._init_execute_phase_validator()

    type_adapter_mock.assert_called_once_with(
        Annotated[Any, BeforeValidator(int), BeforeValidator(str)]
    )
    assert parameter_mock._execute_phase_validator == "TypeAdapter"


def test_with_build_phase_nostrict(parameter, type_adapter_mock):
    param_type = Param(
        execute_phase_validators=[int, str], core_validation_phase="build"
    )
    parameter_mock = parameter(param_type)
    parameter_mock._init_execute_phase_validator()

    type_adapter_mock.assert_called_once_with(
        Annotated[Any, BeforeValidator(int), BeforeValidator(str)]
    )
    assert parameter_mock._execute_phase_validator == "TypeAdapter"


def test_with_execute_phase_nostrict(parameter, type_adapter_mock):
    param_type = Param(
        execute_phase_validators=[int, str], core_validation_phase="execute"
    )
    parameter_mock = parameter(param_type)
    parameter_mock._init_execute_phase_validator()

    type_adapter_mock.assert_called_once_with(
        Annotated[int, BeforeValidator(int), BeforeValidator(str)]
    )
    assert parameter_mock._execute_phase_validator == "TypeAdapter"


def test_with_execute_phase_strict(parameter, type_adapter_mock):
    param_type = Param(
        execute_phase_validators=[int, str],
        core_validation_phase="execute",
        strict=True,
    )
    parameter_mock = parameter(param_type)
    parameter_mock._init_execute_phase_validator()

    type_adapter_mock.assert_called_once_with(
        Annotated[int, BeforeValidator(int), BeforeValidator(str), Strict()]
    )
    assert parameter_mock._execute_phase_validator == "TypeAdapter"
