# type: ignore

from typing import Annotated

import pytest
from pydantic import Strict

from clios.operator.model import Parameter, ParameterKind
from clios.operator.params import Input, Param


@pytest.fixture
def mock_type_adapter(mocker):
    mocked_type_adapter = mocker.patch("clios.operator.model.TypeAdapter")
    mocked_type_adapter.return_value = "type_adapter"
    return mocked_type_adapter


def test_post_init_with_var_positional_kind(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.VAR_POSITIONAL,
        param_type=Param(),
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(int)
    assert param._type_adapter == "type_adapter"


def test_post_init_with_var_keyword_kind(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.VAR_KEYWORD,
        param_type=Param(),
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(int)
    assert param._type_adapter == "type_adapter"


def test_post_init_with_positional_only_kind(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Param(),
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(int)
    assert param._type_adapter == "type_adapter"


def test_post_init_with_strict(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Param(strict=True),
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(Annotated[int, Strict()])
    assert param._type_adapter == "type_adapter"


def test_post_init_with_var_input(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.VAR_POSITIONAL,
        param_type=Input(strict=True),
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(Annotated[int, Strict()])
    assert param._type_adapter == "type_adapter"


def test_post_init_with_extra_annotation(mock_type_adapter):
    param = Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        param_type=Input(strict=True),
        annotation=Annotated[list[int], "extra annotation"],
    )
    mock_type_adapter.assert_called_once_with(
        Annotated[list[int], "extra annotation", Strict()]
    )
    assert param._type_adapter == "type_adapter"
