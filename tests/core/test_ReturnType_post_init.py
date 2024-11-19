# type: ignore

from typing import Annotated

import pytest
from pydantic import Strict
from pydantic.functional_validators import (
    AfterValidator,
    BeforeValidator,
    PlainValidator,
    WrapValidator,
)

from clios.core.operator_fn import ReturnValue


@pytest.fixture
def mock_type_adapter(mocker):
    mocked_type_adapter = mocker.patch("clios.operator.model.TypeAdapter")
    mocked_type_adapter.return_value = "type_adapter"
    return mocked_type_adapter


def test_(mock_type_adapter):
    param = ReturnValue(
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(Annotated[int, Strict()])
    assert param._type_adapter == "type_adapter"


def test_after_validator(mock_type_adapter):
    param = ReturnValue(annotation=Annotated[int, AfterValidator(str)])
    mock_type_adapter.assert_called_once_with(Annotated[int, Strict()])
    assert param._type_adapter == "type_adapter"


def test_after_plain_wrap_validator(mock_type_adapter):
    param = ReturnValue(
        annotation=Annotated[
            int, PlainValidator(str), WrapValidator(str), AfterValidator(str)
        ]
    )
    mock_type_adapter.assert_called_once_with(Annotated[int, Strict()])
    assert param._type_adapter == "type_adapter"


def test_before_validator(mock_type_adapter):
    param = ReturnValue(annotation=Annotated[int, BeforeValidator(str)])
    mock_type_adapter.assert_called_once_with(
        Annotated[int, BeforeValidator(str), Strict()]
    )
    assert param._type_adapter == "type_adapter"
