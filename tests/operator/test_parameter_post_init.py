# type: ignore

import pytest

from clios.operator.model import InputType, Parameter, ParameterKind


@pytest.fixture
def mock_type_adapter(mocker):
    return mocker.patch("clios.operator.model.TypeAdapter")


def test_post_init_with_var_positional_kind(mock_type_adapter):
    Parameter(
        name="param",
        kind=ParameterKind.VAR_POSITIONAL,
        input_type=InputType.PARAMETER,
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(list[int])


def test_post_init_with_var_keyword_kind(mock_type_adapter):
    Parameter(
        name="param",
        kind=ParameterKind.VAR_KEYWORD,
        input_type=InputType.PARAMETER,
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(dict[str, int])


def test_post_init_with_positional_only_kind(mock_type_adapter):
    Parameter(
        name="param",
        kind=ParameterKind.POSITIONAL_ONLY,
        input_type=InputType.PARAMETER,
        annotation=int,
    )
    mock_type_adapter.assert_called_once_with(int)
